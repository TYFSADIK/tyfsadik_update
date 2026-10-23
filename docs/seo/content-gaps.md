# Content gaps

Queries the site should answer but does not yet cover with a dedicated page
or section. Each suggestion fits the existing structure; none requires
inventing facts. Ordered by likely value.

## High value, content already exists to support them

1. **"How I cut SOC alert MTTR by 25%"** as a standalone write-up. The claim
   is on the homepage, About, and resume, but no page explains the method
   (workflow mapping, the 3 bottlenecks, the enrichment pipelines). Suggested
   page: `work/infrastructure/soc-mttr-case-study.html` or a blog post. This
   is the single most quotable career metric on the site.
2. **Per-track lab landing content for search**: the nine track indexes exist
   (`blog/labs/<track>/index.html`) and the labs index now has anchors. Each
   track index could gain a 40-60 word answer-first summary and a visible FAQ
   to match the pattern used on individual labs.
3. **"Kubernetes on Proxmox homelab" full guide**: the cluster page covers
   the architecture; a step-by-step "from bare metal to running cluster"
   guide would target the highest-volume infrastructure query in the seed
   bank. Much of the content exists across the cluster page and labs; it
   needs assembly, not invention.
4. **Cold-soak battery dataset page**: the rig page exists; the "Next" list
   says the dataset will be published. When it is, a dedicated dataset page
   (schema.org Dataset) would be a genuinely citable artifact.

## Medium value

5. **"Chakor vs hosted AI chat"** comparison: what self-hosting buys and
   what it costs, written from the Chakor page's own architecture facts.
6. **Pi-hole and DNS filtering page**: the self-hosted DNS project exists;
   a focused Pi-hole + Unbound write-up matches strong evergreen queries
   (verify what is actually deployed first; do not claim Unbound if absent).
7. **Proxmox backup and restore drill**: the zero-trust page covers ZFS
   snapshot retention; a restore-drill page (tested steps, not theory) would
   answer "proxmox restore from snapshot" queries with first-hand proof.
8. **Glossary expansion**: DDIL, EKF, SBOM, MTTR, ADS-B, AIS are defined on
   project pages; promoting each to a glossary anchor entry makes them
   linkable from every lab that uses the term.

## Lower value, skip unless time allows

9. City-specific service pages: explicitly NOT recommended. The site is a
   global technical portfolio; `work-with-me.html` covers local intent
   honestly. Doorway pages would violate the no-spam rule.
10. Video or audio versions of labs: only if the owner records them; do not
    fake multimedia schema.

## Verification needed before writing

- The MTTR case study needs the owner's confirmation that the workflow
  details are shareable (docs/CLAIMS-TO-VERIFY.md).
- Any dataset page must wait for the actual dataset.
