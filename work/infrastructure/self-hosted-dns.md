# Self-Hosted DNS

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 10 min read

Network-wide ad blocking with Pi-hole + recursive DNS via Unbound

## Overview

This project replaces the default ISP DNS resolver with a fully self-hosted, two-layer DNS stack.
        Pi-hole acts as the network's primary DNS server, intercepting every DNS query
        from every device on the LAN. When a domain appears on any of the configured blocklists (ad
        networks, trackers, malware domains), Pi-hole returns a blocked response immediately
        (0.0.0.0 for A queries and :: for AAAA queries, Pi-hole's
        default NULL blocking mode). Allowed queries are forwarded to
        Unbound, a validating recursive resolver that walks the DNS tree from the
        root nameservers rather than trusting a third-party upstream like Google (8.8.8.8) or
        Cloudflare (1.1.1.1).

The stack runs in Docker containers on a Proxmox LXC container using a macvlan network so
        Pi-hole gets its own IP on the LAN, allowing the router's DHCP to advertise it as the DNS
        server for all connected devices. Blocklists from Steven Black and OISD block well over one
        hundred thousand ad, tracker, and malware domains (the exact count changes with every list
        update). DNSSEC validation is enabled in Unbound for additional query integrity, with
        Pi-hole-side validation left off to avoid validating twice.

## Architecture

DNS query :53

check domain

blocked

allowed

query root

referral

answer

resolved IP

answer

Client Devices(any LAN host)

Pi-holeport 53(macvlan IP)

BlocklistsSteven BlackOISD

Unboundport 5335(recursive)

Root Nameservers(IANA)

Authoritative DNS(e.g. ns1.example.com)

Blocked responsereturned to client

## Tech Stack

- Pi-hole, DNS sinkhole with web dashboard and blocklist management

- Unbound, validating, recursive, caching DNS resolver with DNSSEC

- Docker & Docker Compose, container runtime for both services

- pihole-FTL, Pi-hole's integrated DNS/DHCP engine (dnsmasq-derived, embedded in v6)

- macvlan, Docker network driver giving Pi-hole its own LAN IP

- Linux (Debian), host OS inside Proxmox LXC container

## Build Process

### Deploy Pi-hole via Docker Compose with macvlan

Pi-hole is deployed using a macvlan Docker network so it receives a dedicated IP address
              on the physical LAN segment. This allows the router to advertise Pi-hole's IP as the DNS
              server via DHCP, causing all client devices to use it automatically without any per-device
              configuration changes. A second container runs Unbound on a shared internal network,
              because a macvlan container cannot reach services on the Docker host's loopback.
              The admin password is kept in a .env file, never in the compose file.

# Create the macvlan Docker network
docker network create \
  -d macvlan \
  -subnet=192.168.1.0/24 \
  -gateway=192.168.1.1 \
  -o parent=eth0 \
  macvlan_net

# docker-compose.yml for Pi-hole + Unbound
# Both containers share an internal network so Pi-hole can reach Unbound
# as unbound#5335; Pi-hole also sits on macvlan for its own LAN IP.
services:
  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    hostname: pihole
    networks:
      macvlan_net:
        ipv4_address: 192.168.1.53
      dns_internal:
    environment:
      TZ: "America/Toronto"
      # Pi-hole v6 variable names (v5 names like WEBPASSWORD no longer work)
      FTLCONF_webserver_api_password: ${PIHOLE_PASSWORD:?set a password in .env}
      FTLCONF_dns_upstreams: "unbound#5335"
      # Leave Pi-hole-side DNSSEC off: Unbound already validates (see Step 2)
      FTLCONF_dns_dnssec: "false"
    volumes:
      - ./pihole/etc-pihole:/etc/pihole
      - ./pihole/etc-dnsmasq.d:/etc/dnsmasq.d
    restart: unless-stopped

  unbound:
    image: mvance/unbound:latest
    container_name: unbound
    hostname: unbound
    networks:
      dns_internal:
    ports:
      - "127.0.0.1:5335:5335/udp"
      - "127.0.0.1:5335:5335/tcp"
    volumes:
      # Mount the whole config directory: unbound.conf, root.hints, and the
      # writable root.key trust anchor all live here inside the container
      - ./unbound:/opt/unbound/etc/unbound
    restart: unless-stopped

networks:
  macvlan_net:
    external: true
  dns_internal:

