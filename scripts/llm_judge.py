"""Optional LLM judge entry point; never fabricates unavailable scores."""

import json
import os
from pathlib import Path


def main() -> None:
    output = Path("evaluation/results/llm_judge.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    if not os.getenv("OPENAI_API_KEY"):
        result = {
            "status": "unavailable",
            "reason": "OPENAI_API_KEY is not set; no LLM judge scores were generated.",
        }
    else:
        result = {
            "status": "not_run",
            "reason": "An API adapter must be configured before making external requests.",
        }
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()