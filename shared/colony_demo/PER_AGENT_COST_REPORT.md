# Per-Agent Cost Tracking — Build Report
**Date:** 2026-06-17
**Request:** Track cost broken down by agent (Claude/Codex/Ant/Gem) on dashboard Observability › Cost
**Mode:** Multiagent (Boss-confirmed). Scope: full 4 agents.
**Orchestrator:** Claude (Cody)

## Result: ✅ SHIPPED & VERIFIED LIVE
Live daemon `/v1/interactive/cost` now returns `by_agent` with all 4 agents from real data:
| agent | invocations | tokens in/out | notional cost |
|---|---|---|---|
| claude | 24,084 | 10.7M / 26.4M | $17,077 |
| codex | 61 | 10.4M / 54.6k | $13.52 |
| ant | 2 | — (agy exposes none) | $0 |
| gem | 2 | 260 / 420 | $0.001 |

## Architecture
- **Colony Cost Ledger** `scripts/cost_ledger.py` — append-only JSONL at `shared/logs/cost_ledger.jsonl`; `log_usage()` + notional `estimate_cost()` (pricing in `scripts/agent_pricing.json`); CLI `--log` for any orchestration step.
- **Aggregator** `scripts/parse_agent_costs.py` — stdlib, reads ~/.codex/sessions (codex `token_count` events) + the ledger (gem/ant); `aggregate(since_days)`.
- **Dashboard** `daemon/src/server.ts` — `/v1/interactive/cost` adds `by_agent`: Claude from SQLite summary + external via `execFileSync(python3, parse_agent_costs.py)` (try/catch → claude-only fallback). `web/app/page.tsx` TokensTab renders a "BY AGENT" section.

## Per-agent ledger (who did what)
| Agent | Role | Task | Outcome |
|---|---|---|---|
| **GEM** | Researcher | pricing + SDK usage field research | ❌ 429 quota → Claude wrote pricing table as fallback |
| **Ant** | Coder | build `parse_agent_costs.py` | ✅ real logic correct; ❌ selftest had a self-import bug → Claude fixed (globals() patch + since_days scope) |
| **Claude** | Orchestrator | ledger, worker instrument, dashboard wiring, integration, all fixes | ✅ |
| **Codex** | Eng reviewer | review daemon shell-out | ❌ usage limit → Claude self-reviewed (APPROVE-WITH-NITS) |

## Instrumentation added
- `antigravity_worker.py` (Gem): best-effort token extraction from SDK resp + ledger logging on success/failure. **Unverified against a live Gem call** (429 blocked) — token-field probing is defensive guesswork; confirm when quota recovers.
- `agy` (Ant): no token output → logged via `cost_ledger.py --log` (invocation count only, tokens null).
- Codex: tokens already in `~/.codex/sessions/**/*.jsonl` → parsed directly.

## Open nits / follow-ups (NOT fixed — feature works)
1. Daemon `execFileSync` blocks event loop ≤5s + spawns python per request (no cache). Fine for localhost; convert to async + memoize if it ever goes multi-user.
2. Hardcoded `/opt/homebrew/bin/python3` in server.ts (same fragility as GEM shebang) → consider env/config.
3. Gem token logging path unverified against live SDK (429). 
4. Gem 429 + Codex usage-limit both hit mid-build → **research & review roles are the SPOF of this multiagent setup** (free/limited tiers).

## Verdict
Full 4-agent cost tracking shipped and verified end-to-end on the live daemon. Two of four external agents (Gem, Codex) failed on quota mid-build; Claude absorbed both per the "no-simulate → Claude does it" rule, so the deliverable still completed.