### Configure Unbound Recursive Resolver

Unbound runs in its own container on the shared internal network, listening on port
              5335. It performs recursive resolution from the IANA root nameservers, validates DNSSEC
              signatures, and refuses queries from outside the container network. The root hints file
              is downloaded to bootstrap the root nameserver list.

# ./unbound/unbound.conf (mounted into the unbound container)
server:
    verbosity: 0
    interface: 0.0.0.0
    port: 5335
    do-ip4: yes
    do-udp: yes
    do-tcp: yes
    do-ip6: no

    # Only answer the internal Docker network
    access-control: 127.0.0.1 allow
    access-control: 172.16.0.0/12 allow

    # Root hints
    root-hints: "/opt/unbound/etc/unbound/root.hints"

    # DNSSEC
    auto-trust-anchor-file: "/opt/unbound/etc/unbound/root.key"

    # Security
    hide-identity: yes
    hide-version: yes
    harden-glue: yes
    harden-dnssec-stripped: yes
    use-caps-for-id: yes

    # Performance
    cache-min-ttl: 3600
    num-threads: 2

# Download root hints next to the config before first start
wget -O unbound/root.hints \
  https://www.internic.net/domain/named.cache

docker compose up -d unbound
docker compose logs unbound

### Point Pi-hole Upstream DNS to Unbound

Pi-hole's upstream is set to the Unbound container on the shared internal network.
              In the Pi-hole admin dashboard under Settings → DNS, all default upstream DNS
              providers are disabled and the custom upstream is set to unbound#5335,
              so allowed queries route to the local Unbound instance. (Using
              127.0.0.1#5335 would fail: from inside the Pi-hole container, loopback
              is the container itself, not the host.)

# Set via environment variable in docker-compose.yml:
FTLCONF_dns_upstreams: "unbound#5335"

# Verify Pi-hole forwards to Unbound
docker exec pihole pihole -d | grep "DNS"

# Test full resolution chain from the host
dig @192.168.1.53 github.com

### Set Router DHCP to Use Pi-hole as DNS

The router's DHCP server configuration is updated so that it distributes Pi-hole's
              macvlan IP as the DNS server for all DHCP clients on the LAN. This ensures every
              device automatically routes DNS through Pi-hole without manual configuration.

# On OpenWrt, advertise Pi-hole via DHCP option 6
# (Network > Interfaces > LAN > DHCP Server > Advanced > DHCP-Options):
# 6,192.168.1.53
# Note: this is different from "DNS forwardings", which controls where the
# router itself forwards queries, not what it tells DHCP clients to use.

# For dnsmasq-based routers (/etc/dnsmasq.conf):
dhcp-option=6,192.168.1.53

# Verify a client received the correct DNS server
# On any LAN device:
nslookup - 192.168.1.53
> google.com

# Check Pi-hole dashboard for new queries appearing
# http://192.168.1.53/admin

### Import Blocklists

Additional blocklists beyond the default Pi-hole list are imported via the web
              dashboard under Group Management → Adlists. After adding the URLs, the gravity
              database is updated to compile all lists into a single SQLite database. The combined
              lists block well over one hundred thousand known ad, tracker, and malware domains
              (the exact count changes with every list update).

# Blocklist URLs to add in Pi-hole dashboard:
# Steven Black unified hosts:
https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts

# OISD full list:
https://big.oisd.nl/domainswild

# After adding lists, update gravity:
docker exec pihole pihole -g

# Check gravity count
docker exec pihole pihole -q example-ad-domain.com
docker exec pihole sqlite3 /etc/pihole/gravity.db \
  "SELECT COUNT(*) FROM gravity;"

### Verify with dig and Pi-hole Dashboard

Full verification covers both the blocking path and the recursive resolution path.
              A known ad domain should return the blocked response; a regular domain should resolve
              through Unbound. The Pi-hole dashboard shows query statistics and confirms upstream
              forwarding to the Unbound instance.

# Test that a known ad domain is blocked
dig @192.168.1.53 doubleclick.net
# Expected: 0.0.0.0 (Pi-hole's default blocking mode)

# Test that a regular domain resolves
dig @192.168.1.53 github.com
# Expected: valid A record

# Check recursive resolution via Unbound directly
dig @127.0.0.1 -p 5335 github.com

# Confirm DNSSEC validation is working
dig @127.0.0.1 -p 5335 sigfail.verteiltesysteme.net
# Expected: SERVFAIL (DNSSEC failure detected correctly)

