# FTP Curve Taxonomy: Complete Guide

## Project Architecture

This document describes the FTP curve taxonomy and its implementation across two projects:

- **Risk_Factors**: Market data fetching and core curve construction (funding curves).
- **Funds_Transfer_Pricing_Simulation**: FTP application layer (behavioral, product, and regulatory curves).

---

## The Complete Curve List

### Summary by Category

| Category | # of Curves | Status | Primary Project |
|----------|------------|--------|-----------------|
| **Core Funding Curves** | 6 | 1 implemented, 5 planned | Risk_Factors |
| **Behavioural / NMD Curves** | 3 | 3 implemented | FTP Simulation |
| **Liquidity & Regulatory** | 3 | 3 planned | FTP Simulation |
| **Product-Specific** | 4 | 4 planned | FTP Simulation |
| **FX & Capital** | 2 | 2 planned | FTP Simulation |
| **TOTAL** | **18** | **3 implemented, 15 planned** | Both |

---

## Detailed Curve Descriptions

### Core Funding Curves (Risk_Factors Project)

These are **market-based curves** representing the cost of funds at different maturities and risk levels. They form the foundation of all FTP.

#### 1. Central Bank Policy Rates 🔄 DATA SOURCE
- **What**: ECB deposit facility rate (DFR), main refinancing operations rate (MRO), and marginal lending facility rate (MLF).
- **Why**: These administered rates anchor short-term funding costs and market curves.
- **How**: Fetched from market/reference data sources; pricing and FTP calculations remain in the FTP Simulation layer.
- **FTP Use**: Input data for central bank cash and other short-rate-linked FTP calculations.

#### 2. Overnight Index Curve 🔄 PLANNED
- **What**: ESTR (Euro Short-Term Rate); successor to EONIA.
- **Why**: Benchmark for overnight unsecured lending. ESTR = DFR + credit spread.
- **How**: Bootstrap from ECB MMSR data or published fixes.
- **Learning**: Learn how credit spreads are added to risk-free rates.
- **FTP Use**: Price short-duration unsecured funding and overnight interbank placements.
- **Status**: Will import from Risk_Factors; extend with bank-specific credit spreads.

#### 3. Money Market Curve 🔄 PLANNED
- **What**: EURIBOR or ESTR forwards for 1M-1Y tenors.
- **Why**: Benchmark for short-term unsecured lending (banks borrow from each other at EURIBOR).
- **How**: Derived from ESTR curve + term premium and liquidity adjustments.
- **Learning**: Understand term premium and basis spreads.
- **FTP Use**: Price interbank placements, commercial paper, short-term deposits.
- **Status**: Build from Risk_Factors OIS curve.

#### 4. Matched Swap Curve 🔄 PLANNED
- **What**: EURIBOR swap rates for 1Y-30Y tenors.
- **Why**: Industry-standard benchmark for term funding and hedging. Used in IRRBB calculations.
- **How**: Bootstrap from swap market data or ECB yield curve data.
- **Learning**: Build multi-curve framework; understand swap mathematics.
- **FTP Use**: Price mortgages, term loans, bond issuance; hedge interest rate risk.
- **Status**: Extend Risk_Factors `bootstrap_ecb_ois_zero_curve` functionality.

#### 5. Secured Funding Curve 🔄 PLANNED
- **What**: GC (general collateral) repo rates for 1D-1Y.
- **Why**: Banks can borrow cheaply against high-quality collateral. Secured funding is cheaper than unsecured.
- **How**: Repo rates over OIS; typically 10-50 bps below unsecured rates.
- **Learning**: Understand collateral valuation and haircuts.
- **FTP Use**: Price reverse repos, repurchase agreements, collateralized liquidity.
- **Status**: Build from ECB GC repo data.

#### 6. Term Unsecured Funding Curve 🔄 PLANNED
- **What**: Corporate bond yields for 1Y-10Y.
- **Why**: Long-term funding cost for bond issuance; reflects bank's credit quality.
- **How**: Bootstrap from bond market yields or CDS spreads.
- **Learning**: Decompose spreads into term premium, credit spread, and liquidity premium.
- **FTP Use**: Price long-term debt, senior unsecured bonds.
- **Status**: Source from Bloomberg or ECB data.

---

### Behavioural / NMD Curves (FTP Simulation Project)

These curves model how customer deposits **actually reprice** (often slower than market rates) based on customer behavior.

