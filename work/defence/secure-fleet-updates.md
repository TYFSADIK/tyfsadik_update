# Secure Robot-Fleet Updates

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building · 29 min read

Every node in my fleet boots only signed code, accepts only updates signed by an offline key, and rolls a bad update back automatically, then I prove it in a freezer, because that is where Canadian robots actually work.

## Overview

The Army's MINERVA challenges say it plainly: Canada has bought foreign
        robotic systems of mixed quality, with components from unstable supply chains. The
        Defence Drone Initiative (launched July 23, 2026) makes supply-chain
        integrity a theme rather than an afterthought. A drone or ground robot that will accept
        any firmware image anyone hands it is a liability, no matter how good its sensors are.

This build connects my DevOps discipline to hardware. The fleet is small, the Raspberry Pi
        nodes from my rover and sensor builds, but the rules are the ones a real program needs:

- Every device boots only signed code, a secure-boot chain from the bootloader up, with a TPM 2.0 measuring each stage and holding the disk keys hostage to that measurement.

- Every update is signed by an offline key, Ed25519 keys that live on YubiKeys, not on any machine connected to a network.

- A bad update rolls itself back, A/B partitions with health checks, so a broken image never strands a node in the field.

And because these robots are meant to operate in the cold, the same cold the MINERVA
        documents complain about, the whole update-and-rollback cycle gets validated in a freezer,
        not just on a warm bench.

## Proof of Build

What each part of the photo does:

- Raspberry Pi fleet node: the same kind of computer that runs the rovers and sensors, used here as the update target.

- TPM 2.0 module: measures the boot chain and holds keys, so the node can prove it booted only signed software.

- Oscilloscope: used while bringing up the TPM connection to the Pi.

- Laptop: shows the verified secure-boot log, the TPM integrity status, and the rollback screen after a deliberately bad update.

## Bill of Materials

Everything below is already purchased and on my bench. The fleet nodes themselves are shared
        with the rover and sensor builds, so the incremental cost of making the whole fleet
        trustworthy is essentially the TPM and the keys.

| Item | What I used | Est. US$ |
| --- | --- | --- |
| TPM | TPM 2.0 add-on board for the Pi | 25-40 |
| Signing keys | 2 YubiKeys (one as backup) | 100-110 |
| Targets | Raspberry Pi fleet nodes from the rover/sensor builds | (shared) |
| Cold chamber | Canadian winter (free) or chest freezer (shared with the cold-soak rig) | 0-300 |

## Architecture

FLEET NODE (Pi)

HOMELAB FLEET SERVER

OFFLINE SIGNING

checks fail

YubiKeyEd25519 root key

Image buildsyft SBOM + sign

Update serverper-device identity + policy

Store-and-forwardcampaign queue

Signed bootloader+ kernel

TPM 2.0measured boot (PCRs)

A/B slotsRAUC

Health checksauto rollback

Figure 1: images are signed by a key that never touches a network, delivered through a store-and-forward campaign queue, and installed into the inactive A/B slot, health checks decide whether the new slot stays or the node rolls back.

Two trust chains meet here. The boot chain (signed bootloader, signed
        kernel, TPM measurement) guarantees the node runs only what I signed. The
        update chain (offline signing, per-device policy, A/B slots with
        automatic fallback) guarantees I can change what it runs without ever being able to brick
        it. A node that misses a campaign because its link is down simply picks the bundle up when
        the link returns, the same DDIL store-and-forward pattern as my field nodes.

## Measured Boot vs Secure Boot

Steps 01 through 04 implement two different ideas that are easy to conflate. Secure boot
        is a gate: the bootloader checks signatures and refuses to execute
        anything unsigned, so bad code never runs. Measured boot is a record:
        each boot stage hashes the next and extends the hash into a TPM Platform Configuration
        Register (PCR), so at the end the TPM holds a fingerprint of exactly what booted, and
        the disk keys are sealed to that fingerprint. Tamper with the image and the PCRs change;
        the TPM then refuses to unseal, and the attacker gets a brick, not the data.

extends hash

extends hash

measurements match baseline

any stage changed

Bootloader(signed, OTP key)

Kernel + initramfs(bundled in boot image)

Rootfs(LUKS2 encrypted)

PCR 0(firmware)

PCR 7(secure-boot policy)

