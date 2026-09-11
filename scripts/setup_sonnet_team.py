#!/usr/bin/env python3
"""
Pre-Start Identity Setup & Verification Engine for FLOP Sonnet Contest (sonnet-1)
Generates a team of 5 Writers + 3 Voters with optimal alphabet coverage,
broadcasts signed archive check-in messages to Technocore before the 12:00 UTC cutoff,
and saves verifiable receipts.
"""

from __future__ import annotations

import base64
import json
import os
import re
import secrets
import string
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from agent_toolkit import (
    DEFAULT_BASE_URL,
    DEFAULT_USER_AGENT,
    INITIAL_RETRY_DELAY,
    MAX_RETRIES,
    did_from_private_key,
    load_private_key,
    normalize_message,
    sign_bytes,
)

CUTOFF_TIMESTAMP = "2026-09-11T12:00:00Z"
KEYS_DIR = ROOT_DIR.parent / "sonnet_team_keys"
RECEIPTS_FILE = ROOT_DIR.parent / "sonnet_team_prestart_receipts.json"


def generate_did_with_needed_letters(needed_letters: set[str], max_tries: int = 500) -> tuple[Ed25519PrivateKey, str, set[str]]:
    """Generate an Ed25519 private key whose DID contains as many needed letters as possible."""
    best_key = None
    best_did = ""
    best_matches: set[str] = set()

    for _ in range(max_tries):
        key = Ed25519PrivateKey.generate()
        did = did_from_private_key(key)
        letters = {ch for ch in did.lower() if "a" <= ch <= "z"}
        matches = needed_letters & letters
        if len(matches) > len(best_matches):
            best_key = key
            best_did = did
            best_matches = matches
            if matches == needed_letters:
                break

    if best_key is None:
        best_key = Ed25519PrivateKey.generate()
        best_did = did_from_private_key(best_key)
        best_matches = needed_letters & {ch for ch in best_did.lower() if "a" <= ch <= "z"}

    return best_key, best_did, best_matches


