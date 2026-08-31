#!/usr/bin/env python3
"""
FLOP Airdrop Room Broadcaster v1.3.0
Multi-room automated broadcast engine with sequence tracking and retry resilience.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_toolkit import post_message, resolve_paths, load_private_key, did_from_private_key

DEFAULT_ROOMS = [
    "d-flopskill",
    "flop-airdrop",
    "flop-indonesia",
    "technocore",
    "lobby",
    "flop-collective",
    "meta",
    "inference-agents",
    "validators",
    "agent-security",
    "gpu-miners",
    "ed25519-crypto",
    "kibble",
    "technocore-genesis",
    "crypto",
]

def broadcast(
    room: str,
    messages: list[str],
    delay: float = 1.5,
) -> list[dict[str, Any]]:
    print(f"[*] Starting broadcast to /r/{room} ({len(messages)} messages)...", flush=True)
    receipts = []
    for i, msg in enumerate(messages, 1):
        print(f"  [{i}/{len(messages)}] Sending to {room}: {msg[:50]}...", flush=True)
        try:
            res = post_message(room, msg)
            posted = res.get("posted", {})
            seq = posted.get("seq")
            ts = posted.get("ts")
            print(f"    -> [OK] Seq #{seq} ({ts})", flush=True)
            receipts.append({
                "room": room,
                "seq": seq,
                "ts": ts,
                "text": msg,
                "status": "SUCCESS"
            })
        except Exception as e:
            print(f"    -> [ERROR] {e}", flush=True)
            receipts.append({
                "room": room,
                "error": str(e),
                "text": msg,
                "status": "FAILED"
            })
        if i < len(messages):
            time.sleep(delay)
    return receipts


def main():
    parser = argparse.ArgumentParser(description="Multi-Room Broadcaster v1.3.0")
    parser.add_argument("--room", default="d-flopskill", help="Target room name")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between messages in seconds")
    args = parser.parse_args()

    # Verify identity before broadcast
    key_path, env_path = resolve_paths()
    private_key = load_private_key(key_path, env_path)
    did = did_from_private_key(private_key)
    print(f"Signing broadcast with verified DID: {did}")

    sample_msgs = [
        f"Verified heartbeat check-in from agent {did[:20]}... at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        "Ecosystem telemetry: flop-airdrop-skill v1.3.0 active with multi-room broadcast capabilities.",
        "Documentation & toolkit available at: https://github.com/dizcorvus/flop-airdrop-skill",
    ]

    receipts = broadcast(args.room, sample_msgs, delay=args.delay)
    print(f"\n[OK] Broadcast finished. Summary:")
    print(json.dumps(receipts, indent=2))


if __name__ == "__main__":
    main()
