# SPEC — colony_status.py

**Author:** Claude (Orchestrator/Planner, F08)
**Research input:** GEM (F07) — use `os.scandir` + `entry.is_file()` + `entry.stat().st_mtime`, convert via `datetime.fromtimestamp(ts).isoformat()`; must handle `FileNotFoundError` / `PermissionError`.

## Goal
A standard-library-only CLI utility that scans the Colony's `shared/` channels and reports per-channel activity.

## Function contract
```python
def scan_channels(base: str, channels: list[str] | None = None) -> dict:
    ...
```
- `base`: path to the `shared/` directory.
- `channels`: defaults to `["inbox", "results", "logs"]`.
- Returns an ordered dict, one key per channel:
  ```python
  {
    "inbox":   {"file_count": 0, "latest_mtime": None},
    "results": {"file_count": 3, "latest_mtime": "2026-06-17T12:00:00"},
    "logs":    {"file_count": 1, "latest_mtime": "2026-06-14T13:09:00"},
  }
  ```
- `file_count`: count of immediate **files only** (not subdirs) in the channel dir.
- `latest_mtime`: ISO-8601 string of the newest file mtime, or `None` if no files.
- Missing/inaccessible channel dir → `{"file_count": 0, "latest_mtime": None, "error": "<reason>"}` (do NOT raise).

## CLI
```
python colony_status.py [--base PATH] [--json]
```
- `--base`: default = directory containing this script (i.e. `shared/`).
- `--json`: emit raw JSON (indent=2, ensure_ascii=False). Default = human-readable table.
- Exit code 0 always (report tool, not a gate).

## Constraints
- **Standard library only.** No third-party imports.
- Python 3.9+ compatible.
- Include an inline self-test guarded by `if __name__ == "__main__"` is NOT enough — add a `_selftest()` runnable via `python colony_status.py --selftest` that creates a tempdir with known files and asserts counts/mtime ordering.

## Acceptance
1. `python colony_status.py --selftest` exits 0 and prints `SELFTEST OK`.
2. `python colony_status.py --base ../  --json` returns valid JSON for the 3 channels.
3. No exceptions on a missing channel dir.
