# AI Support Chatbot — Evaluation Project

A project simulating real-world AI self-service quality work: build a retrieval-grounded support chatbot, validate its responses against a structured test set, identify failure patterns, and translate findings into actionable recommendations.

## What This Project Does

This project mirrors the core workflow of AI self-service evaluation in a contact center context:

1. **Knowledge base** — 20 FAQ entries covering a fictional SaaS product (billing, account management, technical support, integrations, data privacy, and plans)
2. **Chatbot** — a RAG-style pipeline that retrieves relevant KB entries via TF-IDF cosine similarity, then passes them to Claude as grounded context with a strict system prompt preventing hallucination
3. **Test set** — 25 queries spanning 6 categories: straightforward, ambiguous, out-of-scope, multi-intent, and adversarial
4. **Evaluation harness** — runs all 25 queries against the live API, auto-labels out-of-scope and adversarial cases, and outputs a CSV for manual accuracy grading
5. **Findings report** — documents accuracy results, failure patterns, root cause analysis, and prioritized recommendations

## Key Results

- **78% accuracy** on answerable questions (14/18)
- **100% appropriate deflection** on out-of-scope and adversarial queries (7/7)
- **0% hallucination rate** across all 25 test cases
- **Primary failure pattern identified:** TF-IDF retrieval misses colloquial phrasing with low vocabulary overlap (e.g. "I want my money back" fails to retrieve the refund KB entry) — full analysis in [`results/findings.md`](results/findings.md)

## Project Structure

```
ai-support-chatbot/
├── data/
│   ├── knowledge_base.json     # 20 FAQ entries
│   └── test_queries.json       # 25 test cases with expected KB mappings
├── scripts/
│   ├── chatbot.py              # RAG chatbot (TF-IDF retrieval + Claude API)
│   └── evaluate.py             # Evaluation harness and auto-labeling
├── results/
│   ├── eval_results.csv        # Full graded results
│   └── findings.md             # Failure pattern analysis and recommendations
└── requirements.txt
```

## Setup & Usage

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"

# Run a single query
python scripts/chatbot.py "How do I reset my password?"

# Run the full evaluation
python scripts/evaluate.py
```

## Tech Stack

- **Python** — core scripting
- **scikit-learn** — TF-IDF vectorization and cosine similarity for retrieval
- **Anthropic Claude API** (claude-sonnet-4-6) — grounded answer generation
- **Excel / CSV** — manual response grading and results analysis

## Skills Demonstrated

- AI response validation and accuracy grading against a structured rubric
- Test case design across multiple difficulty categories (straightforward, ambiguous, adversarial)
- Root cause analysis of AI failure patterns (retrieval vs. generation layer)
- Knowledge base gap identification and self-service improvement recommendations
- RAG pipeline implementation with hallucination prevention via prompt grounding
