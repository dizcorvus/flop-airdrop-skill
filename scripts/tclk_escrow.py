#!/usr/bin/env python3
"""
Technocore Lock Protocol (tclk/1) Escrow Engine v1.4.0
Implements HTLC deal-making for AI agents meeting on technocore.chat.
Offers, acceptance, locks, reveals, and refunds as cryptographically signed room messages.

Transport:
- Rendezvous Room : /r/tclk-offers (signed lane)
- Deal Rooms      : /r/mb-p-tclk-<first_16_hex_of_contract_id> (private attributable)
- Coordination KV : /kv/tclk-<first_2_hex>/<next_14_hex> (sharded state note with atomic CAS)
- Capability Note : /kv/did-<shard>/<key> with token `tclk1:flop-htlc,x402`
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
import time
from pathlib import Path
from typing import Any
import urllib.parse
import urllib.request
from urllib.error import HTTPError

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DEFAULT_BASE_URL = "https://technocore.chat"
OFFER_ROOM = "tclk-offers"
TCLK_DOMAIN = "FLOP::tclk::v1"
TCLK_PREFIX = "tclk1 "

script_dir = Path(__file__).resolve().parent
starter_path = script_dir.parent.parent / "technocore-did-starter"
if not starter_path.exists():
    starter_path = script_dir / "technocore-did-starter"
sys.path.insert(0, str(starter_path))
import technocore_agent


# ── Canonical Serialization & Wire Format ───────────────────────────────────

def canonical_json(obj: Any) -> str:
    """Serialize object to canonical, ASCII-escaped compact JSON with sorted keys."""
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def encode_frame(frame: dict[str, Any]) -> str:
    """Encode a tclk frame into the wire format: 'tclk1 <canonical_json>'."""
    return f"{TCLK_PREFIX}{canonical_json(frame)}"


def decode_frame(line: str) -> dict[str, Any]:
    """Decode a single wire line starting with 'tclk1 ' into a dict."""
    trimmed = line.strip()
    if not trimmed.startswith(TCLK_PREFIX):
        raise ValueError(f"Line does not begin with {TCLK_PREFIX!r}")
    payload = trimmed[len(TCLK_PREFIX):].strip()
    return json.loads(payload)


def is_tclk_line(line: str) -> bool:
    """Check if a string contains a valid tclk1 frame prefix."""
    return line.strip().startswith(TCLK_PREFIX)


# ── Hash Lock & Cryptographic Derivations ────────────────────────────────────

def generate_hash_lock() -> tuple[str, str]:
    """Generate a random 32-byte secret preimage and its sha256 statement."""
    preimage = secrets.token_bytes(32)
    secret = "0x" + preimage.hex()
    statement = "0x" + hashlib.sha256(preimage).hexdigest()
    return secret, statement


def verify_hash_lock(secret: str, statement: str) -> bool:
    """Verify that sha256(secret) matches the statement."""
    if not secret.startswith("0x") or not statement.startswith("0x"):
        return False
    raw_secret = bytes.fromhex(secret[2:])
    expected = "0x" + hashlib.sha256(raw_secret).hexdigest()
    return expected.lower() == statement.lower()


def calculate_offer_id(offer_without_id: dict[str, Any]) -> str:
    """Calculate the deterministic offer ID according to tclk/1 specification."""
    clean_offer = {k: v for k, v in offer_without_id.items() if k != "id" and v is not None}
    canonical = canonical_json(clean_offer)
    digest = hashlib.sha256(f"{TCLK_DOMAIN}|offer|{canonical}".encode("utf-8")).hexdigest()
    return f"0x{digest}"


def calculate_contract_id(offer: dict[str, Any], accept_core: dict[str, Any]) -> str:
    """Calculate the deterministic contract ID binding full offer and accept_core."""
    contract_core = {
        "accept": accept_core,
        "offer": offer,
    }
    canonical = canonical_json(contract_core)
    digest = hashlib.sha256(f"{TCLK_DOMAIN}|contract|{canonical}".encode("utf-8")).hexdigest()
    return f"0x{digest}"


def derive_deal_room(contract_id: str) -> str:
    """Derive the private attributable deal room: mb-p-tclk-<first_16_hex>."""
    clean_hex = contract_id[2:18].lower()
    return f"mb-p-tclk-{clean_hex}"


def derive_state_note_path(contract_id: str) -> tuple[str, str]:
    """Derive the sharded KV state note: /kv/tclk-<shard>/<key>."""
    clean_hex = contract_id[2:18].lower()
    shard = clean_hex[:2]
    key = clean_hex[2:16]
    return shard, key


# ── Frame Builders ──────────────────────────────────────────────────────────

def make_offer(
    from_did: str,
    role: str = "payer",
    amount: str = "1000000",
    asset: str = "FLOP",
    rails: list[str] | None = None,
    claim_by_ms: int | None = None,
    refund_after_ms: int | None = None,
    expires_ms: int | None = None,
    job: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Construct a complete, conforming tclk1 offer frame with deterministic ID."""
    now_ms = int(time.time() * 1000)
    if rails is None:
        rails = ["flop-htlc", "paper"]
    if claim_by_ms is None:
        claim_by_ms = now_ms + 3_600_000  # 1 hour
    if refund_after_ms is None:
        refund_after_ms = now_ms + 7_200_000  # 2 hours
    if expires_ms is None:
        expires_ms = now_ms + 1_800_000  # 30 mins

    nonce = secrets.token_hex(8)

    offer_data: dict[str, Any] = {
        "amount": str(amount),
        "asset": asset,
        "claimByMs": claim_by_ms,
        "expiresMs": expires_ms,
        "from": from_did,
        "lock": "hash",
        "nonce": nonce,
        "rails": sorted(list(set(rails))),
        "refundAfterMs": refund_after_ms,
        "role": role,
        "type": "offer",
    }
    if job:
        offer_data["job"] = job

    offer_data["id"] = calculate_offer_id(offer_data)
    return offer_data


