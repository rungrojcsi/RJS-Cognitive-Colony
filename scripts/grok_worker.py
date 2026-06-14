#!/usr/bin/env python3
"""
Grok API Worker — TCC Agent Wrapper
Usage: grok_worker.py -p "prompt" [--model grok-3-mini] [--system "..."] [--json]
API: xAI (OpenAI-compatible endpoint)
Key: GROK_API_KEY from ~/.mempalace/cloud.env
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def load_env(env_path: str = "~/.mempalace/cloud.env") -> dict:
    env = {}
    path = Path(env_path).expanduser()
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def call_grok(prompt: str, system: str = "", model: str = "grok-3-mini", api_key: str = "") -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }).encode()

    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def main():
    parser = argparse.ArgumentParser(description="Grok API Worker for TCC")
    parser.add_argument("-p", "--prompt", required=True, help="Prompt to send")
    parser.add_argument("--system", default="", help="System prompt")
    parser.add_argument("--model", default="grok-3-mini", help="Model (default: grok-3-mini)")
    parser.add_argument("--json", action="store_true", dest="raw_json", help="Output raw JSON")
    args = parser.parse_args()

    env = load_env()
    api_key = env.get("GROK_API_KEY", os.environ.get("GROK_API_KEY", ""))
    if not api_key:
        print("ERROR: GROK_API_KEY not found in ~/.mempalace/cloud.env", file=sys.stderr)
        sys.exit(1)

    try:
        result = call_grok(
            prompt=args.prompt,
            system=args.system,
            model=args.model,
            api_key=api_key,
        )
        if args.raw_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["choices"][0]["message"]["content"])
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
