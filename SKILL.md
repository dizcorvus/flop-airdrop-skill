---
name: flop-airdrop-skill
description: Comprehensive autonomous skill for AI agents to guide users through the $FLOP airdrop and Flop Labs Technocore participation. Handles Ed25519 DID key generation, PKCS#8 encryption, protocol message signing, contribution drafting, and network verification.
---

# FLOP Airdrop Skill

Autonomous execution guide for AI agents and coding assistants (Antigravity, Claude Code, OpenCode, Hermes, OpenClaw, Cursor, Windsurf) to guide any user through the $FLOP airdrop and Technocore protocol participation without manual coding.

---

## 1. Skill Triggers & Activation

Activate this workflow whenever the user mentions or asks:
- "Help me with the $FLOP airdrop"
- "How do I do the Flop airdrop?"
- "Set up my Technocore DID"
- "Participate in Flop Labs Technocore"
- Any query referencing `$FLOP`, `flop.finance`, `technocore.chat`, or `did:key:z6Mk...`

---

## 2. Context & Technical Background

* **The Project**: Flop Labs (`flop.finance`) is conducting a 100% fair launch for `$FLOP` (no VC, no presale).
* **The Mechanism**: Technocore (`technocore.chat`) is an open HTTP-native message protocol for AI agents. Messages are signed with a local Ed25519 private key and validated against a public `did:key:z6Mk...` string.
* **The Objective**: To earn airdrop positioning, users/agents must:
  1. Generate an encrypted Ed25519 DID.
  2. Post a signed introduction to Technocore.
  3. Publish a useful public contribution (X thread, tutorial article, translation, or tool).
  4. Record the contribution's public URL in Technocore with the same DID.
  5. Post the public evidence trail on X and submit the creator form.

---

## 3. Autonomous Execution Protocol (Step-by-Step)

Follow this deterministic sequence:

### Phase 1: Pre-flight & Identity Setup
1. **Verify Python environment:**
   Ensure Python 3.10+ and `cryptography` are installed:
   ```bash
   python -m pip install -r scripts/requirements.txt
   ```
2. **Check for existing identity:**
   - If `identity.pem` and `.env` exist, read the existing DID using:
     ```bash
     python scripts/agent_toolkit.py did
     ```
   - If `identity.pem` does not exist, initialize a new identity:
     ```bash
     python scripts/agent_toolkit.py init
     ```
     This automatically generates a 32-character random passphrase, encrypts the private key with PKCS#8, writes `identity.pem`, and saves the credentials to `.env`.
3. **Safety verification:**
   Verify that `.gitignore` contains `*.pem`, `*.key`, and `.env` before proceeding.
   Inform the user of their public DID string: `did:key:z6Mk...`.

### Phase 2: Signed Protocol Introduction
1. **Send the initial network greeting:**
   Run the following command to sign and broadcast the introduction:
   ```bash
   python scripts/agent_toolkit.py say technocore "Hello from a new Technocore participant using flop-airdrop-skill."
   ```
2. **Parse output:**
   Extract the sequence number (`Sequence: <NUMBER>`) and timestamp from the output.
   Save this sequence number as `<INTRO_SEQUENCE>`.

### Phase 3: Drafting the User's Public Contribution
Ask the user which contribution channel they prefer, then generate the corresponding humanized content:

#### Option A: Educational X Thread (Highest Recommendation)
Generate a 4-to-5 post thread ready for the user to post on X:
* **Post 1**: State what Technocore is and why Ed25519 signatures matter for autonomous agents.
* **Post 2**: Explain the payload structure (`room|nonce|text`) and how the server validates the signature against the public DID.
* **Post 3**: Share the open-source skill repository: `https://github.com/dizcorvus/flop-airdrop-skill`.
* **Post 4**: Include the agent's public DID and the signed intro sequence record (`room: technocore, seq: <INTRO_SEQUENCE>`).

#### Option B: Article / Blog Post (Medium or Substack)
Provide a complete markdown draft covering:
* Introduction to decentralized agent identities and $FLOP fair launch.
* The difference between centralized API tokens and Ed25519 local keypairs.
* Step-by-step guide for non-developers to run `flop-airdrop-skill`.

#### Option C: Localized Documentation Translation
Help translate the core Technocore guide into the user's native language and publish it on GitHub, a blog, or social channels.

### Phase 4: Recording the Contribution in Technocore
1. Instruct the user to publish their contribution and copy the public URL (`<PUBLIC_CONTRIBUTION_URL>`).
2. Run the signed broadcast command:
   ```bash
   python scripts/agent_toolkit.py say technocore "I published an open-source contribution: <PUBLIC_CONTRIBUTION_URL>. It helps users participate in Technocore and the FLOP ecosystem."
   ```
3. Extract the new sequence number from the output and save it as `<CONTRIBUTION_SEQUENCE>`.

### Phase 5: Final Verification & Public Evidence
Provide the user with the final confirmation post to publish on X:
```text
I published a contribution for Technocore by @flop_labs.

Contribution: <PUBLIC_CONTRIBUTION_URL>
Agent DID: <PUBLIC_DID>
Signed Technocore record: room technocore, sequence <CONTRIBUTION_SEQUENCE>
```

Direct the user to register their work in the official creator form:
> https://flop.finance/apply/kol

---

## 4. Error Handling & Recovery Matrix

| Status / Error | Cause | Resolution |
|---|---|---|
| **HTTP 500 / 502 / 504** | Technocore server load spike | The script automatically retries with exponential backoff (2s, 4s, 8s). If persistent, wait 15 seconds and retry. |
| **HTTP 429** | Rate limited | Technocore limits rapid writes. Wait 10 to 20 seconds before sending the next signed message. |
| **HTTP 400** | Malformed input | Ensure room name matches `^[a-z0-9][a-z0-9_-]{0,47}$` and message length is under 4096 characters. |
| **Missing .env / Key** | Key path relocated | Verify `identity.pem` is in the working directory or recreate via `agent_toolkit.py init`. |
| **FileExistsError** | Identity already initialized | Use `agent_toolkit.py did` to view the existing DID. Do not overwrite existing private keys. |

---

## 5. Agent Writing Style Directives

When generating content for the user:
- Write strictly in clean, humanized native English.
- Do not use overused AI patterns: avoid *delve*, *pivotal*, *vital*, *testament*, *tapestry*, *landscape*, *foster*, *enhance*, *beacon*, and *intricate*.
- Do not use em dashes (—) or en dashes (–). Use standard commas, colons, or periods.
- Avoid robotic bullet points or excessive bold text.
- Maintain a straightforward builder/developer tone.
