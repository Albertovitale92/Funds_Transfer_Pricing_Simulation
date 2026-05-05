# Funds Transfer Pricing Simulation TODO

## Current State

- Static Deutsche Bank-style balance-sheet sample exists at `data/static/deutsche_bank_balance_sheet_sample.csv`.
- Balance sheet is granular by `raw_portfolio` and reconciles to simplified public control totals.
- Mapping-based segmentation exists at `data/static/portfolio_segmentation_sample.csv`.
- Editable repricing-rule assumptions exist at `data/static/repricing_rules_sample.csv`.
- `prepare_ftp_balance_sheet` composes raw balances, repricing rules, and portfolio segmentation into one in-memory FTP-ready DataFrame.
- Validation checks schema, control rows, total reconciliation, and mapping coverage.

## Step 3: Define FTP Curve Taxonomy - ✅ DONE

- **18-curve FTP curve taxonomy** defined and partially implemented across Risk_Factors and FTP Simulation projects.
- **4 curves fully implemented** with working code, theory documents, and learning exercises:
  - ✅ Central Bank Remuneration Curve (Risk_Factors): DFR = 3.5%, opportunity cost calculation
  - ✅ Retail NMD Curve (FTP Simulation): Beta = 0.5, effective maturity = 3y
  - ✅ Corporate NMD Curve (FTP Simulation): Beta = 0.7, effective maturity = 1y
  - ✅ Wholesale NMD Curve (FTP Simulation): Beta = 0.95, effective maturity = 0.3y
- **Learning materials created**:
  - `Risk_Factors/docs/01_central_bank_remuneration_theory.md`: DFR concept, monetary policy transmission, exercise
  - `FTP Simulation/docs/02_nmd_curves_theory.md`: Beta decay, effective maturity, 3 exercises
  - `FTP Simulation/docs/00_curve_taxonomy_guide.md`: Complete 18-curve overview, architecture, roadmap
- **CSV taxonomies created** for both projects with curve attributes (type, currency, base rate, behavioral model, learning objective, interview relevance, implementation status).

### What's Next: Curve Implementation Roadmap

**Phase 2 - Core Funding Curves (Risk_Factors):**
- Overnight Index Curve (ESTR): Learn about credit spreads and OIS
- Money Market Curve (EURIBOR): Understand term premiums and basis
- Matched Swap Curve: Multi-curve framework and swap bootstrapping
- Secured Funding Curve (GC Repo): Collateral valuation and repo mechanics
- Term Unsecured Funding Curve: Bond yield decomposition

**Phase 3-5 - FTP-Specific Curves (FTP Simulation):**
- Liquidity & Regulatory: Liquidity Buffer, LCR Outflow, NSFR curves
- Product-Specific: Mortgage (with prepayment model), Corporate Loan, Trading Funding
- Advanced: FX Swap, Capital Allocation curves

**Integration with Main FTP Workflow:**
- Use curves in Step 4 (Behavioral models), Step 5 (FTP charge logic), Step 6-7 (Scenarios & reporting)

### Testing Your Knowledge: DIY Learning Exercises

**Exercise 1: Extend the Central Bank Remuneration Curve**
- Add a function `calculate_ecb_corridor()` that shows the spread between deposit facility rate (DFR) and marginal lending facility rate (MLF)
- Example: If DFR = 3.5% and MLF = 4.0%, the corridor is 50 bps
- Why: Understand how the ECB's rate corridor constrains interbank spreads
- Test: Verify spread widens when monetary conditions tighten

**Exercise 2: Implement a Mortgage Prepayment Model**
- Create a simplified PSA (Public Securities Association) curve for the residential mortgages portfolio (€125,000m fixed + €65,000m floating)
- Model: If rates drop 100 bps, assume 50% CPR (Conditional Prepayment Rate); if rates rise 100 bps, assume 10% CPR
- Calculate: Effective maturity under three scenarios (rates down 100 bps, base case, rates up 100 bps)
- Why: Mortgages have embedded optionality; you need to account for customer refinancing behavior
- Test: Verify effective maturity is shorter when rates drop (customers refinance)

**Exercise 3: Build Your Own NMD Model**
- Collect historical data on how your deposit rates changed vs. market rates (even hypothetical data)
- Estimate beta for each deposit type using regression: Δdeposit_rate = α + β × Δmarket_rate
- Compare your betas to Deutsche Bank assumptions (retail 0.5, corporate 0.7, wholesale 0.95)
- Why: Every bank has different deposit characteristics; yours might be different
- Test: Use your estimates in an FTP simulation and see if margins make sense

