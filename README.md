# Funds_Transfer_Pricing_Simulation
Simulation engine for Funds Transfer Pricing (FTP) with a stylized bank balance sheet, behavioral models, and risk-sensitive internal funding curves. Uses the Risk_Factors library for market data, curve construction, and factor transformations.

## Balance-Sheet Repricing Buckets

The raw balance-sheet sample at `data/static/deutsche_bank_balance_sheet_sample.csv` intentionally does not store `repricing_bucket`.
It stores source-like attributes and mapping drivers instead, including contractual maturity, rate type, interest-rate index, reset frequency, fixed-rate period, amortization profile, behavioral profile, and valuation basis.

Repricing buckets are derived separately from editable assumptions in `data/static/repricing_rules_sample.csv`.
Use `ftp_simulation.balance_sheet.repricing.derive_repricing_buckets` to attach:

- `repricing_bucket`
- `repricing_rule_id`
- `repricing_mapping_method`

This keeps the raw balance sheet stable while allowing FTP assumptions to be challenged by changing the rule table.

For a full FTP-ready in-memory balance sheet, use `prepare_ftp_balance_sheet` with the raw balance sheet, repricing rules, and portfolio segmentation assumptions:

```python
from ftp_simulation.balance_sheet.loader import load_balance_sheet
from ftp_simulation.balance_sheet.repricing import load_repricing_rules
from ftp_simulation.balance_sheet.segmentation import load_segmentation, prepare_ftp_balance_sheet

balance_sheet = load_balance_sheet()
repricing_rules = load_repricing_rules()
segmentation = load_segmentation()

ftp_balance_sheet = prepare_ftp_balance_sheet(balance_sheet, repricing_rules, segmentation)
```

The returned DataFrame keeps detail rows only and includes both derived repricing fields and FTP segmentation fields. It is not written to disk automatically.

The segmentation file maps raw portfolios into first-version FTP reporting categories such as residential mortgages, corporate lending, retail deposits, wholesale deposits, liquidity buffers, secured financing, derivatives, trading inventory, operating balances, structural balances, and capital funding.