LUKS key sealedto PCRs 0+7

Disk unlocks

TPM refuses to unseal

Figure 2: the measured-boot chain: each boot stage extends a PCR, and the LUKS disk key is sealed to PCRs 0+7. A modified initramfs changes the measurements, the seal policy fails, and the disk stays locked. This is the mechanism T2 exercises.

### Why both are needed

Secure boot alone can refuse a tampered image, but it tells you nothing about what
          actually ran, and a keyed attacker with a valid signature could boot an older,
          vulnerable image. Measured boot alone cannot stop anything; it only records. Together
          they close both gaps: the signature check decides whether code may run, and the PCR
          chain decides whether the disk keys may be released, so even a validly-signed-but-old
          image cannot unlock data sealed to the current measurements. The recovery passphrase
          in a separate LUKS keyslot (step 04) is the escape hatch for when the measurements
          change legitimately, as any kernel update does.

### Why the signing key never leaves the card

The Ed25519 fleet root key is generated on the YubiKey with
          gpg --edit-card, admin PIN, and generate. On-card generation
          means the private key material never exists on any disk, it physically cannot be
          exported, so there is no backup file to steal and no laptop image that can leak it.
          Answering "no" to the "off-card backup of encryption key" prompt keeps even that
          option closed for the signing slot. The RAUC bundles in step 07 are signed with a
          second on-card key in the YubiKey's PIV slot (generated with yubico-piv-tool, accessed
          via the pkcs11: URI) rather than the OpenPGP key, because cosign and RAUC speak
          PKCS#11 and cannot reach the OpenPGP application: two applications on the same card,
          two keys, same never-leaves-the-card property. One firmware note: Ed25519 in the PIV
          slot needs YubiKey firmware 5.7 or later; older cards do the same job in the PIV slot
          with RSA-2048 or P-256, reached through the same pkcs11: URI. The cost of this property is real: if the card is
          lost, the key is gone, which is exactly why the second YubiKey holds a backup key
          generated the same way, stored separately and offline. The pipeline verifies with the
          exported public key only, the proof that verification needs nothing secret.

## Test Status

A quick visual of where the six tests stand, drawn straight from the targets table below.
        This is a status snapshot, not results: "passing" means the mechanism fires correctly on
        the bench rig (T1, T2), not that the run counts are statistically meaningful. Full
        numbers land only when the campaign, rollback, cold-matrix, and chaos batteries have
        accumulated enough runs.

Figure 3: test status as of this writing. Two tests have their mechanisms firing correctly on the bench rig; three are accumulating runs; the full power-cut chaos battery is next. No pass-rate numbers are published yet.

## Wiring & Connections

The hardware side of this build is deliberately boring, most of the security lives in
        software. What is physically connected, and why:

| From | To | Cable or interface | Notes |
| --- | --- | --- | --- |
| TPM 2.0 module (Infineon SLB9670) | Pi 5 GPIO header | SPI0: MOSI/MISO/SCLK on GPIO 9/10/11, CE0 on GPIO 8, 3.3 V + GND | Module seats directly on the header; keep leads short so the SPI clock stays clean |
| Pi 5 UART (GPIO 14/15) | Bench laptop | 3.3 V USB-UART adapter | The only way to see early-boot failures when secure boot refuses an image and the screen stays black |
| DS18B20 temperature probe | Pi 5 GPIO 4 (1-Wire) | 3-wire lead, 4.7 kΩ pull-up to 3.3 V | Logs freezer temperature next to update logs; shared with the cold-soak rig |
| Wi-Fi smart plug | Pi 27 W USB-C supply | Mains side | The chaos-test power switch: cuts the node at random offsets mid-flash |
| Oscilloscope probes | SPI lines (SCLK, MOSI, MISO, CS) | Scope probes + ground clips | Used while bringing up the TPM overlay to confirm clock and traffic; visible in the bench photo |
| Fleet server (homelab) | Fleet nodes | Ethernet on the bench, Wi-Fi in the field | Campaigns over TLS; nodes resume partial downloads when the link drops |
| YubiKey (root signing key) | Offline signing laptop | USB | Never plugged into a networked machine; signed bundles cross to the server on removable media |

## How I Built It

**Q: Build steps (12 steps with code; expand to read)**

