#!/opt/homebrew/bin/python3
"""
Colony Cost Ledger — single append-only record of every external-agent invocation
made by the Colony orchestration (Gem, Ant, Codex). Claude's own main-session cost
already lives in ~/.claude/projects/*.jsonl; this ledger captures the agents whose
token usage does NOT land there.

Record schema (one JSON object per line) → shared/logs/cost_ledger.jsonl:
  {
    "ts": "2026-06-17T16:00:00",   # ISO-8601 local
    "agent": "gem"|"ant"|"codex"|"claude",
    "engine": "antigravity-sdk"|"agy"|"codex-cli"|"claude-code",
    "model": "gemini-2.5-flash",
    "task": "research dir-scan",   # short label
    "tokens_in": 1234,             # int | null
    "tokens_out": 567,             # int | null
    "tokens_total": 1801,          # int | null
    "est_cost_usd": 0.0012,        # float | null (notional, token x public price)
    "session_id": "8023cb21-...",  # str | null (origin trace)
    "ok": true                     # bool — false if the agent call failed
  }

Pricing is notional (USD per 1M tokens, public list price). For flat-rate / OAuth
engines (agy, codex ChatGPT acct) cost is still computed notionally so the dashboard
can compare token-weighted value across agents — NOT a real billed amount.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

LEDGER_PATH = Path(__file__).resolve().parent.parent / "shared" / "logs" / "cost_ledger.jsonl"
PRICING_PATH = Path(__file__).resolve().parent / "agent_pricing.json"

# Seed pricing (USD per 1M tokens). Confirmed/extended by Gem research (F07).
# Keys are matched case-insensitively by prefix against the record's "model".
_DEFAULT_PRICING = {
    "claude-opus-4-8": {"in": 5.00, "out": 25.00},
    "claude-sonnet-4-6": {"in": 3.00, "out": 15.00},
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},
    "gemini-2.5-flash": {"in": 0.30, "out": 2.50},
    "gemini-2.0-flash": {"in": 0.10, "out": 0.40},
    "gpt-5-codex": {"in": 1.25, "out": 10.00},
    "default": {"in": 1.00, "out": 5.00},
}


def _load_pricing() -> dict:
    if PRICING_PATH.exists():
        try:
            return json.loads(PRICING_PATH.read_text())
        except (OSError, json.JSONDecodeError):
            pass
    return _DEFAULT_PRICING


def estimate_cost(model: str, tokens_in: int | None, tokens_out: int | None) -> float | None:
    """Notional USD = tokens x public price-per-1M. None if no token data."""
    if tokens_in is None and tokens_out is None:
        return None
    pricing = _load_pricing()
    rate = None
    m = (model or "").lower()
    for key, val in pricing.items():
        if key != "default" and m.startswith(key.lower()):
            rate = val
            break
    if rate is None:
        rate = pricing.get("default", {"in": 1.0, "out": 5.0})
    cost = ((tokens_in or 0) * rate["in"] + (tokens_out or 0) * rate["out"]) / 1_000_000
    return round(cost, 6)


def log_usage(
    agent: str,
    engine: str,
    model: str,
    task: str = "",
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    session_id: str | None = None,
    ok: bool = True,
) -> dict:
    """Append one usage record to the ledger. Never raises — returns the record."""
    total = None
    if tokens_in is not None or tokens_out is not None:
        total = (tokens_in or 0) + (tokens_out or 0)
    rec = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "agent": agent,
        "engine": engine,
        "model": model,
        "task": task[:120],
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "tokens_total": total,
        "est_cost_usd": estimate_cost(model, tokens_in, tokens_out),
        "session_id": session_id or os.environ.get("TCC_SESSION_ID"),
        "ok": ok,
    }
    try:
        LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LEDGER_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass  # ledger is best-effort; never break the agent call
    return rec


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Colony Cost Ledger writer")
    p.add_argument("--log", action="store_true", help="Append a usage record")
    p.add_argument("--agent", help="claude|codex|ant|gem")
    p.add_argument("--engine", default="", help="agy|codex-cli|antigravity-sdk|claude-code")
    p.add_argument("--model", default="", help="model id")
    p.add_argument("--task", default="", help="short task label")
    p.add_argument("--tokens-in", type=int, default=None, dest="tin")
    p.add_argument("--tokens-out", type=int, default=None, dest="tout")
    p.add_argument("--session-id", default=None, dest="sid")
    p.add_argument("--fail", action="store_true", help="mark the call as failed (ok=false)")
    p.add_argument("--selftest", action="store_true", help="run a smoke test")
    args = p.parse_args()

    if args.log:
        if not args.agent:
            p.error("--log requires --agent")
        rec = log_usage(
            agent=args.agent, engine=args.engine, model=args.model, task=args.task,
            tokens_in=args.tin, tokens_out=args.tout, session_id=args.sid, ok=not args.fail,
        )
        print(json.dumps(rec, ensure_ascii=False))
        return

    # default / --selftest: smoke test (does NOT write to the real ledger path twice)
    r = log_usage("gem", "antigravity-sdk", "gemini-2.5-flash", "selftest", 1000, 500, "test-session")
    print(json.dumps(r, ensure_ascii=False, indent=2))
    print("LEDGER:", LEDGER_PATH)


if __name__ == "__main__":
    _cli()
