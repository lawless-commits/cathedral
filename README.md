# Cathedral

A medieval-themed, lightweight Linux distro based on Arch Linux, built with archiso.

**Status:** early work. Milestone 1 (boot in a VM) passes: the live ISO boots on BIOS and UEFI with 1 GiB RAM. There is no desktop or installer yet.

- Desktop: XFCE (planned; the live ISO has no desktop yet)
- Target: usable on about 1 GB of RAM
- Filesystem: BTRFS with snapshots (planned)

The ISO is built on GitHub Actions runners with [gh-offload](https://github.com/lawless-commits/gh-offload).

## Building

Builds run on a GitHub Actions runner, inside an `archlinux` container:

```sh
gh offload --get test-results -- bash scripts/ci.sh
```

That builds `out/cathedral-*.iso` with mkarchiso, boots it in QEMU with 1 GiB RAM under BIOS and
UEFI, and brings back `test-results/` (summary, serial logs, screenshots). Add `--get out` to
download the ISO too (about 1.3 GB).