#### 7. Retail NMD Curve ✅ IMPLEMENTED
- **What**: Checking and savings accounts; modeled with beta = 0.5 (slow repricing).
- **Why**: Retail deposits are sticky (switching costs, relationship value, inertia). Banks don't pass through full rate moves.
- **How**: Behavioral model using beta decay and historical repricing data.
- **Learning**: Model deposit beta; understand customer stickiness as a funding advantage.
- **FTP Use**: Price checking accounts, savings accounts (€305,000m in DB).
- **Code Location**: `ftp_simulation/curves/behavioral_nmd.py`
- **Theory**: See `Funds_Transfer_Pricing_Simulation/docs/02_nmd_curves_theory.md`

**Key Concepts:**
- Beta = 0.5: Deposits reprice 50% as fast as market rates.
- Half-life = 2 years: Takes 2 years for deposit repricing to slow to 50% sensitivity.
- Effective maturity = 3 years: On average, retail deposits behave like 3-year funding.

#### 8. Corporate NMD Curve ✅ IMPLEMENTED
- **What**: Operating deposits; modeled with beta = 0.7 (medium repricing).
- **Why**: Corporate treasurers monitor rates more actively. Faster repricing than retail.
- **How**: Similar to retail but with higher beta and shorter half-life (1 year).
- **Learning**: Compare retail vs. corporate behavior; understand corporate funds management.
- **FTP Use**: Price corporate operating accounts (€165,000m in DB).

**Key Differences from Retail:**
- Beta = 0.7 (vs. 0.5): More sensitive to rate moves.
- Half-life = 1 year (vs. 2 years): Repricing accelerates sooner.
- Effective maturity = 1 year (vs. 3 years): Shorter duration.

#### 9. Wholesale NMD Curve ✅ IMPLEMENTED
- **What**: Brokered and institutional deposits; beta = 0.95 (nearly market-sensitive).
- **Why**: Institutional money is highly rate-sensitive; runs off quickly if rates move against the bank.
- **How**: Rapid repricing model; effectively like floating-rate liability.
- **Learning**: Model run-off risk under stress; connect to LCR assumptions.
- **FTP Use**: Price brokered deposits, institutional deposits (€66,658m in DB).

**Key Properties:**
- Beta = 0.95: Almost fully market-sensitive.
- Half-life = 0.25 years (3 months): Very fast repricing.
- Effective maturity = 0.3 years (3.4 months): Behaves like short-term borrowing.
- LCR Treatment: 100% outflow in 30 days (assumed to flee immediately).

---

### Liquidity & Regulatory Curves (FTP Simulation Project)

These curves integrate regulatory constraints (LCR, NSFR) into FTP pricing.

#### 10. Liquidity Buffer Curve 🔄 PLANNED
- **What**: HQLA (High-Quality Liquid Assets) yields; the opportunity cost of holding liquidity.
- **Why**: Regulators require banks to hold liquid buffers (for LCR). These have low yields.
- **How**: Compute from HQLA bond yields adjusted for LCR haircuts (e.g., securities with 50% haircut earn half the yield).
- **Learning**: Calculate LCR; understand haircut mechanics.
- **FTP Use**: Price HQLA investment portfolio (bonds, HQLA securities).
- **Example**: €47,010m HQLA bonds earning 2.0% before haircut → 1.0% after 50% LCR haircut effect.

#### 11. LCR Outflow Curve 🔄 PLANNED
- **What**: Deposit outflow rates under 30-day liquidity stress.
- **Why**: LCR regulation assumes deposits flee under stress. Stable retail: 10% outflow; corporate: 25%; wholesale: 100%.
- **How**: Stress-adjusted beta and run-off assumptions from regulatory guidelines.
- **Learning**: Model liquidity crisis scenarios; link to deposit repricing.
- **FTP Use**: Stress-test deposit funding under adverse scenarios.
- **Example**: If €305,000m retail deposits have 10% outflow, bank needs €30,500m liquidity buffer.

#### 12. NSFR Curve 🔄 PLANNED
- **What**: Long-term funding cost reflecting NSFR (Net Stable Funding Ratio) requirements.
- **Why**: NSFR requires stable funding for longer-term assets. Deposits classified as "stable" get favorable treatment (ASF > RSF).
- **How**: Blend of longer-term deposit and wholesale funding rates; adjusted for NSFR stability factors.
- **Learning**: Compute NSFR and Available/Required Stable Funding (ASF/RSF).
- **FTP Use**: Price 6M+ term funding to ensure NSFR compliance.

---

### Product-Specific Curves (FTP Simulation Project)

These curves are tailored to specific asset classes and account for product-specific risks.

