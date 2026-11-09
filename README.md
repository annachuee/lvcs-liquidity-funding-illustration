# Why Terminal Returns Can Hide Liquidity Failure

**A constructed funding-policy illustration of capital-call obligations, liquidity management and public-market return sequencing.**

*Leeds Venture Capital Society (LVCS) | 2026*

> Can two portfolios with the same terminal public-market return produce different funding outcomes when private-fund capital calls must be paid on specific dates?

## Overview

An investor can have a strong long-run return and still lack the money needed on a particular date. This project makes that distinction concrete with a small, reproducible LP funding model.

The general partner (GP) manages the fund and issues capital calls. The limited partner (LP) commits capital and must meet those calls. We track the LP’s funding account, including its liquid investments, payments to the fund and receipts from it. We do not model a startup’s runway or the GP’s cash balance.

The analysis uses hypothetical private-fund cash flows and constructed public-market paths. Its purpose is to show a mechanism clearly, not to estimate how often institutional investors default.

## Key finding

For a **$100m commitment financed from a $100m public-market portfolio**, the constructed early-loss path produces this funding check:

| Item | Model result |
|---|---:|
| Initial liquid budget | $100m |
| Fund commitment | $100m |
| Public-market loss | −40% in year 2 |
| First missed call | Year 4 |
| Capital call due | $19.00m |
| Liquid assets available before the call | $9.83m |
| Funding shortfall | **$9.17m** |

Moving the same −40% return to year 12 allows every baseline call to be funded. Both paths contain exactly the same 14 annual return observations and compound to approximately **8% annually over 14 years**. Only their order changes.

The other thirteen annual returns are approximately +13%, deliberately compensating for the loss. These are selected stress paths, not historical market data or forecasts. A 50% commitment survives the same early-loss path, illustrating the importance of sizing without establishing a universal safe allocation limit.

All figures above are **original LVCS calculations under hypothetical assumptions**. Academic sources provide context; they do not supply or empirically validate these numbers.

## Three funding policies

Each policy starts with the same total budget. They are alternatives, not three simultaneous allocations.

1. **Full liquid reserve.** Set aside the commitment in a reserve earning an assumed 3%. Pay calls from it and reinvest any reserve remaining after the final call.
2. **Two-year forecast reserve plus a 10% buffer.** Hold the next two forecast annual calls plus 10% of uncalled commitments, subject to the stated caps. Invest the balance in public assets and rebalance annually.
3. **Public-market-funded calls.** Invest the liquid budget in public assets and sell what is needed when a call falls due.

Under the separate, assumed smooth 8% public-return path, the same hypothetical fund produces these whole-budget outcomes:

| Funding policy | Year-14 wealth |
|---|---:|
| Full reserve earning an assumed 3% | $298.31m |
| Two-year forecast reserve plus 10% buffer | $310.59m |
| Public-market-funded calls | $330.67m |

Different policies carry different exposures. Higher terminal wealth in one path does not establish a universally preferable funding rule.

## Model assumptions

- **Capital:** $100m initial liquid wealth and a $100m commitment in the main illustration.
- **Calls:** $19m annually at dates 0–4, then $1m annually at dates 5–9, totalling $100m. The early calls comprise $17m of investment and $2m of fees per date; later calls are fees.
- **Fund receipts:** 40% of gross proceeds at date 9 and 60% at date 10, with the stated 20% carry after cumulative paid-in capital. Gross proceeds are solved to produce a hypothetical 10% net fund IRR; that is not an estimate of accessible VC returns.
- **Timing:** returns accrue, then calls are tested and paid, then distributions arrive. A future or same-date receipt cannot rescue an earlier missed call.
- **Common endpoint:** year 14. Net distributions and released reserves are reinvested in the declared public-return path.
- **Financing:** no borrowing, outside top-ups, other institutional assets or liabilities, or subscription-facility changes to the call schedule.
- **Implementation:** annual, frictionless trading and rebalancing; no taxes, default recovery or ending private-fund NAV.

Fund-level subscription facilities and an LP’s own financing resources are different arrangements. Neither is included here. Real institutions can have broader resources, obligations and liquidity systems than this restricted account.

## Reproduce the results

**Requirements:** Python 3 and its standard library. No external packages, credentials, proprietary data or network downloads are needed.

Download this repository, open a terminal in its root directory, and run:

```sh
python3 code/reproduce.py
```

On Windows, `python code/reproduce.py` may be the appropriate command.

The script checks the approved cases against frozen expected outputs and writes:

```text
results/policy_results.csv
results/annual_ledgers.csv
results/verification.json
```

A successful run reports `"status": "PASS"`. It verifies the fund cash flows, three smooth-path wealth figures, early/late sequence comparison, half-commitment control and the **$114.65m total starting-budget threshold** for the selected full-commitment public-funded stress case. The latter is a different quantity from the $9.17m dated shortfall.

`code/funding_model.py` is the unchanged numerical engine. Run the reproduction wrapper above; the retained legacy module has a broader standalone entry point that is not the release interface. Inputs are in `data/`, original comparison values in `expected/`, and the actual dated balances in `results/`.

## Research limitations

This is a conditional accounting illustration, not a representative institutional balance sheet or an empirical study of VC defaults. It does not estimate:

- actual LP default probabilities or a representative fund call schedule;
- optimal reserves or a universal commitment-size limit;
- expected returns from accessible VC funds;
- an empirical illiquidity premium or risk-adjusted allocation recommendation.

The sequence effect is an application of established liquidity principles. We make no claim to a new finance theorem, external independent peer review or independent audit certification. The annual grid and excluded financing resources materially limit the interpretation.

## Academic references

The [bibliography](BIBLIOGRAPHY.md) records full citations, primary-source links, verification status and limitations. The [claim-to-source table](CLAIM_TO_SOURCE.md) distinguishes conceptual support from LVCS’s calculations.

Core references include Gourier, Phalippou and Westerfield (2024); Ang, Papanikolaou and Westerfield (2014); Robinson and Sensoy (2016); Sørensen and Jagannathan (2015); ILPA (2017); and CalPERS (2024). Published models and empirical samples are not passed off as calibration of this illustration.

## Research methodology

Read the [methodology](METHODOLOGY.md) for the contract, policy rules, dated feasibility equations, starting-budget boundary and complete limitations. The [verification register](REFERENCE_VERIFICATION.json) identifies the sources actually checked.

The accompanying carousel is not redistributed here: its photograph and artwork are excluded from this personal repository. This text-only release contains the research explanation and reproducible calculations.

## Attribution

Prepared for Leeds Venture Capital Society (LVCS), 2026. This personal repository does not imply formal endorsement or approval by the University of Leeds.

**Licensing:** Copyright © 2026 annachuee. [MIT for code](LICENSE-CODE) and [CC BY 4.0 for original writing and constructed data/results](LICENSE-CONTENT), with the [scope and attribution requirements](LICENSE). Third-party works are cited and linked, not redistributed. Permission to use the LVCS name does not grant trademark rights to downstream users.