A: The foundation is Raspberry Pi secure boot: the EEPROM bootloader signature-checks the boot image, which bundles the kernel, initramfs, and device tree, so nothing unsigned ever executes. I generated an RSA-2048 device key on the offline signing machine, hashed the public key into the Pi's one-time-programmable (OTP) memory, and set SIGNED_BOOT=1 in the EEPROM config. From that moment the board is a device that will only boot my code.

## Testing & Metrics

The test protocol treats trust properties as measurable, pass/fail things. Each run below
        has a fixed setup, procedure, and metric; results are logged per run so the eventual
        dataset is counts, not vibes.

### T1, Boot-chain rejection

- Setup: OTP-programmed node, serial console attached to catch early-boot output.

- Procedure: attempt to boot (a) an unsigned image, (b) an image signed with the wrong key, (c) a valid image with one byte flipped.

- Metric: boots accepted. Target: 0 of 3, every variant must be refused before the kernel starts.

### T2, TPM seal integrity

- Setup: node with LUKS rootfs, key sealed to PCRs 0+7, recovery passphrase in a separate keyslot.

- Procedure: boot a deliberately modified initramfs; attempt to unlock the disk. Repeat with the unmodified image as control.

- Metric: unseal blocked for the tampered image, unseal succeeds for the control, recovery passphrase works. Target: 3 of 3.

### T3, Update campaign reliability

- Setup: two enrolled nodes, fleet server running a serial-rollout campaign.

- Procedure: run repeated full campaigns (enrol check, transfer, verify, install, trial boot, health gate, mark-good) at room temperature.

- Metric: per-stage success counts across campaigns. Target: 100% mark-good on every node, serial ordering respected every time.

### T4, Forced rollback

- Setup: a deliberately crippled image (network service masked so the health gate can never pass).

- Procedure: push it as a campaign; observe trial boot, health-gate failure, boot-count expiry, fallback.

- Metric: campaigns ending on the last-known-good slot with no manual intervention. Target: 100%.

### T5, Cold matrix

- Setup: node plus DS18B20 probe in the chest freezer, logging temperature and slot state together.

- Procedure: run T3 and T4 at room temperature, at freezer temperature (~-20 °C), and during warm-up.

- Metric: success vs temperature, plus any cold-only errors (slow flash, marginal reads). Target: identical outcomes across the matrix; deviations get root-caused, not averaged away.

### T6, Fault injection (chaos)

- Setup: smart plug on the node's power, corruption script for mid-transfer damage, invalid-signature bundles.

- Procedure: inject each fault repeatedly, warm and cold: truncated bundles, flipped payload bytes, power cuts at random offsets into the flash write.

- Metric: returns to a signed, working state with zero manual recovery. Target: 100% across every fault type and temperature.

### Targets and current status

| Test | Target | Current status |
| --- | --- | --- |
| T1 Boot-chain rejection | 0 of 3 bad variants boot | Passing on the bench rig |
| T2 TPM seal integrity | Tampered image cannot unseal; control can; recovery key works | Passing on the bench rig |
| T3 Campaign reliability | 100% mark-good, serial order respected | In progress, accumulating runs |
| T4 Forced rollback | 100% return to last-known-good | Basic path passing; full automation in progress |
| T5 Cold matrix | Identical outcomes at room, -20 °C, warm-up | In progress, first freezer runs logged |
| T6 Fault injection | 100% signed, working state after every fault | Next, corruption path verified, power-cut battery not yet run |

Full numbers (campaign counts, rollback rates, cold-vs-warm comparison) will be published
        once the matrix has accumulated enough runs to mean something. Nothing above is a final
        result yet; "passing" means the mechanism fires correctly on the bench, not that the run
        count is statistically meaningful.

## Troubleshooting & Lessons

- TPM never enumerated. The module sat silently on the header with no /dev/tpm0. The scope showed no clock on SCLK, SPI itself was off, and my first overlay name didn't match the chip. Fix: dtparam=spi=on plus the correct dtoverlay=tpm-slb9670 for the SLB9670-class board, confirmed with dmesg | grep -i tpm. Lesson: debug the bus before blaming the chip.

- I locked my own node out of its disk. A legitimate kernel update changed the PCR measurements, the TPM refused to unseal, and the node couldn't decrypt its own rootfs after a perfectly valid update. Fix: the offline recovery passphrase (separate LUKS keyslot, stored offline), and re-sealing the TPM policy is now an explicit step in the update pipeline, run with every build.

