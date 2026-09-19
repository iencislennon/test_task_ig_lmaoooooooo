"""CLI entry point for research_agent, meant to be invoked as a subprocess
(e.g. from a Java backend) and produce a single JSON object on stdout.

Usage:
    python -m research_agent.cli "find a github project for parsing pdf files in python"
    python -m research_agent.cli "vector databases" --top-k 3 --model Qwen/Qwen2.5-0.5B-Instruct

On success, prints the ResearchResult JSON (see agent.ResearchResult.to_dict) to
stdout and exits 0. On failure, prints {"error": "..."} to stdout and exits 1,
so callers can always parse stdout as JSON regardless of outcome.
"""

from __future__ import annotations

import argparse
import json
import sys

from .agent import ResearchAgent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GitHub research agent (JSON output)")
    parser.add_argument("query", help="Natural-language research request")
    parser.add_argument("--top-k", type=int, default=5, help="Max candidate repos to consider")
    parser.add_argument("--model", default=None, help="Override the default HF model name")
    args = parser.parse_args(argv)

    try:
        agent = ResearchAgent(model_name=args.model, top_k=args.top_k)
        result = agent.research(args.query)
    except Exception as exc:  # noqa: BLE001 - surface any failure as JSON, not a traceback
        print(json.dumps({"error": str(exc)}))
        return 1

    print(result.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
