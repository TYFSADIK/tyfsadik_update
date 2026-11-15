# Private Email Server

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 9 min read

Self-hosted SMTP/IMAP with custom domain @tyfsadik.org

## Overview

This project is a fully self-hosted email infrastructure using Postfix as the
        SMTP server and Dovecot for IMAP access, deployed on a VPS with the custom
        domain tyfsadik.org. The goal was to eliminate reliance on Gmail or Proton while
        aiming for reliable delivery to major providers.

Deliverability is supported through a complete set of DNS-based email authentication
        records: DKIM (DomainKeys Identified Mail) signs every outbound message with
        a 2048-bit RSA key, SPF (Sender Policy Framework) authorizes the server's IP,
        and DMARC enforces policy alignment and provides aggregate reporting. TLS is
        mandatory on the submission port and IMAP via Let's Encrypt certificates, and opportunistic
        on port 25 as SMTP standards require. Inbox placement also depends on IP reputation and
        recipient policies, so DMARC reports and queue health are monitored on an ongoing basis.

On ports: outbound client mail uses the submission port (587) with STARTTLS rather than
        the legacy SMTPS port 465, so modern clients work with standard settings. Port 25 stays
        opportunistic-TLS-only because MX-to-MX mail must accept peers that cannot negotiate TLS;
        making TLS mandatory there would break inbound mail.

## Architecture

Outbound Mail

Inbound Mail

port 25 MX lookup

local deliveryMaildir

IMAP :993

SMTP submission:587 STARTTLS

OpenDKIM signs

signed + TLS

DNS Records (tyfsadik.org)

MX recordmail.tyfsadik.org

SPF TXTv=spf1 ip4:x.x.x.x -all

DKIM TXTmail._domainkey

DMARC TXT_dmarc policy

PTR recordreverse DNS

Internet(sender MTA)

Postfix SMTPport 25

DovecotMailbox Store

Mail Client(Thunderbird/mobile)

DKIM Milter

Recipient MX(Gmail, Outlook...)

## Tech Stack

- Postfix, MTA handling SMTP reception (port 25) and submission (port 587)

- Dovecot, IMAP server with Maildir storage and SASL authentication

- OpenDKIM, DKIM signing milter integrated with Postfix

- SPF / DMARC, DNS TXT records for sender authorization and policy enforcement

- Let's Encrypt / Certbot, TLS certificates for SMTP and IMAP

- Linux (Debian 12), VPS host operating system

- Thunderbird / mobile clients, IMAP clients for reading and sending mail

## Build Process

### Install and Configure Postfix

Postfix is installed from apt and configured for internet site operation. The
              main.cf file sets the hostname, domain, mailbox format (Maildir),
              and enables SASL authentication for the submission port. The
              master.cf file activates the submission service on port 587 with
              mandatory STARTTLS.

apt install postfix -y
# Select "Internet Site" during setup, set domain to tyfsadik.org

# /etc/postfix/main.cf key settings:
myhostname = mail.tyfsadik.org
mydomain = tyfsadik.org
myorigin = $mydomain
inet_interfaces = all
mydestination = $myhostname, localhost.$mydomain, $mydomain
home_mailbox = Maildir/
smtpd_tls_cert_file = /etc/letsencrypt/live/mail.tyfsadik.org/fullchain.pem
smtpd_tls_key_file  = /etc/letsencrypt/live/mail.tyfsadik.org/privkey.pem
# Opportunistic TLS on port 25 (required for MX-to-MX mail); mandatory on submission
smtpd_tls_security_level = may
# SASL stays off globally and is enabled only on the submission port (see master.cf)
smtpd_sasl_auth_enable = no
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
# Relay only for local networks and authenticated submission clients
smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination

# Enable submission port in /etc/postfix/master.cf:
submission inet n - y - - smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_security_level=encrypt
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_recipient_restrictions=permit_sasl_authenticated,reject

systemctl restart postfix

### Configure Dovecot IMAP

Dovecot is configured to use Maildir storage, authenticate against system users,
              provide IMAP on port 993 with SSL, and expose a SASL socket that Postfix uses for
              submission authentication. Three key config files are modified.

apt install dovecot-core dovecot-imapd -y

# /etc/dovecot/conf.d/10-mail.conf
mail_location = maildir:~/Maildir

