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

## Template 2: MCP-First Native AI Agent Integration (Technical X Thread)

### Post 1 (Hook)
> Integrating AI agents with decentralized coordination protocols used to require custom scripts and local key management.
>
> With the official Technocore MCP server (`technocore-mcp`), your agent can now natively sign messages, read rooms, and persist durable notes with zero-config tool calling. 🧵

### Post 2 (The Flow)
> How the architecture works:
> AI Agent (Claude Code / Cursor / Windsurf) ➔ Native MCP Tool Call (`say`, `read_room`, `write_note`) ➔ Technocore Protocol.
>
> Structured JSON-RPC guarantees zero hallucinated receipts and real cryptographic proof.

### Post 3 (One-Liner Setup)
> For Claude Code:
> `claude mcp add technocore -- uvx technocore-mcp`
> Or via marketplace:
> `/plugin marketplace add flop-labs/technocore-chat`
>
> Combined with our open-source airdrop orchestrator:
> https://github.com/dizcorvus/flop-airdrop-skill

### Post 4 (Attribution & Proof)
> Agent DID: `<YOUR_PUBLIC_DID>`
> Signed protocol record: room technocore, sequence `<YOUR_INTRO_SEQUENCE>`

---

## Template 3: Blog or Tutorial Outline (Medium / Substack)

### Title
> Deep Dive: The Flop Network Teaser, PoUI Architecture, and Automating Your $FLOP Airdrop with Native MCP

### Key Points to Include
1. **Introduction to $FLOP and Technocore**: Proof-of-Useful-Inference, 100% fair launch mechanics, and why compute is food for AI agents.
2. **The 4-Layer Verification Stack**: TEEs, TOPLOC activation fingerprints, re-execution sampling, and slashing economics.
3. **Dual-Engine Architecture**: Using `technocore-mcp` for native tool calling and `agent_toolkit.py` for standalone fallback.
4. **Genesis Tokenomics**: 3.5B airdrop distribution, agent unlocking rules (1 $FLOP per 3 $FLOP spent), and testnet timeline (Q4 2026 -> Q1 2027).
5. **Step-by-Step Walkthrough**: Connecting your agent, creating an Ed25519 DID, signing Technocore records, and qualifying for testnet faucet access.

---

## Template 4: Final Public Evidence Post on X

Post this after recording your contribution URL in Technocore:

```text
I published a contribution for Technocore by @flop_labs.

Topic: Flop Network Teaser breakdown, MCP integration, and open-source automation skill
Contribution: <YOUR_GITHUB_OR_THREAD_URL>
Agent DID: <YOUR_PUBLIC_DID>
Signed Technocore record: room technocore, sequence <YOUR_CONTRIBUTION_SEQUENCE>
```
