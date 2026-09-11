"""Run a clean command-line AmazonHelp prediction."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agent import SupportAgent  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    args = parser.parse_args()
    retrieval_path = ROOT / "evaluation" / "retrieval_set.csv"
    training_path = ROOT / "evaluation" / "training_set.csv"
    human_training_path = ROOT / "evaluation" / "human_training_set.csv"
    if not retrieval_path.exists() or not training_path.exists():
        raise SystemExit("Run python scripts/prepare_data.py and python scripts/train_baselines.py first")
    result = SupportAgent.from_project_files(
        retrieval_path,
        training_path,
        human_training_path if SupportAgent.human_training_ready(human_training_path) else None,
    ).predict(args.text)
    print("INPUT\n" + result["input"])
    print("\nINTENT\n" + result["intent"])
    print(f"\nCONFIDENCE\n{result['confidence']:.2f}")
    print("\nRETRIEVED EVIDENCE")
    for evidence in result["evidence"]:
        print(f"- score={evidence.score:.3f} customer={evidence.customer_message}")
        print(f"  AmazonHelp={evidence.amazonhelp_response}")
    print("\nDRAFT REPLY\n" + result["draft_reply"])
    print("\nDECISION\n" + result["decision"])
    print("\nREASON\n" + result["reason"])


if __name__ == "__main__":
    main()