# /etc/dovecot/conf.d/10-auth.conf
disable_plaintext_auth = yes
auth_mechanisms = plain login

# /etc/dovecot/conf.d/10-ssl.conf
ssl = required
ssl_cert = </etc/letsencrypt/live/mail.tyfsadik.org/fullchain.pem
ssl_key = </etc/letsencrypt/live/mail.tyfsadik.org/privkey.pem

# /etc/dovecot/conf.d/10-master.conf (SASL socket for Postfix)
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0660
    user = postfix
    group = postfix
  }
}

systemctl restart dovecot

### Provision TLS with Let's Encrypt

TLS certificates are provisioned for mail.tyfsadik.org using certbot in
              standalone mode (since Nginx is not running on this server). A deploy hook restarts
              Postfix and Dovecot automatically on renewal so they pick up the refreshed certificate.

apt install certbot -y

certbot certonly --standalone \
  -d mail.tyfsadik.org \
  --agree-tos --email taki@tyfsadik.org

# /etc/letsencrypt/renewal-hooks/deploy/restart-mail.sh
#!/bin/bash
systemctl restart postfix dovecot

chmod +x /etc/letsencrypt/renewal-hooks/deploy/restart-mail.sh

# Test renewal
certbot renew --dry-run

### Configure OpenDKIM

OpenDKIM is installed, a 2048-bit RSA signing key is generated for the
              mail selector, and the public key is published as a DNS TXT record.
              Postfix is connected to the OpenDKIM milter so every outbound message is signed
              before delivery.

apt install opendkim opendkim-tools -y

# Generate a 2048-bit key pair (opendkim-genkey defaults to 1024-bit)
mkdir -p /etc/opendkim/keys/tyfsadik.org
opendkim-genkey -s mail -d tyfsadik.org -b 2048 \
  -D /etc/opendkim/keys/tyfsadik.org/
chown opendkim:opendkim /etc/opendkim/keys/tyfsadik.org/mail.private

# /etc/opendkim.conf (key settings)
Domain                  tyfsadik.org
KeyFile                 /etc/opendkim/keys/tyfsadik.org/mail.private
Selector                mail
Socket                  inet:12301@localhost

# /etc/postfix/main.cf (add milter)
milter_protocol = 6
milter_default_action = accept
smtpd_milters = inet:localhost:12301
non_smtpd_milters = $smtpd_milters

# Publish the DNS TXT record from:
cat /etc/opendkim/keys/tyfsadik.org/mail.txt

systemctl enable opendkim && systemctl restart opendkim postfix

### Add SPF and DMARC DNS Records

SPF, DMARC, and MX records are added in the DNS control panel for
              tyfsadik.org. The PTR (reverse DNS) record is set at the VPS provider
              to match the mail hostname, which is critical for avoiding spam classification.

# DNS records to add in domain registrar / DNS panel:

# MX record
tyfsadik.org.      IN  MX  10  mail.tyfsadik.org.

# A record for mail subdomain
mail.tyfsadik.org. IN  A   x.x.x.x

# SPF TXT (authorize only this server's IP)
tyfsadik.org.      IN  TXT "v=spf1 ip4:x.x.x.x -all"

# DKIM TXT (copy public key from mail.txt)
mail._domainkey.tyfsadik.org. IN TXT "v=DKIM1; k=rsa; p=MIIBIj..."

# DMARC TXT (report only first, then reject)
_dmarc.tyfsadik.org. IN TXT "v=DMARC1; p=reject; rua=mailto:taki@tyfsadik.org"

# PTR record (set at VPS provider control panel)
x.x.x.x  -->  mail.tyfsadik.org

### Test with mail-tester.com and swaks

The full email stack is tested by sending a test message to a mail-tester.com address
              and reviewing the report for authentication gaps. Swaks is used for command-line SMTP
              testing to verify SASL authentication, TLS negotiation, and DKIM signing without a
              mail client. Note that SASL authenticates against system user accounts as configured
              in Step 2, so the auth username is the system login, not the full email address.

apt install swaks -y

# Send a test email via the submission port with auth
# (auth-user is the system account; use that account's password)
swaks -to test@mail-tester.com \
  -from taki@tyfsadik.org \
  -server mail.tyfsadik.org:587 \
  -auth LOGIN \
  -auth-user taki \
  -auth-password 'yourpassword' \
  -tls