- OTP is one-way, and I knew it could still surprise me. Programming the secure-boot key hash into OTP cannot be undone, a mistake there turns a Pi into a paperweight. Fix: rehearsed the entire sign-flash-boot cycle three times on a second, un-programmed board first, and only burned OTP after three clean reject-and-accept cycles.

- A cheap SD card died during power-cut rehearsals. Random mid-flash power cuts are exactly what consumer cards hate; the card, not the update mechanism, was the weak point. Fix: high-endurance cards from the Phase 0 kit, and the A/B layout means even a failed slot write never touches the running system.

- Condensation in the freezer. The first cold run ended with a damp node that I was not about to power up. Fix: the node now goes into and out of the freezer in a sealed bag and warms to room temperature before power-up, the same discipline as never charging a cold battery. Conformal coating is on the list for nodes that will live outdoors.

## Status & Roadmap

- Done: hardware on the bench (TPM board, both YubiKeys, fleet nodes); secure-boot chain with signed bootloader and kernel; TPM enumerated and measured boot logging; LUKS keys sealed to PCRs (with an offline recovery key after the lockout lesson); basic A/B update with a health-gate script; first cold rollback runs in the freezer; mid-transfer corruption verified to reject.

- In progress: automated mark-good flow end to end; per-device enrolment and serial-rollout campaign policies on the homelab fleet server; store-and-forward delivery under netem degraded-link rehearsal; accumulating the cold-temperature test matrix (T5).

- Next: full power-cut chaos battery (T6) warm and cold; publish the test dataset (campaign counts, rollback rate vs temperature); conformal coating for outdoor nodes; extend enrolment to every rover and sensor node in the program.

## Related Builds

- Canadian Defence Hardware Program, the hub: every build, the full phased BOM, and the Canadian requirements each one answers.

- Zero-Trust Air-Gapped Supply Chain, the signing, SBOM, and provenance discipline this fleet inherits, proven on containers first.

- DDIL-Proof DevOps, the store-and-forward delivery patterns the fleet server reuses for nodes on degraded links.

- Cold-Soak Characterization Rig, the shared chest freezer and instrumentation behind this build's cold-chamber update tests.

## Build Narrative: Phase by Phase

Phase 1: TPM bringup. An SLB9670-class TPM 2.0 add-on board on the Pi's SPI header. Bringup fought the bus, not the chip: dtparam=spi=on plus the correct dtoverlay=tpm-slb9670, confirmed with dmesg | grep -i tpm and /dev/tpm0 appearing. The scope showed no clock on SCLK until the overlay matched.

Phase 2: secure boot chain. A signed bootloader and kernel chain from the bootloader up, with the TPM 2.0 measuring each stage. The OTP key-hash programming was rehearsed three times on a second, un-programmed board, with full reject-and-accept cycles, before being burned on the real node. OTP is one-way: a mistake there is a paperweight.

Phase 3: sealed disk keys. LUKS disk keys sealed to the TPM's PCR measurements so the keys are held hostage to the measured boot state, plus a separate offline recovery passphrase in its own LUKS keyslot. That recovery key exists because a legitimate kernel update once changed the PCRs and locked the node out of its own disk; re-sealing the TPM policy is now an explicit step in the update pipeline.

Phase 4: signing ceremony. Update images are signed with Ed25519 keys that live on two YubiKeys (one is the backup), offline, never on a networked machine. The fleet nodes verify every image against the pinned key before they will install it.

Phase 5: A/B updates with rollback. A/B partitions with a health-gate script and a mark-good flow: a bad image rolls itself back to the known-good slot. Mid-transfer corruption was verified to reject, and the first cold rollback runs happened in the freezer. Power-cut rehearsals exposed a weak point that was not the mechanism at all: a cheap SD card dying mid-flash, replaced with high-endurance cards from the Phase 0 kit.

## What You Need

