"""
Three-agent debate: a bull, a bear, and a synthesizer argue over a single
ticker.  In mock mode the arguments come from templates that reference
real data; flip MOCK_LLM=0 to route through an actual LLM.
"""

import os
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

# we picked PAYFIN since it has the highest beta in our universe
DEBATE_TICKER = "PAYFIN"


def capm_expected_return(beta):
    """Standard CAPM expected return."""
    return RISK_FREE_RATE + beta * (MARKET_RETURN - RISK_FREE_RATE)


def bull_agent(ticker, data):
    """Makes the optimistic case for owning this stock."""
    capm_r = capm_expected_return(data["beta"])
    mock_llm = os.environ.get("MOCK_LLM", "1")

    if mock_llm != "0":
        argument = (
            f"BULL CASE for {ticker}: With a CAPM expected return of {capm_r:.1%} — driven by a "
            f"beta of {data['beta']:.2f} that captures the equity risk premium — {ticker} offers "
            f"attractive risk-adjusted upside. The analyst consensus expected return of "
            f"{data['analyst_expected_return']:.1%} further supports the thesis that this stock is "
            f"positioned to outperform the market return of {MARKET_RETURN:.1%}. For investors with "
            f"a higher risk appetite, the elevated beta translates to leveraged exposure to broad "
            f"market gains, making {ticker} a compelling growth pick."
        )
    else:
        argument = "[MOCK_LLM=0: LLM call would go here]"

    return argument


def bear_agent(ticker, data):
    """Makes the pessimistic case — why you should stay away."""
    capm_r = capm_expected_return(data["beta"])
    mock_llm = os.environ.get("MOCK_LLM", "1")

    if mock_llm != "0":
        argument = (
            f"BEAR CASE for {ticker}: The standard deviation of {data['std_dev']:.1%} signals "
            f"significant volatility risk — this is substantially above the market average. "
            f"While the CAPM expected return is {capm_r:.1%}, the beta of {data['beta']:.2f} means "
            f"that in a downturn, {ticker} would amplify losses by {data['beta']:.2f}x relative to "
            f"the market. The risk-return tradeoff, measured by the Sharpe-style ratio of "
            f"({capm_r:.1%} - {RISK_FREE_RATE:.1%}) / {data['std_dev']:.1%} = "
            f"{(capm_r - RISK_FREE_RATE) / data['std_dev']:.3f}, is not compelling enough to "
            f"justify the drawdown risk for most retail investors."
        )
    else:
        argument = "[MOCK_LLM=0: LLM call would go here]"

    return argument


def synthesizer_agent(ticker, data, bull_arg, bear_arg):
    """Takes both sides and tries to reach a balanced conclusion."""
    capm_r = capm_expected_return(data["beta"])
    mock_llm = os.environ.get("MOCK_LLM", "1")

    if mock_llm != "0":
        synthesis = (
            f"SYNTHESIS for {ticker}: The debate highlights a classic high-beta tradeoff. "
            f"The bull correctly identifies {ticker}'s {capm_r:.1%} CAPM return as attractive, "
            f"but the bear's concern about {data['std_dev']:.1%} volatility is equally valid — "
            f"the stock's {data['beta']:.2f} beta cuts both ways. "
            f"On balance, {ticker} is suitable for aggressive investors with a long horizon who "
            f"can absorb short-term drawdowns, but should be limited to a minority allocation "
            f"within a diversified portfolio. Conservative and moderate investors should underweight "
            f"or avoid this name entirely."
        )
    else:
        synthesis = "[MOCK_LLM=0: LLM call would go here]"

    return synthesis


if __name__ == "__main__":
    print("=" * 70)
    print("  MULTI-AGENT DEBATE DEMO")
    print(f"  Ticker: {DEBATE_TICKER}")
    print(f"  MOCK_LLM={os.environ.get('MOCK_LLM', '1')} (default=1, mock mode)")
    print("=" * 70)

    data = STOCK_UNIVERSE[DEBATE_TICKER]
    capm_r = capm_expected_return(data["beta"])
    print(f"\n  Ticker data: beta={data['beta']}, analyst_expected_return={data['analyst_expected_return']}, "
          f"std_dev={data['std_dev']}")
    print(f"  CAPM E(R) = {RISK_FREE_RATE} + {data['beta']} * ({MARKET_RETURN} - {RISK_FREE_RATE}) = {capm_r:.4f}")

    print(f"\n{'─'*70}")
    bull_arg = bull_agent(DEBATE_TICKER, data)
    print(f"\n[AGENT 1 — BULL]\n{bull_arg}")

    print(f"\n{'─'*70}")
    bear_arg = bear_agent(DEBATE_TICKER, data)
    print(f"\n[AGENT 2 — BEAR]\n{bear_arg}")

    print(f"\n{'─'*70}")
    synthesis = synthesizer_agent(DEBATE_TICKER, data, bull_arg, bear_arg)
    print(f"\n[AGENT 3 — SYNTHESIZER]\n{synthesis}")
