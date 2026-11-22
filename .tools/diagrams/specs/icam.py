from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/defence/identity-credential-access-management.html"

platform = (
    Flow("icam-platform", "One identity, every kind of access",
         "The HR file is the source of truth. The directory holds identities, Keycloak brokers them to every "
         "application with MFA, OpenBao turns them into short-lived credentials, OPA decides access from "
         "attributes, and every component writes to one hash-chained audit trail.", cols=4)
    .node("hr", "HR file", "source of truth: joiners, movers, leavers", at=(0, 0), color="grey")
    .node("ldap", "OpenLDAP directory", "300 people, groups, devices; unique IDs", at=(0, 1), color="blue")
    .node("kc", "Keycloak broker", "LDAP federation, TOTP / WebAuthn, sessions, lockout", at=(0, 2), color="blue")
    .node("bao", "OpenBao", "SSH user + host CAs, device PKI, revocation", at=(0, 3), color="purple")
    .node("web", "Mission app + Grafana", "OIDC single sign-on, back-channel logout", at=(1, 2), color="green")
    .node("srv", "Linux servers", "SSH certificates, revocation list, no passwords", at=(1, 3), color="green")
    .node("opa", "OPA policy", "RBAC + ABAC as code: clearance, release caveat, need to know", at=(1, 1), color="yellow")
    .node("door", "Door controller", "badge readers with device certificates (mTLS)", at=(1, 0), color="orange")
    .node("audit", "Audit trail", "one record shape, SHA-256 chain, Loki, Grafana, access review", at=(2, 0), span=4, color="red")
    .edge("hr", "ldap", "icamctl jml").edge("ldap", "kc", "federation").edge("kc", "bao", "60 s tokens")
    .edge("kc", "web").edge("bao", "srv", "certificates")
    .edge("web", "opa", "decide").edge("door", "opa", "decide", exit="r", enter="l")
)

leaver = (
    Sequence("icam-leaver", "A leaver, end to end",
             "One change in the HR file removes access everywhere. Measured in the rehearsal: web session, new "
             "sign-in, existing SSH certificate and door all gone 0.98 s after the change.",
             [("hr", "HR / icamctl", "grey"), ("kc", "Keycloak", "blue"), ("app", "Mission app", "green"),
              ("srv", "Servers", "green"), ("door", "Door", "orange"), ("ldap", "Directory", "blue"), ("aud", "Audit", "red")])
    .msg("hr", "kc", "log out every session")
    .msg("kc", "app", "back-channel logout: session dropped")
    .msg("hr", "srv", "revocation list: key ID jwt-<uid>")
    .msg("hr", "door", "block pushed")
    .msg("hr", "ldap", "move to ou=leavers, remove from groups")
    .msg("ldap", "kc", "sync: no new sign-in")
    .msg("hr", "aud", "one record per step", dashed=True)
)

credentials = (
    Flow("icam-credentials", "Credentials from OpenBao",
         "People never hold long-lived secrets for servers: a Keycloak sign-in with MFA becomes a 60-second "
         "token, the token becomes a short SSH certificate whose key ID names the person. Servers and badge "
         "readers get certificates too, so identity runs both ways.", cols=4)
    .node("u", "Person signs in", "password + TOTP (or a hardware key)", at=(0, 0), color="blue")
    .node("t", "60 s ID token", "groups and attributes as claims", at=(0, 1), color="blue")
    .node("j", "OpenBao JWT login", "role-sysadmin -> ssh-admin policy", at=(0, 2), color="purple")
    .node("c", "SSH certificate", "30 min (admin) or 1 h; key ID = the person", at=(0, 3), color="purple")
    .node("h", "Server", "trusts the user CA, presents a host certificate, checks the revocation list", at=(1, 3), color="green")
    .node("d", "Badge reader", "device certificate from the device CA", at=(1, 1), color="orange")
    .node("dc", "Door controller", "mTLS + CRL refreshed every 30 s or on push", at=(1, 0), color="orange")
    .edge("u", "t").edge("t", "j").edge("j", "c").edge("c", "h")
    .edge("d", "dc", "mTLS")
)

stack = (
    Stack("icam-stack", "Software stack",
          "All open source, configured as code; the lifecycle tool, audit collector, mission app and door "
          "controller are my own.")
    .layer("Identity", ["OpenLDAP\ndirectory", "Keycloak 26\nbroker, MFA", "PostgreSQL\nKeycloak store"], "blue")
    .layer("Credentials", ["OpenBao 2.1\nSSH CAs, PKI", "TOTP / WebAuthn\nauthenticators", "Device\ncertificates"], "purple")
    .layer("Policy", ["OPA\nRBAC + ABAC", "Rego tests\n12 cases"], "yellow")
    .layer("Access points", ["Mission app\nOIDC", "Linux servers\nSSH certs", "Door controller\nmTLS readers", "Grafana\nSSO"], "green")
    .layer("Audit", ["Audit collector\nhash chain", "Loki\nlogs", "Prometheus\nmetrics", "Grafana\naccess audit"], "red")
)

times = (
    Bars("icam-revocation", "How long a leaver keeps access (seconds after the HR change)",
         "Measured in the final rehearsal run. Everything except an already-issued CLI token is gone within a "
         "second; that token dies with its 60 s lifetime plus OpenBao's 5 s leeway (359 s before the fix).", unit="s")
    .bar("Web session", 0.98, "back-channel logout", "green")
    .bar("New sign-in", 0.98, "directory + sync", "green")
    .bar("Existing SSH certificate", 0.98, "revocation list", "green")
    .bar("Badge at the door", 0.98, "block pushed", "green")
    .bar("Issued CLI token at OpenBao", 64.72, "was 359 s before the fix", "yellow")
)

timeline = (
    Timeline("icam-timeline", "Build status",
             "The platform runs end to end in Docker and is measured; the physical badge reader and door strike "
             "come next.")
    .phase("Platform as code", "Keycloak, OpenBao, OPA", "done")
    .phase("Rehearsal", "3 runs, 10 fixes", "done")
    .phase("Badge reader", "Pi, PN532, strike", "doing")
    .phase("Hardware keys", "WebAuthn for admins", "next")
    .phase("Proxmox + real servers", "join-server.sh", "next")
)

DIAGRAMS = [platform, credentials, leaver, times, stack, timeline]
