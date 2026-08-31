# Dashboard Interpretations

## Layer 1 — Headline Scorecards

**Layer 1 Interpretation:** Over the 30-day window the platform moved ₹382,603 in GMV.  85.6% of transactions went through successfully.  When we reconcile against the gateway, 90.5% of our ledger lines match perfectly — the remaining ~9.5% have some kind of discrepancy (missing rows, amount diffs, or status diffs).  The chargeback ratio sits at 5.1%, which is above a healthy baseline; most of that comes from the burner-account fraud we seeded, but in a real system this would trigger an immediate review by the fraud ops team.

## Layer 2 — Trends

**Layer 2 Interpretation:** GMV bounces around between roughly ₹5k and ₹30k per day, which is normal variance for this transaction volume.  The chargeback line is what's interesting — it spikes on a handful of days (mostly in the second half of the month) and sits at zero on many others.  That bursty pattern is typical of organized fraud rather than random bad-luck chargebacks scattered evenly across the calendar.

## Layer 3 — Breakdown

**Layer 3 Interpretation:** UPI leads GMV as expected since it carries about 55% of transaction weight.  Card shows up higher than you might expect, partly because every injected fraud txn (burner accounts, velocity clusters) was routed through Card, pulling that bar up.  On the category side, things are spread fairly evenly across verticals — merchants were randomly assigned, so no single category dominates.

## Layer 4 — Details

**Layer 4 Interpretation:** Looking at the busiest 10 merchants, a few of them carry chargeback ratios above 1% and are flagged accordingly.  A high ratio doesn't necessarily mean the merchant is complicit—it could simply be that fraudsters are targeting them because of weaker KYC or higher ticket sizes.  Either way, these names should go on the fraud team's watch list for a deeper look.

