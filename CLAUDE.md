# Cathedral: project brief for Claude Code

Cathedral is a medieval-themed, Arch-based Linux distro that the user is building with you. This
file is the starting brief (copied from the user's CLAUDE.md.pdf, 2026-11-17). Read all of it
before doing anything, then read DECISIONS.md.

## How this repo works

- Builds and VM boot tests run on GitHub Actions runners through `gh offload`, not on the
  laptop (it is low on RAM). The build runs in an `archlinux` Docker container on the runner,
  so the packages come from the official Arch repos only, not from the Garuda host's repos.
- `profile/` is the archiso `releng` profile with Cathedral's branding edited in.
- `packages/*.x86_64` are the package lists; the build joins them into the profile's
  `packages.x86_64`. Add or swap a desktop by editing one list.
- `theme/` holds theme assets (palette, wallpaper, boot splash). The wallpaper is not
  committed until its rights are settled (open decision 10).
- `scripts/` holds the build and test scripts. They are bash and run on the runner; tell the
  user to run any local script with `bash script.sh`.
- The repo is public: commit as `289270538+lawless-commits@users.noreply.github.com`.

## Rules for working with this user

1. **Never assume. Ask.** For any decision not listed under "Decided", ask the user first (use
   AskUserQuestion with concrete options). If you are unsure whether something counts as a
   decision, ask.
2. Record every answer in `DECISIONS.md` (decision, answer, date) so later sessions do not ask
   again.
3. The user will change things along the way. Keep package lists, theme assets, installer config
   and build scripts in separate files so a swap is a small edit.
4. The user's shell is **fish**. Write scripts with `#!/usr/bin/env bash` and tell the user to run
   them with `bash script.sh`. Do not hand them bash-syntax one-liners to paste into the terminal.
5. The host is Garuda Linux (Arch-based), so archiso can be built natively. Test only in a VM.
   Never write to a real disk or USB unless asked, and confirm the device name first.
6. Say plainly what has and has not been tested. Check every package name with `pacman -Si <pkg>`
   before adding it. The candidate names below were NOT verified.

## Goal

An Arch-based distro called **Cathedral** with a medieval look. The default wallpaper is the
knight image the user supplied (`knight_enhanced_v3_4k.png`, 3840x2160, dark armoured knight in a
field of red flowers). The user wants it to have "the same sort of feeling" as Garuda Dragonized,
and it should run on about **1 GB of RAM if possible**.

## Decided (by the user)

- Base: Arch Linux, built with archiso, starting from the `releng` profile.
- Name: Cathedral. Theme: medieval. Wallpaper: the knight image.
- Must be lightweight (about 1 GB RAM). KDE Plasma, which Garuda Dragonized uses, is therefore
  likely too heavy; confirm with the user (see Open decisions).
- Filesystem and snapshots: the user wants BTRFS with snapper-style snapshots, and asked for the
  best user-friendly setup based on research. They may change this later.
- **First milestone: boot Cathedral in a VM.** Nothing more until that works.
- The user will give feedback and change things as the project goes on.

## Open decisions: ask these first, one at a time

(Answered ones are in DECISIONS.md.)

1. **Desktop: XFCE or LXQt?** Also ask whether a tiling WM or a bare window manager is of
   interest.
2. **What does "Dragonized feel" mean to them?** Ask which parts they like: the dark glassy look,
   the accent colours, the fish prompt and welcome screen, the performance tuning, the snapshots
   and rollback, the welcome app.
3. **Display server and login manager.** Lean: X11 with LightDM for the VM milestone and for low
   RAM.
4. **Installer.** Calamares is a graphical installer but needs a package source (see below).
   `archinstall` or a manual install is simpler for the first VM test. Ask which they want for
   milestone 1 and later.
5. **Kernel.** Lean: the standard `linux` kernel. Ask whether they want `linux-zen` or
   `linux-lts`.
6. **Bootloader.** GRUB works with `grub-btrfs` (boot from snapshots). Ask before choosing
   systemd-boot.
7. **Default apps**, especially the browser. Firefox is heavy on 1 GB; ask what they want to
   trade off.
8. **Palette and fonts.** Palette is sampled below; ask them to confirm and pick an accent
   colour. Ask about medieval fonts (for example blackletter for the logo only, a readable serif
   for the UI).
9. **Where to host** the ISO and package repo later (not needed for milestone 1).
10. **Wallpaper rights.** Ask where the knight file lives and where it came from. If Cathedral is
    ever shared publicly, the user needs rights to it. The user also linked a stock photo of a
    cathedral altar for the name; do NOT use that photo in the distro.

## Milestones

1. **VM boot (current).** Copy `/usr/share/archiso/configs/releng` into this project. Rebrand
   (`profiledef.sh` name and labels, `/etc/os-release` with `ID=cathedral`, `ID_LIKE=arch`), set
   the wallpaper, set the boot menu text, build with `mkarchiso`, boot in QEMU or virt-manager.
   Test UEFI (`edk2-ovmf`) and BIOS, with **1 GiB RAM** assigned to the VM. Record `free -m`
   after boot.
2. **Themed desktop** on the live ISO (desktop choice above).
3. **Install to disk in a VM** with a BTRFS layout and snapper.
4. **Snapshot and rollback test** (break something, roll back, boot a snapshot).
5. **1 GB RAM pass:** measure idle RAM of the installed system, trim services and packages.
6. **Own package repo, release process, polish.**

## Research notes (verify before relying on them)

**Desktop RAM.** One Oct 2026 comparison on an Ubuntu 26.04 base measured Lubuntu (LXQt, X11) at
745 MiB idle total, of which the desktop itself cost 318 MiB over a 427 MiB base. A general guide
puts idle use at roughly 0.2-0.4 GB for LXQt and 0.3-0.5 GB for XFCE. A forum comparison had KDE
Plasma at about twice the RAM of XFCE or LXQt (2,670 vs about 1,360 MiB, on a 15 GB machine, so
caching inflates the numbers). A browser adds a lot on top, and one reviewer says neither Linux
Lite (XFCE) nor Lubuntu (LXQt) feels pleasant on 1 GB with real apps. Plan for a bare desktop
fitting in 1 GB, not a full workload.

**XFCE vs LXQt.** LXQt is lighter. XFCE has more GUI settings, a larger theme ecosystem (GTK) and
is easier for a new user to customise, which suits a heavily themed distro. Qt theming for LXQt
is done through Kvantum.

**Live ISO RAM.** The ArchWiki says Arch itself needs at least 512 MB RAM, but more is needed to
boot the live system. One older community test found the stock live ISO needed about 740 MiB to
boot. So a 1 GiB VM may be tight for a live session with a desktop even if the installed system
fits. Measure it; do not assume. Keep the live image small and consider no desktop effects in the
live session.

**Calamares.** Existing Arch-based projects get Calamares from the Chaotic-AUR repo or the
ArcoLinux repo, adding that repo to the ISO's `pacman.conf` and keyring. Check whether it is now
in the official repos before adding a third-party repo. Third-party repos are a trust and
maintenance decision: ask the user.

**BTRFS and snapper on little RAM.** Forum reports say BTRFS runs fine on 512 MiB devices. Two
cautions from reports: BTRFS quotas (qgroups) have caused large RAM use when deleting many
snapshots, but snapper needs quotas to show per-snapshot space usage. For a 1 GB target, the lean
is to leave quotas off and cap the number of snapshots. Common practice, to be checked on the
ArchWiki before use: `@`, `@home`, `@snapshots` and `@var_log` subvolumes, mount options
`noatime,compress=zstd`, `snap-pac` for pacman pre/post snapshots, `grub-btrfs` to boot
snapshots, `zram-generator` for compressed swap in RAM. `btrfs-assistant` is a friendly GUI but a
Qt app, so it costs RAM; ask the user.

**archiso.** `releng` is the profile used for the official ISO and the recommended starting
point. You edit `packages.x86_64`, put files in `airootfs/`, and change `profiledef.sh`.
`pacman.conf` in the profile controls which repos the build uses. Do not build the profile on
NTFS or FAT32 (permission problems).

## Candidate packages

Checked with `pacman -Si` on 2026-11-18 (on the Garuda host; all in Arch `core`/`extra`):
`base`, `linux`, `linux-firmware`, `networkmanager`, `grub`, `efibootmgr`, `btrfs-progs`,
`snapper`, `snap-pac`, `grub-btrfs`, `zram-generator`, `fish`, `starship`, `fastfetch`,
`lightdm`, `lightdm-gtk-greeter`, `pipewire`, `pipewire-pulse`, `wireplumber`, `qemu-base`,
`edk2-ovmf`, `archiso`. `xfce4` is a package group, not a package; check its members in the
Arch container before relying on the list (the Garuda host shows an extra member). Not yet
checked: `lxqt`, `sddm`.

## Theme notes

Colours sampled from the knight wallpaper, by share of the image:

| Colour    | Share | Use                                 |
| --------- | ----- | ----------------------------------- |
| `#0d0d13` | 15%   | near-black navy, window background |
| `#371015` | 13%   | deep blood red                      |
| `#500d13` | 13%   | blood red, dark accent              |
| `#1f2325` | 12%   | charcoal, panels                    |
| `#353943` | 5%    | steel grey, borders                 |

The reds are too dark for text or small icons on the dark background. Propose a brighter crimson
for accents and check contrast (WCAG AA) before the user approves it. Do not use Garuda's logos,
wallpapers or theme assets.

## Sources

- https://wiki.archlinux.org/title/Archiso
- https://wiki.archlinux.org/title/Installation_guide
- https://computingforgeeks.com/desktop-environment-ram-usage/
- https://unihost.com/help/how-to-choose-linux-desktop-environment-ram-usage/
- https://www.fosslinux.com/linux-lite-vs-lubuntu
- https://forum.endeavouros.com/t/linux-des-resource-usage-compared/70060
- https://github.com/arch-linux-calamares-installer/alci-iso (how an existing project adds
  Calamares and Chaotic-AUR)
- https://discuss.cachyos.org/t/snapper-taking-ungodly-amount-of-space/21012 (snapper and quotas)
