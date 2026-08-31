"""
Portfolio advisory agent that walks through think/act/observe for each
investor profile.  Uses CAPM for expected returns and a simple pairwise-
correlation model for portfolio variance.  Kicks anything too volatile
over to a human advisor.
"""

import os
import math
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN
from investor_profiles import INVESTOR_PROFILES

# what each risk bucket gets allocated to
ALLOCATION_MAP = {
    "Conservative": ["PAYBOND", "PAYGOLD", "PAYRETAIL"],
    "Moderate":     ["PAYRETAIL", "PAYINFRA", "PAYGOLD"],
    "Aggressive":   ["PAYTECH", "PAYFIN", "PAYINFRA"],
}

# assumed pairwise correlation across all stocks
RHO = 0.3

# if portfolio vol lands above this, bump it to a human
ESCALATION_THRESHOLD = 0.20  # 20% portfolio std dev


def get_stock_data(ticker):
    """Simulates calling an external data API to fetch a stock's risk stats."""
    if ticker not in STOCK_UNIVERSE:
        raise ValueError(f"Ticker '{ticker}' not found in STOCK_UNIVERSE")
    data = STOCK_UNIVERSE[ticker]
    return {
        "ticker": ticker,
        "beta": data["beta"],
        "analyst_expected_return": data["analyst_expected_return"],
        "std_dev": data["std_dev"],
    }


def capm_expected_return(beta):
    """Plain CAPM: risk-free rate plus beta times the equity risk premium."""
    return RISK_FREE_RATE + beta * (MARKET_RETURN - RISK_FREE_RATE)


def compute_portfolio_metrics(tickers, weights):
    """Weighted CAPM return + variance (assuming rho=0.3 between every pair)."""
    stock_data = []
    for t in tickers:
        sd = get_stock_data(t)
        sd["capm_return"] = capm_expected_return(sd["beta"])
        stock_data.append(sd)

    # weighted average of individual CAPM returns
    portfolio_return = sum(w * sd["capm_return"] for w, sd in zip(weights, stock_data))

    # variance = sum of w_i^2 * sigma_i^2 plus all the cross terms
    n = len(tickers)
    variance = 0.0
    for i in range(n):
        variance += weights[i] ** 2 * stock_data[i]["std_dev"] ** 2
    for i in range(n):
        for j in range(i + 1, n):
            cov_ij = RHO * stock_data[i]["std_dev"] * stock_data[j]["std_dev"]
            variance += 2 * weights[i] * weights[j] * cov_ij

    portfolio_std = math.sqrt(variance)

    return portfolio_return, variance, portfolio_std, stock_data