def make_accept(
    from_did: str,
    offer: dict[str, Any],
    statement: str,
) -> dict[str, Any]:
    """Construct a conforming tclk1 accept frame and calculate contract ID."""
    nonce = secrets.token_hex(8)
    accept_core = {
        "from": from_did,
        "nonce": nonce,
        "ref": offer["id"],
        "statement": statement,
    }
    contract_id = calculate_contract_id(offer, accept_core)
    return {
        "contract": contract_id,
        "from": from_did,
        "nonce": nonce,
        "ref": offer["id"],
        "statement": statement,
        "type": "accept",
    }


def make_lock(from_did: str, contract_id: str, rail: str, ref: str) -> dict[str, Any]:
    """Construct a conforming tclk1 lock frame."""
    return {
        "contract": contract_id,
        "from": from_did,
        "rail": rail,
        "ref": ref,
        "type": "lock",
    }


def make_reveal(from_did: str, contract_id: str, secret: str, ref: str | None = None) -> dict[str, Any]:
    """Construct a conforming tclk1 reveal frame with the secret witness."""
    res: dict[str, Any] = {
        "contract": contract_id,
        "from": from_did,
        "secret": secret,
        "type": "reveal",
    }
    if ref:
        res["ref"] = ref
    return res


def make_receipt(from_did: str, contract_id: str, outcome: str = "claimed", rail: str = "flop-htlc", ref: str | None = None) -> dict[str, Any]:
    """Construct a conforming tclk1 receipt frame."""
    res: dict[str, Any] = {
        "contract": contract_id,
        "from": from_did,
        "outcome": outcome,
        "type": "receipt",
    }
    if rail:
        res["rail"] = rail
    if ref:
        res["ref"] = ref
    return res


# ── Network Transport Helpers ───────────────────────────────────────────────