#### 13. Mortgage Curve 🔄 PLANNED
- **What**: Fixed and floating mortgage rates; accounts for prepayment risk (customers refinance when rates drop).
- **Why**: Mortgages have **embedded optionality**: if rates drop, customers prepay and you lose the high-rate asset.
- **How**: Option-adjusted spread (OAS) technique. Adjust matched swap curve by prepayment risk premium.
- **Learning**: Model prepayment using PSA (Public Securities Association) curves.
- **FTP Use**: Price residential mortgages (€125,000m fixed + €65,000m floating in DB).
- **Example**: 
  - Matched Swap Curve (fixed 3Y-5Y maturity equivalent): 3.5%.
  - Prepayment Risk Premium: +50 bps (customers can refinance if rates drop).
  - Mortgage FTP Rate: 3.5% + 0.5% = 4.0%.

#### 14. Corporate Loan Curve 🔄 PLANNED
- **What**: Floating-rate corporate loans; breaks down into base rate, credit spread, and behavior adjustments.
- **Why**: Corporate loans have **credit risk** (borrower default) and **refinancing optionality** (customer may not renew).
- **How**: Base rate (EURIBOR) + credit spread (1-3% depending on creditworthiness) + behavioral adjustments.
- **Learning**: Decompose loan spreads; understand credit fundamentals.
- **FTP Use**: Price corporate loans (€155,000m term + €60,000m revolving in DB).
- **Example**:
  - Base (EURIBOR 6M): 3.5%.
  - Credit Spread (BBB corporate): 2.0%.
  - Refinancing Beta: 0.8 (80% reprice when rates move; 20% stick due to relationship).
  - Loan FTP Rate: 3.5% + 2.0% + 0.2% (behavioral adj.) = 5.7%.

#### 15. Trading Funding Curve 🔄 PLANNED
- **What**: Repo or fed funds rates for financing trading inventories.
- **Why**: Trading books must be funded daily or weekly; high turnover means short-duration funding.
- **How**: GC repo rates; similar to secured funding but with desk-specific adjustments.
- **Learning**: Understand mark-to-market funding and balance-sheet optimization.
- **FTP Use**: Price trading inventories (€172,469m in trading assets in DB).

---

### FX & Capital Curves (FTP Simulation Project)

#### 16. FX Swap Curve 🔄 PLANNED
- **What**: Cross-currency basis (EUR/USD); the premium to swap EUR funding into USD (or vice versa).
- **Why**: Multinational banks borrow in one currency and swap into another. The swap has a cost (basis).
- **How**: Interest rate parity: FX basis = interest rate differential (adjusted for forward premium).
- **Learning**: Compute interest rate parity; understand currency carry.
- **FTP Use**: Price cross-currency borrowing and hedging.

#### 17. Capital Allocation Curve 🔄 PLANNED
- **What**: WACC (Weighted Average Cost of Capital) or cost of equity.
- **Why**: Equity capital has a cost; products must cover this cost or they destroy shareholder value.
- **How**: Computed from cost of equity + cost of debt; reflects bank's risk profile and leverage.
- **Learning**: Compute RAROC (Risk-Adjusted Return on Capital); understand EVA (Economic Value Added).
- **FTP Use**: Calculate capital charge in NPM (Net Product Margin) = revenue - FTP cost - capital charge.
- **Example**: Cost of equity = 10%. €10,000m equity allocated to a product. Annual capital charge = €1,000m.

---

## Implementation Roadmap

### Phase 1: Core Learning (Curves 1-2) ✅ DONE
- [x] Central Bank Remuneration Curve (Risk_Factors)
  - [x] Code: `central_bank_rates.py`
  - [x] Theory: `01_central_bank_remuneration_theory.md`
  - [x] Exercise: Opportunity cost calculation
  
- [x] Retail/Corporate/Wholesale NMD Curves (FTP Simulation)
  - [x] Code: `behavioral_nmd.py`
  - [x] Theory: `02_nmd_curves_theory.md`
  - [x] Exercises: Effective maturity, beta decay, repricing ladder

### Phase 2: Funding Curves (Curves 3-6) 🔄 COMING
- [ ] Overnight Index Curve (Risk_Factors)
- [ ] Money Market Curve (Risk_Factors)
- [ ] Matched Swap Curve (Risk_Factors)
- [ ] Secured Funding Curve (Risk_Factors)
- [ ] Term Unsecured Funding Curve (Risk_Factors)

### Phase 3: Liquidity & Regulatory (Curves 10-12) 🔄 COMING
- [ ] Liquidity Buffer Curve (FTP Simulation)
- [ ] LCR Outflow Curve (FTP Simulation)
- [ ] NSFR Curve (FTP Simulation)

### Phase 4: Product-Specific (Curves 13-15) 🔄 COMING
- [ ] Mortgage Curve (FTP Simulation)
- [ ] Corporate Loan Curve (FTP Simulation)
- [ ] Trading Funding Curve (FTP Simulation)