def run_agent(profile):
    """Run the full think/act/observe cycle for one investor."""
    investor_id = profile["investor_id"]
    risk_tolerance = profile["risk_tolerance"]
    horizon = profile["horizon_years"]
    amount = profile["investment_amount_inr"]

    print(f"\n{'='*70}")
    print(f"  AGENT RUN: {investor_id} | {risk_tolerance} | {horizon}yr | INR {amount:,}")
    print(f"{'='*70}")

    # THINK: figure out who we're dealing with
    print(f"\n[THINK] Reading investor profile {investor_id}...")
    print(f"  Risk tolerance: {risk_tolerance}")
    print(f"  Horizon: {horizon} years")
    print(f"  Investment amount: INR {amount:,}")

    tickers = ALLOCATION_MAP[risk_tolerance]
    weights = [1/3, 1/3, 1/3]
    print(f"  Prescribed allocation: {tickers} (equal-weight 1/3 each)")

    # ACT: go grab the data for each ticker
    print(f"\n[ACT] Calling get_stock_data() for each ticker...")
    for t in tickers:
        data = get_stock_data(t)
        print(f"  get_stock_data('{t}') → beta={data['beta']}, "
              f"analyst_expected_return={data['analyst_expected_return']}, "
              f"std_dev={data['std_dev']}")

    # OBSERVE: crunch the numbers and decide whether to escalate
    print(f"\n[OBSERVE] Computing portfolio metrics (CAPM + variance)...")
    portfolio_return, portfolio_var, portfolio_std, stock_data = compute_portfolio_metrics(tickers, weights)

    print(f"\n  Per-stock CAPM expected returns:")
    for sd in stock_data:
        print(f"    {sd['ticker']}: E(R) = {RISK_FREE_RATE} + {sd['beta']} * ({MARKET_RETURN} - {RISK_FREE_RATE}) "
              f"= {sd['capm_return']:.4f} ({sd['capm_return']*100:.2f}%)")

    print(f"\n  Portfolio expected return (weighted avg): {portfolio_return:.4f} ({portfolio_return*100:.2f}%)")
    print(f"  Portfolio variance: {portfolio_var:.6f}")
    print(f"  Portfolio std dev:  {portfolio_std:.4f} ({portfolio_std*100:.2f}%)")

    # does this portfolio's volatility need a human's sign-off?
    escalated = portfolio_std > ESCALATION_THRESHOLD
    if escalated:
        print(f"\n  *** ESCALATED_TO_HUMAN_ADVISOR ***")
        print(f"  Reason: Portfolio std dev ({portfolio_std*100:.2f}%) exceeds {ESCALATION_THRESHOLD*100:.0f}% threshold.")
        print(f"  Computed metrics attached for human review:")
        print(f"    - Expected return: {portfolio_return*100:.2f}%")
        print(f"    - Volatility: {portfolio_std*100:.2f}%")
        print(f"    - Tickers: {tickers}")
    else:
        print(f"\n  Escalation check: PASS (std dev {portfolio_std*100:.2f}% <= {ESCALATION_THRESHOLD*100:.0f}%)")
        print(f"  → Auto-finalizing recommendation.")

    # build the narrative (template in mock mode, would be LLM in prod)
    mock_llm = os.environ.get("MOCK_LLM", "1")

    if mock_llm != "0":
        # deterministic template so the output is reproducible
        ticker_str = ", ".join(tickers)
        if escalated:
            narrative = (
                f"For {risk_tolerance} investor {investor_id}, the prescribed allocation across "
                f"{ticker_str} yields an expected portfolio return of {portfolio_return:.1%} "
                f"and volatility of {portfolio_std:.1%}. However, the volatility exceeds the 20% "
                f"threshold, so this recommendation has been ESCALATED_TO_HUMAN_ADVISOR for review "
                f"before finalization."
            )
        else:
            narrative = (
                f"For {risk_tolerance} investor {investor_id}, we recommend an allocation across "
                f"{ticker_str} with an expected portfolio return of {portfolio_return:.1%} and "
                f"volatility of {portfolio_std:.1%}."
            )
    else:
        # would hit the Groq API here in a real deployment
        narrative = "[MOCK_LLM=0 mode: LLM call would go here]"

    print(f"\n  NARRATIVE: {narrative}")

    return {
        "investor_id": investor_id,
        "risk_tolerance": risk_tolerance,
        "tickers": tickers,
        "weights": weights,
        "portfolio_return": portfolio_return,
        "portfolio_std": portfolio_std,
        "portfolio_variance": portfolio_var,
        "escalated": escalated,
        "narrative": narrative,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("  PAYTM MONEY — PORTFOLIO ADVISORY AGENT")
    print(f"  MOCK_LLM={os.environ.get('MOCK_LLM', '1')} (default=1, mock mode)")
    print("=" * 70)

    results = []
    for profile in INVESTOR_PROFILES:
        result = run_agent(profile)
        results.append(result)

    # recap table so you can see everything at a glance
    print("\n\n" + "=" * 70)
    print("  AGENT RUN SUMMARY")
    print("=" * 70)
    print(f"\n{'Investor':<10} {'Risk':<14} {'Tickers':<30} {'E(R)':>8} {'Std':>8} {'Escalated':>10}")
    print("─" * 85)
    for r in results:
        ticker_str = ", ".join(r["tickers"])
        print(f"{r['investor_id']:<10} {r['risk_tolerance']:<14} {ticker_str:<30} "
              f"{r['portfolio_return']*100:>7.2f}% {r['portfolio_std']*100:>7.2f}% "
              f"{'YES' if r['escalated'] else 'NO':>10}")
