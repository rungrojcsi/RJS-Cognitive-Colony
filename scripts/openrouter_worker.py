#!/usr/bin/env python3
"""
OpenRouter API Worker — TCC Agent Wrapper
Usage: openrouter_worker.py -p "prompt" [--model gemini] [--system "..."] [--json] [--list-models]
API: OpenRouter (OpenAI-compatible endpoint)
Key: OPENROUTER_API_KEY from ~/.mempalace/cloud.env
Docs: https://openrouter.ai/docs

Model aliases (verified 2026-05-10):
  gemini          → google/gemini-2.5-flash-lite       $0.10/$0.40 per 1M  [DEFAULT]
  gemini-flash    → google/gemini-2.5-flash            $0.30/$2.50 per 1M
  gemini-pro      → google/gemini-2.5-pro              $1.25/$10.0 per 1M
  claude          → anthropic/claude-sonnet-4.5        $3.00/$15.0 per 1M
  claude-haiku    → anthropic/claude-haiku-4.5         $1.00/$5.00 per 1M
  grok            → x-ai/grok-3-mini                   $0.30/$0.50 per 1M
  grok-fast       → x-ai/grok-4-fast                   $0.20/$0.50 per 1M
  grok4           → x-ai/grok-4.20                     $1.25/$2.50 per 1M
  deepseek        → deepseek/deepseek-v4-flash         $0.14/$0.28 per 1M
  deepseek-pro    → deepseek/deepseek-v4-pro           $0.44/$0.87 per 1M
  mistral         → mistralai/mistral-small-3.2-24b    $0.08/$0.20 per 1M
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash-lite"

# Verified aliases — updated 2026-05-10
MODEL_ALIASES = {
    "gemini":        "google/gemini-2.5-flash-lite",
    "gemini-flash":  "google/gemini-2.5-flash",
    "gemini-pro":    "google/gemini-2.5-pro",
    "claude":        "anthropic/claude-sonnet-4.5",
    "claude-haiku":  "anthropic/claude-haiku-4.5",
    "grok":          "x-ai/grok-3-mini",
    "grok-fast":     "x-ai/grok-4-fast",
    "grok4":         "x-ai/grok-4.20",
    "deepseek":      "deepseek/deepseek-v4-flash",
    "deepseek-pro":  "deepseek/deepseek-v4-pro",
    "mistral":       "mistralai/mistral-small-3.2-24b-instruct",
}


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


def call_openrouter(
    prompt: str,
    system: str = "",
    model: str = DEFAULT_MODEL,
    api_key: str = "",
    site_url: str = "https://tcc.rojios.local",
    site_name: str = "The Cognitive Colony",
) -> dict:
    # Resolve model alias
    model = MODEL_ALIASES.get(model, model)

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
        OPENROUTER_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": site_url,
            "X-Title": site_name,
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def list_models():
    """Show available model aliases with pricing."""
    PRICING = {
        "gemini":       "$0.10/$0.40",
        "gemini-flash": "$0.30/$2.50",
        "gemini-pro":   "$1.25/$10.0",
        "claude":       "$3.00/$15.0",
        "claude-haiku": "$1.00/$5.00",
        "grok":         "$0.30/$0.50",
        "grok-fast":    "$0.20/$0.50",
        "grok4":        "$1.25/$2.50",
        "deepseek":     "$0.14/$0.28",
        "deepseek-pro": "$0.44/$0.87",
        "mistral":      "$0.08/$0.20",
    }
    print("Model aliases (use with --model) — price per 1M tokens in/out:")
    for alias, full_name in MODEL_ALIASES.items():
        price = PRICING.get(alias, "")
        marker = " ← default" if full_name == DEFAULT_MODEL else ""
        print(f"  {alias:<15} {price:<14} → {full_name}{marker}")
    print("\nOr pass any full OpenRouter model ID directly.")


def main():
    parser = argparse.ArgumentParser(description="OpenRouter API Worker for TCC")
    parser.add_argument("-p", "--prompt", help="Prompt to send")
    parser.add_argument("--system", default="", help="System prompt")
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Model alias or full ID (default: {DEFAULT_MODEL}). Use --list-models to see aliases."
    )
    parser.add_argument("--json", action="store_true", dest="raw_json", help="Output raw JSON")
    parser.add_argument("--list-models", action="store_true", help="List model aliases and exit")
    args = parser.parse_args()

    if args.list_models:
        list_models()
        return

    if not args.prompt:
        parser.error("-p/--prompt is required")

    env = load_env()
    api_key = env.get("OPENROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))
    if not api_key:
        print(
            "ERROR: OPENROUTER_API_KEY not found.\n"
            "Add it to ~/.mempalace/cloud.env:\n"
            "  OPENROUTER_API_KEY=sk-or-v1-...\n"
            "Get key at: https://openrouter.ai/keys",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result = call_openrouter(
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
