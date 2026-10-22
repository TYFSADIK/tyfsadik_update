# Engineering Documentation

How the projects on this site are documented, what the status labels mean, and where the glossary and decision records live.

## Documentation Philosophy

Every project page on this site follows the same rule: evidence first, explanation second, presentation third.
      Evidence means the thing actually ran: command output, photographs, measured values, and configuration files that were
      applied to real hardware. Explanation means the reasoning is written down, including the options that were rejected and why.
      Presentation, the layout, diagrams, and polish, comes last and never substitutes for the first two.

This ordering has practical consequences. Pages state what is verified and what is not, challenges and failures are
      documented alongside successes, and unknowns are labeled as unknowns rather than smoothed over. When a number cannot be
      backed by a measurement, the page says so.

## Project Status Conventions

Projects and components across this site carry one of five status labels. They mean specific things:

- Verified: the claim was tested on the running system and the result is recorded on the page. Example: a component table entry marked “Verified, in daily use” on the server room page.

- Documented: the work is complete and written up with enough detail to reproduce it, but the claim rests on the write-up rather than a fresh re-test.

- In Progress: the build is underway; parts work, parts do not yet. Pages with this status change as work lands.

- Simulation: the design was validated in simulation (for example Gazebo, ArduPilot SITL, or Mininet) but not yet on physical hardware.

- Planned: scoped and designed, not started. Appears in roadmap and future-work sections.

If a page does not say which of these applies to a claim, treat the claim as unverified until it is updated.

## Reference Documents

- Engineering Glossary, the vocabulary used across this site: networking, orchestration, storage, security, AI, and defence terms, each defined in one or two plain sentences.

- Engineering Decision Records, reconstructed ADRs covering the major platform choices behind the homelab: hypervisor, Kubernetes distribution, storage, remote access, and local AI inference.

- Infrastructure Asset Register, the physical and logical inventory behind the lab: what is confirmed, what is stated but not yet evidenced, and what is planned, including the GPU-cluster feasibility analysis and the storage capacity model.

## Where the Documentation Applies

The main project categories live on the [projects page](../work.html): infrastructure, defence, applications, games, and web development. The three flagship case studies below show the documentation philosophy applied end-to-end:

- Kubernetes Infrastructure, a 7-node kubeadm cluster on Proxmox hosts, with Calico, MetalLB, and Longhorn, including the wireless-node flapping failure and its fix.

- Homelab Server Room, the physical layer: racks, 802.1Q VLAN trunking, a 5 GHz wireless backhaul, power, and cooling, with an explicit list of what is not yet measured.

- Canadian Defence Hardware Program, eleven hobby-scale sensor and robotics builds mapped to publicly stated Canadian defence requirements.
