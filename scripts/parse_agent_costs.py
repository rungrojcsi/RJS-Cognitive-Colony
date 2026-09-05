#!/usr/bin/env python3
"""
parse_agent_costs.py — Aggregate per-agent token usage + notional cost.

Sources:
  1. Codex sessions  : ~/.codex/sessions/**/*.jsonl  (recursive)
  2. Colony ledger   : <project>/shared/logs/cost_ledger.jsonl

Usage:
  python parse_agent_costs.py [--since N] [--json] [--table] [--selftest]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Import estimate_cost from sibling module cost_ledger (same scripts/ dir)
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from cost_ledger import estimate_cost  # type: ignore
except Exception:
    def estimate_cost(model: str, tokens_in: Optional[int], tokens_out: Optional[int]) -> Optional[float]:  # type: ignore
        if tokens_in is None and tokens_out is None:
            return None
        rate_in, rate_out = 1.25, 10.00  # gpt-5-codex fallback
        return round(((tokens_in or 0) * rate_in + (tokens_out or 0) * rate_out) / 1_000_000, 6)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CODEX_SESSIONS_GLOB = str(Path.home() / ".codex" / "sessions" / "**" / "*.jsonl")
LEDGER_PATH = (
    Path(__file__).resolve().parent.parent / "shared" / "logs" / "cost_ledger.jsonl"
)
CODEX_MODEL = "gpt-5-codex"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EMPTY_RECORD = dict(
    invocations=0,
    tokens_in=0,
    tokens_out=0,
    tokens_total=0,
    est_cost_usd=0.0,
    last_ts=None,
)


def _new_record() -> dict:
    return dict(_EMPTY_RECORD)


def _parse_ts(ts_str: Optional[str]) -> Optional[datetime]:
    """Return an aware datetime (UTC) or None on failure."""
    if not ts_str:
        return None
    try:
        s = ts_str.rstrip("Z")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _since_cutoff(since_days: Optional[int]) -> Optional[datetime]:
    if since_days is None:
        return None
    return datetime.now(tz=timezone.utc) - timedelta(days=since_days)


def _update_last_ts(record: dict, ts_str: Optional[str]) -> None:
    if not ts_str:
        return
    if record["last_ts"] is None or ts_str > record["last_ts"]:
        record["last_ts"] = ts_str


# ---------------------------------------------------------------------------
# Source 1: Codex sessions
# ---------------------------------------------------------------------------

def _read_codex_sessions(cutoff: Optional[datetime]) -> dict:
    """
    Glob ~/.codex/sessions/**/*.jsonl recursively.
    Each file is one session; take the LAST token_count event (cumulative).
    Agent name = 'codex'.
    """
    records: dict = {}
    agent = "codex"

    try:
        paths = glob.glob(CODEX_SESSIONS_GLOB, recursive=True)
    except OSError:
        paths = []

    for path in paths:
        try:
            _process_codex_file(path, agent, cutoff, records)
        except OSError:
            continue

    return records


def _process_codex_file(
    path: str,
    agent: str,
    cutoff: Optional[datetime],
    records: dict,
) -> None:
    last_usage: Optional[dict] = None
    last_ts_str: Optional[str] = None

    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                if obj.get("type") != "event_msg":
                    continue
                payload = obj.get("payload") or {}
                if payload.get("type") != "token_count":
                    continue
                info = payload.get("info") or {}
                usage = info.get("total_token_usage")
                if not isinstance(usage, dict):
                    continue

                last_usage = usage
                last_ts_str = obj.get("timestamp")
    except OSError:
        return

    if last_usage is None:
        return

    if cutoff is not None and last_ts_str:
        dt = _parse_ts(last_ts_str)
        if dt is not None and dt < cutoff:
            return

    tin = last_usage.get("input_tokens") or 0
    tout = last_usage.get("output_tokens") or 0
    ttotal = last_usage.get("total_tokens") or (tin + tout)

    if agent not in records:
        records[agent] = _new_record()

    rec = records[agent]
    rec["invocations"] += 1
    rec["tokens_in"] += tin
    rec["tokens_out"] += tout
    rec["tokens_total"] += ttotal
    cost = estimate_cost(CODEX_MODEL, tin, tout)
    rec["est_cost_usd"] += cost or 0.0
    _update_last_ts(rec, last_ts_str)


# ---------------------------------------------------------------------------
# Source 2: Colony cost ledger
# ---------------------------------------------------------------------------

def _read_ledger(cutoff: Optional[datetime]) -> dict:
    records: dict = {}

    try:
        with open(LEDGER_PATH, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return records

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue

        ts_str = row.get("ts") or row.get("timestamp")

        if cutoff is not None and ts_str:
            dt = _parse_ts(ts_str)
            if dt is not None and dt < cutoff:
                continue

        agent = str(row.get("agent") or "unknown").strip() or "unknown"
        if agent not in records:
            records[agent] = _new_record()

        rec = records[agent]
        rec["invocations"] += 1

        tin = row.get("tokens_in") or 0
        tout = row.get("tokens_out") or 0
        ttotal = row.get("tokens_total") or (tin + tout)

        rec["tokens_in"] += tin
        rec["tokens_out"] += tout
        rec["tokens_total"] += ttotal

        existing_cost = row.get("est_cost_usd")
        if existing_cost is not None:
            try:
                rec["est_cost_usd"] += float(existing_cost)
            except (TypeError, ValueError):
                model = str(row.get("model") or "default")
                rec["est_cost_usd"] += estimate_cost(model, tin, tout) or 0.0
        else:
            model = str(row.get("model") or "default")
            rec["est_cost_usd"] += estimate_cost(model, tin, tout) or 0.0

        _update_last_ts(rec, ts_str)

    return records


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def aggregate(since_days: Optional[int] = None) -> dict:
    """
    Aggregate per-agent token usage and notional cost.

    Returns:
        {
            agent: {
                invocations: int,
                tokens_in: int,
                tokens_out: int,
                tokens_total: int,
                est_cost_usd: float,
                last_ts: str | None,
            }
        }

    Filters by timestamp if since_days is given.
    Never raises on missing files or directories.
    """
    cutoff = _since_cutoff(since_days)

    try:
        codex_records = _read_codex_sessions(cutoff)
    except Exception:
        codex_records = {}

    try:
        ledger_records = _read_ledger(cutoff)
    except Exception:
        ledger_records = {}

    result: dict = {}

    for agent, rec in codex_records.items():
        result[agent] = dict(rec)

    for agent, rec in ledger_records.items():
        if agent in result:
            existing = result[agent]
            existing["invocations"] += rec["invocations"]
            existing["tokens_in"] += rec["tokens_in"]
            existing["tokens_out"] += rec["tokens_out"]
            existing["tokens_total"] += rec["tokens_total"]
            existing["est_cost_usd"] = round(existing["est_cost_usd"] + rec["est_cost_usd"], 6)
            if rec["last_ts"] and (
                existing["last_ts"] is None or rec["last_ts"] > existing["last_ts"]
            ):
                existing["last_ts"] = rec["last_ts"]
        else:
            result[agent] = dict(rec)

    for rec in result.values():
        rec["est_cost_usd"] = round(rec["est_cost_usd"], 6)

    return result


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _run_selftest() -> None:
    """Write a temp ledger, assert aggregation, print SELFTEST OK."""
    now_iso = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")

    ledger_rows = [
        {
            "ts": now_iso,
            "agent": "gem",
            "engine": "antigravity-sdk",
            "model": "gemini-2.5-flash",
            "task": "selftest-1",
            "tokens_in": 1000,
            "tokens_out": 500,
            "tokens_total": 1500,
            "est_cost_usd": 0.0015,
            "session_id": "test-123",
            "ok": True,
        },
        {
            "ts": now_iso,
            "agent": "gem",
            "engine": "antigravity-sdk",
            "model": "gemini-2.5-flash",
            "task": "selftest-2",
            "tokens_in": 200,
            "tokens_out": 100,
            "tokens_total": 300,
            "est_cost_usd": None,
            "session_id": "test-124",
            "ok": True,
        },
        {
            "ts": now_iso,
            "agent": "ant",
            "engine": "agy",
            "model": "claude-sonnet-4-6",
            "task": "selftest-3",
            "tokens_in": 500,
            "tokens_out": 250,
            "tokens_total": 750,
            "est_cost_usd": 0.005,
            "session_id": "test-125",
            "ok": True,
        },
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as tf:
        for row in ledger_rows:
            tf.write(json.dumps(row) + "\n")
        tmp_path = Path(tf.name)

    # Patch THIS module's globals directly. Importing the module by name while
    # running as __main__ would create a duplicate module object, so the patch
    # would not affect the functions reading __main__'s globals.
    g = globals()
    original_ledger = g["LEDGER_PATH"]
    original_glob_pat = g["CODEX_SESSIONS_GLOB"]
    try:
        g["LEDGER_PATH"] = tmp_path
        g["CODEX_SESSIONS_GLOB"] = str(tmp_path.parent / "nonexistent_codex_**" / "*.jsonl")

        result = aggregate()
        # since_days=1 must also read the patched temp sources
        result_recent = aggregate(since_days=1)
    finally:
        g["LEDGER_PATH"] = original_ledger
        g["CODEX_SESSIONS_GLOB"] = original_glob_pat
        try:
            tmp_path.unlink()
        except OSError:
            pass

    assert "gem" in result, f"Expected 'gem' in result, got: {list(result.keys())}"
    assert "ant" in result, f"Expected 'ant' in result, got: {list(result.keys())}"

    gem = result["gem"]
    assert gem["invocations"] == 2, f"gem invocations: expected 2, got {gem['invocations']}"
    assert gem["tokens_in"] == 1200, f"gem tokens_in: expected 1200, got {gem['tokens_in']}"
    assert gem["tokens_out"] == 600, f"gem tokens_out: expected 600, got {gem['tokens_out']}"
    assert gem["tokens_total"] == 1800, f"gem tokens_total: expected 1800, got {gem['tokens_total']}"

    # Row 1: est_cost_usd=0.0015 (existing). Row 2: recomputed gemini-2.5-flash
    # in=0.30, out=2.50 per 1M => (200*0.30 + 100*2.50)/1M = 0.00031
    expected_gem_cost = round(0.0015 + (200 * 0.30 + 100 * 2.50) / 1_000_000, 6)
    assert abs(gem["est_cost_usd"] - expected_gem_cost) < 1e-8, (
        f"gem est_cost_usd: expected {expected_gem_cost}, got {gem['est_cost_usd']}"
    )
    assert gem["last_ts"] == now_iso, f"gem last_ts mismatch"

    ant = result["ant"]
    assert ant["invocations"] == 1, f"ant invocations: expected 1, got {ant['invocations']}"
    assert ant["tokens_in"] == 500
    assert ant["tokens_out"] == 250
    assert ant["est_cost_usd"] == 0.005

    # since_days=1 should still include records made just now (computed above
    # while the temp sources were patched in)
    assert "gem" in result_recent, "since_days=1 should include recent records"

    print("SELFTEST OK")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _format_table(data: dict) -> str:
    if not data:
        return "(no data)"

    header = f"{'AGENT':<14} {'INVOC':>6} {'TOK_IN':>10} {'TOK_OUT':>10} {'TOK_TOT':>10} {'COST_USD':>12}  LAST_TS"
    sep = "-" * 80
    lines = [header, sep]

    for agent in sorted(data):
        rec = data[agent]
        lines.append(
            f"{agent:<14} {rec['invocations']:>6} {rec['tokens_in']:>10,} "
            f"{rec['tokens_out']:>10,} {rec['tokens_total']:>10,} "
            f"{rec['est_cost_usd']:>12.6f}  {rec['last_ts'] or '-'}"
        )

    totals = {
        k: sum(data[a][k] for a in data)
        for k in ("invocations", "tokens_in", "tokens_out", "tokens_total", "est_cost_usd")
    }
    lines.append(sep)
    lines.append(
        f"{'TOTAL':<14} {totals['invocations']:>6} {totals['tokens_in']:>10,} "
        f"{totals['tokens_out']:>10,} {totals['tokens_total']:>10,} "
        f"{totals['est_cost_usd']:>12.6f}"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate per-agent token usage and notional cost."
    )
    parser.add_argument(
        "--since",
        metavar="N",
        type=int,
        default=None,
        help="Only include records from the last N days.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output as JSON (default).",
    )
    parser.add_argument(
        "--table",
        action="store_true",
        dest="output_table",
        help="Output as human-readable table.",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run self-test and print SELFTEST OK.",
    )
    args = parser.parse_args()

    if args.selftest:
        _run_selftest()
        return

    data = aggregate(since_days=args.since)

    if args.output_table:
        print(_format_table(data))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
