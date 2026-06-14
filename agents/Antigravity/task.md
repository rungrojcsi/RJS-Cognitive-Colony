# Task — Antigravity (Foundation Page: P1 Skeleton)

**Status:** active
**Assigned by:** Claude (Orchestrator — Foundation Build 2026-06-11)
**Priority:** P1 — build UI skeleton + Hono route + WebSocket broadcast

---

## Context

Boss's **agent-dashboard** project needs a new **Foundation** tab — a page that shows 6 AI agents working on a task in real-time. This is the "Agentic Workbench" showcase.

**Project path:** `/Users/rojios/Documents/Claude/Projects/agent-dashboard/`

**Stack (existing, do NOT change):**
- Frontend: Next.js 16 + React 19 + Tailwind CSS — port 3030 — `web/`
- Daemon: Hono TypeScript — port 7777 — `daemon/src/`
- DB: SQLite via better-sqlite3 (`state.db`)
- WebSocket: `ws` library — already in `daemon/src/server.ts`

---

## What You Build (P1 only)

### 1. `daemon/src/foundation.ts`

Hono sub-app with 2 endpoints:

```typescript
// POST /api/foundation/run
// Body: { task: string }
// Returns: { run_id: string }
// Side effect: insert row into foundation_runs, then call runFoundationPipeline() async

// GET /api/foundation/runs
// Returns: last 10 rows from foundation_runs table
```

**foundation_runs table** (add to `daemon/src/schema.sql` AND create in `db.ts`):
```sql
CREATE TABLE IF NOT EXISTS foundation_runs (
  id TEXT PRIMARY KEY,
  task TEXT NOT NULL,
  status TEXT DEFAULT 'pending',   -- pending|running|done|error
  result TEXT,
  created_at INTEGER DEFAULT (unixepoch()),
  updated_at INTEGER DEFAULT (unixepoch())
);
```

**runFoundationPipeline stub** (async, fire-and-forget):
```typescript
async function runFoundationPipeline(runId: string, task: string, broadcast: (evt: object) => void) {
  // Stub — just simulate agent activity for now
  const agents = ["Orchestrator", "Researcher", "Planner", "Coder", "Executor", "Scribe"];
  for (const agent of agents) {
    broadcast({ type: "agent_event", run_id: runId, agent, status: "working", message: `${agent} started`, ts: Date.now() });
    await new Promise(r => setTimeout(r, 800));
    broadcast({ type: "agent_event", run_id: runId, agent, status: "done", message: `${agent} finished`, ts: Date.now() });
  }
  broadcast({ type: "run_complete", run_id: runId, ts: Date.now() });
}
```

**WebSocket event schema:**
```typescript
type FoundationEvent =
  | { type: "agent_event"; run_id: string; agent: string; status: "working"|"done"|"error"; message: string; ts: number }
  | { type: "run_complete"; run_id: string; ts: number };
```

**How to get the broadcast function:** `foundation.ts` exports a `setFoundationBroadcast(fn)` setter. `server.ts` calls it after the WSS is created — same pattern as existing code.

---

### 2. `web/app/foundation/page.tsx`

React client component. Match existing style (dark theme, same as `todos/page.tsx`).

**Layout:**
```
[NavSwitch with "Foundation" tab active]

[Task input: text field + "Run" button]

[Agent Cards grid — 6 cards]
  Each card shows:
  - Agent name + model label (Orchestrator·Claude, Researcher·Gemini, etc.)
  - Status dot: grey=idle, yellow=working, green=done, red=error
  - Last message (from WS event)

[Activity Log — scrollable list, newest first]
  Each entry: timestamp + agent name + message
```

**Model labels per agent:**
| Agent | Label |
|---|---|
| Orchestrator | Claude Sonnet |
| Researcher | Gemini Flash |
| Planner | Claude Sonnet |
| Coder | Antigravity SDK |
| Executor | Gemini Flash |
| Scribe | Pure Code |

**WebSocket connection:**
- Connect to `ws://localhost:7777/ws` (same as existing monitor page)
- Filter messages where `msg.type === "agent_event"` or `msg.type === "run_complete"`
- On `agent_event`: update card status + append to activity log
- On `run_complete`: set all cards to idle after 2s delay

**API calls:**
- POST `/api/foundation/run` with `{ task }` to start
- Use `api()` + `apiPost()` from `@/lib/api` (same pattern as todos/page.tsx)
- Show run_id in activity log header

**PinGate:** wrap in `<PinGate>` same as todos page.

---

### 3. Update `web/components/NavSwitch.tsx`

Add "Foundation" tab:
```typescript
// Change the type union:
active: "dashboard" | "cases" | "todos" | "monitor" | "settings" | "foundation"

// Add item:
{item("/foundation", "foundation", "⬡ Foundation")}
```

---

## What NOT to build (P2 — Claude does later)

- Actual LLM calls in `runFoundationPipeline` (stub is enough for P1)
- Agent module files in `daemon/src/agents/`
- Any changes to CLAUDE.md or other config

---

## Code style rules

- Match existing file style exactly (no new eslint directives, match imports)
- TypeScript strict mode — no `any` without comment
- No new dependencies — use only what's already in `package.json`
- Server-side: Hono patterns from `server.ts`
- Frontend: React hooks + Tailwind only — no new component libs

---

## How to wire foundation.ts into server.ts

At bottom of imports in `server.ts`:
```typescript
import { foundationApp, setFoundationBroadcast } from "./foundation.js";
```

After WSS setup (find the `wss.on("connection", ...)` block):
```typescript
setFoundationBroadcast((evt) => {
  const msg = JSON.stringify(evt);
  wss.clients.forEach(c => { if (c.readyState === 1) c.send(msg); });
});
```

Mount the sub-app:
```typescript
app.route("/api/foundation", foundationApp);
```

---

## Deliverable

Write the 3 files above. Put each file's full content into `results.md` with this format:

```markdown
# Foundation P1 — Results

## FILE: daemon/src/foundation.ts
\`\`\`typescript
...full file content...
\`\`\`

## FILE: web/app/foundation/page.tsx
\`\`\`tsx
...full file content...
\`\`\`

## FILE: web/components/NavSwitch.tsx (full file)
\`\`\`tsx
...full file content...
\`\`\`

## Notes
...any observations or decisions made...
```

Write results to:
`/Users/rojios/Documents/Claude/Projects/The Cognitive Colony/agents/Antigravity/results.md`
