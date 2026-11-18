#!/usr/bin/env bash
# One-time setup of virt-manager on this laptop (Garuda/Arch). Uses sudo.
# Run it in your own terminal:
#
#   bash ~/cathedral/scripts/vm/setup-host.sh
#
# It installs virt-manager, libvirt, virt-install and QEMU, starts the libvirt
# service, adds you to the libvirt group and turns on libvirt's default NAT
# network. Safe to run again.
set -euo pipefail

packages=(libvirt virt-manager virt-install qemu-desktop edk2-ovmf dnsmasq)

echo "› installing: ${packages[*]}"
sudo pacman -S --needed "${packages[@]}"

echo "› starting the libvirt service"
sudo systemctl enable --now libvirtd.service

echo "› adding $USER to the libvirt group"
sudo usermod -aG libvirt "$USER"

echo "› turning on the default NAT network"
if ! sudo virsh --connect qemu:///system net-info default >/dev/null 2>&1; then
  sudo virsh --connect qemu:///system net-define /usr/share/libvirt/networks/default.xml
fi
sudo virsh --connect qemu:///system net-autostart default
sudo virsh --connect qemu:///system net-start default 2>/dev/null || true

echo
echo "Done. Log out and back in once so the libvirt group applies"
echo "(until then virt-manager asks for your password)."
echo "Next: bash ~/cathedral/scripts/vm/create-vm.sh"
