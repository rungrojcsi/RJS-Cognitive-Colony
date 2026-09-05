"""colony_status.py — Colony shared-channel activity reporter.

Spec: SPEC.md (Author: Claude F08 / Research: GEM F07)
Standard library only. Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path


DEFAULT_CHANNELS: list[str] = ["inbox", "results", "logs"]


def scan_channels(
    base: str,
    channels: list[str] | None = None,
) -> dict:
    """Scan Colony shared/ channels and return per-channel activity.

    Args:
        base: Path to the shared/ directory.
        channels: Channel names to scan. Defaults to ["inbox", "results", "logs"].

    Returns:
        Ordered dict keyed by channel name, each value a dict with:
            file_count  (int)        — number of immediate files (no subdirs)
            latest_mtime (str|None)  — ISO-8601 newest file mtime, or None
            error (str, optional)    — present when dir is missing/inaccessible
    """
    if channels is None:
        channels = DEFAULT_CHANNELS

    result: dict = {}

    for channel in channels:
        channel_path = os.path.join(base, channel)
        try:
            mtimes: list[float] = []
            with os.scandir(channel_path) as it:
                for entry in it:
                    if entry.is_file():
                        mtimes.append(entry.stat().st_mtime)

            file_count = len(mtimes)
            latest_mtime: str | None = None
            if mtimes:
                latest_mtime = datetime.fromtimestamp(max(mtimes)).isoformat()

            result[channel] = {
                "file_count": file_count,
                "latest_mtime": latest_mtime,
            }

        except OSError as exc:
            # FileNotFoundError, PermissionError, NotADirectoryError, and
            # stat() races all subclass OSError — report, never raise.
            result[channel] = {
                "file_count": 0,
                "latest_mtime": None,
                "error": str(exc),
            }

    return result


def _render_table(data: dict) -> str:
    """Render scan results as a human-readable table."""
    header = f"{'Channel':<16} {'Files':>6}  {'Latest mtime':<25}  {'Status'}"
    sep = "-" * len(header)
    rows = [header, sep]

    for channel, info in data.items():
        status = info.get("error", "OK")
        mtime_str = info.get("latest_mtime") or "-"
        rows.append(
            f"{channel:<16} {info['file_count']:>6}  {mtime_str:<25}  {status}"
        )

    return "\n".join(rows)


def _selftest() -> None:
    """Self-test: create a tmpdir with known files and assert correctness."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create channel dirs
        inbox_dir = os.path.join(tmpdir, "inbox")
        results_dir = os.path.join(tmpdir, "results")
        logs_dir = os.path.join(tmpdir, "logs")
        # "missing" channel intentionally not created

        os.makedirs(inbox_dir)
        os.makedirs(results_dir)
        os.makedirs(logs_dir)

        # inbox — 0 files (empty dir)
        # results — 3 files with controlled mtimes
        t_base = time.time()
        file_times: list[float] = []
        for i in range(3):
            fpath = os.path.join(results_dir, f"result_{i}.json")
            with open(fpath, "w") as f:
                f.write(f'{{"i": {i}}}')
            # Stagger mtimes so we can assert ordering
            t = t_base - (3 - i) * 10  # latest = t_base - 10
            os.utime(fpath, (t, t))
            file_times.append(t)

        latest_results_t = max(file_times)

        # logs — 1 file
        log_path = os.path.join(logs_dir, "run.log")
        with open(log_path, "w") as f:
            f.write("ok")
        t_log = t_base - 100
        os.utime(log_path, (t_log, t_log))

        # Also put a subdir inside results — must NOT be counted
        os.makedirs(os.path.join(results_dir, "subdir"))

        # Run scan with a missing channel ("missing")
        data = scan_channels(tmpdir, channels=["inbox", "results", "logs", "missing"])

        # --- Assertions ---
        assert data["inbox"]["file_count"] == 0, (
            f"inbox file_count expected 0, got {data['inbox']['file_count']}"
        )
        assert data["inbox"]["latest_mtime"] is None, (
            f"inbox latest_mtime expected None, got {data['inbox']['latest_mtime']}"
        )

        assert data["results"]["file_count"] == 3, (
            f"results file_count expected 3, got {data['results']['file_count']}"
        )
        expected_mtime = datetime.fromtimestamp(latest_results_t).isoformat()
        assert data["results"]["latest_mtime"] == expected_mtime, (
            f"results latest_mtime mismatch: "
            f"got {data['results']['latest_mtime']!r}, expected {expected_mtime!r}"
        )

        assert data["logs"]["file_count"] == 1, (
            f"logs file_count expected 1, got {data['logs']['file_count']}"
        )
        assert data["logs"]["latest_mtime"] is not None, "logs latest_mtime must not be None"

        assert "error" in data["missing"], "missing channel must have 'error' key"
        assert data["missing"]["file_count"] == 0
        assert data["missing"]["latest_mtime"] is None

    print("SELFTEST OK")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Colony shared-channel activity reporter."
    )
    parser.add_argument(
        "--base",
        default=str(Path(__file__).parent),
        help="Path to the shared/ directory (default: directory of this script).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit raw JSON output instead of human-readable table.",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run inline self-test and exit.",
    )
    args = parser.parse_args()

    if args.selftest:
        _selftest()
        sys.exit(0)

    data = scan_channels(args.base)

    if args.as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(_render_table(data))

    sys.exit(0)


if __name__ == "__main__":
    main()
