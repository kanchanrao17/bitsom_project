"""
Pulls structured signals (risk flags, hedging language, sentiment) out of
company disclosures.  In mock mode we do it with keyword matching; swap
MOCK_LLM=0 to wire up a real LLM instead.
"""

import os
import re
from disclosure_snippets import DISCLOSURE_SNIPPETS


def extract_signals(snippet: str) -> dict:
    """Return risk_flags, hedging_detected, and sentiment for a single snippet."""
    mock_llm = os.environ.get("MOCK_LLM", "1")

    if mock_llm != "0":
        return _mock_extract(snippet)
    else:
        # placeholder for a real LLM call
        return _mock_extract(snippet)


def _mock_extract(snippet: str) -> dict:
    """Quick-and-dirty keyword scan — good enough for the demo."""
    text_lower = snippet.lower()
    risk_flags = []
    hedging_detected = False

    # look for the usual red-flag keywords
    if "litigation" in text_lower:
        risk_flags.append("litigation risk")

    # regulatory trouble
    if "regulatory" in text_lower or "regulator" in text_lower:
        risk_flags.append("regulatory risk")

    # revenue concentration
    if re.search(r"(top\s+\w+\s+customers?|customer\s+concentration)", text_lower):
        risk_flags.append("customer concentration risk")

    # management downplaying exposure
    if "exposure" in text_lower and "not material" in text_lower:
        risk_flags.append("potential exposure (management view: not material)")

    # hedging language ("assuming", "cautiously", etc.)
    hedging_phrases = ["assuming", "cautiously", "visibility"]
    for phrase in hedging_phrases:
        if phrase in text_lower:
            hedging_detected = True
            break

    # simple sentiment bucketing
    if "confident" in text_lower or "approved" in text_lower:
        sentiment = "confident"
    elif hedging_detected:
        sentiment = "cautious"
    else:
        sentiment = "neutral"

    return {
        "risk_flags": risk_flags,
        "hedging_detected": hedging_detected,
        "sentiment": sentiment,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("  DISCLOSURE SIGNAL EXTRACTION")
    print(f"  MOCK_LLM={os.environ.get('MOCK_LLM', '1')} (default=1, mock mode)")
    print("=" * 70)

    for i, snippet in enumerate(DISCLOSURE_SNIPPETS):
        doc_id = f"doc_{i+1:02d}"
        result = extract_signals(snippet)
        print(f"\n--- {doc_id} ---")
        print(f"  Snippet: {snippet[:80]}...")
        print(f"  Risk Flags:       {result['risk_flags']}")
        print(f"  Hedging Detected: {result['hedging_detected']}")
        print(f"  Sentiment:        {result['sentiment']}")
