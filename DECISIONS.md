# Decisions

Every answer the user has given, so later sessions do not ask again. The "Decided" list in
CLAUDE.md came with the brief and is not repeated here.

| Date       | Decision | Answer |
| ---------- | -------- | ------ |
| 2026-11-18 | How to build and test | Use `gh offload`: builds and VM tests run on GitHub Actions runners, not the laptop. |
| 2026-11-18 | GitHub repo | Public, `lawless-commits/cathedral`, local copy at `~/cathedral`. |
| 2026-11-18 | Desktop (open decision 1) | XFCE. |
| 2026-11-18 | Wallpaper rights (open decision 10) | The user made the knight image with AI. It is committed to the public repo as `theme/wallpaper/knight.png`. |
| 2026-11-18 | "Dragonized feel" (open decision 2) | Wanted: the dark glassy look, accent colours, and the system side (snapshots and rollback, performance tuning such as zram, a welcome app). Not picked: fish as the default shell with a styled prompt and fastfetch. |
| 2026-11-18 | Display server and login manager (open decision 3) | X11 with LightDM (GTK greeter). |
| 2026-11-18 | Installer (open decision 4) | A Cathedral install script for now (sets up the BTRFS subvolumes and snapper); Calamares later. Calamares is not in the official repos (checked 2026-11-18), so its source is a separate decision when we get there. |
| 2026-11-18 | Kernel (open decision 5) | The standard `linux` kernel. |
| 2026-11-18 | Bootloader for the installed system (open decision 6) | GRUB with grub-btrfs (boot snapshots from the menu). The live ISO keeps releng's syslinux (BIOS) and systemd-boot (UEFI) menus. |
| 2026-11-18 | Default browser (open decision 7) | Firefox (accepting its RAM cost on 1 GB). |
| 2026-11-18 | Accent colour (open decision 8, part 1) | `#EF5350` bright crimson. Contrast 5.6:1 on `#0d0d13` and 4.5:1 on `#1f2325` (WCAG AA for normal text on both). White text on it is only 3.5:1, so filled crimson buttons use dark text. |
| 2026-11-18 | Fonts (open decision 8, part 2) | Mixed: blackletter (UnifrakturMaguntia, OFL) only in the logo image; Cormorant (`otf-cormorant`, extra) for window titles, the login screen and the boot menu; a plain sans for menus and body text. |
| 2026-11-18 | Base palette (open decision 8, part 3) | Use the sampled colours as they are: `#0d0d13` window background, `#1f2325` panels, `#353943` borders, `#500d13` and `#371015` dark accents, `#EF5350` bright accent. |
| 2026-11-18 | Local test VM | virt-manager (libvirt, `qemu:///system`), set up by `scripts/vm/setup-host.sh` and `scripts/vm/create-vm.sh`. |
| 2026-11-18 | Local test VM RAM | 2 GiB by default (`scripts/vm/vm.conf`); Cathedral's target stays 1 GiB and the CI test still uses 1 GiB. |
