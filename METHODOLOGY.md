# Why terminal returns can hide liquidity failure

## Purpose and evidence boundary

This is a **constructed funding-policy illustration** of an LP’s ability to finance dated private-fund commitments. It is not a historical study of institutional defaults or a risk-adjusted VC recommendation. All displayed dollar results, selected return paths and numerical policy comparisons are original LVCS calculations under hypothetical assumptions. Academic and institutional references provide context, not empirical calibration of these figures.

The GP (general partner) manages the fund and issues capital calls. The LP (limited partner) commits capital and must meet those calls. Portfolio companies receive investment from the fund; they are not drawing money directly from the LP funding-policy account modelled here. Commitment management is an established research topic, including Gourier, Phalippou and Westerfield (2024). Our accounting example is an application of familiar liquidity and sequencing principles.

## Capital budget, contract and dates

The LP starts with $100m of liquid wealth at date 0. The main illustration commits $100m to one hypothetical fund, so the commitment equals the entire starting budget. This is a deliberately restricted reference case, not a representative institutional allocation. A preserved control scales the commitment to 50%, without reducing initial wealth.

| Model dates | Annual investment | Annual management fee | Annual LP call |
|---|---:|---:|---:|
|0–4 inclusive|$17m|$2m|$19m|
|5–9 inclusive|$0m|$1m|$1m|
|10–14|$0m|$0m|$0m|
|Total|$85m|$15m|$100m|

There are five early and five late call dates. The annual grid omits intrayear notices and settlement risk. All policies share endpoint14.

Gross investment proceeds are40% at 9 and 60% at 10. Cumulative carry is20% of positive cumulative gross receipts less cumulative paid-in capital; each distribution subtracts the change in cumulative carry. The contract excludes preferred returns, catch-up, recycling, taxes, subscription-line changes, extension fees and ending private NAV. Gross proceeds were solved in the verified reference case to give a10% LP net fund IRR after these model fees/carry. This is not an estimated expected return from accessible VC funds. Exact gross/net flows are in `data/baseline_fund_schedule.csv`.

## Funding resources and financing exclusions

The model has no borrowing, outside top-ups, other institutional assets, income, spending obligations or broader liabilities. These exclusions make the accounting clear but limit institutional applicability. An equity drawdown does not automatically cause a real LP to default.

Fund-level subscription facilities can bridge investments before LP calls and change the timing and measurement of LP cash flows. They are distinct from an LP’s own credit lines and balance-sheet resources. ILPA (2017) discusses fund-line exposure, uncalled commitments and disclosure; use is not universal, and a bridge does not extinguish the underlying funding obligation. LVCS models neither extra LP financing nor rescheduling of its stated calls through fund borrowing. No claim is made that such arrangements remove liquidity risk.

Institutional practice can evaluate a broader set of liquidity sources and uses; CalPERS (2024, PDF p.56) is one documented example. It is not evidence that our reserve buffer or annual grid is institutionally optimal.

## Three alternative policies, one budget

1. **Full liquid reserve:** initially segregate the commitment amount, earning an assumed constant3% annually. Pay calls from that reserve. Release unused reserve after the final call and invest it in the declared public-market path.
2. **Two-year forecast reserve plus 10% buffer:** retain the next two forecast annual calls plus 10% of uncalled commitments, capped by the remaining commitment and available liquid wealth. The initial reserve includes the immediate call. Rebalance annually; invest the balance in public assets. The forecast is the stated baseline schedule, not an estimated industry schedule.
3. **Public-market-funded calls:** hold the liquid budget in public assets and sell the amount needed at each call date. No leverage, short positions or outside cash rescue is allowed.

All net fund distributions are reinvested in the same declared public-return path. These are alternatives using the same initial budget, not additive allocations. Different holdings create different risks. A higher terminal value alone does not make a policy preferable if its calls cannot be met.

## Return assumptions and sequence experiment

For the smooth-path comparison, public assets earn an **assumed** constant8% annually and the reserve earns an **assumed**3%. Neither is a guaranteed future yield or an estimate from Cambridge Associates. Whole-budget year 14 wealth is $298.31m, $310.59m and $330.67m for the respective policies above.

