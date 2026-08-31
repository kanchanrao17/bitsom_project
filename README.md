# Paytm FinTech Analytics & AI Platform

**Capstone Project — Executive Certification in FinTech & Artificial Intelligence**

A single, coherent analytics platform spanning three Paytm verticals: Payments (UPI/wallet/QR fraud analytics), Postpaid/Lending (credit-risk ML pipeline), and Money/Wealth (AI-augmented advisory with blockchain risk appendix).

## Repository Structure

```
bitsom/
├── README.md                          # This file
├── requirements.txt                   # Consolidated Python dependencies
├── payments_fraud_analytics/          # Part 1 (35 marks)
│   ├── README.md
│   ├── generate_data.py               # Seed data generator (seed=42)
│   ├── merchants.csv, users.csv, ledger.csv, gateway_export.csv
│   ├── merchant_workbook.xlsx         # VLOOKUP/HLOOKUP/IF-AND/Pivot
│   ├── sql_fraud_detection.py         # SQLite DB + 7 SQL queries
│   ├── paytm_payments.db             # SQLite database
│   ├── sql_query_outputs.md          # Query results
│   ├── reconcile.py                   # Reconciliation engine
│   ├── dashboard.py                   # Four-layer dashboard
│   ├── dashboard_interpretations.md
│   ├── create_workbook.py             # Excel workbook generator
│   └── charts/                        # Saved chart images
├── credit_risk_lending_ml/            # Part 2 (40 marks)
│   ├── README.md
│   ├── generate_data.py               # Seed data generator (seed=42)
│   ├── credit_applicants.csv, txn_behaviour.csv
│   ├── credit_risk_pipeline.py        # Full ML pipeline
│   └── charts/                        # ROC curves etc.
└── ai_advisory_blockchain/            # Part 3 (25 marks)
    ├── README.md
    ├── stock_universe.py, investor_profiles.py, disclosure_snippets.py
    ├── advisory_agent.py              # Agentic Think-Act-Observe
    ├── extract_disclosure.py          # Structured signal extraction
    ├── debate.py                      # 3-agent debate demo
    ├── dcf_calculator.py              # DCF + sensitivity table
    └── blockchain_risk_note.md        # Blockchain/crypto risk appendix
```

## Setup

### Prerequisites
- Python 3.9+
- pip

### Installation
One consolidated `requirements.txt` at the repository root:

```bash
pip install -r requirements.txt
```

Required packages: `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `openpyxl`

## How to Run Each Part

### Part 1 — Payments & Fraud Analytics

```bash
cd payments_fraud_analytics
python generate_data.py          # Generate seed CSVs
python sql_fraud_detection.py    # Create SQLite DB + run queries
python reconcile.py              # Run reconciliation engine
python dashboard.py              # Generate dashboard charts
python create_workbook.py        # Generate Excel workbook
```

### Part 2 — Credit Risk & Lending ML

```bash
cd credit_risk_lending_ml
python generate_data.py          # Generate seed CSVs
python credit_risk_pipeline.py   # Run full ML pipeline
```

### Part 3 — AI Advisory & Blockchain

```bash
cd ai_advisory_blockchain
python advisory_agent.py         # Run portfolio advisory agent
python extract_disclosure.py     # Run disclosure extraction
python debate.py                 # Run multi-agent debate
python dcf_calculator.py         # Run DCF valuation
```

All Part 3 scripts run with `MOCK_LLM=1` (default) — fully deterministic, no API key needed.

## Design Decisions Summary

### Part 1 — Payments & Fraud Analytics
- **Seed data**: 547-row ledger (500 baseline + 15 burner-account chargebacks + 32 velocity-attack rows), 40 merchants, 365 users.
- **Excel workbook**: VLOOKUP with `$`-locked range + `IFERROR`; HLOOKUP on a horizontal MDR fee-tier table (UPI=0%, Wallet=0.5%, Card=1.8%, Netbanking=1.2%); nested IF/AND classification with INR 500 per-txn cutoff + East-region exclusion; pivot table with count-vs-unique-days comparison.
- **SQL**: 7 queries covering all required clauses; burner-account query surfaces all 15 seeded rows; velocity-attack query surfaces all 8 seeded clusters.
- **Reconciliation**: Set operations + pd.merge; results consistent with ~5%/~3%/~2%/~2% injection rates.
- **Dashboard**: Four layers (scorecards, trends, breakdown, details table as saved image). `match_rate` and `chargeback_ratio` use the exact definitions from the brief.

### Part 2 — Credit Risk & Lending ML
- **Default rate**: 20.25% (within 15-25% range), 80 thin-file applicants.
- **Preprocessing order**: (1) `is_thin_file` flag from raw data → (2) stratified train/test split (75/25, `random_state=42`) → (3) median imputation from train only (median=612.0) → (4) one-hot encoding of `employment_type` → (5) StandardScaler fit on train only.
- **Logistic Regression** (AUC=0.719, F1=0.368) outperforms **Decision Tree** (AUC=0.519, F1=0.255) — recommended for deployment due to better discrimination, calibrated probabilities, and interpretability.
- **Risk pricing**: 4 tiers with monotonically increasing default rates (8% → 12% → 20% → 40%).
- **Isolation Forest**: 73.3% recall on seeded anomalies (11/15 flagged).
- **Bias note**: `employment_type` as gender proxy, `monthly_income_inr` as socioeconomic proxy, `credit_bureau_score` absence as rurality/age proxy; recommends maker-checker human review for declined thin-file applicants.

### Part 3 — AI Advisory & Blockchain
- **Advisory agent**: Prescribed allocation lookup, CAPM from beta only, ρ=0.3 pairwise correlation, >20% std dev escalation. Conservative (~8.44%) and Moderate (~12.57%) don't escalate; Aggressive (~20.58%) escalates.
- **Disclosure extraction**: Keyword/regex mock rules correctly flag doc_02 (litigation), doc_01/doc_04 (hedging), doc_05 (confident).
- **Debate**: PAYFIN ticker, template-based arguments referencing actual beta/std_dev/CAPM values.
- **DCF**: WACC=11.77% (PAYINFRA beta), terminal growth=4.00% (7.77pp gap), 3×3 sensitivity table with WACC>TG in all 9 cells. EV/EBITDA cross-check at 15x.
- **Blockchain note**: Fiat-collateralized vs algorithmic stablecoin distinction, DAO governance risks, zero crypto allocation recommendation, T.A.N.G. analysis (Authority + Greed vectors with bank-side defenses).

## All Monetary Figures
All figures throughout this project are in **Indian Rupees (INR)**.
