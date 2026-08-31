# Part 3 — AI-Augmented FinTech Advisory & Blockchain Risk

## Overview
Lightweight AI-assisted advisory toolkit for Paytm Money: a portfolio-allocation agent (CAPM + variance), structured disclosure extraction, multi-agent debate demo, DCF valuation calculator, and a blockchain/crypto risk appendix.

**All outputs recorded with `MOCK_LLM=1` (default, fully deterministic mock mode, no API key required).**

## How to Run

```bash
cd ai_advisory_blockchain

# 1. Portfolio advisory agent (all 5 investor profiles)
python advisory_agent.py

# 2. Structured disclosure extraction (all 6 snippets)
python extract_disclosure.py

# 3. Multi-agent debate demo (PAYFIN)
python debate.py

# 4. DCF valuation calculator
python dcf_calculator.py
```

## Deliverables
- **stock_universe.py**, **investor_profiles.py**, **disclosure_snippets.py** — Seed data
- **advisory_agent.py** — Agentic Think-Act-Observe pattern with CAPM + portfolio variance
- **extract_disclosure.py** — Rule-based signal extraction (risk flags, hedging, sentiment)
- **debate.py** — 3-agent bull/bear/synthesizer debate
- **dcf_calculator.py** — 5-year FCFF projection, terminal value, 3×3 sensitivity table, EV/EBITDA cross-check
- **blockchain_risk_note.md** — Stablecoin/DAO risk, crypto allocation recommendation, T.A.N.G. analysis

## Agent Run Summary

| Investor | Risk Tolerance | Tickers                        | E(R)   | Std Dev | Escalated |
|----------|---------------|--------------------------------|--------|---------|-----------|
| INV01    | Conservative  | PAYBOND, PAYGOLD, PAYRETAIL    | 9.20%  | 8.44%   | NO        |
| INV02    | Moderate      | PAYRETAIL, PAYINFRA, PAYGOLD   | 11.30% | 12.57%  | NO        |
| INV03    | Aggressive    | PAYTECH, PAYFIN, PAYINFRA      | 15.00% | 20.58%  | YES       |
| INV04    | Moderate      | PAYRETAIL, PAYINFRA, PAYGOLD   | 11.30% | 12.57%  | NO        |
| INV05    | Aggressive    | PAYTECH, PAYFIN, PAYINFRA      | 15.00% | 20.58%  | YES       |

Conservative and Moderate investors do NOT escalate; Aggressive investors DO escalate (std dev 20.58% > 20% threshold).

## Disclosure Extraction Results

| Doc   | Risk Flags                                 | Hedging | Sentiment  |
|-------|--------------------------------------------|---------|------------|
| doc_01| (none)                                     | True    | cautious   |
| doc_02| litigation risk, potential exposure         | False   | neutral    |
| doc_03| customer concentration risk                | False   | neutral    |
| doc_04| (none)                                     | True    | cautious   |
| doc_05| (none)                                     | False   | confident  |
| doc_06| regulatory risk                            | False   | neutral    |

## DCF Sensitivity Table (Enterprise Value in Cr)

| WACC \ TG   | TG=3.00%      | TG=4.00%      | TG=5.00%      |
|-------------|---------------|---------------|---------------|
| WACC=10.77% | 5,849.2 Cr    | 6,527.9 Cr    | 7,441.9 Cr    |
| WACC=11.77% | 5,153.5 Cr    | 5,659.0 Cr    | 6,313.7 Cr    |
| WACC=12.77% | 4,601.2 Cr    | 4,989.1 Cr    | 5,476.9 Cr    |

**Self-check:** WACC exceeds terminal growth in all 9 cells (worst-case gap: 5.77%). Terminal growth (4%) is 7.77pp below base-case WACC (11.77%), satisfying the ≥3pp constraint.

## Design Decisions

### Advisory Agent (Part A)
- Allocation follows the **prescribed lookup table exactly** (Conservative/Moderate/Aggressive → specific ticker sets, equal-weight 1/3 each).
- CAPM expected return uses **only beta** (never `analyst_expected_return`).
- Portfolio variance uses `Var(R_p) = Σ wᵢ²σᵢ² + 2·Σ wᵢwⱼ·ρ·σᵢ·σⱼ` with ρ=0.3.
- Human-in-the-loop escalation fires at >20% portfolio std dev.
- Narrative sentence gated by `MOCK_LLM` environment variable.

### Disclosure Extraction (Part B)
- Mock mode uses keyword/regex matching: "litigation"/"regulatory"/"top...customers" → risk flags; "assuming"/"cautiously"/"visibility" → hedging; "confident"/"approved" → confident sentiment.

### Debate Demo (Part C)
- Chose **PAYFIN** (beta=1.35, std_dev=28%) as the debate ticker.
- Each agent's argument references actual numeric values from STOCK_UNIVERSE.

### DCF Calculator (Part D)
- **FCFF** = EBIT × (1−tax) + D&A − CapEx − ΔNWC = INR 305 Cr base.
- **WACC** = 11.77% (R_e=13.60% from PAYINFRA beta=1.10, after-tax R_d=7.50%, 70/30 E/D split).
- **Terminal growth** = 4.00% (7.77pp below WACC, satisfying ≥3pp constraint).
- **EV/EBITDA cross-check**: 15.0x multiple on INR 580 Cr EBITDA = INR 8,700 Cr vs. DCF's INR 5,659 Cr (−35% difference, reflecting DCF's more conservative explicit growth assumptions).
