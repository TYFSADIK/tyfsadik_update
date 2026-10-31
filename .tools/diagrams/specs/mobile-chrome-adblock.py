from svgdiagram import Bars, Flow, Sequence, Timeline

PAGE = "work/applications/mobile-chrome-adblock.html"

options = (
    Flow("mca-options", "Five ways to run it",
         "Four of the five options use the same blocklists: the Android app and the iPhone app filter on the phone, "
         "Termux root mode filters with firewall rules, and the Go server filters for every phone that points at it. "
         "The free iPhone profile is the exception: it points the phone at AdGuard DNS instead.", cols=4)
    .node("and", "Android app", "local VPN that only carries DNS", at=(0, 0), color="green")
    .node("ios", "iPhone app", "packet tunnel, same design", at=(0, 1), color="green")
    .node("tmx", "Termux root mode", "iptables sends port 53 to a local blocker", at=(0, 2), color="yellow")
    .node("srv", "Your own server", "DNS-over-HTTPS and DNS-over-TLS in Go", at=(0, 3), color="blue")
    .node("lists", "Shared blocklists", "Strong: 397,531 domains, Ultimate: 421,945", at=(1, 0), span=4, color="cyan")
    .node("prof", "Free iPhone profile", "one tap in Safari, no app", at=(2, 2), color="purple")
    .node("adg", "AdGuard DNS", "free public ad-blocking resolver", at=(2, 3), color="grey")
    .edge("and", "lists").edge("ios", "lists").edge("tmx", "lists").edge("srv", "lists")
    .edge("prof", "adg")
)

lookup = (
    Flow("mca-lookup", "What happens to every lookup on Android",
         "The app tells Android to use a DNS server at 10.111.222.2 and routes only that one address into the "
         "tunnel. Every lookup arrives at the app as a raw packet. Blocked names are answered with 0.0.0.0 on the "
         "phone; the rest go to a public resolver through a protected socket, and the answer is checked for "
         "disguised trackers before it goes back.", cols=5)
    .node("chrome", "Chrome or any app", "asks for ads.example.com", at=(0, 0), color="cyan")
    .node("os", "Android", "DNS server is 10.111.222.2", at=(0, 1), color="blue")
    .node("tun", "Tunnel", "routes only 10.111.222.2/32", at=(0, 2), color="blue")
    .node("check", "Blocklist", "name and every parent", at=(0, 3), color="yellow")
    .node("zero", "Blocked", "answer 0.0.0.0 on the phone", at=(0, 4), color="red")
    .node("up", "Allowed", "forward to 1.1.1.1, 9.9.9.9 or 8.8.8.8", at=(1, 3), color="green")
    .node("cname", "CNAME check", "is the real target a tracker?", at=(1, 2), color="yellow")
    .node("reply", "Answer", "written back into the tunnel", at=(1, 1), color="cyan")
    .edge("chrome", "os").edge("os", "tun").edge("tun", "check")
    .edge("check", "zero", "listed")
    .edge("check", "up", "not listed")
    .edge("up", "cname").edge("cname", "reply")
)

cname = (
    Sequence("mca-cname", "Catching a disguised tracker",
             "Some sites point a subdomain of their own at a tracking company, so the name looks first party. The "
             "app forwards the lookup, reads the CNAME chain in the answer, and replaces the whole answer with "
             "0.0.0.0 when any target is on the list.",
             [("c", "Chrome", "cyan"), ("a", "AdBlock", "green"), ("u", "1.1.1.1", "blue")])
    .msg("c", "a", "metrics.shop.example?")
    .note("not listed, so forward it", over=("a", "a"))
    .msg("a", "u", "metrics.shop.example?")
    .msg("u", "a", "CNAME shop.tracker.example, A 203.0.113.7", dashed=True)
    .msg("a", "a", "cnameTargets(): shop.tracker.example is listed")
    .msg("a", "c", "metrics.shop.example A 0.0.0.0", dashed=True)
)

lists = (
    Bars("mca-lists", "Domains in each list, after parsing, in thousands",
         "Unique domains each bundled list contributes after the app's parser drops comments, wildcards and rules "
         "that only apply to certain clients: StevenBlack 76,737, AdGuard 184,568, HaGeZi Pro++ 225,331 and HaGeZi "
         "encrypted DNS 3,277. Lists overlap, so the Strong total of 397,531 is less than the sum. The Ultimate "
         "total of 421,945 is what the app showed after downloading the Ultimate lists.", unit="thousand")
    .bar("StevenBlack hosts", 76.7, color="grey")
    .bar("AdGuard DNS filter", 184.6, color="blue")
    .bar("HaGeZi Pro++", 225.3, color="cyan")
    .bar("HaGeZi encrypted DNS", 3.3, color="purple")
    .bar("Strong, combined", 397.5, color="green")
    .bar("Ultimate, combined", 421.9, color="yellow")
)

build = (
    Timeline("mca-build", "How it came together",
             "The project grew from a server that needed a VPS and a domain into apps that need nothing but the "
             "phone. Every phase shipped and is in the public repo.")
    .phase("Go DNS server", "DoH and DoT, Let's Encrypt, setup page and iPhone profile", "done")
    .phase("Free iPhone path", "profile on GitHub Pages pointing at AdGuard DNS", "done")
    .phase("Android app", "on-device blocking through a DNS-only VPN", "done")
    .phase("iPhone app and Termux", "packet tunnel IPA, on and off from a terminal", "done")
    .phase("Stronger lists", "Strong and Ultimate levels, bypass and CNAME blocking", "done")
)

DIAGRAMS = [options, lookup, cname, lists, build]
