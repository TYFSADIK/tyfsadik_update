from svgdiagram import Flow, Sequence, Stack, Timeline

PAGE = "work/applications/macstyle.html"

install = (
    Flow("macstyle-install", "One command, step by step",
         "Everything the install will change is saved first. Packages come from apt or dnf; extensions from the copy "
         "in the repository, or the release made for this GNOME; a final login starts them.", cols=4)
    .node("check", "Check", "Fedora, Ubuntu or Debian; GNOME 43 to 51", at=(0, 0), color="grey")
    .node("pkg", "Packages", "apt or dnf: menus, Quick Look, zsh", at=(1, 0), color="blue")
    .node("save", "Save", "your settings and every file replaced", at=(2, 0), color="purple")
    .node("ext", "Extensions", "bundled or downloaded, checked per version", at=(0, 1), color="yellow")
    .node("theme", "Themes", "WhiteSur, MacTahoe icons; built for GNOME 47 and older", at=(1, 1), color="yellow")
    .node("set", "Settings", "dock, top bar, buttons, wallpaper", at=(2, 1), color="yellow")
    .node("svc", "Services", "Dark Style switch, app helper", at=(0, 2), color="green")
    .node("term", "Terminal", "zsh, prompt, colours (Ptyxis or GNOME Terminal)", at=(1, 2), color="green")
    .node("login", "Log out and in", "GNOME starts the extensions", at=(2, 2), color="cyan")
    .edge("check", "pkg").edge("pkg", "save").edge("save", "ext", exit="b", enter="t")
    .edge("ext", "theme").edge("theme", "set").edge("set", "svc", exit="b", enter="t")
    .edge("svc", "term").edge("term", "login")
)

resolve = (
    Sequence("macstyle-resolve", "Choosing an extension for this GNOME",
             "extensions.gnome.org answers with its nearest release even when that release does not support the "
             "version asked for, so every download is checked against the GNOME version before it is switched on.",
             [("inst", "install.sh", "blue"), ("repo", "Bundled copy", "grey"), ("ego", "extensions.gnome.org / GitHub", "yellow"),
              ("shell", "GNOME Shell", "green")])
    .msg("inst", "repo", "does the bundled copy declare GNOME 46?")
    .msg("repo", "inst", "no (made for 50 and 51)", dashed=True)
    .msg("inst", "ego", "the release made for GNOME 46")
    .msg("ego", "inst", "a zip: its metadata must list 46", dashed=True)
    .msg("inst", "shell", "switched on only if it does; otherwise skipped with a message")
)

stack = (
    Stack("macstyle-stack", "What it is built from",
          "macstyle's own code ties the pieces together and makes every change reversible; the rest is open source "
          "from many authors, credited in the repository.")
    .layer("GNOME", ["GNOME Shell\n43 to 51", "17 to 19\nextensions", "WhiteSur theme,\nMacTahoe icons"], "blue")
    .layer("KDE Plasma", ["Plasma 6:\ntop bar, dock", "MacTahoe global\ntheme, Kvantum", "Konsole follows\ndark mode"], "cyan")
    .layer("macstyle", ["install.sh,\nuninstall.sh", "Dark Style\nswitch", "Version-checked\ndownloads", "Backups of\nevery change"], "yellow")
    .layer("Terminal", ["zsh,\nPowerlevel10k", "Starship\n(Windows)", "fastfetch, lsd,\nzoxide, fzf"], "green")
    .layer("Windows", ["Seelen UI\ndock + top bar", "QuickLook,\nPowerToys", "Auto Dark Mode,\nmacOS cursor"], "purple")
    .layer("Tests", ["6 GNOME and\n4 KDE systems", "Headless GNOME\nShell and Plasma", "Windows\nServer 2025"], "grey")
)

timeline = (
    Timeline("macstyle-timeline", "Build status",
             "Installs, checks and uninstalls cleanly on six GNOME and four KDE Plasma systems and on Windows in CI; "
             "next is a test on real hardware with a live login.")
    .phase("Fedora", "GNOME 50, 51", "done")
    .phase("Ubuntu, Debian", "any GNOME 43+", "done")
    .phase("Windows", "10 and 11", "done")
    .phase("KDE Plasma", "Plasma 6.3 to 6.8", "done")
    .phase("CI, 12 jobs", "all green", "done")
    .phase("Live login", "real hardware", "next")
)

DIAGRAMS = [install, resolve, stack, timeline]
