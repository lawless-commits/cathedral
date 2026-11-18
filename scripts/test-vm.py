#!/usr/bin/env python3
"""Boot the Cathedral ISO in QEMU with 1 GiB of RAM, once with BIOS and once
with UEFI (OVMF), and check that it reaches a login.

For each mode it logs in as root on the serial console, records free -m,
/etc/os-release, failed units and the kernel command line, takes screenshots
of the boot menu and of the console, then powers off. Everything goes to
test-results/. Exits non-zero if either mode fails.

Runs where QEMU and edk2-ovmf are installed (the container in scripts/ci.sh).
Standard library only.
"""

import glob
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time

RAM_MIB = 1024
RESULTS = "test-results"
BOOT_TIMEOUT = 600  # seconds to reach a login prompt (software emulation is slow)


def find_iso():
    isos = sorted(glob.glob("out/cathedral-*.iso"))
    if not isos:
        sys.exit("no out/cathedral-*.iso: build it first (scripts/build-iso.sh)")
    return isos[-1]


def find_ovmf():
    for code, vars_ in [
        ("/usr/share/edk2/x64/OVMF_CODE.4m.fd", "/usr/share/edk2/x64/OVMF_VARS.4m.fd"),
        ("/usr/share/edk2-ovmf/x64/OVMF_CODE.fd", "/usr/share/edk2-ovmf/x64/OVMF_VARS.fd"),
    ]:
        if os.path.exists(code) and os.path.exists(vars_):
            return code, vars_
    sys.exit("OVMF firmware not found; install edk2-ovmf")


def connect(path, timeout=20):
    deadline = time.time() + timeout
    while True:
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(path)
            return s
        except OSError:
            s.close()
            if time.time() > deadline:
                raise
            time.sleep(0.1)


