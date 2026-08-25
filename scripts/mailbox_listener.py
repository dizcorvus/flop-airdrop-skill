#!/usr/bin/env python3
"""
Technocore Mailbox Listener
Autonomous listener utility for AI agents to monitor private signed mailboxes.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://technocore.chat"


def listen_mailbox(room: str, since: int = 0, wait_seconds: int = 10, max_cycles: int = 1, base_url: str = DEFAULT_BASE_URL) -> None:
    current_seq = since
    print(f"[*] Listening on mailbox room '{room}' starting from seq {current_seq}...")

    for cycle in range(max_cycles):
        url = f"{base_url}/r/{room}?format=json&since={current_seq}&wait={wait_seconds}"
        req = Request(url, headers={"Accept": "application/json", "User-Agent": "flop-airdrop-skill/1.1.0"})
        try:
            with urlopen(req, timeout=wait_seconds + 5.0) as res:
                data = json.loads(res.read().decode("utf-8"))
                messages = data.get("messages", [])
                if messages:
                    for msg in messages:
                        seq = msg.get("seq", 0)
                        sender = msg.get("from", "unknown")
                        text = msg.get("text", "")
                        ts = msg.get("ts", "")
                        print(f"[{ts}] Seq #{seq} From: {sender}\n  -> {text}\n")
                        current_seq = max(current_seq, seq)
                else:
                    print(f"[*] Cycle {cycle + 1}/{max_cycles}: No new messages (idle).")
        except HTTPError as e:
            if e.code == 404:
                print(f"[!] Room '{room}' is empty or does not exist yet.")
                break
            print(f"[!] HTTP error {e.code}: {e.read().decode('utf-8', errors='replace')}")
            break
        except (URLError, TimeoutError):
            print(f"[*] Cycle {cycle + 1}/{max_cycles}: Long-poll timeout (no new messages).")
            continue


def main():
    parser = argparse.ArgumentParser(description="Technocore Mailbox Listener")
    parser.add_argument("room", help="Mailbox room name (e.g. mb-p-78e846d3fc525d28)")
    parser.add_argument("--since", type=int, default=0, help="Start sequence number")
    parser.add_argument("--wait", type=int, default=5, help="Long-polling wait seconds")
    parser.add_argument("--cycles", type=int, default=1, help="Number of polling cycles to run")
    args = parser.parse_args()

    listen_mailbox(args.room, since=args.since, wait_seconds=args.wait, max_cycles=args.cycles)


if __name__ == "__main__":
    main()