### Phase 5: Advanced (Curves 16-17) 🔄 COMING
- [ ] FX Swap Curve (FTP Simulation)
- [ ] Capital Allocation Curve (FTP Simulation)

---

## How to Use The Curve Taxonomy

### As a Learning Tool

Each curve has a theory document explaining:
1. **Concept**: What it is and why banks use it.
2. **Building**: How it's constructed (market data, behavioral models, etc.).
3. **Learning Exercises**: Concrete calculations you can do.
4. **FTP Application**: How to price balance-sheet positions.
5. **Interview Relevance**: Why it matters for treasury discussions.

**Recommended Learning Path:**
1. Read the theory document.
2. Run the code examples.
3. Do the exercises (by hand or in code).
4. Apply to the Deutsche Bank balance sheet.

### As a Reference

The **ftp_curve_taxonomy.csv** files catalog all curves with attributes:
- Curve type, currency, base rate, maturity range
- Behavioral model, regulatory component
- Data sources, update frequency
- Learning objectives, interview relevance
- Implementation status

Load in Python:
```python
from ftp_simulation.curves import load_curve_taxonomy, summarize_curve_taxonomy

# Load from CSV
taxonomy = load_curve_taxonomy("data/static/ftp_curve_taxonomy.csv")

# Summarize
summary = summarize_curve_taxonomy(taxonomy)
print(summary)
```

### As a Development Tracker

The **implementation_status** column tracks progress:
- **implemented**: Fully coded and tested.
- **planned**: Scoped; code skeleton and theory doc ready.
- **in_progress**: Code being written.

---

## Inter-Project Dependencies

### Risk_Factors Provides to FTP Simulation

```
Risk_Factors (Market Curves)
  ├── Central Bank Remuneration
  ├── Overnight Index Curve (ESTR/EONIA)
  ├── Money Market Curve (EURIBOR)
  ├── Matched Swap Curve
  ├── Secured Funding Curve (GC Repo)
  └── Term Unsecured Funding Curve
         ↓
FTP Simulation (FTP Application)
  ├── Import Risk_Factors curves
  ├── Add Behavioral/NMD overlays
  ├── Add Regulatory (LCR/NSFR) adjustments
  ├── Compute product-specific adjustments
  └── Price balance-sheet portfolios
```

**Example Data Flow:**
```python
# In FTP Simulation
from risk_factors.api import risk_factors_api as rf

rates_curve = rf.get_rates_curve("eur_aaa", date="2026-05-06")

# Add behavioral overlay
from ftp_simulation.curves import RETAIL_NMD, calculate_effective_maturity
nmd_result = calculate_effective_maturity(balance_eur_m=305_000, deposit_type="retail")
# Output: Effective maturity = 3.0 years for retail deposits

# Combine in FTP pricing
ftp_rate = 0.035 + nmd_adjustment  # Simplified
```

---

## Next Steps

1. **Review and approve** this taxonomy.
2. **Implement Phase 2 curves** (Overnight Index, Money Market, etc.) in Risk_Factors.
3. **Build FTP charge logic** (Step 5 in main TODO) using the curves.
4. **Connect curves to prepared FTP balance sheet** for end-to-end FTP simulation.
5. **Add scenario support** (rate shocks, spread widening, deposit stress).

---

## Files Reference

### Risk_Factors Project
- **Code**:
  - `risk_factors/curves/central_bank_rates.py` ✅
  - `risk_factors/curves/builders.py` (existing; extend for money market, swap curves)
- **Data**:
  - `data/ftp_curve_taxonomy.csv` (core funding curves from Risk_Factors)
- **Docs**:
  - `docs/01_central_bank_remuneration_theory.md` ✅

### FTP Simulation Project
- **Code**:
  - `ftp_simulation/curves/__init__.py` ✅
  - `ftp_simulation/curves/behavioral_nmd.py` ✅
  - `ftp_simulation/curves/liquidity.py` (planned)
  - `ftp_simulation/curves/products.py` (planned)
  - `ftp_simulation/curves/capital.py` (planned)
- **Data**:
  - `data/static/ftp_curve_taxonomy.csv` ✅ (all curves for FTP)
- **Docs**:
  - `docs/02_nmd_curves_theory.md` ✅
  - `docs/03_mortgage_curve_theory.md` (planned)
  - `docs/04_liquidity_curves_theory.md` (planned)
  - (and more as we implement)

---

**Status**: Phase 1 complete. Ready to proceed with Phase 2 (funding curves in Risk_Factors).

