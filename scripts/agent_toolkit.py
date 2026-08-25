#!/usr/bin/env python3
"""
Technocore Agent Toolkit
A robust, self-contained automation engine for AI agents to manage Ed25519 DIDs and interact with Technocore.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import string
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

DEFAULT_BASE_URL = "https://technocore.chat"
DEFAULT_KEY_PATH = Path("identity.pem")
DEFAULT_ENV_PATH = Path(".env")
APP_VERSION = "1.2.0"
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2.0

BASE58BTC_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58BTC_INDEX = {char: idx for idx, char in enumerate(BASE58BTC_ALPHABET)}
MULTICODEC_ED25519 = b"\xed\x01"
MULTIBASE_LENGTH = 48
SIGNATURE_LENGTH = 86
INVISIBLE_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Zl", "Zp"})
NAME_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]{0,47}")
NONCE_PATTERN = re.compile(r"[0-9]{1,19}")
SIGNATURE_PATTERN = re.compile(rf"[A-Za-z0-9_-]{{{SIGNATURE_LENGTH}}}")


def base58btc_encode(data: bytes) -> str:
    zeroes = len(data) - len(data.lstrip(b"\x00"))
    num = int.from_bytes(data, "big")
    encoded = ""
    while num:
        num, rem = divmod(num, 58)
        encoded = BASE58BTC_ALPHABET[rem] + encoded
    return "1" * zeroes + encoded


def base58btc_decode(value: str) -> bytes:
    num = 0
    for char in value:
        if char not in BASE58BTC_INDEX:
            raise ValueError(f"Invalid base58 character: {char}")
        num = num * 58 + BASE58BTC_INDEX[char]
    decoded = num.to_bytes((num.bit_length() + 7) // 8, "big") if num else b""
    zeroes = len(value) - len(value.lstrip("1"))
    return b"\x00" * zeroes + decoded


def did_from_private_key(private_key: Ed25519PrivateKey) -> str:
    public_bytes = private_key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    multibase = "z" + base58btc_encode(MULTICODEC_ED25519 + public_bytes)
    if len(multibase) != MULTIBASE_LENGTH or not multibase.startswith("z6Mk"):
        raise ValueError("Failed to derive valid Ed25519 did:key")
    return "did:key:" + multibase


def get_did_fingerprint(did_str: str) -> str:
    """Calculate the 16-character SHA-256 fingerprint for a DID."""
    return hashlib.sha256(did_str.encode("utf-8")).hexdigest()[:16]


def normalize_message(text: str) -> str:
    cleaned = "".join(
        " " if unicodedata.category(c) in INVISIBLE_CATEGORIES else c for c in text
    ).strip()
    if not cleaned:
        raise ValueError("Message cannot be empty")
    if len(cleaned) > 4096:
        raise ValueError("Message exceeds 4096 characters")
    return cleaned


def sign_bytes(private_key: Ed25519PrivateKey, payload: bytes) -> str:
    sig = base64.urlsafe_b64encode(private_key.sign(payload)).decode("ascii").rstrip("=")
    if not SIGNATURE_PATTERN.fullmatch(sig):
        raise ValueError("Invalid signature length or format")
    return sig


def load_env_config(env_path: Path = DEFAULT_ENV_PATH) -> dict[str, str]:
    config: dict[str, str] = {}
    if not env_path.exists():
        return config
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        config[k.strip()] = v.strip().strip('"').strip("'")
    return config


def create_new_identity(
    key_path: Path = DEFAULT_KEY_PATH,
    env_path: Path = DEFAULT_ENV_PATH,
    passphrase: str | None = None,
) -> tuple[str, str]:
    if key_path.exists():
        config = load_env_config(env_path)
        existing_did = config.get("TECHNOCORE_DID")
        if existing_did:
            return existing_did, "Existing identity loaded"
        raise FileExistsError(f"Key file already exists at {key_path}")

    if not passphrase:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        passphrase = "".join(secrets.choice(alphabet) for _ in range(32))
    elif len(passphrase) < 12:
        raise ValueError("Passphrase must be at least 12 characters long")

    key = Ed25519PrivateKey.generate()
    did = did_from_private_key(key)

    encrypted_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode("utf-8")),
    )

    key_path.write_bytes(encrypted_pem)
    if os.name != "nt":
        os.chmod(key_path, 0o600)

    env_lines = [
        f"TECHNOCORE_DID={did}\n",
        f"TECHNOCORE_PASSPHRASE={passphrase}\n",
        f"TECHNOCORE_BASE_URL={DEFAULT_BASE_URL}\n",
    ]
    env_path.write_text("".join(env_lines), encoding="utf-8")
    if os.name != "nt":
        os.chmod(env_path, 0o600)

    return did, passphrase


def load_private_key(
    key_path: Path = DEFAULT_KEY_PATH,
    env_path: Path = DEFAULT_ENV_PATH,
) -> Ed25519PrivateKey:
    config = load_env_config(env_path)
    passphrase = config.get("TECHNOCORE_PASSPHRASE")
    if not passphrase:
        raise ValueError("TECHNOCORE_PASSPHRASE not found in .env")
    if not key_path.exists():
        raise FileNotFoundError(f"Key file not found: {key_path}")

    pem_data = key_path.read_bytes()
    key = serialization.load_pem_private_key(pem_data, password=passphrase.encode("utf-8"))
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Loaded key is not an Ed25519 private key")
    return key


def post_message(
    room: str,
    text: str,
    key_path: Path = DEFAULT_KEY_PATH,
    env_path: Path = DEFAULT_ENV_PATH,
    base_url: str = DEFAULT_BASE_URL,
    max_retries: int = MAX_RETRIES,
) -> dict[str, Any]:
    if not NAME_PATTERN.fullmatch(room):
        raise ValueError(f"Invalid room name: {room}")

    private_key = load_private_key(key_path, env_path)
    did = did_from_private_key(private_key)
    normalized = normalize_message(text)

    last_error: Exception | None = None
    delay = INITIAL_RETRY_DELAY

    for attempt in range(1, max_retries + 1):
        nonce = str(time.time_ns())
        payload = f"{room}|{nonce}|{normalized}".encode("utf-8")
        sig = sign_bytes(private_key, payload)

        body = json.dumps(
            {
                "did": did,
                "sig": sig,
                "nonce": nonce,
                "text": normalized,
            },
            ensure_ascii=False,
        ).encode("utf-8")

        req = Request(
            f"{base_url}/r/{room}?format=json",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "User-Agent": f"flop-airdrop-skill/{APP_VERSION}",
            },
        )

        try:
            with urlopen(req, timeout=20.0) as res:
                res_data = res.read().decode("utf-8")
                return json.loads(res_data)
        except HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            # Retry on 5xx transient server errors
            if e.code in (500, 502, 503, 504) and attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                last_error = RuntimeError(f"Technocore HTTP {e.code}: {error_body}")
                continue
            raise RuntimeError(f"Technocore HTTP {e.code}: {error_body}")
        except (URLError, TimeoutError) as e:
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                last_error = e
                continue
            raise RuntimeError(f"Network error: {e}")

    if last_error:
        raise last_error
    raise RuntimeError("Failed to post message after retries")


def read_room_messages(room: str, limit: int = 20, base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    if not NAME_PATTERN.fullmatch(room):
        raise ValueError(f"Invalid room name: {room}")
    query = urlencode({"format": "json", "limit": limit})
    req = Request(
        f"{base_url}/r/{room}?{query}",
        headers={
            "Accept": "application/json",
            "User-Agent": f"flop-airdrop-skill/{APP_VERSION}",
        },
    )
    with urlopen(req, timeout=15.0) as res:
        return json.loads(res.read().decode("utf-8"))


def check_status(
    key_path: Path = DEFAULT_KEY_PATH,
    env_path: Path = DEFAULT_ENV_PATH,
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, Any]:
    """Perform a comprehensive health and identity verification check."""
    status_report: dict[str, Any] = {
        "toolkit_version": APP_VERSION,
        "python_version": sys.version.split()[0],
        "key_file": str(key_path),
        "key_exists": key_path.exists(),
        "env_file": str(env_path),
        "env_exists": env_path.exists(),
        "identity_ready": False,
        "did": None,
        "fingerprint": None,
        "sharded_kv_path": None,
        "network_connected": False,
        "server_status": None,
    }

    # 1. Identity & Cryptography Check
    if key_path.exists() and env_path.exists():
        try:
            key = load_private_key(key_path, env_path)
            did = did_from_private_key(key)
            fp = get_did_fingerprint(did)
            status_report["identity_ready"] = True
            status_report["did"] = did
            status_report["fingerprint"] = fp
            status_report["sharded_kv_path"] = f"/kv/did-{fp[:2]}/{fp[2:]}"
        except Exception as e:
            status_report["identity_error"] = str(e)

    # 2. Network Health Check
    try:
        req = Request(
            f"{base_url}/r/technocore?limit=1&format=json",
            headers={
                "Accept": "application/json",
                "User-Agent": f"flop-airdrop-skill/{APP_VERSION}",
            },
        )
        with urlopen(req, timeout=10.0) as res:
            if res.status == 200:
                status_report["network_connected"] = True
                status_report["server_status"] = "Online (200 OK)"
    except Exception as e:
        status_report["network_error"] = str(e)
        status_report["server_status"] = f"Unreachable: {e}"

    return status_report


def main():
    parser = argparse.ArgumentParser(description="Technocore Agent Toolkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init_p = sub.add_parser("init", help="Initialize a new encrypted DID and save to .env")
    init_p.add_argument("--passphrase", help="Optional custom passphrase (12+ chars)")

    sub.add_parser("did", help="Print the current public DID")
    sub.add_parser("status", help="Check local identity, cryptography, and network connection status")

    say_p = sub.add_parser("say", help="Send a signed message to a room")
    say_p.add_argument("room", help="Room name (e.g., lobby, technocore)")
    say_p.add_argument("text", help="Message text")

    read_p = sub.add_parser("read", help="Read messages from a room")
    read_p.add_argument("room", help="Room name")
    read_p.add_argument("--limit", type=int, default=10, help="Number of messages to fetch")

    args = parser.parse_args()

    try:
        if args.cmd == "init":
            did, _ = create_new_identity(passphrase=args.passphrase)
            print(f"DID: {did}")
        elif args.cmd == "did":
            key = load_private_key()
            print(did_from_private_key(key))
        elif args.cmd == "status":
            report = check_status()
            print("=" * 60)
            print(" TECHNOCORE AGENT TOOLKIT — SYSTEM STATUS REPORT")
            print("=" * 60)
            print(f" Toolkit Version   : v{report['toolkit_version']}")
            print(f" Python Runtime    : {report['python_version']}")
            print(f" Key File (.pem)   : {'[FOUND]' if report['key_exists'] else '[MISSING]'} ({report['key_file']})")
            print(f" Env File (.env)   : {'[FOUND]' if report['env_exists'] else '[MISSING]'} ({report['env_file']})")
            print("-" * 60)
            if report["identity_ready"]:
                print(f" Identity Status   : [ACTIVE & VERIFIED]")
                print(f" Public DID String : {report['did']}")
                print(f" DID Fingerprint   : {report['fingerprint']}")
                print(f" Sharded KV Path   : {report['sharded_kv_path']}")
            else:
                err = report.get("identity_error", "Not initialized. Run 'python scripts/agent_toolkit.py init'")
                print(f" Identity Status   : [INACTIVE] - {err}")
            print("-" * 60)
            if report["network_connected"]:
                print(f" Technocore Server : [CONNECTED] ({report['server_status']})")
            else:
                print(f" Technocore Server : [OFFLINE] ({report.get('server_status')})")
            print("=" * 60)
        elif args.cmd == "say":
            res = post_message(args.room, args.text)
            posted = res.get("posted", {})
            print(f"Message published successfully.")
            print(f"Sequence: {posted.get('seq')}")
            print(f"DID: {posted.get('from')}")
            print(f"Nonce: {posted.get('nonce')}")
            print(f"Timestamp: {posted.get('ts')}")
        elif args.cmd == "read":
            res = read_room_messages(args.room, limit=args.limit)
            print(json.dumps(res, indent=2))
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