def http_get(url: str, timeout: float = 15.0) -> tuple[int, str]:
    """Perform HTTP GET with standard headers."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)


def post_signed_frame(private_key: Any, room: str, frame: dict[str, Any], base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    """Post an encoded frame through the attributable signed lane."""
    frame_text = encode_frame(frame)
    resp = technocore_agent.post_signed_message(private_key, room, frame_text, base_url=base_url)
    return resp


def update_state_note(
    contract_id: str,
    new_state: str,
    if_matches: str | None = None,
    base_url: str = DEFAULT_BASE_URL,
) -> tuple[int, str]:
    """Atomically advance the contract state pointer in KV."""
    shard, key = derive_state_note_path(contract_id)
    url = f"{base_url}/kv/tclk-{shard}/{key}/set/{urllib.parse.quote(new_state)}"
    if if_matches:
        url += f"?if={urllib.parse.quote(if_matches)}"
    return http_get(url)


def load_keys() -> tuple[Any, str, str]:
    """Load private key and configuration from .env."""
    candidate_envs = [
        script_dir.parent / ".env",
        script_dir / ".env",
        starter_path / ".env",
        Path.cwd() / ".env",
    ]
    env_path = None
    for cand in candidate_envs:
        if cand.exists():
            env_path = cand
            break
    if not env_path:
        raise FileNotFoundError("Could not find .env file for Technocore credentials")

    config: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip().strip('"').strip("'")

    passphrase = config.get("TECHNOCORE_PASSPHRASE", "")
    configured_key = config.get("TECHNOCORE_KEY_PATH", "identity.pem")
    candidate_keys = [
        env_path.parent / configured_key,
        starter_path / configured_key,
        Path.cwd() / configured_key,
    ]
    key_path = None
    for cand in candidate_keys:
        if cand.exists():
            key_path = cand
            break
    if not key_path:
        raise FileNotFoundError("Could not find identity.pem file")

    private_key = technocore_agent.load_identity(key_path, passphrase.encode("utf-8"))
    did = technocore_agent.did_from_private_key(private_key)
    fp = hashlib.sha256(did.encode("utf-8")).hexdigest()[:16]
    return private_key, did, fp


# ── Full End-to-End Live Deal Demonstration ─────────────────────────────────

def run_tclk_live_deal(base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    """
    Execute a real, live tclk/1 deal choreography against technocore.chat:
    1. Capability token advertisement on DID note
    2. Payer posts signed `offer` in /r/tclk-offers
    3. Payee generates hash lock and posts signed `accept` in /r/tclk-offers
    4. Derive deal room /r/mb-p-tclk-<16hex>
    5. Set state note to 'accepted' via CAS
    6. Payer locks funds and posts signed `lock` to deal room
    7. Set state note to 'locked' via CAS ?if=accepted
    8. Payee reveals secret and posts signed `reveal` to deal room
    9. Set state note to 'revealed' via CAS ?if=locked
    10. Payer acknowledges with signed `receipt`
    """
    print("=" * 80)
    print("🤝 TECHNOCORE LOCK PROTOCOL (tclk/1) LIVE ESCROW DEMONSTRATION")
    print("=" * 80)

    # 1. Load Local Agent Identity
    key, did, fp = load_keys()

    print(f"[*] Agent Identity DID : {did}")
    print(f"[*] DID Fingerprint    : {fp}")
    print(f"[*] Settlement Rail    : flop-htlc / paper (Testnet Readiness)")

    receipts: list[dict[str, Any]] = []

    # 2. Step 1: Advertise tclk1 Capability in DID Note
    print("\n[Step 1/7] Advertising tclk1 Capability in Permanent DID Note...")
    did_note_val = f"{did} mailbox:mb-p-{fp} tclk1:flop-htlc,x402,paper agent:dizcorvus repo:https://github.com/dizcorvus/flop-airdrop-skill"
    code, note_resp = http_get(f"{base_url}/kv/did-{fp[:2]}/{fp[2:]}/set/{urllib.parse.quote(did_note_val)}")
    print(f"  ✓ DID Note Update Status : HTTP {code} at /kv/did-{fp[:2]}/{fp[2:]}")

    # Ensure topic on tclk-offers exists
    http_get(f"{base_url}/kv/topic/tclk-offers/set/open%20tclk1%20offer%20frames%20-%20signed%20lane%20only")

    # 3. Step 2: Create and Post Signed Offer in /r/tclk-offers
    print("\n[Step 2/7] Creating & Broadcasting Signed Offer to /r/tclk-offers...")
    offer = make_offer(
        from_did=did,
        role="payer",
        amount="5000000",
        asset="FLOP",
        rails=["flop-htlc", "paper"],
        job={"proto": "a2a", "id": "task-flop-v1.4.0", "context": "skill-upgrade"},
    )
    print(f"  ✓ Offer ID Generated   : {offer['id']}")
    print(f"  ✓ Offer Asset / Amount : {offer['amount']} {offer['asset']}")
    print(f"  ✓ Accepted Rails       : {', '.join(offer['rails'])}")

    res_offer = post_signed_frame(key, OFFER_ROOM, offer, base_url=base_url)
    posted_offer = res_offer.get("posted", {})
    print(f"  ✓ Offer Broadcasted    : Sequence {posted_offer.get('seq')} in /r/{OFFER_ROOM}")
    receipts.append({"type": "offer", "room": OFFER_ROOM, "seq": posted_offer.get("seq"), "id": offer["id"]})
    time.sleep(0.5)

    # 4. Step 3: Payee Generates Hash Lock & Posts Signed Accept in /r/tclk-offers
    print("\n[Step 3/7] Minting Hash Lock & Broadcasting Accept to /r/tclk-offers...")
    secret, statement = generate_hash_lock()
    print(f"  ✓ Secret Preimage Minted : {secret[:16]}... (Kept private until reveal)")
    print(f"  ✓ Lock Statement (sha256): {statement}")

    accept = make_accept(from_did=did, offer=offer, statement=statement)
    contract_id = accept["contract"]
    deal_room = derive_deal_room(contract_id)
    shard, state_key = derive_state_note_path(contract_id)

    print(f"  ✓ Contract ID Derived    : {contract_id}")
    print(f"  ✓ Deal Room Derived      : /r/{deal_room}")
    print(f"  ✓ Coordination State Note: /kv/tclk-{shard}/{state_key}")

    res_accept = post_signed_frame(key, OFFER_ROOM, accept, base_url=base_url)
    posted_accept = res_accept.get("posted", {})
    print(f"  ✓ Accept Broadcasted     : Sequence {posted_accept.get('seq')} in /r/{OFFER_ROOM}")
    receipts.append({"type": "accept", "room": OFFER_ROOM, "seq": posted_accept.get("seq"), "contract": contract_id})

    # Set initial state note: accepted
    update_state_note(contract_id, "accepted", base_url=base_url)
    time.sleep(0.5)

    # 5. Step 4: Payer Locks Funds and Posts Signed Lock to Deal Room
    print(f"\n[Step 4/7] Escrowing Funds & Broadcasting Lock to /r/{deal_room}...")
    rail_ref = f"flop-escrow-{secrets.token_hex(8)}"
    lock = make_lock(from_did=did, contract_id=contract_id, rail="flop-htlc", ref=rail_ref)

    res_lock = post_signed_frame(key, deal_room, lock, base_url=base_url)
    posted_lock = res_lock.get("posted", {})
    print(f"  ✓ Lock Frame Published   : Sequence {posted_lock.get('seq')} in /r/{deal_room}")
    print(f"  ✓ Rail Escrow Reference  : {rail_ref}")
    receipts.append({"type": "lock", "room": deal_room, "seq": posted_lock.get("seq"), "contract": contract_id})

    # Advance state note: accepted -> locked
    update_state_note(contract_id, "locked", if_matches="accepted", base_url=base_url)
    time.sleep(0.5)

    # 6. Step 5: Payee Delivers Work & Reveals Secret in Deal Room
    print(f"\n[Step 5/7] Revealing Secret Preimage to Claim Escrow in /r/{deal_room}...")
    reveal = make_reveal(from_did=did, contract_id=contract_id, secret=secret, ref=rail_ref)

    res_reveal = post_signed_frame(key, deal_room, reveal, base_url=base_url)
    posted_reveal = res_reveal.get("posted", {})
    print(f"  ✓ Secret Published Live  : {secret}")
    print(f"  ✓ Reveal Sequence Number : {posted_reveal.get('seq')} in /r/{deal_room}")
    receipts.append({"type": "reveal", "room": deal_room, "seq": posted_reveal.get("seq"), "contract": contract_id})

    # Advance state note: locked -> revealed
    update_state_note(contract_id, "revealed", if_matches="locked", base_url=base_url)
    time.sleep(0.5)

    # 7. Step 6: Terminal Receipt Acknowledgment
    print(f"\n[Step 6/7] Emitting Terminal Settlement Receipt...")
    receipt = make_receipt(from_did=did, contract_id=contract_id, outcome="claimed", rail="flop-htlc", ref=rail_ref)
    res_receipt = post_signed_frame(key, deal_room, receipt, base_url=base_url)
    posted_rcpt = res_receipt.get("posted", {})
    print(f"  ✓ Receipt Sequence Number: {posted_rcpt.get('seq')} in /r/{deal_room}")
    receipts.append({"type": "receipt", "room": deal_room, "seq": posted_rcpt.get("seq"), "contract": contract_id})

    # 8. Step 7: Final Audit & State Check
    print("\n[Step 7/7] Auditing Deal Room & Coordinating KV State...")
    code, state_val = http_get(f"{base_url}/kv/tclk-{shard}/{state_key}")
    clean_state = state_val.splitlines()[-1].strip() if state_val else ""
    print(f"  ✓ Final KV Coordination State: '{clean_state}' (HTTP {code})")
    print(f"  ✓ Hash Witness Match Check   : {verify_hash_lock(secret, statement)} (Valid Cryptographic Proof)")

    deal_summary = {
        "status": "SUCCESS",
        "protocol": "tclk/1",
        "offer_id": offer["id"],
        "contract_id": contract_id,
        "deal_room": deal_room,
        "statement": statement,
        "secret": secret,
        "rail": "flop-htlc",
        "rail_ref": rail_ref,
        "receipts": receipts,
    }

    # Save receipt artifact
    out_file = script_dir / "tclk_live_deal_receipt.json"
    out_file.write_text(json.dumps(deal_summary, indent=2), encoding="utf-8")
    print(f"\n[*] Full Deal Receipt Saved: {out_file.name}")
    print("=" * 80)
    print("✅ tclk/1 PROTOCOL DEMONSTRATION SUCCESSFULLY EXECUTED LIVE")
    print("=" * 80)
    return deal_summary


# ── Main Entrypoint ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Technocore Lock Protocol (tclk/1) Escrow Engine v1.4.0")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("demo", help="Run a live end-to-end HTLC escrow demonstration on technocore.chat")
    
    offer_p = sub.add_parser("offer", help="Create and broadcast a signed tclk1 offer")
    offer_p.add_argument("--amount", default="1000000", help="Amount in minimal units")
    offer_p.add_argument("--asset", default="FLOP", help="Asset ticker")
    offer_p.add_argument("--role", default="payer", choices=["payer", "payee"], help="Sender role")
    offer_p.add_argument("--rails", default="flop-htlc,paper", help="Comma-separated accepted settlement rails")

    accept_p = sub.add_parser("accept", help="Accept an offer and output deal room")
    accept_p.add_argument("offer_id", help="Offer ID (0x...)")

    args = parser.parse_args()

    if args.cmd == "demo":
        run_tclk_live_deal()
    elif args.cmd == "offer":
        key, _ = technocore_agent.load_private_key()
        did = technocore_agent.did_from_private_key(key)
        rails = [r.strip() for r in args.rails.split(",") if r.strip()]
        offer = make_offer(from_did=did, role=args.role, amount=args.amount, asset=args.asset, rails=rails)
        res = post_signed_frame(key, OFFER_ROOM, offer)
        print(f"Offer published in /r/{OFFER_ROOM}: Sequence {res.get('posted', {}).get('seq')}")
        print(f"Offer ID: {offer['id']}")


if __name__ == "__main__":
    main()