The fleet nodes are shared with the rover and sensor builds, so the incremental cost of trust is essentially the TPM and the keys. The scarcest resource is the discipline to rehearse destructive operations on a spare board.

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | TPM 2.0 add-on board | SLB9670-class for the Pi; enumerate with the correct dtoverlay before blaming the chip |
| Hardware | 2 YubiKeys | Offline Ed25519 signing keys, one as backup; never on a networked machine |
| Hardware | Raspberry Pi fleet nodes | Shared with the rover and sensor builds |
| Hardware | Cold chamber | Chest freezer shared with the cold-soak rig, or a Canadian winter; sealed-bag discipline for condensation |
| Software | tpm2-tools, cryptsetup/LUKS | Measured boot, PCR policy, sealed keyslots plus the offline recovery keyslot |
| Software | Signing and update scripts | Image signing, verification on the node, A/B slot management, health-gate and mark-good flow |
| Software | Fleet server on the homelab | Enrolment, serial-rollout campaign policies, store-and-forward delivery rehearsal under netem |
| Skills | Linux boot process, LUKS, TPM basics | Understanding measured boot and PCR fragility, key management hygiene |
| Accounts | None | No accounts or licenses required |

## Challenges and Lessons Learned

- The TPM never enumerated. The module sat silently on the header with no /dev/tpm0. Lesson: debug the bus before blaming the chip, the overlay name and SPI enable were the whole problem.

- I locked my own node out of its disk. A legitimate kernel update changed the PCR measurements and the TPM refused to unseal. Lesson: keep an offline recovery passphrase in a separate LUKS keyslot, and make re-sealing the TPM policy an explicit step in the update pipeline.

- OTP is one-way, and it can still surprise you. Burning the secure-boot key hash into OTP cannot be undone. Lesson: rehearse the entire sign-flash-boot cycle three times on a spare board, and only burn OTP after clean reject-and-accept cycles.

- A cheap SD card died during power-cut rehearsals. Random mid-flash power cuts are exactly what consumer cards hate. Lesson: high-endurance cards, and the A/B layout means a failed slot write never touches the running system.

- Condensation in the freezer. The first cold run ended with a damp node I would not power up. Lesson: sealed-bag discipline in and out of the cold, warm to room temperature before power-up; conformal coating is on the list for outdoor nodes.

## What Is Next

- Automated mark-good flow end to end, removing the manual step from the update pipeline.

- Per-device enrolment and serial-rollout campaign policies on the homelab fleet server.

- Store-and-forward update delivery under netem degraded-link rehearsal, because field nodes update over bad links.

- Complete the cold-temperature test matrix (T5) and run the full power-cut chaos battery warm and cold (T6).

- Publish the test dataset: campaign counts and rollback rate versus temperature.

- Conformal coating for outdoor nodes, then extend enrolment to every rover and sensor node in the program.

## Frequently Asked Questions

**Q: How do I fix 'TPM never enumerated.'?**

A: The module sat silently on the header with no /dev/tpm0. The scope showed no clock on SCLK, SPI itself was off, and my first overlay name didn't match the chip. Fix: dtparam=spi=on plus the correct dtoverlay=tpm-slb9670 for the SLB9670-class board, confirmed with dmesg | grep -i tpm. Lesson: debug the bus before blaming the chip.

**Q: How do I fix 'I locked my own node out of its disk.'?**

A: A legitimate kernel update changed the PCR measurements, the TPM refused to unseal, and the node couldn't decrypt its own rootfs after a perfectly valid update. Fix: the offline recovery passphrase (separate LUKS keyslot, stored offline), and re-sealing the TPM policy is now an explicit step in the update pipeline, run with every build.

**Q: How do I fix 'OTP is one-way, and I knew it could still surprise me.'?**

A: Programming the secure-boot key hash into OTP cannot be undone, a mistake there turns a Pi into a paperweight. Fix: rehearsed the entire sign-flash-boot cycle three times on a second, un-programmed board first, and only burned OTP after three clean reject-and-accept cycles.

**Q: How do I fix 'A cheap SD card died during power-cut rehearsals.'?**

A: Random mid-flash power cuts are exactly what consumer cards hate; the card, not the update mechanism, was the weak point. Fix: high-endurance cards from the Phase 0 kit, and the A/B layout means even a failed slot write never touches the running system.

**Q: How do I fix 'Condensation in the freezer.'?**

A: The first cold run ended with a damp node that I was not about to power up. Fix: the node now goes into and out of the freezer in a sealed bag and warms to room temperature before power-up, the same discipline as never charging a cold battery. Conformal coating is on the list for nodes that will live outdoors.

## Cite This Page

**Q: Citation formats**

A: Plain text