class Serial:
    """Collects everything the guest writes to its serial port."""

    def __init__(self, sock, log_path):
        self.sock = sock
        self.buffer = ""
        self.lock = threading.Lock()
        self.log = open(log_path, "w", encoding="utf-8", errors="replace")
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        while True:
            try:
                data = self.sock.recv(4096)
            except OSError:
                return
            if not data:
                return
            text = data.decode("utf-8", errors="replace")
            with self.lock:
                self.buffer += text
            self.log.write(text)
            self.log.flush()

    def text(self):
        with self.lock:
            return self.buffer

    def wait_for(self, pattern, timeout, start=0):
        """Wait until regex `pattern` appears after offset `start`; return the match."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            match = re.search(pattern, self.text()[start:])
            if match:
                return match
            time.sleep(0.5)
        return None

    def send(self, line):
        self.sock.sendall((line + "\r").encode())


class Monitor:
    """The QEMU human monitor, for screenshots and key presses."""

    def __init__(self, path):
        self.sock = connect(path)
        self.sock.settimeout(2)
        self._drain()

    def _drain(self):
        try:
            while self.sock.recv(4096):
                pass
        except OSError:
            pass

    def command(self, line):
        self.sock.sendall((line + "\n").encode())
        time.sleep(1)
        self._drain()

    def screenshot(self, path):
        self.command(f"screendump {os.path.abspath(path)} -f png")


def run_mode(mode, iso, kvm):
    print(f"› {mode}: booting {os.path.basename(iso)} with {RAM_MIB} MiB RAM ({'KVM' if kvm else 'no KVM'})", flush=True)
    tmp = f"/tmp/cathedral-vm-{mode}"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    serial_sock, monitor_sock = f"{tmp}/serial.sock", f"{tmp}/monitor.sock"

    args = [
        "qemu-system-x86_64",
        "-m", str(RAM_MIB),
        "-smp", "2",
        "-accel", "kvm" if kvm else "tcg",
        "-cdrom", iso,
        "-boot", "d",
        "-vga", "std",
        "-display", "none",
        "-nic", "user,model=virtio-net-pci",
        "-chardev", f"socket,id=ser0,path={serial_sock},server=on,wait=off",
        "-serial", "chardev:ser0",
        "-monitor", f"unix:{monitor_sock},server=on,wait=off",
    ]
    if kvm:
        args += ["-cpu", "host"]
    if mode == "uefi":
        code, vars_template = find_ovmf()
        vars_copy = f"{tmp}/OVMF_VARS.fd"
        shutil.copy(vars_template, vars_copy)
        args += [
            "-drive", f"if=pflash,format=raw,readonly=on,file={code}",
            "-drive", f"if=pflash,format=raw,file={vars_copy}",
        ]

    qemu = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    result = {"mode": mode, "ok": False, "notes": []}
    try:
        serial = Serial(connect(serial_sock), f"{RESULTS}/{mode}-serial.log")
        monitor = Monitor(monitor_sock)

        # The boot menu waits 15 s; photograph it, then pick the default entry.
        time.sleep(8 if kvm else 20)
        monitor.screenshot(f"{RESULTS}/{mode}-boot-menu.png")
        monitor.command("sendkey ret")
        started = time.time()

        if not serial.wait_for(r"login:", BOOT_TIMEOUT):
            result["notes"].append(f"no login prompt on the serial console within {BOOT_TIMEOUT}s")
            monitor.screenshot(f"{RESULTS}/{mode}-stuck.png")
            return result
        result["boot_seconds"] = round(time.time() - started)
        print(f"› {mode}: login prompt after {result['boot_seconds']}s", flush=True)

        mark = len(serial.text())
        serial.send("root")
        # Root has no password on the live system; answer a prompt if one appears.
        if serial.wait_for(r"Password:", 5, mark):
            serial.send("")
        time.sleep(5)

        # Let start-up finish so free -m shows the settled idle state. The
        # markers are split with '' so the echoed command line does not match,
        # and start with @ because zsh expands words that start with =.
        # Pagers are off: a pager would wait for a key press forever.
        mark = len(serial.text())
        serial.send(
            "export SYSTEMD_PAGER= PAGER=cat; stty cols 250; "
            "systemctl is-system-running --wait; sleep 10; "
            "echo @@BEG''IN@@; cat /etc/os-release; echo @@FREE@@; free -m; "
            "echo @@FAILED@@; systemctl --failed --no-legend --plain --full; "
            "for u in $(systemctl --failed --no-legend --plain --full | cut -d' ' -f1); do "
            "systemctl status --full --lines=20 $u; done; "
            "echo @@CMDLINE@@; cat /proc/cmdline; uname -r; echo @@E''ND@@"
        )
        match = serial.wait_for(r"(?s)@@BEGIN@@(.*?)@@END@@", 300, mark)
        if not match:
            result["notes"].append("commands on the serial console did not finish")
            return result
        report = match.group(1).replace("\r", "")
        result["report"] = report
        monitor.screenshot(f"{RESULTS}/{mode}-console.png")

        os_release = report.split("@@FREE@@")[0]
        if not re.search(r"^ID=cathedral$", os_release, re.M):
            result["notes"].append("/etc/os-release does not say ID=cathedral")
        if not re.search(r"^ID_LIKE=arch$", os_release, re.M):
            result["notes"].append("/etc/os-release does not say ID_LIKE=arch")
        result["ok"] = not result["notes"]

        serial.send("poweroff")
        try:
            qemu.wait(timeout=90)
        except subprocess.TimeoutExpired:
            result["notes"].append("did not power off within 90s (killed)")
        return result
    finally:
        if qemu.poll() is None:
            qemu.kill()
        out = qemu.communicate()[0]
        if out.strip():
            with open(f"{RESULTS}/{mode}-qemu.log", "w") as f:
                f.write(out)


def main():
    os.makedirs(RESULTS, exist_ok=True)
    iso = find_iso()
    kvm = os.access("/dev/kvm", os.R_OK | os.W_OK)
    results = [run_mode(mode, iso, kvm) for mode in ("bios", "uefi")]

    lines = [
        "# Cathedral VM boot test",
        "",
        f"- ISO: `{os.path.basename(iso)}` ({os.path.getsize(iso) / 2**20:.0f} MiB)",
        f"- VM: {RAM_MIB} MiB RAM, 2 CPUs, {'KVM' if kvm else 'software emulation'}",
        "",
    ]
    for r in results:
        lines += [f"## {r['mode'].upper()}: {'PASS' if r['ok'] else 'FAIL'}", ""]
        if "boot_seconds" in r:
            lines.append(f"Login prompt {r['boot_seconds']}s after choosing the boot entry.")
            lines.append("")
        for note in r["notes"]:
            lines.append(f"- {note}")
        if "report" in r:
            lines += ["", "```", r["report"].strip(), "```"]
        lines.append("")
    with open(f"{RESULTS}/summary.md", "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    sys.exit(0 if all(r["ok"] for r in results) else 1)


if __name__ == "__main__":
    main()
