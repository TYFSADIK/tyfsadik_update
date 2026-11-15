# Public Wiki Server

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 9 min read

Full Wikipedia mirror for restricted regions: wiki.tyfsadik.org

## Overview

This project serves a complete, compressed Wikipedia mirror at
        [wiki.tyfsadik.org](https://wiki.tyfsadik.org)
        using Kiwix. Kiwix serves content from ZIM files, a
        custom compressed archive format designed for offline encyclopedias. A single Wikipedia ZIM
        file contains the full text and images of the English Wikipedia (roughly 90 GB; the exact
        size varies by release) in a format that Kiwix can serve article-by-article with full-text
        search, without unpacking the archive. Note that full-text search only works when the ZIM
        was built with a full-text index; some ZIM variants ship without one.

The primary purpose is to provide Wikipedia access to users in countries where the site is
        restricted or intermittently blocked. The Kiwix server requires no JavaScript from external
        sources, no CDN dependencies, and makes no outbound network requests during operation -
        every response is served entirely from the local ZIM file. The stack is intentionally minimal:
        a single kiwix-serve process behind an Nginx reverse proxy with Let's Encrypt SSL.
        No database, no dynamic backend, no user tracking.

## Architecture

HTTPS requestwiki.tyfsadik.org

proxy_pass :8080

mmap read(random access)

article HTML+ assets

response(no external deps)

User Browser(any region)

Nginx:443 SSL termination

kiwix-serve:8080

ZIM FileWikipedia EN~90 GB (varies)

DedicatedStorage Volume

## Tech Stack

- Kiwix / kiwix-serve, ZIM file HTTP server with full-text search

- ZIM format, compressed archive for offline Wikipedia content

- Nginx, reverse proxy, SSL termination, access logging

- Let's Encrypt / Certbot, TLS certificate for wiki.tyfsadik.org

- systemd, service unit for kiwix-serve auto-start and restart

- Linux (Debian), host operating system

- aria2c, resumable multi-connection download for the roughly 90 GB ZIM file

## Build Process

### Install kiwix-tools

The kiwix-tools package provides kiwix-serve (the HTTP server) and
              kiwix-manage (library management). On Debian, the package is available
              in the standard repository. Alternatively, a static binary is downloaded from the
              Kiwix releases page for systems where the packaged version is outdated.

apt install kiwix-tools -y

# Verify installation
kiwix-serve --version

# If package version is too old, use static binary:
wget https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-x86_64.tar.gz
tar xf kiwix-tools_linux-x86_64.tar.gz
# The extracted directory name carries the release version; use a wildcard
mv kiwix-tools_linux-x86_64*/kiwix-serve /usr/local/bin/
chmod +x /usr/local/bin/kiwix-serve

### Download Wikipedia ZIM File

The Wikipedia ZIM file is downloaded from the Kiwix library. ZIM filenames carry the
              release date and change with every dump, so check
              https://download.kiwix.org/zim/wikipedia/ for the current filename and
              substitute it below. Due to its size (roughly 90 GB), aria2c is used for
              resumable multi-connection download. The kiwix-manage tool creates a
              library XML file that kiwix-serve reads to locate the ZIM.

apt install aria2 -y

mkdir -p /var/lib/kiwix

# Download with aria2c: 4 connections, resumable
# (substitute the current dated filename from the Kiwix library)
aria2c -x 4 -c -d /var/lib/kiwix \
  https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_YYYY-MM.zim

# Verify file integrity
ls -lh /var/lib/kiwix/wikipedia_en_all_maxi_YYYY-MM.zim

# The service runs as www-data (see Step 3), so it must be able to read the files
chown -R www-data:www-data /var/lib/kiwix

# Create Kiwix library
kiwix-manage /var/lib/kiwix/library.xml add \
  /var/lib/kiwix/wikipedia_en_all_maxi_YYYY-MM.zim

cat /var/lib/kiwix/library.xml

### Create systemd Service for kiwix-serve

A systemd service unit ensures kiwix-serve starts on boot, restarts automatically on
              failure, and runs as an unprivileged user. The service is configured to listen on
              port 8080 (localhost only) and serve from the library XML file. Adding
              --monitorLibrary (or sending the process a SIGHUP) reloads the library
              XML without a restart when new ZIM files are added.

# /etc/systemd/system/kiwix-serve.service
[Unit]
Description=Kiwix ZIM HTTP Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
ExecStart=/usr/local/bin/kiwix-serve \
    --library /var/lib/kiwix/library.xml \
    --port 8080 \
    --address 127.0.0.1 \
    --threads 4
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

# Enable and start
systemctl daemon-reload
systemctl enable kiwix-serve
systemctl start kiwix-serve
systemctl status kiwix-serve

### Nginx Reverse Proxy Configuration

Nginx proxies requests from wiki.tyfsadik.org to kiwix-serve on
              localhost port 8080. The proxy timeout is set high enough to accommodate
              full-text search queries, which can take several seconds on large ZIM files.

# /etc/nginx/sites-available/wiki.tyfsadik.org
server {
    listen 80;
    server_name wiki.tyfsadik.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name wiki.tyfsadik.org;

    ssl_certificate /etc/letsencrypt/live/wiki.tyfsadik.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wiki.tyfsadik.org/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }
}

ln -s /etc/nginx/sites-available/wiki.tyfsadik.org /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

### Provision SSL Certificate

Certbot provisions the Let's Encrypt certificate using the Nginx plugin, which also
              handles the HTTP-to-HTTPS redirect configuration automatically. The certificate
              auto-renews via a systemd timer.