The early/late experiment uses the same set of 14 annual public-return observations: one gross factor0.6 (−40%) and thirteen factors

`a = ((1.08**14) / 0.6)**(1/13)`.

The loss occurs at 2 in the early path and 12 in the late path; the remaining observations are the identical `a` factors. Both products equal `1.08**14`, subject to floating-point representation. The other annual returns are approximately+13%, deliberately compensating for the loss; this is a constructed isolation of order, not a typical history or forecast. The stress example uses the public-funded policy with the full commitment.

Call and receipt dynamics can have market and fund-age components in published research (Robinson and Sensoy,2016). Our fixed schedule does not estimate those relationships or a joint distribution. No actual public-return history is used in these carousel paths.

## Dated funding calculation

At each date: accrue reserve/public returns; assess usable liquid assets; pay the call from reserve and then public sales; only then receive any same-date distribution; rebalance the reserve. Current and future receipts cannot finance an earlier call. Stop at the first unpaid call. No investable terminal wealth is reported for an infeasible policy, and legal default consequences or recovery are not modelled.

For public funding, let P_t be the cumulative public gross-return level, c_t the call and d_t the net distribution. Before any failure, available assets satisfy:

`A_t = W_(t-1) * (P_t/P_(t-1))`, with `A_0 = initial budget`;

`fundable if A_t >= c_t`; then `W_t = A_t - c_t + d_t`.

The general reserve/public wallet applies the respective return factor to each holding before that same call test. Exact annual balances, calls and receipts are reproduced in `results/annual_ledgers.csv`.

At4 on the early-loss public-funded path, available assets are $9.83233541519861m against a $19m call: a $9.16766458480139m shortfall, displayed as $9.17m. On the reordered late-loss path every baseline call is funded. The50% commitment also survives this selected early path; that is a counterexample, not a recommended safe allocation limit.

The total minimum initial public-funded budget for the fixed $100m stress commitment is

`max_t(sum_(u<=t)(c_u/P_u) - sum_(u<t)(d_u/P_u))`.

The strict inequality on receipt dates enforces calls-before-receipts. This yields $114.65444488315346m, displayed as $114.65m **total** starting capital, not extra capital. Its binding prefix is9; with the actual $100m budget the first missed call is4. Neither number is a minimum across every possible funding policy or a universal institutional buffer.

## Measurement and limitations

Net fund IRR discounts only the LP’s fund payments/receipts. Whole-budget terminal wealth also includes uncalled capital, reserve earnings, liquid holdings and reinvested distributions. They answer different questions. Sørensen and Jagannathan (2015) provide a separate theoretical treatment of PME; we do not claim to implement that risk-adjusted performance framework here. Ang, Papanikolaou and Westerfield (2014) provide broader liquidity/portfolio-choice context, not this example’s calibration.

The illustration does not identify actual institutional failure frequency, a representative VC call schedule, optimal reserves, a universal commitment-size limit, expected accessible-fund performance, an empirical illiquidity premium or a universally superior funding rule. There is no Monte Carlo, statistical significance claim, investor utility model or external independent audit clearance. Annual frictionless trading and the omission of broader liabilities/resources are material constraints. Funding failure in the restricted wallet is not an estimated real-world LP default probability.

## Reproduction and attribution

Use Python 3 and the standard library from this folder:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 code/reproduce.py
```

The wrapper imports the frozen model copy, reproduces only the five original policy/path cases, the original half-commitment survival control and original starting-budget boundary, then compares unrounded results with the expected frozen records. It writes all selected annual ledgers and a verification receipt. The prefix calculation is also reconstructed directly from discounted calls and prior receipts. No model change, new scenario or new research experiment is introduced.

The release is checked against the frozen expected results and dated ledger. These are internal reproduction checks, not external audit certification. The code/data bundle contains only LVCS model assumptions and constructed inputs; it does not redistribute proprietary fund transactions, academic PDFs or the building photograph.

Full author/year/venue/DOI details, verification status, claim support and limitations are in [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md). The complete attribution map is [CLAIM_TO_SOURCE.md](CLAIM_TO_SOURCE.md).
