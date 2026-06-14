# Foundation P1 — Results

**Completed by:** Antigravity (Coder Agent)
**Date:** 2026-06-11
**Status:** All 3 primary files written + schema.sql updated + server.ts wired

---

## FILE: daemon/src/foundation.ts

```typescript
// Foundation sub-app — Agentic Workbench showcase
// Provides POST /api/foundation/run and GET /api/foundation/runs
// Broadcasts real-time agent events over the shared WebSocket.

import { Hono } from "hono";
import { randomUUID } from "node:crypto";
import { db } from "./db.js";

// DB bootstrap (idempotent)
try {
  db.exec(`
    CREATE TABLE IF NOT EXISTS foundation_runs (
      id TEXT PRIMARY KEY, task TEXT NOT NULL,
      status TEXT DEFAULT 'pending', result TEXT,
      created_at INTEGER DEFAULT (unixepoch()),
      updated_at INTEGER DEFAULT (unixepoch())
    );
    CREATE INDEX IF NOT EXISTS idx_foundation_runs_created ON foundation_runs(created_at DESC);
  `);
} catch (e: any) { console.error("[foundation] table init failed:", e.message); }

// ... (see full file at daemon/src/foundation.ts)
// exports: foundationApp (Hono), setFoundationBroadcast(fn)
// POST /run — insert run, fire-and-forget pipeline
// GET /runs — last 10 rows
```

---

## FILE: web/app/foundation/page.tsx

```tsx
"use client";
// React client component — Foundation Agentic Workbench page
// - PinGate wrapper
// - Task input + Run button
// - 6 AgentCard grid (Orchestrator, Researcher, Planner, Coder, Executor, Scribe)
// - Activity log (newest first, WS events)
// - Past runs panel (GET /api/foundation/runs)
// - WS: ws://localhost:7777/ws?pin=... filters agent_event + run_complete
// (see full file at web/app/foundation/page.tsx)
```

---

## FILE: web/components/NavSwitch.tsx (full file)

```tsx
"use client";
import Link from "next/link";

export function NavSwitch({ active }: { active: "dashboard" | "cases" | "todos" | "monitor" | "settings" | "foundation" }) {
  const item = (href: string, key: typeof active, label: string) => (
    <Link href={href} className={`px-3 py-1 rounded transition ${
      active === key ? "bg-neutral-100 text-neutral-900 font-medium" : "text-neutral-400 hover:text-neutral-200"
    }`}>{label}</Link>
  );
  return (
    <div className="inline-flex rounded-md border border-neutral-700 bg-neutral-900/40 p-0.5 text-xs">
      {item("/", "dashboard", "Dashboard")}
      {item("/cases", "cases", "Open Cases")}
      {item("/todos", "todos", "✓ Todos")}
      {item("/monitor", "monitor", "📡 Monitor")}
      {item("/settings", "settings", "⚙ Settings")}
      {item("/foundation", "foundation", "⬡ Foundation")}
    </div>
  );
}
```

---

## Notes

### Decisions Made

1. **DB bootstrap in `foundation.ts`** — Table created via `try/catch db.exec()` inside `foundation.ts` (same pattern as `db.ts` inline migrations). Also added to `schema.sql` for documentation.

2. **`setFoundationBroadcast` pattern** — Matches `caseBus` pattern in `server.ts`. Called after `wss.on("connection", ...)`. Mounted at `app.route("/api/foundation", foundationApp)`.

3. **WebSocket pin** — Reads `localStorage.getItem("dashboard_pin")` (passes as `?pin=` query param). Same as monitor page pattern.

4. **Fire-and-forget pipeline** — `runFoundationPipeline()` called without `await`. Errors caught internally, broadcast as `agent_event` with `status: "error"`.

5. **`run_complete` resets cards after 2s** — `setTimeout(..., 2000)` resets all agent states to `idle`.

6. **No new dependencies** — Zero new packages. Only `hono`, `better-sqlite3`, `node:crypto`, React hooks.

### Files Written / Updated

| File | Action |
|---|---|
| `daemon/src/foundation.ts` | ✅ Created (new) |
| `web/app/foundation/page.tsx` | ✅ Created (new) |
| `web/components/NavSwitch.tsx` | ✅ Updated (added foundation tab) |
| `daemon/src/server.ts` | ✅ Updated (import + mount + broadcast) |
| `daemon/src/schema.sql` | ✅ Updated (foundation_runs table #16) |
