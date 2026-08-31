"""
Builds the four-layer executive dashboard (scorecards, trends, breakdown,
merchant details) and saves each chart as a PNG.  Interpretations get
written to a separate markdown file.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
from reconcile import reconcile_payments

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)


def load_data():
    ledger = pd.read_csv(os.path.join(BASE_DIR, "ledger.csv"), parse_dates=["transaction_time"])
    gateway = pd.read_csv(os.path.join(BASE_DIR, "gateway_export.csv"), parse_dates=["transaction_time"])
    merchants = pd.read_csv(os.path.join(BASE_DIR, "merchants.csv"))
    return ledger, gateway, merchants


def compute_match_rate(ledger, gateway):
    """Fraction of ledger txns that appear in the gateway with the same amount AND status."""
    merged = pd.merge(
        ledger[["transaction_id", "amount_inr", "status"]],
        gateway[["transaction_id", "amount_inr", "status"]],
        on="transaction_id",
        suffixes=("_l", "_g"),
        how="inner"
    )
    matched = ((merged["amount_inr_l"] == merged["amount_inr_g"]) &
               (merged["status_l"] == merged["status_g"])).sum()
    return matched / len(ledger)


# --- Layer 1: the big numbers at a glance ---
def layer1_scorecards(ledger, gateway):
    """Creates the headline scorecards for the dashboard."""
    total_gmv = ledger["amount_inr"].sum()
    success_rate = (ledger["status"] == "captured").sum() / len(ledger) * 100
    match_rate = compute_match_rate(ledger, gateway) * 100
    chargeback_ratio = (ledger["status"] == "chargeback").sum() / len(ledger) * 100

    labels = ["Total GMV (INR)", "Success Rate", "Recon Match Rate", "Chargeback Ratio"]
    values = [f"₹{total_gmv:,.0f}", f"{success_rate:.1f}%", f"{match_rate:.1f}%", f"{chargeback_ratio:.1f}%"]
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336"]

    fig, axes = plt.subplots(1, 4, figsize=(16, 3.5))
    fig.suptitle("Paytm Payments — Headline Scorecards", fontsize=14, fontweight="bold", y=1.02)
    for ax, label, val, color in zip(axes, labels, values, colors):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.text(0.5, 0.6, val, ha="center", va="center", fontsize=22, fontweight="bold", color=color)
        ax.text(0.5, 0.2, label, ha="center", va="center", fontsize=11, color="#555")
        ax.axis("off")
        ax.patch.set_facecolor("#f9f9f9")
        for spine in ax.spines.values():
            spine.set_visible(False)
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "layer1_scorecards.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    interpretation = (
        f"**Layer 1 Interpretation:** Over the 30-day window the platform moved ₹{total_gmv:,.0f} "
        f"in GMV.  {success_rate:.1f}% of transactions went through successfully.  "
        f"When we reconcile against the gateway, {match_rate:.1f}% of our ledger lines match "
        f"perfectly — the remaining ~{100-match_rate:.1f}% have some kind of discrepancy "
        f"(missing rows, amount diffs, or status diffs).  "
        f"The chargeback ratio sits at {chargeback_ratio:.1f}%, which is above a healthy baseline; "
        f"most of that comes from the burner-account fraud we seeded, but in a real system "
        f"this would trigger an immediate review by the fraud ops team."
    )
    print(interpretation)
    return interpretation


# --- Layer 2: how things moved day-to-day ---
def layer2_trends(ledger):
    """Creates the daily trends chart for the dashboard."""
    ledger = ledger.copy()
    ledger["txn_date"] = ledger["transaction_time"].dt.date
    daily = ledger.groupby("txn_date").agg(
        daily_gmv=("amount_inr", "sum"),
        chargeback_count=("status", lambda s: (s == "chargeback").sum())
    ).reset_index()
    daily["txn_date"] = pd.to_datetime(daily["txn_date"])

    fig, ax1 = plt.subplots(figsize=(14, 5))
    ax1.bar(daily["txn_date"], daily["daily_gmv"], color="#2196F3", alpha=0.7, label="Daily GMV (INR)")
    ax1.set_ylabel("Daily GMV (INR)", color="#2196F3", fontsize=11)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax1.tick_params(axis="y", labelcolor="#2196F3")

    ax2 = ax1.twinx()
    ax2.plot(daily["txn_date"], daily["chargeback_count"], color="#F44336", marker="o",
             linewidth=2, label="Chargeback Count")
    ax2.set_ylabel("Chargeback Count", color="#F44336", fontsize=11)
    ax2.tick_params(axis="y", labelcolor="#F44336")

    ax1.set_xlabel("Date")
    ax1.set_title("Daily GMV and Chargeback Count — 30-Day Window", fontsize=13, fontweight="bold")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "layer2_trends.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    interpretation = (
        "**Layer 2 Interpretation:** GMV bounces around between roughly ₹5k and ₹30k per day, "
        "which is normal variance for this transaction volume.  The chargeback line is what's "
        "interesting — it spikes on a handful of days (mostly in the second half of the month) "
        "and sits at zero on many others.  That bursty pattern is typical of organized fraud "
        "rather than random bad-luck chargebacks scattered evenly across the calendar."
    )
    print(interpretation)
    return interpretation


# --- Layer 3: where the money is going ---
def layer3_breakdown(ledger, merchants):
    """Creates the breakdown chart for the dashboard."""
    ledger_m = ledger.merge(merchants, on="merchant_id", how="left")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # left chart: payment rails
    pm = ledger_m.groupby("payment_method")["amount_inr"].sum().sort_values(ascending=True)
    pm.plot(kind="barh", ax=ax1, color=["#FF9800", "#4CAF50", "#2196F3", "#9C27B0"])
    ax1.set_title("GMV by Payment Method", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Total GMV (INR)")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    # right chart: merchant verticals
    cat = ledger_m.groupby("category")["amount_inr"].sum().sort_values(ascending=True)
    cat.plot(kind="barh", ax=ax2, color="#2196F3")
    ax2.set_title("GMV by Merchant Category", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Total GMV (INR)")
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "layer3_breakdown.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    interpretation = (
        "**Layer 3 Interpretation:** UPI leads GMV as expected since it carries about 55% of "
        "transaction weight.  Card shows up higher than you might expect, partly because every "
        "injected fraud txn (burner accounts, velocity clusters) was routed through Card, "
        "pulling that bar up.  On the category side, things are spread fairly evenly across "
        "verticals — merchants were randomly assigned, so no single category dominates."
    )
    print(interpretation)
    return interpretation


# --- Layer 4: the merchant-level detail table (saved as an image) ---
def layer4_details(ledger, merchants):
    """Creates the merchant-level detail table for the dashboard."""
    ledger_m = ledger.merge(merchants, on="merchant_id", how="left")

    merchant_stats = ledger_m.groupby(["merchant_id", "merchant_name", "category", "region"]).agg(
        txn_count=("transaction_id", "count"),
        total_gmv=("amount_inr", "sum"),
        chargeback_count=("status", lambda s: (s == "chargeback").sum()),
    ).reset_index()
    merchant_stats["chargeback_ratio_pct"] = (
        merchant_stats["chargeback_count"] / merchant_stats["txn_count"] * 100
    ).round(2)
    merchant_stats["high_risk_flag"] = merchant_stats["chargeback_ratio_pct"].apply(
        lambda x: "⚠ HIGH" if x > 1.0 else ""
    )

    top10 = merchant_stats.sort_values("txn_count", ascending=False).head(10).reset_index(drop=True)

    # render it as a PNG table so it lives alongside the other charts
    fig, ax = plt.subplots(figsize=(16, 4))
    ax.axis("off")
    ax.set_title("Top 10 Merchants by Transaction Count (High-Risk Flag: Chargeback Ratio > 1%)",
                 fontsize=12, fontweight="bold", pad=15)

    col_labels = ["Merchant ID", "Name", "Category", "Region", "Txn Count",
                  "GMV (INR)", "Chargebacks", "CB Ratio %", "Risk Flag"]
    cell_data = []
    cell_colors = []
    for _, row in top10.iterrows():
        cell_data.append([
            row["merchant_id"], row["merchant_name"], row["category"], row["region"],
            row["txn_count"], f"₹{row['total_gmv']:,.0f}", row["chargeback_count"],
            f"{row['chargeback_ratio_pct']:.2f}%", row["high_risk_flag"]
        ])
        if row["chargeback_ratio_pct"] > 1.0:
            cell_colors.append(["#ffcccc"] * len(col_labels))
        else:
            cell_colors.append(["#ffffff"] * len(col_labels))

    table = ax.table(cellText=cell_data, colLabels=col_labels, cellLoc="center",
                     loc="center", cellColours=cell_colors)
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.5)

    # make the header row pop
    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#2196F3")
        table[0, j].set_text_props(color="white", fontweight="bold")

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "layer4_details_table.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    interpretation = (
        "**Layer 4 Interpretation:** Looking at the busiest 10 merchants, a few of them carry "
        "chargeback ratios above 1% and are flagged accordingly.  A high ratio doesn't necessarily "
        "mean the merchant is complicit—it could simply be that fraudsters are targeting them "
        "because of weaker KYC or higher ticket sizes.  Either way, these names should go on the "
        "fraud team's watch list for a deeper look."
    )
    print(interpretation)
    return interpretation


if __name__ == "__main__":
    ledger, gateway, merchants = load_data()

    print("=" * 70)
    print("  PAYTM PAYMENTS — FOUR-LAYER ANALYTICS DASHBOARD")
    print("=" * 70)

    print("\n─── Layer 1: Headline Scorecards ───")
    interp1 = layer1_scorecards(ledger, gateway)

    print("\n─── Layer 2: Trends ───")
    interp2 = layer2_trends(ledger)

    print("\n─── Layer 3: Breakdown ───")
    interp3 = layer3_breakdown(ledger, merchants)

    print("\n─── Layer 4: Details ───")
    interp4 = layer4_details(ledger, merchants)

    # persist the write-ups so they're in the repo even without re-running
    interp_path = os.path.join(BASE_DIR, "dashboard_interpretations.md")
    with open(interp_path, "w", encoding="utf-8") as f:
        f.write("# Dashboard Interpretations\n\n")
        f.write("## Layer 1 — Headline Scorecards\n\n")
        f.write(interp1 + "\n\n")
        f.write("## Layer 2 — Trends\n\n")
        f.write(interp2 + "\n\n")
        f.write("## Layer 3 — Breakdown\n\n")
        f.write(interp3 + "\n\n")
        f.write("## Layer 4 — Details\n\n")
        f.write(interp4 + "\n\n")

    print(f"\nAll charts saved to {CHARTS_DIR}/")
    print(f"Interpretations saved to {interp_path}")