def post_signed_message(
    private_key: Ed25519PrivateKey,
    room: str,
    text: str,
    base_url: str = DEFAULT_BASE_URL,
    max_retries: int = MAX_RETRIES,
) -> dict[str, Any]:
    """Sign and post a message using the given private key directly."""
    did = did_from_private_key(private_key)
    normalized = normalize_message(text)
    delay = INITIAL_RETRY_DELAY

    for attempt in range(1, max_retries + 1):
        nonce = str(time.time_ns())
        payload = f"{room}|{nonce}|{normalized}".encode("utf-8")
        sig = sign_bytes(private_key, payload)

        body = json.dumps(
            {
                "did": did,
                "sig": sig,
                "nonce": str(nonce),
                "text": normalized,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        req = Request(
            f"{base_url}/r/{room}?format=json",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "User-Agent": DEFAULT_USER_AGENT,
            },
        )

        try:
            with urlopen(req, timeout=12.0) as res:
                res_data = res.read().decode("utf-8")
                return json.loads(res_data)
        except HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            if e.code == 429:
                time.sleep(delay * 2)
                delay = min(delay * 2.0, 10.0)
                continue
            if e.code in (500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 1.8, 10.0)
                continue
            raise RuntimeError(f"HTTP {e.code}: {err_body}")
        except URLError as e:
            time.sleep(delay)
            delay = min(delay * 1.5, 8.0)
            continue

    raise RuntimeError(f"Failed to post signed message after {max_retries} attempts.")


def main() -> int:
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 70)
    print(" FLOP SONNET CONTEST (sonnet-1) — PRE-START FLEET SETUP & ARCHIVE VERIFICATION")
    print("=" * 70)
    print(f" Cutoff S : {CUTOFF_TIMESTAMP}")
    print(f" Keys Dir : {KEYS_DIR}")
    print("-" * 70)

    # 1. Load primary key (Writer 1 / Captain)
    primary_key = load_private_key()
    primary_did = did_from_private_key(primary_key)
    print(f" [Writer 1 - Captain] Loaded Primary DID: {primary_did}")

    # Calculate what letters Writer 1 has and lacks
    alphabet = set("abcdefghijklmnopqrstuvwxyz")
    w1_letters = {ch for ch in primary_did.lower() if "a" <= ch <= "z"}
    missing = alphabet - w1_letters
    print(f"   Letters in Writer 1 ({len(w1_letters)}/26): {''.join(sorted(w1_letters))}")
    print(f"   Missing Letters to cover: {''.join(sorted(missing))}")

    team_members = [
        {
            "role": "writer",
            "name": "writer_1_captain",
            "key": primary_key,
            "did": primary_did,
            "is_primary": True,
        }
    ]

    # 2. Generate 4 additional writers to cover missing letters
    current_covered = set(w1_letters)
    for i in range(2, 6):
        needed = alphabet - current_covered
        if not needed:
            needed = set("aeiou")  # Double down on vowels
        key, did, matched = generate_did_with_needed_letters(needed)
        did_letters = {ch for ch in did.lower() if "a" <= ch <= "z"}
        current_covered.update(did_letters)

        # Save private key securely
        key_path = KEYS_DIR / f"writer_{i}.pem"
        key_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        key_path.write_bytes(key_pem)

        team_members.append({
            "role": "writer",
            "name": f"writer_{i}",
            "key": key,
            "did": did,
            "key_path": str(key_path),
            "is_primary": False,
        })
        print(f" [Writer {i}] Generated DID: {did}")
        print(f"   Supplies letters: {''.join(sorted(did_letters))}")

    print("-" * 70)
    print(f" Total Team Letter Coverage: {len(current_covered)}/26 letters")
    print(f" Letters Covered: {''.join(sorted(current_covered))}")
    if alphabet - current_covered:
        print(f" Still missing: {''.join(sorted(alphabet - current_covered))}")
    else:
        print(" PERFECT! 100% of the English alphabet (A-Z) is covered across the writers!")

    # 3. Generate 3 Voter DIDs
    print("-" * 70)
    for i in range(1, 4):
        key = Ed25519PrivateKey.generate()
        did = did_from_private_key(key)
        key_path = KEYS_DIR / f"voter_{i}.pem"
        key_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        key_path.write_bytes(key_pem)

        team_members.append({
            "role": "voter",
            "name": f"voter_{i}",
            "key": key,
            "did": did,
            "key_path": str(key_path),
            "is_primary": False,
        })
        print(f" [Voter {i}] Generated DID: {did}")

    # 4. Broadcast archive verification check-in for EVERY identity
    print("=" * 70)
    print(" BROADCASTING PRE-START SIGNED MESSAGES TO TECHNOCORE ARCHIVE...")
    print("=" * 70)

    receipts = []
    for idx, member in enumerate(team_members, 1):
        role_label = member["role"].upper()
        name = member["name"]
        did = member["did"]
        text = (
            f"Pre-start identity archive verification for FLOP Technocore sonnet-1 contest. "
            f"Role: {member['role']}, Name: {name}, DID: {did}"
        )

        print(f"[{idx}/{len(team_members)}] Broadcasting for {name} ({role_label})...")
        try:
            res = post_signed_message(member["key"], "technocore", text)
            posted = res.get("posted", {})
            seq = posted.get("seq")
            ts = posted.get("ts")
            nonce = posted.get("nonce")

            is_pre_cutoff = ts < CUTOFF_TIMESTAMP if ts else False
            status_str = "ELIGIBLE (PRE-CUTOFF)" if is_pre_cutoff else "WARNING (AFTER CUTOFF)"

            receipt_record = {
                "name": name,
                "role": member["role"],
                "did": did,
                "key_file": member.get("key_path", "identity.pem"),
                "seq": seq,
                "ts": ts,
                "nonce": nonce,
                "room": "technocore",
                "pre_cutoff_verified": is_pre_cutoff,
            }
            receipts.append(receipt_record)
            print(f"    Seq: {seq} | Timestamp: {ts} | Status: {status_str}")
            time.sleep(1.2)  # Avoid rate limiting
        except Exception as e:
            print(f"    FAILED for {name}: {e}", file=sys.stderr)

    # 5. Save all receipts to JSON
    RECEIPTS_FILE.write_text(json.dumps(receipts, indent=2), encoding="utf-8")
    print("=" * 70)
    print(f" SUCCESS! All receipts saved to:\n {RECEIPTS_FILE}")
    print(f" Total Identities Verified: {len([r for r in receipts if r.get('pre_cutoff_verified')])} / {len(team_members)}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