**Exercise 4: Implement a Liquidity Stress Scenario**
- Create an LCR_OutflowCurve for the three deposit types using regulatory stress assumptions:
  - Retail stable: 10% outflow in 30 days
  - Corporate: 25% outflow
  - Wholesale: 100% outflow
- Calculate: Total liquidity need = €305,000m × 10% + €165,000m × 25% + €66,658m × 100%
- How much liquidity buffer (HQLA) does the bank need?
- Why: Regulatory requirement; shows how quickly deposits can flee under stress
- Test: Verify calculation matches Basel III LCR definition

**Exercise 5: Decompose a Loan Spread**
- Take the corporate_term_loans (€155,000m) at floating EURIBOR 6M + X bps
- Decompose the spread into: base rate (EURIBOR) + credit spread + behavioral adjustment + FLP (funding liquidity premium)
- Example: If the loan price is EURIBOR + 250 bps:
  - Base (EURIBOR 6M): ~3.5%
  - Credit spread (BBB corp): ~1.5%
  - FTP liquidity (behavioral + structural): ~0.3%
  - Your implicit profit margin: could be 1-2% after funding
- Why: Critical for understanding product profitability
- Test: Compare your decomposition to internal pricing guides (if available)

**Exercise 6: Implement a Rate Shock Scenario**
- Take the prepared FTP balance sheet (all detail rows with ftp_rate assigned)
- Apply a +100 bps parallel rate shock to all curves
- Recalculate FTP rates for each portfolio using the shocked curves
- Calculate: NIM change = (new interest income - new interest expense) - (old interest income - old interest expense)
- Why: This is IRRBB (Interest Rate Risk in Banking Book); essential for Treasury FTP
- Test: Verify that assets reprice faster than liabilities (volume gap) creates positive NIM sensitivity in up-rate scenarios

### Where to Implement These Exercises

**In Risk_Factors Project:**
- Exercise 1-3: Add functions to `risk_factors/curves/central_bank_rates.py` and `builders.py`
- Create test files in `tests/curves/`

**In FTP Simulation Project:**
- Exercise 4-6: Add functions to `ftp_simulation/curves/behavioral_nmd.py` or create new modules (`products.py`, `scenarios.py`)
- Create test files in `tests/curves/`

### How to Know You've Learned It

After each exercise, ask yourself:
1. **Can I explain it in an interview?** (2-3 minute elevator pitch)
2. **Why does the bank care about this?** (Revenue, risk, regulation, competitive advantage)
3. **How does it connect to other curves?** (Is this the foundation for another concept?)
4. **Could I adjust the assumptions and rerun?** (Sensitivity analysis, sensitivity to your assumptions)

If you can answer all 4, you've internalized that concept. ✅

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

3. Define FTP curve taxonomy - ✅ DONE, see above for details and exercises

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

9. Build FTP metrics library
   - Core metrics that every FTP simulation should expose:
     - Net Interest Margin (NIM): `(interest_income - interest_expense) / earning_assets`.
     - FTP Spread: `product_rate - ftp_rate`.
     - Liquidity Premium: `ftp_rate - base_curve_rate`.
     - Capital Charge, RWA-based: `rwa * cost_of_capital`.
     - Net Product Margin (NPM): `product_revenue - ftp_cost - capital_charge`.
   - Intermediate Treasury metrics:
     - Transfer Pricing Rate Decomposition into base rate, liquidity premium, term premium, credit spread, and behavioral adjustment.
     - Behavioral Maturity Adjustment for non-maturity deposits, using effective maturity as a function of decay rate.
     - Duration Gap: `duration_assets - duration_liabilities`.
     - Earnings at Risk (EaR), measuring interest-margin sensitivity to rate shocks.
     - Simplified Liquidity Coverage Ratio (LCR): `HQLA / net_outflows`.
   - Advanced FTP and value metrics:
     - Shareholder Value Added (SVA): `NOPAT - (WACC * allocated_capital)`.
     - Marginal vs Average FTP for new production, maturity changes, and rate-curve changes.
     - FTP P&L Explain by volume effect, rate effect, mix effect, and curve shift effect.
     - Product Internal Rate of Return (IRR) for multi-cash-flow products.
     - Economic Value of Equity (EVE) for IRRBB value sensitivity.
   - Implement the skeleton under `ftp_simulation/metrics`.
   - Later connect metrics to prepared FTP balance-sheet rows, curve assumptions, scenario outputs, and reports.

## Design Principle

The raw balance sheet should remain the source of truth. Segmentation should classify raw rows into FTP-modelable categories, not allocate broad rows by percentages.