# Verify DKIM header in received message
# Look for: DKIM-Signature: v=1; a=rsa-sha256; d=tyfsadik.org; s=mail;

# Check mail logs for delivery status
tail -f /var/log/mail.log

## Request Flow

## Challenges & Solutions

- Mail landing in spam at Gmail: Initial deliveries were filtered as spam due
          to a missing PTR record. The VPS provider's reverse DNS panel was used to set the PTR for
          the server's IP to mail.tyfsadik.org, closing the authentication gap.

- Postfix TLS certificate permission errors: Postfix could not read the
          Let's Encrypt private key because its process runs as the postfix user, which
          lacked read access to the /etc/letsencrypt/live/ directory. Resolved by adding
          the postfix user to the ssl-cert group and adjusting the cert
          directory permissions with chmod 750.

- DKIM signing failing silently: Messages were sent without DKIM headers
          because the milter socket was not accessible to Postfix. Fixed by changing the milter
          socket from a Unix socket to a TCP socket (inet:12301@localhost) which is
          accessible regardless of socket file permissions.

- Port 25 blocked by VPS provider: Many VPS providers block outbound port 25
          by default to prevent spam. Resolved by submitting a ticket to the provider to unblock
          port 25 for the server IP after demonstrating legitimate email server configuration.

## What I Learned

- SMTP protocol flow: EHLO, STARTTLS, AUTH, DATA, and QUIT sequence

- Email authentication stack: SPF authorization, DKIM cryptographic signing, DMARC policy enforcement

- PTR record importance for SMTP reputation and inbox delivery

- Postfix queue management, delivery logs, and bounce handling

- Dovecot SASL integration with Postfix for submission authentication

- TLS certificate lifecycle management for non-Nginx services using deploy hooks

## How I built it

Running your own mail server is famously a deliverability project disguised as a server project. The goal here was full ownership of tyfsadik.org mail without landing in spam folders, so authentication and reputation got as much attention as the daemons.

- Phase 1, provision the platform: Deployed a Debian 12 VPS and pointed the tyfsadik.org DNS at it, including reverse DNS which receiving servers check.

- Phase 2, configure Postfix: Set up Postfix for SMTP on port 25 and authenticated submission on port 587 with mandatory STARTTLS, using Maildir storage.

- Phase 3, configure Dovecot: Added Dovecot for IMAP access with SASL authentication wired into Postfix submission.

- Phase 4, prove legitimacy with DNS: Published SPF, DKIM (via OpenDKIM signing), and DMARC records so receivers can verify every message is authorized.

- Phase 5, secure and connect clients: Issued Let's Encrypt certificates for SMTP and IMAP, then configured Thunderbird and mobile clients.

## What you need

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | VPS with a static public IP | Port 25 must be open; many providers block it by default, so confirm first |
| Accounts | A domain with full DNS control | SPF, DKIM, and DMARC all live in DNS |
| Accounts | Reverse DNS (PTR) set by the VPS provider | Receivers check that the IP resolves back to the mail hostname |
| Software | Debian 12, Postfix, Dovecot, OpenDKIM, Certbot | The full mail stack |
| Skills | DNS record management and SMTP fundamentals | Authentication records are where deliverability is won or lost |

## Challenges and lessons learned

- Deliverability to major providers: Gmail and Outlook are skeptical of new sending IPs. Lesson: warm up gradually, keep volume consistent, and monitor DMARC reports for failures.

- DKIM key rotation: rotating keys means publishing new DNS records before switching signers. Lesson: run old and new selectors in parallel during the transition window.

- Inbound spam: owning the server means owning the spam problem too. Lesson: plan for server-side filtering early rather than bolting it on after the first spam wave.

## What is next

- Deploy Rspamd for server-side spam and phishing filtering with per-user scores.

- Add Sieve filtering so users get server-side rules that work across all clients.

- Build queue health monitoring with alerts for deferred mail and blacklist hits.

- Evaluate a lightweight webmail option for access from untrusted devices.

## Related Work

- Self-Hosted DNS, the DNS records every mail server depends on: MX, SPF, DKIM, DMARC.

- Data Sovereignty Stack, the backup story that keeps mail data under your control.

- Self-Hosted Cloud Storage, file storage to round out the self-hosted productivity suite.
