#!/usr/bin/env python3
"""
Antigravity SDK Worker — TCC Agent Wrapper
Usage: antigravity_worker.py -p "prompt" [--model gemini-2.5-flash] [--system "..."] [--json]
SDK: google-antigravity v0.1.2 (from google.antigravity import Agent, LocalAgentConfig)
Key: GEMINI_API_KEY from ~/.mempalace/cloud.env
Note: import is 'from google.antigravity' NOT 'from antigravity' (Python Easter egg conflict)
"""

import argparse
import asyncio
import json
import os
import sys
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


async def call_antigravity(
    prompt: str,
    system: str = "",
    model: str = "gemini-2.5-flash",
    api_key: str = "",
) -> dict:
    from google.antigravity import Agent, LocalAgentConfig

    config = LocalAgentConfig(
        api_key=api_key,
        model=model,
        system_instructions=system if system else None,
    )

    async with Agent(config=config) as agent:
        resp = await agent.chat(prompt)
        chunks = await resp.resolve()

    text_parts = []
    thought_parts = []
    for chunk in chunks:
        name = type(chunk).__name__
        if name == "Text":
            text_parts.append(chunk.text)
        elif name == "Thought":
            thought_parts.append(chunk.text)

    return {
        "text": "".join(text_parts),
        "thoughts": "".join(thought_parts),
        "model": model,
    }


def main():
    parser = argparse.ArgumentParser(description="Antigravity SDK Worker for TCC")
    parser.add_argument("-p", "--prompt", required=True, help="Prompt to send")
    parser.add_argument("--system", default="", help="System prompt")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Model (default: gemini-2.5-flash)")
    parser.add_argument("--json", action="store_true", dest="raw_json", help="Output raw JSON")
    args = parser.parse_args()

    env = load_env()
    api_key = env.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in ~/.mempalace/cloud.env", file=sys.stderr)
        sys.exit(1)

    try:
        result = asyncio.run(call_antigravity(
            prompt=args.prompt,
            system=args.system,
            model=args.model,
            api_key=api_key,
        ))
        if args.raw_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["text"])
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