## Request Flow

## Challenges & Solutions

- Docker macvlan container cannot reach the host: By default, a container
          on a macvlan network cannot communicate with the host machine running Docker, because macvlan
          bypasses the host network stack. This would have prevented Pi-hole from talking to Unbound
          on the host loopback. Resolved by running Unbound in a second container attached to a
          shared internal Docker network; Pi-hole reaches it as unbound#5335, sidestepping
          macvlan's host isolation entirely.

- DNS loop between Pi-hole and Unbound: When both resolvers listen on port 53,
          Pi-hole can forward queries to Unbound, which in some configurations forwards back to
          Pi-hole. Resolved by running Unbound strictly on port 5335 and pointing Pi-hole upstream
          explicitly to unbound#5335, ensuring a one-way forwarding chain.

- Gravity update failing inside container: The pihole -g command
          failed because the container initially had no working outbound route to download
          blocklists. Fixed by correcting the macvlan gateway and default route so the container
          can reach the internet during gravity updates.

- Some legitimate domains blocked: OISD's full list occasionally blocks CDN
          subdomains used by legitimate services. Whitelisting is managed via the Pi-hole dashboard
          under Whitelist, and the OISD basic list is used instead of the full list for stricter
          environments.

## What I Learned

- DNS resolution hierarchy: root nameservers, TLD delegation, and authoritative records

- DNSSEC validation chain and how SERVFAIL signals a tampered record

- Docker macvlan networking and its limitations with host communication

- Pi-hole gravity database structure and SQLite query patterns

- The performance impact of recursive vs forwarding DNS (latency vs privacy)

- Router DHCP option 6 for network-wide DNS distribution without per-device config

## How I built it

ISPs log DNS, and third-party resolvers see every domain your household looks up. This stack keeps resolution in-house: Pi-hole filters the junk, Unbound walks the DNS tree itself, and nothing is forwarded to Google or Cloudflare.

- Phase 1, deploy Pi-hole with its own IP: Created a Docker macvlan network so Pi-hole gets a dedicated address on the LAN, letting the router advertise it as the DNS server via DHCP with zero per-device configuration.

- Phase 2, add the recursive resolver: Deployed Unbound as the upstream: a validating recursive resolver that walks from the root nameservers instead of trusting a third party, with DNSSEC validation enabled.

- Phase 3, load the blocklists: Subscribed to the Steven Black and OISD lists, blocking well over one hundred thousand ad, tracker, and malware domains at the DNS layer (counts change with every update).

- Phase 4, cut over the network: Pointed the router's DHCP DNS advertisement at Pi-hole so every device on the LAN picks it up automatically.

- Phase 5, containerize on Proxmox: Runs the whole stack in Docker inside a Proxmox LXC container for easy snapshots and migration.

## What you need

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | Proxmox host or any Linux machine on the LAN | Runs inside an LXC container or directly on Docker |
| Software | Docker and Docker Compose | Hosts Pi-hole and Unbound |
| Software | Pi-hole, Unbound, dnsmasq (embedded) | Filtering frontend and recursive backend |
| Network | Router with DHCP DNS control | Needed to advertise Pi-hole network-wide |
| Skills | Docker macvlan networking and DNS basics | macvlan quirks and blocklist management |

## Challenges and lessons learned

- macvlan host isolation: with macvlan, the Docker host itself cannot reach the Pi-hole container IP. Lesson: manage it from another LAN device or add a macvlan shim interface on the host.

- False positives: aggressive lists occasionally break legitimate sites or apps. Lesson: keep the Pi-hole audit log handy and whitelist deliberately; the dashboard makes the offending domain obvious.

- DNSSEC validation failures: misconfigured domains fail validation and look like outages. Lesson: learn to read Unbound logs so a broken remote domain is not mistaken for a local problem.

## What is next

- Deploy a secondary resolver so DNS survives maintenance on the primary.

- Offer DNS-over-HTTPS as an optional upstream for specific clients.

- Use Pi-hole client groups for per-device policies, such as stricter filtering for IoT.

- Build query-log analytics to spot new trackers and compromised devices.

## Related Work

- Private Email Server, the mail server that depends on these DNS records.

- Proxmox Homelab, the virtualization host for the DNS VMs.

- Public Search Engine, another self-hosted network service.
