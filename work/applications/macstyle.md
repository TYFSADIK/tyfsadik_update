# macstyle

Written by [Taki Sadik](../../about) · Last updated 2026-11-27 · 9 min read

A macOS-like desktop for Fedora, Ubuntu and Debian (GNOME or KDE Plasma) and Windows, in one command, and back again in one command

## Overview

The parts of macOS that make daily work easier, on a Linux or Windows computer: a dock that magnifies, the app's menus in the top bar, window buttons on the left, Quick Look, and a Dark Style that switches everything at once, wallpaper included.

On Linux with GNOME it sets up up to 19 extensions, the WhiteSur theme and MacTahoe icons, day-and-night wallpapers and a terminal with a round-pill prompt, on any GNOME from 43 to 51 (Fedora 42 to 45, Ubuntu 24.04 to 26.10, Debian 12 and 13). Inside KDE Plasma 6 the same command sets up the KDE edition: a top bar with the app's menus, a floating dock, the MacTahoe global theme in light and dark, Kvantum for Qt apps, and Konsole that follows dark mode (Fedora KDE, Kubuntu 25.04 and newer, Debian 13). On Windows 10 and 11 it installs free, open-source tools for a dock and a top bar, Quick Look, a Spotlight-like search and automatic dark mode, with macOS icons, the macOS cursor, Mac shortcuts on the key where Cmd sits, and the same terminal look.

