# Reproduced model results

These CSVs/JSON record the approved hypothetical cases. Run `python3 code/reproduce.py` from the repository root to regenerate them.

- `policy_results.csv`: the three smooth-path policies and early/late public-funded cases.
- `annual_ledgers.csv`: actual dated liquid balances, calls, receipts and funding status, stopping at the first failed call.
- `verification.json`: verification receipt, fund cash-flow control, minimum starting-budget threshold and half-commitment control.

Frozen comparison outputs remain separately in `expected/`. No investable terminal wealth is assigned to a strategy after funding failure. The model’s solved fund IRR is a hypothetical control, not an estimated expected VC return. These files do not report institutional default probabilities.
