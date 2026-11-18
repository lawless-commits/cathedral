#!/usr/bin/env bash
# Build the ISO and boot-test it, inside an archlinux container. This is what
# runs on the GitHub runner. From the laptop:
#
#   gh offload --get test-results -- bash scripts/ci.sh
#
# Add `--get out` to also download the ISO (about 1 GB).
set -euo pipefail
cd "$(dirname "$0")/.."

kvm=()
if [[ -e /dev/kvm ]]; then
  kvm=(--device /dev/kvm)
else
  echo "› no /dev/kvm on this runner: the VM test will be slow (software emulation)"
fi

# --privileged: mkarchiso needs mounts and namespaces.
docker run --rm --privileged "${kvm[@]}" -v "$PWD":/w -w /w archlinux:latest bash -c '
  set -euo pipefail
  echo "› installing archiso, QEMU and OVMF"
  pacman -Syu --noconfirm --needed archiso qemu-base edk2-ovmf python >/dev/null
  pacman -Q archiso qemu-base edk2-ovmf
  status=0
  bash scripts/build-iso.sh && python3 scripts/test-vm.py || status=$?
  chmod -R a+rwX out test-results 2>/dev/null || true
  exit $status
'
