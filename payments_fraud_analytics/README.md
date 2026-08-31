# Part 1 — Payments & Fraud Analytics

## Overview
This module implements Paytm's payments operations analytics: merchant data workbench (Excel), SQL fraud-pattern detection, payment reconciliation engine, and a four-layer analytics dashboard.

## How to Run

```bash
cd payments_fraud_analytics

# 1. Generate seed data (must run from this directory)
python generate_data.py

# 2. Build SQLite database and run fraud queries
python sql_fraud_detection.py

# 3. Run payment reconciliation
python reconcile.py

# 4. Generate dashboard charts
python dashboard.py

# 5. Generate Excel workbook
python create_workbook.py
```

## Deliverables
- **generate_data.py** + `merchants.csv`, `users.csv`, `ledger.csv`, `gateway_export.csv`
- **merchant_workbook.xlsx** — VLOOKUP, HLOOKUP, nested IF/AND, pivot table
- **paytm_payments.db** — SQLite database with PK/FK schema
- **sql_fraud_detection.py** + `sql_query_outputs.md` — 7 SQL queries with full output
- **reconcile.py** — Reconciliation engine with four discrepancy categories
- **dashboard.py** + `charts/` — Four-layer dashboard with saved chart images
- **dashboard_interpretations.md** — Written interpretations for each layer

## Design Decisions

### Excel Workbook (Part A)
- **VLOOKUP**: Fixed range `Merchants!$A$2:$D$41` with `IFERROR` wrapping to show "Merchant not found" for unmatched IDs.
- **HLOOKUP**: Horizontal fee-tier table with illustrative MDR percentages: UPI=0.0%, Wallet=0.5%, Card=1.8%, Netbanking=1.2%.
- **Nested IF/AND Rule**: A transaction is labeled "High-Value Merchant Day" when `amount_inr > 500` AND `region ≠ "East"`. The INR 500 per-transaction cutoff serves as a row-level proxy for the INR 5,000 daily-total threshold (documented in the Pivot_Table sheet). Transactions with amount > 500 in the East region are labeled "High-Value East (Excluded)"; all others are "Standard".
- **Pivot Table**: Summarizes total amount and count by merchant × status; includes a count-vs-count-unique comparison (total transactions vs. unique days transacted) for the top 10 merchants.

### SQL Fraud Detection (Part B)
- 7 queries covering SELECT/WHERE/ORDER BY/LIMIT/DISTINCT, GROUP BY/HAVING, INNER JOIN (Q2, Q5), LEFT JOIN (Q4).
- **Burner accounts (Q5)**: `julianday(transaction_time) - julianday(signup_date) >= 0 AND < 30` with `status = 'chargeback'` → surfaces all 15 seeded rows.
- **Velocity attacks (Q6)**: 10-minute time-bucket grouping via `strftime` floor division → surfaces all 8 seeded clusters.

### Reconciliation (Part C)
- Uses set operations on `transaction_id` for missing/extra detection, and `pd.merge` for field-level comparison.
- Results: 27 missing in gateway (~4.9%), 10 extra in gateway (~1.8%), 16 amount mismatches (~2.9%), 9 status mismatches (~1.6%) — consistent with the ~5%/~3%/~2%/~2% injection rates.

### Dashboard (Part D)
- **Headline**: `match_rate` = txns in both files with identical amount AND status / total ledger count. `chargeback_ratio` = count-based, platform-wide.
- **Trends**: Dual-axis chart (bar=GMV, line=chargeback count) over 30 days.
- **Breakdown**: Horizontal bars for GMV by payment method and by merchant category.
- **Details**: Top 10 merchants table rendered as a saved PNG image with conditional highlighting for chargeback_ratio > 1%.
