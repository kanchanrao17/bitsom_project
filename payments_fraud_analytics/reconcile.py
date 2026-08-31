"""
Reconciliation logic for matching our internal ledger against what the
payment gateway says happened.  Catches the four kinds of mismatch we
care about: missing txns on either side, amount diffs, and status diffs.
"""

import pandas as pd
import os


def reconcile_payments(ledger_df, gateway_df):
    """
    Takes our ledger and the gateway export, returns four DataFrames:
      1. missing_in_gateway  -- we recorded it, gateway didn't
      2. missing_in_ledger   -- gateway has it, we don't (suspicious extras)
      3. amount_mismatches   -- both have the txn but disagree on the amount
      4. status_mismatches   -- both have the txn but disagree on the status
    """
    ledger_ids = set(ledger_df["transaction_id"])
    gateway_ids = set(gateway_df["transaction_id"])

    # txns we have but the gateway doesn't
    missing_in_gw_ids = ledger_ids - gateway_ids
    missing_in_gateway = ledger_df[ledger_df["transaction_id"].isin(missing_in_gw_ids)].copy()

    # txns the gateway has that we don't -- could be phantom/duplicate
    missing_in_ledger_ids = gateway_ids - ledger_ids
    missing_in_ledger = gateway_df[gateway_df["transaction_id"].isin(missing_in_ledger_ids)].copy()

    # for txns both sides agree exist, check field-by-field
    common_ids = ledger_ids & gateway_ids
    ledger_common = ledger_df[ledger_df["transaction_id"].isin(common_ids)].copy()
    gateway_common = gateway_df[gateway_df["transaction_id"].isin(common_ids)].copy()

    merged = pd.merge(
        ledger_common[["transaction_id", "amount_inr", "status"]],
        gateway_common[["transaction_id", "amount_inr", "status"]],
        on="transaction_id",
        suffixes=("_ledger", "_gateway")
    )

    # amounts don't line up
    amount_mask = merged["amount_inr_ledger"] != merged["amount_inr_gateway"]
    amount_mismatches = merged[amount_mask].copy()
    amount_mismatches["amount_difference"] = (
        amount_mismatches["amount_inr_gateway"] - amount_mismatches["amount_inr_ledger"]
    )

    # status doesn't line up
    status_mask = merged["status_ledger"] != merged["status_gateway"]
    status_mismatches = merged[status_mask].copy()

    return missing_in_gateway, missing_in_ledger, amount_mismatches, status_mismatches


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ledger = pd.read_csv(os.path.join(base_dir, "ledger.csv"))
    gateway = pd.read_csv(os.path.join(base_dir, "gateway_export.csv"))

    missing_gw, missing_ledger, amt_mm, status_mm = reconcile_payments(ledger, gateway)

    n_ledger = len(ledger)
    print("=" * 60)
    print("  Payment Reconciliation Report")
    print("=" * 60)
    print(f"\nLedger transactions:          {n_ledger}")
    print(f"Gateway transactions:         {len(gateway)}")
    print()
    print(f"1. Missing in gateway:        {len(missing_gw):>4}  "
          f"(~{len(missing_gw)/n_ledger*100:.1f}% of ledger, expected ~5%)")
    print(f"2. Extra in gateway (missing   {len(missing_ledger):>4}  "
          f"(~{len(missing_ledger)/n_ledger*100:.1f}% of ledger, expected ~2%)")
    print(f"   in ledger):")
    print(f"3. Amount mismatches:         {len(amt_mm):>4}  "
          f"(~{len(amt_mm)/n_ledger*100:.1f}% of ledger, expected ~3%)")
    print(f"4. Status mismatches:         {len(status_mm):>4}  "
          f"(~{len(status_mm)/n_ledger*100:.1f}% of ledger, expected ~2%)")

    print("\n--- Amount Mismatches Detail ---")
    print(amt_mm[["transaction_id", "amount_inr_ledger", "amount_inr_gateway",
                   "amount_difference"]].to_string(index=False))

    print("\n--- Status Mismatches Detail ---")
    print(status_mm[["transaction_id", "status_ledger", "status_gateway"]].to_string(index=False))
