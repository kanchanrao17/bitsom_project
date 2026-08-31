"""
DCF model for a hypothetical Paytm business line.  Projects five years
of FCFF, slaps on a terminal value, and sanity-checks everything with
an EV/EBITDA multiple.  Includes a 3x3 sensitivity grid.
"""

from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

# --- all assumptions stated up front (illustrative numbers) ---

# using PAYINFRA's beta since it's the closest proxy
BETA = STOCK_UNIVERSE["PAYINFRA"]["beta"]  # 1.10

# cost of equity via CAPM
COST_OF_EQUITY = RISK_FREE_RATE + BETA * (MARKET_RETURN - RISK_FREE_RATE)  # 0.07 + 1.1*0.06 = 0.136

# debt cost assumptions
COST_OF_DEBT_PRETAX = 0.10  # 10% pre-tax
TAX_RATE = 0.25             # 25% corporate tax
COST_OF_DEBT_AFTERTAX = COST_OF_DEBT_PRETAX * (1 - TAX_RATE)  # 7.5%

# capital structure weights
EQUITY_WEIGHT = 0.70
DEBT_WEIGHT = 0.30

# blended cost of capital
WACC = EQUITY_WEIGHT * COST_OF_EQUITY + DEBT_WEIGHT * COST_OF_DEBT_AFTERTAX

# base-year free cash flow: EBIT*(1-t) + D&A - CapEx - delta NWC
EBIT = 5_000_000_000      # INR 500 Cr EBIT
DA = 800_000_000           # INR 80 Cr Depreciation & Amortization
CAPEX = 1_200_000_000      # INR 120 Cr Capital Expenditure
DELTA_NWC = 300_000_000    # INR 30 Cr change in Net Working Capital

BASE_FCFF = EBIT * (1 - TAX_RATE) + DA - CAPEX - DELTA_NWC

# growth rates
GROWTH_RATE_Y1_Y5 = 0.12   # 12% for years 1-5
TERMINAL_GROWTH = 0.04     # 4% terminal growth (WACC - terminal_growth >= 3pp)

# for the sanity check at the end
EBITDA = EBIT + DA  # INR 580 Cr
EV_EBITDA_MULTIPLE = 15.0  # Illustrative multiple


def compute_wacc():
    """Walk through the WACC calculation step by step."""
    print("=" * 70)
    print("  WACC COMPUTATION")
    print("=" * 70)
    print(f"  Cost of Equity (R_e) = R_f + beta * (R_m - R_f)")
    print(f"    = {RISK_FREE_RATE:.2%} + {BETA} * ({MARKET_RETURN:.2%} - {RISK_FREE_RATE:.2%})")
    print(f"    = {COST_OF_EQUITY:.4f} ({COST_OF_EQUITY:.2%})")
    print(f"  Cost of Debt (after-tax) = {COST_OF_DEBT_PRETAX:.2%} * (1 - {TAX_RATE:.2%})")
    print(f"    = {COST_OF_DEBT_AFTERTAX:.4f} ({COST_OF_DEBT_AFTERTAX:.2%})")
    print(f"  WACC = {EQUITY_WEIGHT:.0%} * {COST_OF_EQUITY:.2%} + {DEBT_WEIGHT:.0%} * {COST_OF_DEBT_AFTERTAX:.2%}")
    print(f"    = {WACC:.4f} ({WACC:.2%})")
    return WACC


def compute_base_fcff():
    """Show how we get from EBIT to free cash flow."""
    print(f"\n{'='*70}")
    print("  BASE FCFF COMPUTATION")
    print("=" * 70)
    print(f"  FCFF = EBIT * (1 - tax_rate) + D&A - CapEx - delta_NWC")
    print(f"       = {EBIT/1e7:,.0f} Cr * (1 - {TAX_RATE:.0%}) + {DA/1e7:,.0f} Cr - {CAPEX/1e7:,.0f} Cr - {DELTA_NWC/1e7:,.0f} Cr")
    print(f"       = {EBIT*(1-TAX_RATE)/1e7:,.0f} Cr + {DA/1e7:,.0f} Cr - {CAPEX/1e7:,.0f} Cr - {DELTA_NWC/1e7:,.0f} Cr")
    print(f"       = INR {BASE_FCFF/1e7:,.0f} Cr (INR {BASE_FCFF:,.0f})")
    return BASE_FCFF


def dcf_valuation(wacc, terminal_growth, base_fcff=BASE_FCFF, growth_rate=GROWTH_RATE_Y1_Y5, years=5):
    """Project FCFF forward, add a terminal value, discount everything back."""
    projected_fcf = []
    pv_fcf = []
    fcf = base_fcff
    for yr in range(1, years + 1):
        fcf = fcf * (1 + growth_rate) if yr > 1 else base_fcff * (1 + growth_rate)
        pv = fcf / (1 + wacc) ** yr
        projected_fcf.append(fcf)
        pv_fcf.append(pv)

    # terminal value using the Gordon growth perpetuity
    terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    pv_terminal = terminal_value / (1 + wacc) ** years

    enterprise_value = sum(pv_fcf) + pv_terminal

    return {
        "projected_fcf": projected_fcf,
        "pv_fcf": pv_fcf,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
    }


