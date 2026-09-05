#!/opt/homebrew/bin/python3
"""
Antigravity SDK Worker — TCC Agent Wrapper
Usage: antigravity_worker.py -p "prompt" [--model gemini-2.5-flash] [--system "..."] [--json]
SDK: google-antigravity v0.1.2 (from google.antigravity import Agent, LocalAgentConfig)
Key: GEMINI_API_KEY from ~/.mempalace/cloud.env
Note: import is 'from google.antigravity' NOT 'from antigravity' (Python Easter egg conflict)
Interpreter: pinned to /opt/homebrew/bin/python3 (py3.14) — the only interpreter with
  google-antigravity installed. Plain `python3` raises ModuleNotFoundError. If invoked as
  `python3 antigravity_worker.py` the caller must use that interpreter explicitly.
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

    usage_obj = None
    async with Agent(config=config) as agent:
        resp = await agent.chat(prompt)
        chunks = await resp.resolve()
        # Best-effort: the SDK may expose token usage on the response object.
        # (Field name unconfirmed — Gem research was rate-limited; we probe a few.)
        for attr in ("usage", "usage_metadata", "token_usage"):
            usage_obj = getattr(resp, attr, None)
            if usage_obj is not None:
                break

    text_parts = []
    thought_parts = []
    for chunk in chunks:
        name = type(chunk).__name__
        if name == "Text":
            text_parts.append(chunk.text)
        elif name == "Thought":
            thought_parts.append(chunk.text)
        elif usage_obj is None and ("Usage" in name or "Metadata" in name):
            usage_obj = chunk

    def _pick(obj, *names):
        for n in names:
            v = getattr(obj, n, None)
            if isinstance(v, int):
                return v
        return None

    text = "".join(text_parts)
    tokens_in = _pick(usage_obj, "input_tokens", "prompt_tokens", "prompt_token_count") if usage_obj else None
    tokens_out = _pick(usage_obj, "output_tokens", "candidates_token_count", "completion_tokens") if usage_obj else None
    # Fallback when the SDK exposes no usage: rough char/4 estimate (approximate).
    if tokens_in is None and tokens_out is None:
        tokens_in = max(1, len(prompt) // 4)
        tokens_out = max(1, len(text) // 4)

    return {
        "text": text,
        "thoughts": "".join(thought_parts),
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
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

    # Best-effort Colony cost-ledger logging (Gem). Never break the call.
    def _log(tokens_in, tokens_out, ok):
        try:
            from cost_ledger import log_usage
            log_usage(
                agent="gem", engine="antigravity-sdk", model=args.model,
                task=os.environ.get("TCC_LEDGER_TASK", args.prompt[:80]),
                tokens_in=tokens_in, tokens_out=tokens_out,
                session_id=os.environ.get("TCC_SESSION_ID"), ok=ok,
            )
        except Exception:
            pass

    try:
        result = asyncio.run(call_antigravity(
            prompt=args.prompt,
            system=args.system,
            model=args.model,
            api_key=api_key,
        ))
        _log(result.get("tokens_in"), result.get("tokens_out"), True)
        if args.raw_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result["text"])
    except Exception as e:
        _log(None, None, False)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
