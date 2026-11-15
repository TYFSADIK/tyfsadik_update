# Public Search Engine

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 8 min read

Privacy-respecting meta-search engine: search.tyfsadik.org

## Overview

This project is a publicly accessible SearXNG instance running at
        [search.tyfsadik.org](https://search.tyfsadik.org).
        SearXNG is a privacy-respecting meta-search engine that aggregates results from Google,
        Bing, DuckDuckGo, Wikipedia, GitHub, and other backends in parallel, then deduplicates and ranks them, without exposing any user identity or search history
        to those engines. No account is required. Two honest limits apply: SearXNG may set
        preference cookies, and queries and client addresses can appear in application, container,
        or reverse-proxy logs unless logging is explicitly controlled. This instance is configured
        to minimize both.

The instance is configured with a custom dark theme and deployed behind Nginx with
        rate limiting to prevent abuse from automated scrapers or bots. Redis
        backs SearXNG's application-aware rate limiter and related runtime state. The deployment
        uses the official searxng-docker repository as a base, with custom
        settings.yml modifications to enable preferred engines and tune the result
        ranking.

## Architecture

Search Backends (parallel)

State Layer

SearXNG Container

Proxy Layer

User Layer

HTTPS query

limit_req_zoneproxy_pass

limiter state

parallel fetch

parallel fetch

parallel fetch

parallel fetch

parallel fetch

results

results

results

results

results

merged results

response

Browser Query

Nginxrate limiting + SSL:443

Result Aggregator

Result Ranker+ Deduplicator

Redislimiter state

Google

Bing

DuckDuckGo

Wikipedia

GitHub

## Tech Stack

- SearXNG, open-source meta-search engine with pluggable backends

- Docker & Docker Compose, containerized deployment via searxng-docker

- Nginx, reverse proxy with limit_req_zone rate limiting and SSL

- Redis, rate limiter state and runtime state for SearXNG

- Let's Encrypt / Certbot, TLS certificate for search.tyfsadik.org

- Linux (Debian), host operating system

## Build Process

### Clone searxng-docker and Configure settings.yml

The official searxng-docker repository provides a pre-built compose
              file with Caddy, SearXNG, and Redis (recent revisions run the cache service on the
              Valkey image). This deployment uses only the SearXNG and cache services from that
              file; the bundled Caddy reverse proxy is replaced by the host Nginx configured in
              Step 4. The settings.yml file is edited
              before first launch to set the instance name, generate a secret key, and configure
              engine preferences.

git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker

# Generate a unique secret key
SECRET_KEY=$(openssl rand -hex 32)

# Edit searxng/settings.yml
# Set: general.instance_name, server.secret_key
sed -i "s/ultrasecretkey/$SECRET_KEY/g" searxng/settings.yml

cat searxng/settings.yml | grep secret_key

### Configure Engines and Limiter

The settings.yml file is edited to enable the preferred engine set,
              keep SearXNG's built-in application-aware limiter enabled as a second layer behind
              Nginx's rate limiting (a public instance should not rely on a single control), and
              turn off the image proxy (which adds latency). Engine timeouts are set conservatively
              to prevent slow backends from blocking the response.

# searxng/settings.yml key settings:
general:
  instance_name: "search.tyfsadik.org"
  debug: false

server:
  secret_key: "..."
  limiter: true           # application-aware limiter stays on; Nginx adds a second layer
  image_proxy: false

search:
  safe_search: 0
  autocomplete: "google"

# Enable specific engines (excerpt):
engines:
  - name: google
    engine: google
    timeout: 3.0
    weight: 2
  - name: bing
    engine: bing
    timeout: 3.0
  - name: duckduckgo
    engine: duckduckgo
    timeout: 3.0
  - name: wikipedia
    engine: wikipedia
    timeout: 2.0
  - name: github
    engine: github
    timeout: 3.0

### Start the Stack

The SearXNG + cache services are started with Docker Compose. The
              pre-built docker-compose.yaml from the searxng-docker repo already
              includes correct inter-service networking for those services; Nginx runs on the host,
              not in Compose.

docker compose up -d

# Check all containers are up
docker compose ps

# Test SearXNG is responding locally
curl "http://localhost:8080/search?q=test&format=json" | jq '.results | length'

# Check Redis is connected
docker compose logs searxng | grep -i redis

### Nginx Config with Rate Limiting

The Nginx configuration uses limit_req_zone to restrict each IP to
              10 requests per minute for the search endpoint. A separate zone with a higher limit
              is applied to static assets. This prevents bot scraping while keeping the service
              usable for legitimate users.

# /etc/nginx/nginx.conf (http block)
limit_req_zone $binary_remote_addr zone=searxng_search:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=searxng_static:10m rate=60r/m;

# /etc/nginx/sites-available/search.tyfsadik.org
server {
    listen 443 ssl;
    server_name search.tyfsadik.org;

    ssl_certificate /etc/letsencrypt/live/search.tyfsadik.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/search.tyfsadik.org/privkey.pem;

    location /search {
        limit_req zone=searxng_search burst=5 nodelay;
        limit_req_status 429;
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        limit_req zone=searxng_static burst=20;
        proxy_pass http://localhost:8080;
    }
}

### Apply Custom Dark Theme

SearXNG supports custom CSS via a theme file. A dark theme based on the existing
              simple theme is created by overriding CSS variables in a custom stylesheet file
              that is bind-mounted into the container's theme directory.

# searxng/static/themes/simple/css/searxng.min.css (custom overrides)
# Create custom.css and add to bind mount in compose file

# In searxng/settings.yml:
ui:
  default_theme: simple
  theme_args:
    simple_style: dark

# Or override via a custom CSS file:
# services.searxng.volumes in docker-compose.yaml:
# - ./searxng/custom.css:/usr/local/searxng/searx/static/themes/simple/css/custom.css

# Verify theme is applied
curl https://search.tyfsadik.org | grep "dark"

### Provision SSL Certificate

Certbot with the Nginx plugin provisions the Let's Encrypt certificate and
              automatically modifies the Nginx server block to add SSL directives and the
              HTTP-to-HTTPS redirect.

apt install certbot python3-certbot-nginx -y

certbot --nginx -d search.tyfsadik.org \
  --agree-tos --email taki@tyfsadik.org

# Verify HTTPS is working
curl -I https://search.tyfsadik.org
# Expected: HTTP/2 200

# Check certificate expiry
echo | openssl s_client -connect search.tyfsadik.org:443 2>/dev/null \
  | openssl x509 -noout -dates

## Request Flow

## Challenges & Solutions

- Some engines rate-limiting the SearXNG IP: Google and Bing occasionally
          returned CAPTCHA challenges or empty results after frequent requests from the same server IP.
          Resolved by setting conservative engine timeouts (3 seconds), marking engines as
          disabled when they return persistent errors, and relying on DuckDuckGo and
          Brave Search as fallback engines that are less aggressive with bot detection.

- High resource usage from concurrent searches: Each search spawns multiple
          outbound HTTP requests in parallel, and with several users searching simultaneously the
          Python worker count became a bottleneck. Tuned by setting the UWSGI_WORKERS environment variable (the
          official image's documented knob for worker processes, default 4) to 2 on the
          constrained server, reducing memory usage while maintaining acceptable
          response times.

- Bot traffic overwhelming the instance: Shortly after the instance was
          indexed by search engines, automated scrapers began sending hundreds of requests per minute.
          The Nginx limit_req_zone rate limiter reduced this to manageable levels,
          and returning HTTP 429 to violators causes well-behaved bots to back off.

- Redis connection refused on first start: SearXNG started before Redis
          was ready, causing connection errors in the logs. Fixed by adding
          depends_on: redis with a condition: service_healthy health
          check in the compose file.

## What I Learned

- Nginx limit_req_zone rate limiting: zones, burst allowance, and nodelay semantics

- SearXNG engine configuration: timeout tuning, weight scoring, and engine disabling

- Redis-backed limiter state and its role in SearXNG

- Meta-search architecture: parallel fan-out requests, result deduplication by URL hash

- Bot mitigation strategies: rate limiting, HTTP 429 responses, and Nginx access logging analysis

- Docker Compose service health checks and dependency ordering

## How I built it

The goal was a search page I could set as my default without feeding a profile to anyone: no account, minimized cookies, minimized logging, with results aggregated from the engines I already trusted.

- Phase 1, deploy the upstream stack: Cloned the official searxng-docker repository, which bundles SearXNG, Nginx, and Redis in one compose file.

- Phase 2, configure identity and engines: Edited settings.yml to set the instance name, generated a unique secret key, enabled the preferred engine set, kept the built-in limiter enabled, and turned off the image proxy.

- Phase 3, harden the front door: Configured Nginx rate limiting to blunt scrapers and bots, with Redis backing SearXNG's limiter state.

- Phase 4, publish with TLS: Issued a Let's Encrypt certificate and published the instance at search.tyfsadik.org.

- Phase 5, theme and tune: Applied the custom dark theme and tuned engine timeouts for a balance of completeness and speed.

## What you need

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | Any small VPS or homelab VM | Modest CPU and RAM; caching keeps it light |
| Software | Docker and Docker Compose | Runs the searxng-docker stack |
| Software | SearXNG, Nginx, Redis | Engine, rate-limited front door, and cache |
| Accounts | A domain with DNS control | For the TLS certificate |
| Skills | YAML config editing and basic Nginx | settings.yml and limit_req_zone tuning |

## Challenges and lessons learned

- Upstream engine pushback: Google and Bing rate-limit or block datacenter IPs hitting them at volume. Lesson: diversify engines and tune timeouts and weights so a single blocked backend never empties the results.

- Abuse from bots: a public instance attracts scrapers fast. Lesson: Nginx rate limiting plus Redis-backed throttling keeps the instance usable without accounts.

- Result quality tuning: defaults favor breadth over relevance. Lesson: curate the engine list per category instead of enabling everything.

## What is next

- Curate per-category engine sets tuned for code, academic, and news queries.

- Add uptime and result-quality monitoring with alerts.

- Enable bang-style shortcuts for power users.

- Configure fallback engines that activate when a primary is blocked.

## Cite This Page

**Q: Citation formats**

A: Plain text
