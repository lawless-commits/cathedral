#!/usr/bin/env bash
# Create the "cathedral" VM in virt-manager from the newest ISO in out/, or put
# a newer ISO into the existing VM. Uses sudo. Run it in your own terminal:
#
#   bash ~/cathedral/scripts/vm/create-vm.sh             # create, or swap in the new ISO
#   bash ~/cathedral/scripts/vm/create-vm.sh --recreate  # delete the VM and its disk, start over
#
# Settings (RAM, CPUs, disk, BIOS or UEFI) are in scripts/vm/vm.conf.
# The ISO comes from: gh offload --get out -- bash scripts/ci.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
source scripts/vm/vm.conf

virsh=(sudo virsh --connect qemu:///system)
iso_src="$(ls -t out/cathedral-*.iso 2>/dev/null | head -1 || true)"
iso="$IMAGES_DIR/$VM_NAME-live.iso"
disk="$IMAGES_DIR/$VM_NAME.qcow2"

if [[ -z "$iso_src" ]]; then
  echo "No ISO in ~/cathedral/out/. Build one first:" >&2
  echo "  gh offload --get out --get test-results -- bash scripts/ci.sh" >&2
  exit 1
fi

exists=false
"${virsh[@]}" dominfo "$VM_NAME" >/dev/null 2>&1 && exists=true

if [[ "${1:-}" == "--recreate" && $exists == true ]]; then
  echo "› deleting the $VM_NAME VM and its disk"
  "${virsh[@]}" destroy "$VM_NAME" >/dev/null 2>&1 || true
  "${virsh[@]}" undefine "$VM_NAME" --nvram --remove-all-storage
  exists=false
fi

if [[ $exists == true ]] && "${virsh[@]}" domstate "$VM_NAME" | grep -q running; then
  echo "The $VM_NAME VM is running. Shut it down in virt-manager, then run this again." >&2
  exit 1
fi

echo "› copying $(basename "$iso_src") to $iso"
sudo install -D -m 0644 "$iso_src" "$iso"

if [[ $exists == true ]]; then
  echo "Updated: the $VM_NAME VM boots the new ISO next time you start it."
  exit 0
fi

# UEFI: name the plain (no Secure Boot) OVMF firmware from edk2-ovmf, so
# libvirt cannot pick a Secure Boot build that refuses the unsigned ISO.
ovmf=/usr/share/edk2/x64
boot=(--boot "loader=$ovmf/OVMF_CODE.4m.fd,loader.readonly=yes,loader.type=pflash,nvram.template=$ovmf/OVMF_VARS.4m.fd")
[[ "$FIRMWARE" == bios ]] && boot=()

echo "› creating the $VM_NAME VM (${RAM_MIB} MiB RAM, $CPUS CPUs, $DISK_GB GB disk, $FIRMWARE)"
sudo virt-install --connect qemu:///system \
  --name "$VM_NAME" \
  --memory "$RAM_MIB" --vcpus "$CPUS" \
  --osinfo archlinux \
  "${boot[@]}" \
  --import \
  --disk "path=$iso,device=cdrom,bus=sata,readonly=on,boot.order=1" \
  --disk "path=$disk,size=$DISK_GB,format=qcow2,bus=virtio,boot.order=2" \
  --network network=default,model=virtio \
  --graphics spice --video virtio \
  --noautoconsole

echo
echo "Created and started. Open virt-manager and double-click \"$VM_NAME\" to see it."
echo "It boots the live ISO; the empty $DISK_GB GB disk is there for the install test later."