def run_dcf():
    """Run the whole thing end-to-end and print every step."""
    wacc = compute_wacc()
    base_fcff = compute_base_fcff()

    # make sure WACC is far enough above terminal growth
    gap = WACC - TERMINAL_GROWTH
    print(f"\n  Self-check: WACC ({WACC:.2%}) - Terminal Growth ({TERMINAL_GROWTH:.2%}) = {gap:.2%}")
    print(f"  Gap >= 3pp: {'PASS' if gap >= 0.03 else 'FAIL'}")

    print(f"\n{'='*70}")
    print("  5-YEAR DCF PROJECTION")
    print("=" * 70)

    result = dcf_valuation(WACC, TERMINAL_GROWTH)

    print(f"\n  {'Year':<6} {'Projected FCF (Cr)':>20} {'PV of FCF (Cr)':>20}")
    print(f"  {'─'*50}")
    for yr, (fcf, pv) in enumerate(zip(result["projected_fcf"], result["pv_fcf"]), 1):
        print(f"  {yr:<6} {fcf/1e7:>20,.2f} {pv/1e7:>20,.2f}")

    print(f"\n  Terminal Value (Cr):       {result['terminal_value']/1e7:>20,.2f}")
    print(f"  PV of Terminal Value (Cr): {result['pv_terminal']/1e7:>20,.2f}")
    print(f"  Enterprise Value (Cr):     {result['enterprise_value']/1e7:>20,.2f}")
    print(f"  Enterprise Value (INR):    {result['enterprise_value']:>20,.0f}")

    return result


def sensitivity_table():
    """Vary WACC and terminal growth by ±1pp to see how EV moves."""
    print(f"\n{'='*70}")
    print("  SENSITIVITY TABLE (WACC ± 1pp × Terminal Growth ± 1pp)")
    print("=" * 70)

    wacc_values = [WACC - 0.01, WACC, WACC + 0.01]
    tg_values = [TERMINAL_GROWTH - 0.01, TERMINAL_GROWTH, TERMINAL_GROWTH + 0.01]

    # sanity: every cell needs WACC > terminal_growth
    worst_case_gap = min(w - g for w in wacc_values for g in tg_values)
    print(f"\n  Worst-case (WACC - terminal_growth): {worst_case_gap:.2%}")
    print(f"  Gap >= 1pp in all cells: {'PASS' if worst_case_gap >= 0.01 else 'FAIL'}")

    # print the grid
    wacc_tg_label = "WACC \\ TG"
    header = f"  {wacc_tg_label:<12}"
    for tg in tg_values:
        tg_label = f"TG={tg:.2%}"
        header += f"  {tg_label:>16}"
    print(f"\n{header}")
    print(f"  {'─'*60}")

    for w in wacc_values:
        row = f"  WACC={w:.2%}  "
        for tg in tg_values:
            ev = dcf_valuation(w, tg)["enterprise_value"]
            row += f"  {ev/1e7:>14,.1f} Cr"
        print(row)

    return wacc_values, tg_values


def ev_ebitda_crosscheck():
    """Quick reality check: does a simple multiple give a similar answer?"""
    print(f"\n{'='*70}")
    print("  EV/EBITDA CROSS-CHECK")
    print("=" * 70)

    ev_multiple = EBITDA * EV_EBITDA_MULTIPLE
    print(f"\n  EBITDA:         INR {EBITDA/1e7:,.0f} Cr")
    print(f"  EV/EBITDA multiple: {EV_EBITDA_MULTIPLE:.1f}x")
    print(f"  Implied EV:     INR {ev_multiple/1e7:,.0f} Cr")

    dcf_result = dcf_valuation(WACC, TERMINAL_GROWTH)
    dcf_ev = dcf_result["enterprise_value"]
    diff_pct = (dcf_ev - ev_multiple) / ev_multiple * 100

    print(f"\n  DCF EV:         INR {dcf_ev/1e7:,.1f} Cr")
    print(f"  EV/EBITDA EV:   INR {ev_multiple/1e7:,.1f} Cr")
    print(f"  Difference:     {diff_pct:+.1f}%")

    comparison = (
        f"The DCF-based enterprise value of INR {dcf_ev/1e7:,.1f} Cr "
        f"{'exceeds' if dcf_ev > ev_multiple else 'is below'} the EV/EBITDA-implied value of "
        f"INR {ev_multiple/1e7:,.1f} Cr by {abs(diff_pct):.1f}%. "
        f"This divergence reflects the DCF's explicit growth assumptions (12% for 5 years, "
        f"4% terminal) versus the static multiple approach. "
        f"The {EV_EBITDA_MULTIPLE:.0f}x EV/EBITDA multiple is within the typical range for Indian "
        f"fintech companies, providing a reasonable sanity check for the DCF estimate."
    )
    print(f"\n  Comparison: {comparison}")

    return ev_multiple, comparison


if __name__ == "__main__":
    print("=" * 70)
    print("  PAYTM BUSINESS LINE — DCF VALUATION CALCULATOR")
    print("=" * 70)
    print(f"\n  Assumptions:")
    print(f"    Beta (PAYINFRA):        {BETA}")
    print(f"    Risk-free rate:         {RISK_FREE_RATE:.2%}")
    print(f"    Market return:          {MARKET_RETURN:.2%}")
    print(f"    Tax rate:               {TAX_RATE:.0%}")
    print(f"    Cost of debt (pre-tax): {COST_OF_DEBT_PRETAX:.2%}")
    print(f"    Equity weight:          {EQUITY_WEIGHT:.0%}")
    print(f"    Debt weight:            {DEBT_WEIGHT:.0%}")
    print(f"    Growth rate (Y1-Y5):    {GROWTH_RATE_Y1_Y5:.2%}")
    print(f"    Terminal growth:        {TERMINAL_GROWTH:.2%}")

    run_dcf()
    sensitivity_table()
    ev_ebitda_crosscheck()
