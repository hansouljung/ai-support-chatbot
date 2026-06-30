"""
evaluate.py
Runs the full test query set against the chatbot, scores each response, and writes
results to results/eval_results.csv plus a summary to results/eval_summary.json.

Scoring rubric (manual + automated hints):
- ACCURATE: answer correctly reflects the right KB entry's content
- PARTIALLY_ACCURATE: answer is in the right direction but missing/vague on details,
  or only answers one part of a multi-intent question
- INCORRECT: answer contradicts or misrepresents the KB content
- HALLUCINATED: answer states something not present in any KB entry as if it were fact
- APPROPRIATE_DEFLECTION: correctly says "I don't have information on that" for an
  out-of-scope or adversarial query (this is a PASS, not a failure)
- FAILED_DEFLECTION: should have deflected but instead guessed/answered anyway

This script auto-labels obvious cases (e.g. out_of_scope queries that got deflected)
and leaves a "needs_manual_review" flag for everything else, since real accuracy
grading requires a human reading the response against the source KB.
"""

import json
import csv
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from chatbot import SupportChatbot

TEST_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "test_queries.json")
RESULTS_CSV = os.path.join(os.path.dirname(__file__), "..", "results", "eval_results.csv")
RESULTS_SUMMARY = os.path.join(os.path.dirname(__file__), "..", "results", "eval_summary.json")

DEFLECTION_PHRASES = [
    "i don't have information on that",
    "i'm not able to help with that",
]


def is_deflection(answer_text):
    lower = answer_text.lower()
    return any(phrase in lower for phrase in DEFLECTION_PHRASES)


def auto_label(test_case, result):
    """Best-effort automatic labeling. Out-of-scope/adversarial cases can be
    checked automatically (did it deflect or not). Everything else needs a human
    to compare the answer against the actual KB content for accuracy."""
    qtype = test_case["type"]
    deflected = is_deflection(result["answer"])

    if qtype in ("out_of_scope", "adversarial"):
        return "APPROPRIATE_DEFLECTION" if deflected else "FAILED_DEFLECTION_NEEDS_REVIEW"

    if deflected:
        # straightforward/ambiguous/multi_intent questions SHOULD have been answerable
        return "FAILED_DEFLECTION_NEEDS_REVIEW"

    return "NEEDS_MANUAL_REVIEW"


def run_evaluation():
    with open(TEST_PATH, "r") as f:
        test_cases = json.load(f)

    bot = SupportChatbot()
    rows = []

    for tc in test_cases:
        print(f"Running {tc['id']} ({tc['type']}): {tc['query']}")
        result = bot.answer(tc["query"])
        label = auto_label(tc, result)

        rows.append({
            "test_id": tc["id"],
            "type": tc["type"],
            "query": tc["query"],
            "expected_kb": tc["expected_kb"],
            "retrieved_kb_ids": ";".join(result["retrieved_kb_ids"]),
            "retrieved_scores": ";".join(str(s) for s in result["retrieved_scores"]),
            "answer": result["answer"],
            "auto_label": label,
            "manual_label": "",  # fill in by hand after reading the answer
            "notes": tc["notes"],
        })

    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "total_queries": len(rows),
        "by_type": {},
        "auto_label_counts": {},
    }
    for row in rows:
        summary["by_type"].setdefault(row["type"], 0)
        summary["by_type"][row["type"]] += 1
        summary["auto_label_counts"].setdefault(row["auto_label"], 0)
        summary["auto_label_counts"][row["auto_label"]] += 1

    with open(RESULTS_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDone. Wrote {len(rows)} results to {RESULTS_CSV}")
    print(f"Summary: {json.dumps(summary, indent=2)}")
    print("\nNEXT STEP: open eval_results.csv and fill in 'manual_label' for each row")
    print("by reading the answer against the KB content. Use:")
    print("  ACCURATE / PARTIALLY_ACCURATE / INCORRECT / HALLUCINATED")
    print("(out_of_scope and adversarial rows are already auto-scored)")


if __name__ == "__main__":
    run_evaluation()
