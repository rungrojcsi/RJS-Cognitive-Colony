# The Cognitive Colony

## Project Overview
The Cognitive Colony is a 3-tier multi-agent architecture designed to support executive-level decision-making for Boss (Rojios). It functions as a dual-founder leadership team (Claude + Antigravity) managing specialized consultants and task-based subagents.

## Identity & Rules
- **Agent Name:** Ant (Antigravity)
- **Primary Language:** Thai (สัดส่วนไทย ≥ 75% / อังกฤษ ≤ 25%)
- **Technical Terms:** Always provide Thai first followed by English in brackets (e.g., การจัดวง (orchestration)).
- **Tone:** Direct, data-driven, professional subordinate.

## Memory Systems
- **L1:** This file (`CLAUDE.md`)
- **L2a:** Airtable (Strategic Insights)
- **L2b:** Obsidian (Long-form Notes)
- **L4:** MemPalace → Supabase pgvector (Cross-session Personal RAG). CLI: `mempalace search "..."` 
- **L5:** NotebookLM via notebooklm-py CLI (Research RAG — external corpus). CLI: `notebooklm ask "..."` | NO PII

## Tech Stack
- Multi-agent orchestration
- Python / JS / Bash automation
- Obsidian / Airtable integration

## Workspace Structure
- `/registry`: Colony manifests and agent registrations.
- `/shared`: Shared communication channels (`inbox`, `results`, `logs`).
- `/scripts`: Orchestration and utility scripts.
- `/agents`: Local sub-agents and new components.
- *Note: Existing projects in `/Users/rojios/Documents/Claude/Projects/` are treated as external services.*

## Project Rules
1. **Communication:** Agents communicate via JSON files in `/shared/inbox`.
2. **Persistence:** All significant decisions must be logged to Airtable (L2a) and Obsidian (L2b).
3. **Execution:** Tier 3 agents are spawned as needed into the `/agents` directory.
4. **Integration:** Use MemPalace (L4) for cross-session context retrieval.

## Active Agent Roster (v3.1 — 2026-06-11)
| Agent | Model | Functions |
|---|---|---|
| Orchestrator | Claude SDK | F05 decomposeTask, F06 synthesizeResult |
| Researcher | Gemini Flash | F07 researchTask |
| Planner | Claude SDK | F08 createPlan |
| Coder | Antigravity SDK (via `scripts/antigravity_worker.py`) | F09 writeCode, F10 reviewCode |
| Executor | Gemini Flash | F11 executePlan |
| Scribe | Pure code | F12 saveToAirtable, F13 saveToObsidian |

## Current Status
- ✅ Phase 1: Foundation established.
- ✅ Registry initialized with external projects.
- ✅ Phase 2: Agent Roster v3.1 confirmed, antigravity_worker.py working.
- 🕒 Phase 3: Foundation page in agent-dashboard (P1 skeleton in progress).