Before changing anything it saves your settings and every file it replaces, and one command puts it all back. The source code is on GitHub at [TYFSADIK/macstyle](https://github.com/TYFSADIK/macstyle), under the GNU General Public License 3.0.

## What You Get

| Feature | Linux (GNOME) | Linux (KDE Plasma) | Windows |
| --- | --- | --- | --- |
| Dock | Magnifies under the pointer, steps aside for windows (Dash2Dock Motion or Lite) | Floating, centred, steps aside for windows; no magnification | Seelen UI's dock (it hides the taskbar); macOS icons in the dock, Start menu, desktop and File Explorer |
| Top bar | The app's own menus (File, Edit, View) for VS Code, Chrome, Firefox, LibreOffice; window buttons there when maximized | The app's menus for KDE and Qt apps (Dolphin, Kate, Konsole, Okular), tray, clock | Seelen UI's top bar |
| Window buttons | On the left | On the left, in macOS order | Not possible on Windows |
| Dark Style | Apps, top bar, dock, icons, shadows, terminal and a day or night wallpaper switch together | MacTahoe Light or Dark global theme (automatic at sunset on Plasma 6.5+); wallpaper and Konsole follow | Auto Dark Mode on a schedule, wallpapers that follow it |
| Quick Look and search | Space on a file in Files (Sushi); GNOME search | Dolphin's preview panel (F11); Alt+Space search (KRunner) | QuickLook; Alt+Space search (PowerToys) |
| Look | WhiteSur theme (a softer light variant), MacTahoe icons and cursor, rounded corners, blur | MacTahoe global theme, Plasma style, window decorations, Kvantum, icons and cursor | macOS cursor, Inter font, blue accent, the wallpaper on the lock screen, File Explorer like Finder |
| Terminal | zsh with round pills, suggestions, z jumps, ls with icons; Ptyxis or GNOME Terminal styled | Konsole in the macstyle colours, see-through, with the same zsh prompt | Windows Terminal and PowerShell with the same pills (Starship) |
| Also | Downloads fan from the dock, cover-flow Alt+Tab, magic lamp, clipboard history, Caffeine, a matching second top bar | Six day-and-night wallpapers that switch with the theme | Mac shortcuts with Alt (copy, paste, undo, save, close, quit), quiet sounds |

## How It Works

One installer for every GNOME version. A GNOME extension declares the versions it runs on, and one made for another version can stop GNOME Shell from starting. For each extension the install uses the copy in the repository if it declares your version; otherwise it downloads the release made for it from extensions.gnome.org, or from the project's own GitHub releases where those are newer, and switches it on only if its metadata lists your version. Nothing made for another version is ever switched on.

Distribution by distribution. Packages come from dnf on Fedora and apt on Debian and Ubuntu, with their different names. Tools a release does not package (fastfetch and lsd on Debian 12 and Ubuntu 24.04) are downloaded from their projects. On GNOME 47 and older the WhiteSur top-bar theme is built for that exact version. Ubuntu Dock is switched off, Debian 13 gets Ptyxis because its Console cannot be styled, and Ubuntu 24.04's GNOME Terminal gets the same colours, switching with Dark Style.

Reversible. The first run saves the full settings database and every file it replaces. Uninstall removes what was added, brings back what was replaced and restores every setting it touched.

## Install

Linux, in a terminal inside your GNOME or KDE Plasma desktop, then log out and back in (inside Plasma it sets up the KDE edition):

git clone https://github.com/TYFSADIK/macstyle
cd macstyle
./install.sh

Windows, in PowerShell in the downloaded folder (not as administrator), then sign out and back in:

powershell -ExecutionPolicy Bypass -File .\windows\install.ps1

Undo with ./uninstall.sh or .\windows\uninstall.ps1.

## Testing

Every push runs the install on six Linux versions with GNOME, four with KDE Plasma, and Windows Server 2025, twelve jobs in all. On Linux the test then starts GNOME Shell without a screen and asks it, extension by extension, whether each one is running; takes a screenshot; uninstalls; and compares every setting with the state before the install. On Windows it checks the fonts, cursor, wallpaper, dark-mode watcher, PowerShell profiles, prompt and Windows Terminal profile, uninstalls and compares the registry.

| System | GNOME | Extensions running | Dock | After uninstall |
| --- | --- | --- | --- | --- |
| Fedora 44 | 50 | 19 of 19 | Dash2Dock Motion | settings identical |
| Fedora 43 | 49 | 18 of 18 | Dash2Dock Lite | settings identical |
| Ubuntu 26.04 | 50 | 18 of 18 | Dash2Dock Motion | settings identical |
| Ubuntu 24.04 | 46 | 17 of 17 | Dash2Dock Lite | settings identical |
| Debian 13 | 48 | 17 of 17 | Dash2Dock Lite | settings identical |
| Debian 12 | 43 | 12 of 12 | Dash2Dock Lite | settings identical |
| Windows Server 2025 |  |  | Seelen UI | registry identical |

KDE Plasma. The test starts KWin and Plasma without a screen, installs macstyle and asks Plasma itself for the result: the global theme, colours, icons, cursor, Kvantum, window decoration and buttons, the two panels and their widgets, the wallpaper and the Konsole profiles. It switches to MacTahoe Dark and checks that Kvantum and Konsole follow, uninstalls, and compares every file under ~/.config and ~/.local/share with the state before.

| System | Plasma | Checks | After uninstall |
| --- | --- | --- | --- |
| Fedora 44 | 6.8 | all pass | every file identical |
| Fedora 43 | 6.7 | all pass | every file identical |
| Ubuntu 26.04 (Kubuntu) | 6.6 | all pass | every file identical |
| Debian 13 | 6.3 | all pass | every file identical |

## What Testing Found

The first runs failed everywhere. Each failure was either a real bug, fixed, or a gap in the test setup:

- Every package looked unavailable on Debian and Ubuntu. The installer runs with pipefail, and apt-cache policy | grep -q fails when grep closes the pipe early. Capturing the output first fixed it.

- The theme did not build on GNOME 47 and older. WhiteSur's installer hides the cursor with setterm, which fails without a terminal and silently stops the build. It now runs with a setterm that does nothing, and every theme variant it makes is recorded so uninstall removes them all.

- Desktop icons could never start on Ubuntu 24.04 and Debian. Python's zip extraction dropped the executable bit from the downloaded extension's launcher. Permissions are now restored from the zip, and checked.

- GTK 4 apps had no theme on Debian 13 and Ubuntu 24.04. GTK before 4.20 rejects the CSS media queries that switch light and dark. Those systems get one marked import that the Dark Style service rewrites.

- The Apps Menu crashed on Ubuntu without the gnome-menus package, which Fedora pulls in and Debian and Ubuntu do not.

- The KDE installer would have opened a crash dialog on Debian 13. It read the Plasma version with plasmashell --version, which crashes there; the version now comes from the package manager.

- Kvantum went unnoticed on Debian and Ubuntu, which keep Qt's plugins in a folder named after the processor, so apps got Plasma's Breeze style. Found and fixed.

- The KDE uninstall left three files behind on Plasma 6.3 (written when a theme is applied) and could not stop Plasma where kquitapp6 is missing; both fixed, and every file is now compared.

- The Windows uninstall stopped at two Start menu shortcuts that Windows protects, leaving the folder icons in place; it now reports such a file and goes on, the registry first.

- Testing GNOME Shell in a container needed what a login provides: an X11 socket folder, a system bus, and a stand-in login manager (python-dbusmock, as GNOME's own tests use).

## Limits

- Tested without a screen. The tests prove every extension and setting is in place and every change is undone; a live login on real hardware (the dock under a real pointer, menus of open apps) is the next test.

- Top-bar menus need GNOME 45 or newer, and apps that publish their menus. Debian 12 gets the Applications menu instead.

- Windows cannot move window buttons or put an app's menus in the top bar; macstyle does not pretend to.

- KDE Plasma 5 is not supported (Kubuntu 24.04, Debian 12), and Plasma's dock does not magnify. Top-bar menus on KDE are for KDE and Qt apps. The KDE tests take no screenshots: KWin's screenshot path needs a graphics card.

- The SF Pro font is not included because of Apple's licence; Inter is used on Windows, and SF Pro on Linux if you have it.

## What Is Next

- A test on real hardware with a live login, on each distribution.

- Top-bar menus for Flatpak and Qt apps.

- Screenshots of the Windows edition from a real desktop.

## Cite This Page

**Q: Citation formats**

A: Plain text
