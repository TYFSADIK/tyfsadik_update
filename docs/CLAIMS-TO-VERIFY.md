# CLAIMS-TO-VERIFY.md

Every employer, title, degree, certification, and metric published on the site,
with where it appears. Confirm each against the resume. Flag anything that
should be reworded; do not edit silently.

## Employers and roles

| Claim | Where it appears | Notes |
|---|---|---|
| Data Center Engineer at Microsoft (cyber threat intelligence applied to physical infrastructure) | index.html hero, about.html, resume.html | Confirm title and that describing CTI work is acceptable |
| Incident Manager at Felixous Technology Inc. | index.html hero, about.html, resume.html | Confirm spelling of employer name |
| CardiOCare: healthcare systems at 99%+ uptime, VLAN-segmented network, compliance data flows | index.html Career Highlights, work pages | Confirm metric and employer naming |

## Education

| Claim | Where it appears | Notes |
|---|---|---|
| University of Toronto, B.Eng, Information Technology | index.html, about.html, resume.html, JSON-LD alumniOf | U of T's engineering faculty does not offer a "B.Eng, Information Technology" under that exact name; confirm the exact credential wording |
| "Seneca College of Applied Arts and Technology" (postgraduate, Cyber/Electronic Operations) | index.html, about.html | Seneca rebranded to "Seneca Polytechnic" in 2023. JSON-LD alumniOf already says "Seneca Polytechnic", visible copy says the old name. Decide which to show; both currently appear on the site |

## Metrics

| Claim | Where it appears | Notes |
|---|---|---|
| Cut SOC alert MTTR by 25% | index.html, about.html, resume.html | Confirm |
| Automated 30+ daily security alerts | index.html, about.html | Confirm |
| 7-node Kubernetes cluster on Proxmox | index.html, work/infrastructure/kubernetes-infrastructure.html | Consistent across site |
| 116 labs across nine tracks | many pages, site-data.json | Consistent (24+12+16+18+14+8+9+9+6 = 116) |
| 99%+ uptime at CardiOCare | index.html, resume.html | Confirm |
| 25+ certifications | index.html, site-data.json, resume.html | Confirm count |
| TYF-AI: "50+ concurrent users under 2s", "~2.5 Gbps SSD", "<50ms tunnel latency" | work/infrastructure/tyf-ai-platform.html | Confirm measured vs estimated |
| Proxmox page: "3-node HA cluster with Ceph" | work/infrastructure/proxmox-zero-trust.html | Homepage says "3-node Proxmox HA cluster" only in Career Highlights; confirm Ceph is actually deployed (asset register lists it as partially verified) |
| 4+ years in IT, 9 self-hosted services, 44 projects | site-data.json stats | Confirm |

## Schema

| Claim | Where it appears | Notes |
|---|---|---|
| jobTitle "Cybersecurity & IT Professional" | JSON-LD on index, about, resume | Aligned to the visible site tagline this round (was "Cybersecurity & IT Infrastructure Specialist"); confirm |
| alumniOf: Seneca Polytechnic, University of Toronto | JSON-LD | Confirm both, and confirm publishing them in schema |
| worksFor | NOT included anywhere | Held back pending confirmation |

## External links needing owner action (not removed)

These returned errors from the link checker. Links were left in place per the
no-removal rule; decide whether the repos should be made public or the URLs
updated.

- 404: github.com/TYFSADIK/Arch-Linux-Remote-Desktop-WSL2
- 404: github.com/TYFSADIK/email_server
- 404: github.com/TYFSADIK/my_proxmox
- 404: github.com/TYFSADIK/DNS_server
- 404: github.com/tyfsadik/tyf-ai
- 404: github.com/TYFSADIK/Birthday
- 404: github.com/TYFSADIK/Hakimi_fruits
- 404: github.com/TYFSADIK/HomeBound_Aisha
- 404: github.com/TYFSADIK/For_habiba_pharmasy_Assignment
- ERR (unresolvable): cdot.senecac.on.ca/projects/toaster/ (only referenced inside `.tools/ref/`, not a public page)
- 403 to bots but fine in browsers: dell.com support pages, rsync.net howto, linkedin.com profile URL

Fixed this round: Proxmox wiki Ceph guide URL (underscores became a hyphen upstream).