apt install certbot python3-certbot-nginx -y

certbot --nginx -d wiki.tyfsadik.org \
  --agree-tos --email taki@tyfsadik.org

# Confirm HTTPS is serving correctly
curl -IL https://wiki.tyfsadik.org
# Expected: HTTP/2 200

# Verify the cert details
certbot certificates

### Test Article Access and Search

Article access and full-text search are tested directly against the kiwix-serve
              endpoint and through the Nginx proxy. The kiwix-serve API exposes a search endpoint
              that returns JSON, which can be tested with curl.

# Test direct access to kiwix-serve
curl http://127.0.0.1:8080/

# Test article access (substitute your ZIM's book name from library.xml)
curl http://127.0.0.1:8080/wikipedia_en_all_maxi_YYYY-MM/A/Python_(programming_language) \
  | grep "<title>"

# Test full-text search API (requires a ZIM built with a full-text index)
curl "http://127.0.0.1:8080/search?pattern=linux&books.name=wikipedia_en_all_maxi_YYYY-MM" \
  | head -50

# Verify through Nginx proxy
curl https://wiki.tyfsadik.org/ | grep "Kiwix"

# Monitor kiwix-serve logs
journalctl -u kiwix-serve -f

## Data Flow

Article page

Search query

User requestsarticle or search

Nginx :443SSL termination

kiwix-serve :8080parse request URL

Request type

mmap ZIM fileseek to article offset

Full-text index(built into ZIM)

Decompress article(zstd / lzma)

Return article list(JSON)

Serve HTML + assets(images, CSS inline)

User sees page(no external requests)

## Challenges & Solutions

- ZIM file download size and reliability: The roughly 90 GB Wikipedia ZIM
          file took many hours to download on a typical VPS connection, and an interrupted download
          would require starting over. Solved by using aria2c with the -c
          flag (continue interrupted downloads) and -x 4 (4 parallel connections), which
          allowed resuming after connection drops.

- Memory pressure from mmap on low-RAM server: kiwix-serve memory-maps the
          ZIM file, so the kernel page cache can grow large; on a small server this leaves little
          headroom for Nginx and the OS. The page cache is reclaimable under pressure, but
          concurrent requests multiply active buffers, so reducing --threads from the
          default 4 to 2 lowered peak memory use.

- kiwix-serve not starting after system reboot: The systemd unit was not
          enabled, so it started manually but not on boot. Resolved by running
          systemctl enable kiwix-serve, which creates the symlink in the appropriate
          wants directory.

- Full-text search returning no results for some queries: Full-text search
          only works when the ZIM was built with a full-text index; ZIM variants without one support
          title search only, which confuses users expecting Google-style fuzzy search. Added a note
          to the landing page explaining the search behavior and linking to the ZIM file's built-in
          search page.

## What I Learned

- ZIM file format: structure, article offsets, embedded full-text index, and compression

- Memory-mapped file I/O and its interaction with the Linux kernel page cache

- systemd service unit design for long-running single-binary services

- aria2c multi-connection resumable downloading for large files

- Serving static content without any database or dynamic backend at scale

- Access considerations for users in internet-restricted regions

## How I built it

Wikipedia is blocked or throttled in several countries, and even where it works, reading it should not require trackers or CDNs. Kiwix serves the whole encyclopedia from a single compressed file with no database, no backend, and no outbound requests.

- Phase 1, install the tools: Installed kiwix-tools on Debian, which provides kiwix-serve for HTTP serving and kiwix-manage for library management; the static binary from Kiwix releases is the fallback when distro packages lag.

- Phase 2, download the archive: Fetched the English Wikipedia ZIM file, roughly 90 GB with full text and images, using aria2c for resumable multi-connection download.

- Phase 3, build the library: Used kiwix-manage to create the library XML that kiwix-serve reads to expose the archive with full-text search.

- Phase 4, run it as a service: Created a systemd unit so kiwix-serve starts on boot and restarts on failure.

- Phase 5, publish with TLS: Placed Nginx in front as a reverse proxy with a Let's Encrypt certificate at wiki.tyfsadik.org, keeping the stack minimal end to end.

## What you need

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | About 100 GB of disk for the ZIM plus headroom | The full-text-and-images archive is roughly 90 GB |
| Software | kiwix-tools (kiwix-serve, kiwix-manage) | From the distro repo or the static Kiwix release binary |
| Software | aria2c for the download | Resumable multi-connection fetching for the roughly 90 GB file |
| Software | Nginx, systemd, Certbot | Reverse proxy, service management, TLS |
| Skills | Basic Linux service administration | systemd units and Nginx proxy config |

## Challenges and lessons learned

- The 90 GB download: a single interrupted transfer wastes hours. Lesson: aria2c with resume is mandatory, and verify the file before pointing the service at it.

- ZIM freshness: dumps are rebuilt periodically, so the mirror slowly goes stale. Lesson: plan a re-download cadence and keep the old file until the new one is verified live.

- Minimalism as a feature: the temptation is to add analytics or a database. Lesson: the no-JS, no-tracking, single-process design is the point; resist feature creep.

## What is next

- Add more ZIM libraries such as WikiMed and Stack Exchange archives.

- Automate scheduled ZIM updates with verification before cutover.

- Add lightweight offline-first tweaks for low-bandwidth readers.

- Publish mirror statistics like served articles and uptime.

## Related Work

- Self-Hosted Cloud Storage, file storage alongside the wiki.

- Public Search Engine, self-hosted search across your own content.

- Data Sovereignty Stack, the backup design behind these services.
