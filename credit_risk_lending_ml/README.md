# Part 2 — Credit Risk & Lending ML

## Overview
End-to-end credit risk ML pipeline for Paytm Postpaid: EDA, preprocessing with thin-file handling, Logistic Regression and Decision Tree classifiers, risk-based pricing, Isolation Forest anomaly detection, bias-awareness analysis, and deployment recommendation.

## How to Run

```bash
cd credit_risk_lending_ml

# 1. Generate seed data (must run from this directory)
python generate_data.py

# 2. Run the full ML pipeline
python credit_risk_pipeline.py
```

## Key Results

### Dataset Statistics
- **400 applicants**, measured default rate: **20.25%** (within 15-25% range)
- **80 rows (20%)** with missing `credit_bureau_score` (thin-file applicants)
- **265 transaction-behaviour rows** with 15 seeded anomalies

### Model Comparison Table

| Model               | Accuracy | Precision | Recall | F1     | AUC    |
|---------------------|----------|-----------|--------|--------|--------|
| Logistic Regression | 0.7600   | 0.3889    | 0.3500 | 0.3684 | 0.7188 |
| Decision Tree       | 0.6500   | 0.2222    | 0.3000 | 0.2553 | 0.5188 |
| Isolation Forest    | N/A      | N/A       | 0.7333 | N/A    | N/A    |

### Risk-Based Pricing Table

| Risk Tier            | Count | Observed Default Rate | Predicted Prob Range | Interest Rate |
|----------------------|-------|-----------------------|----------------------|---------------|
| Tier 1 (Low Risk)    | 25    | 8.0%                  | 0.5% – 3.6%         | 10.0% – 12.0% |
| Tier 2 (Moderate)    | 25    | 12.0%                 | 3.6% – 14.6%        | 12.0% – 15.0% |
| Tier 3 (Elevated)    | 25    | 20.0%                 | 15.2% – 34.3%       | 15.0% – 20.0% |
| Tier 4 (High Risk)   | 25    | 40.0%                 | 35.9% – 94.6%       | 20.0% – 28.0% |

**Monotonicity check: PASS** (8% → 12% → 20% → 40%)

### Isolation Forest Recall
- Contamination rate: 5.66% (15/265)
- **11 out of 15** seeded BTXNA* anomalies correctly flagged
- **Recall: 73.3%**

## Design Decisions

### Thin-File Handling Strategy
1. **`is_thin_file` flag** engineered directly from raw data (1 where `credit_bureau_score` is NaN, 0 otherwise) — safe before split since it's a direct missing-indicator, not a fitted statistic.
2. **Train/test split** (75/25, `random_state=42`, stratified on `default`) — stratification ensures both splits maintain the ~20% default rate, preventing evaluation bias.
3. **Median imputation**: Computed `median(credit_bureau_score)` = 612.0 from **training data only**, applied to fill NaN in both splits. This mirrors the StandardScaler fit-on-train rule and avoids leaking test-set information. Using median (not mean) is robust to the score distribution's skew.
4. **One-hot encoding** for `employment_type` (nominal, no ordinal relationship; `drop_first=True`).
5. **StandardScaler** fit on training split only.

No rows were dropped — every thin-file applicant is preserved, which is critical since these are the exact new-to-credit population Paytm Postpaid aims to serve via alternate data signals (UPI inflow, bounced payments).

### Deployment Recommendation
For Paytm Postpaid credit decisioning, I recommend deploying the **Logistic Regression** model. It achieves an AUC of 0.719 compared to the Decision Tree's 0.519, indicating superior discriminative ability across all probability thresholds. The Logistic Regression's F1 score of 0.368 vs 0.255 shows it better balances precision and recall — critical for a lending product where both false approvals (missed defaults, causing losses) and false declines (rejected good applicants, causing revenue loss) carry real costs. Additionally, Logistic Regression outputs well-calibrated probabilities, enabling the risk-based pricing tiers demonstrated above, and its linear decision boundary is inherently more interpretable for regulatory compliance and model governance reviews.

## Bias-Awareness Note (200-400 words)

Even though this dataset contains no explicit gender, caste, religion, or geographic location fields, several features could act as **correlated proxies for protected attributes** in a real deployment:

**`employment_type`** is a strong proxy for gender and socioeconomic background. In India, women are disproportionately represented in "gig" and informal self-employment categories, while "salaried" status correlates with formal-sector employment that skews male and urban. A model that penalizes gig workers or self-employed applicants would therefore have a disparate impact on women and rural populations, even without explicitly using gender as an input.

**`monthly_income_inr`** correlates with caste, religion, and geographic location due to India's persistent structural inequalities. Lower-income applicants are disproportionately from historically marginalized communities. Using income as a strong negative signal effectively encodes these structural disparities into credit decisions, perpetuating a cycle where disadvantaged groups face higher borrowing costs or outright denial.

**`credit_bureau_score`** is perhaps the most insidious proxy. Bureau scores are unavailable for 20% of our applicants (thin-file). In India, thin-file status correlates strongly with age (younger applicants), gender (women with no formal credit history), and rurality. If the model treats imputed scores differently from genuine scores — or if the imputation value itself is biased — this creates a systematic disadvantage for exactly the populations alternate-data lending claims to serve.

**Recommended governance step:** Before deploying this model, I recommend implementing a **maker-checker human-in-the-loop review** specifically for declined thin-file applicants (those with `is_thin_file = 1` who are predicted as high default risk). A credit analyst should manually review the applicant's alternate data signals — UPI inflow patterns, bounced payment history, and employment stability — before a final decline decision is issued. This review should be logged and auditable, with periodic fairness audits comparing approval rates across employment types and income brackets to detect emerging disparate impact. Additionally, the model's feature importance weights should be monitored quarterly for drift that could amplify proxy discrimination.
