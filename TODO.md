# Funds Transfer Pricing Simulation TODO

## Current State

- Static Deutsche Bank-style balance-sheet sample exists at `data/static/deutsche_bank_balance_sheet_sample.csv`.
- Balance sheet is granular by `raw_portfolio` and reconciles to simplified public control totals.
- Mapping-based segmentation exists at `data/static/portfolio_segmentation_sample.csv`.
- Editable repricing-rule assumptions exist at `data/static/repricing_rules_sample.csv`.
- `prepare_ftp_balance_sheet` composes raw balances, repricing rules, and portfolio segmentation into one in-memory FTP-ready DataFrame.
- Validation checks schema, control rows, total reconciliation, and mapping coverage.

## Next Steps

1. Review granular balance-sheet rows - done for first simulator version
   - Check whether the current simplified DB balance-sheet decomposition is plausible enough for Treasury FTP discussion.
   - Adjust `raw_portfolio`, `business_line`, `product_type`, maturity, repricing, counterparty, and behavioral hints where needed.
   - Initial cleanup completed: raw repricing drivers now avoid embedding FTP outputs such as `swap_curve_sensitive`, `issuance_curve_sensitive`, and `market_sensitive` as contractual reset frequencies.
   - Amounts and public-report-line reconciliation were left unchanged.

2. Review FTP mapping categories - done for first simulator version
   - Confirm each `raw_portfolio` maps to the right `ftp_category` and `ftp_model_portfolio`.
   - Decide whether categories are too broad or too granular for the first simulator version.
   - Initial cleanup completed: broad `customer_loans` and `customer_deposits` categories were split into residential mortgages, corporate lending, trade finance, consumer lending, retail deposits, corporate deposits, and wholesale deposits.
   - Structural liabilities were separated from operating liabilities, and subordinated/trust-preferred instruments were separated into capital funding.
   - Segmentation validation now checks that `funding_role` is consistent with balance-sheet side.

3. Define FTP curve taxonomy
   - Agree the initial set of internal FTP curves, for example:
     - central bank remuneration
     - overnight index curve
     - money market curve
     - matched swap curve
     - secured funding curve
     - term unsecured funding curve
     - retail and corporate non-maturity deposit curves
   - Create a static curve assumption file.

4. Define behavioral models
   - Start simple with named model types rather than full statistical models.
   - Cover non-maturity deposits, prepaying mortgages, revolvers, contractual term products, trading inventory, derivatives, and structural balances.

5. Build FTP charge logic
   - Calculate FTP charge or credit by mapped FTP portfolio.
   - Use balance amount, side, curve, maturity/repricing bucket, and behavioral model.
   - Keep the first version deterministic and explainable.

6. Add scenario support
   - Base case.
   - Parallel rate shock.
   - Liquidity spread widening.
   - Deposit beta or behavioral-life stress.

7. Build reporting outputs
   - Balance by FTP category.
   - FTP charge or credit by portfolio.
   - Net FTP margin by business line.
   - Scenario comparison table.

8. Add documentation for Treasury discussion
   - Explain assumptions.
   - Show how public DB balance-sheet lines are simplified.
   - Show how raw portfolios map into FTP-modelable categories.
   - Highlight open questions for Treasury FTP stakeholders.

## Design Principle

The raw balance sheet should remain the source of truth. Segmentation should classify raw rows into FTP-modelable categories, not allocate broad rows by percentages.
