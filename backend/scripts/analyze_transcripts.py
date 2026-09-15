"""
Runs every call transcript in data/calls.json through the Claude-powered
analysis pipeline (app.services.llm_client.analyze_transcript) and writes
sentiment_score, complexity_score, and escalation_risk_flag back into the
dataset.

Resumable: records that already have a sentiment_score are skipped unless
--force is passed. Writes the file back to disk after every record so an
interruption doesn't lose progress.

Usage:
    python backend/scripts/analyze_transcripts.py [--limit N] [--force]
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

import anthropic

from app.models import TranscriptTurn
from app.services.llm_client import LLMNotConfiguredError, LLMResponseError, analyze_transcript

DATA_PATH = BACKEND_DIR / "data" / "calls.json"
MAX_RETRIES = 3


def analyze_with_retry(transcript, call_reason, escalated):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return analyze_transcript(transcript, call_reason, escalated)
        except anthropic.RateLimitError as exc:
            last_error = exc
            wait = 10 * attempt
            print(f"    rate limited, waiting {wait}s (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait)
        except (anthropic.APIConnectionError, anthropic.APIStatusError, LLMResponseError) as exc:
            last_error = exc
            wait = 2 * attempt
            print(f"    error: {exc} — retrying in {wait}s (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait)
    raise last_error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N pending calls")
    parser.add_argument("--force", action="store_true", help="Re-analyze calls that already have scores")
    args = parser.parse_args()

    with open(DATA_PATH) as f:
        calls = json.load(f)

    pending = [c for c in calls if args.force or c["sentiment_score"] is None]
    if args.limit is not None:
        pending = pending[: args.limit]

    if not pending:
        print("Nothing to do — all calls already analyzed. Use --force to re-run.")
        return

    print(f"Analyzing {len(pending)} of {len(calls)} calls...")

    succeeded = 0
    failed = 0

    for i, call in enumerate(pending, start=1):
        transcript = [TranscriptTurn.model_validate(t) for t in call["transcript"]]
        print(f"[{i}/{len(pending)}] {call['call_id']} ({call['call_reason']})")

        try:
            result = analyze_with_retry(transcript, call["call_reason"], call["escalated_to_coordinator"])
        except Exception as exc:
            print(f"    FAILED after {MAX_RETRIES} attempts: {exc}")
            failed += 1
            continue

        call["sentiment_score"] = result.sentiment_score
        call["complexity_score"] = result.complexity_score
        call["escalation_risk_flag"] = result.escalation_risk_flag
        succeeded += 1
        print(
            f"    sentiment={result.sentiment_score:+.2f} "
            f"complexity={result.complexity_score:.1f} "
            f"risk={result.escalation_risk_flag}"
        )

        with open(DATA_PATH, "w") as f:
            json.dump(calls, f, indent=2)

    print(f"\nDone. {succeeded} succeeded, {failed} failed.")


if __name__ == "__main__":
    try:
        main()
    except LLMNotConfiguredError as exc:
        print(f"Not configured: {exc}")
        sys.exit(1)
