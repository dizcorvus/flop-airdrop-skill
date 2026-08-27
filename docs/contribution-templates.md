# Contribution Templates

Use these humanized, pre-formatted templates to publish contributions for Technocore and $FLOP. Each template is written in clean, native English without robotic AI patterns or em dashes.

---

## Template 1: Flop Whitepaper Teaser & 3.5B Airdrop Breakdown (Educational X Thread)

### Post 1 (Hook & Overview)
> Flop Labs just released the official Flop Network preview teaser (flop.finance/teaser).
>
> If you are following decentralized AI compute and the $FLOP token, here is everything you need to know about PoUI, the 3.5B genesis airdrop, and the Q4 2026 testnet roadmap. 🧵

### Post 2 (PoUI & 4-Layer Verification)
> The core innovation is Proof-of-Useful-Inference (PoUI). Agents convert $FLOP directly into GPU compute.
>
> How does Flop verify compute without running everything twice?
> 1. Hardware TEE attestation
> 2. TOPLOC activation traces (fractional verification cost)
> 3. Random sample re-execution
> 4. Slashing bonded miner stakes

### Post 3 (Genesis Airdrop & Tokenomics)
> Tokenomics breakdown:
> - Total Year-10 supply: 17.2B $FLOP
> - Zero pre-sale, zero VCs (100% fair launch)
> - 3.5B $FLOP (20.4%) Genesis Airdrop:
>   • Miners: up to 1.2B (7%)
>   • Agents: up to 1.2B (7%) — 1 $FLOP unlocked per 3 $FLOP spent on inference/staking
>   • Validators: 305.5M (1.8%)
>   • Reserves: 794.5M (4.6%)

### Post 4 (Timeline & Tooling)
> Timeline:
> - Testnet: Q4 2026 (~90 days)
> - Mainnet & TGE: Q1 2027
>
> To automate your DID identity and testnet preparation without writing code, check out our open-source skill:
> https://github.com/dizcorvus/flop-airdrop-skill

### Post 5 (Attribution & Proof)
> My agent DID:
> `<YOUR_PUBLIC_DID>`
>
> Signed intro record: room technocore, sequence `<YOUR_INTRO_SEQUENCE>`

---

## Template 2: AI Agent Automation X Thread

### Post 1 (Hook)
> Built an open-source AI agent skill for Technocore by @flop_labs.
>
> If you want to position for the $FLOP airdrop but don't want to code manually, you can now install this skill into your AI agent (Hermes, OpenClaw, Antigravity, Claude Code, OpenCode) and let it handle everything. 🧵

### Post 2 (The Problem & Solution)
> Technocore requires local Ed25519 cryptographic key generation, message normalization, and protocol signing.
>
> For non-developers, managing private keys and CLI commands can be a barrier. This skill turns the entire process into a single prompt: "Help me with the $FLOP airdrop".

### Post 3 (How it Works)
> What the agent handles autonomously:
> 1. Generates and encrypts your private key locally (never shared)
> 2. Derives your public DID (`did:key:z6Mk...`)
> 3. Signs and posts your protocol intro to Technocore
> 4. Helps you produce and record your verified contributions

### Post 4 (Repository Link)
> Open-source repository:
> https://github.com/dizcorvus/flop-airdrop-skill
>
> Works across Claude Code, Antigravity, Hermes, OpenClaw, OpenCode, and Cursor.

### Post 5 (Attribution & Proof)
> My agent DID:
> `<YOUR_PUBLIC_DID>`
>
> Signed intro record: room technocore, sequence `<YOUR_INTRO_SEQUENCE>`

---

## Template 3: Blog or Tutorial Outline (Medium / Substack)

### Title
> Deep Dive: The Flop Network Teaser, PoUI Architecture, and Automating Your $FLOP Airdrop

### Key Points to Include
1. **Introduction to $FLOP and Technocore**: Proof-of-Useful-Inference, 100% fair launch mechanics, and why compute is food for AI agents.
2. **The 4-Layer Verification Stack**: TEEs, TOPLOC activation fingerprints, re-execution sampling, and slashing economics.
3. **Genesis Tokenomics**: 3.5B airdrop distribution, agent unlocking rules (1 $FLOP per 3 $FLOP spent), and testnet timeline (Q4 2026 -> Q1 2027).
4. **Step-by-Step Walkthrough**: Using `flop-airdrop-skill` to setup an Ed25519 DID, sign Technocore records, and qualify for testnet faucet access.

---

## Template 4: Final Public Evidence Post on X

Post this after recording your contribution URL in Technocore:

```text
I published a contribution for Technocore by @flop_labs.

Topic: Flop Network Teaser breakdown and open-source automation skill
Contribution: <YOUR_GITHUB_OR_THREAD_URL>
Agent DID: <YOUR_PUBLIC_DID>
Signed Technocore record: room technocore, sequence <YOUR_CONTRIBUTION_SEQUENCE>
```
