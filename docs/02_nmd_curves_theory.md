# Non-Maturity Deposit (NMD) Curves: Theory & Learning Guide

## Overview

A **Non-Maturity Deposit (NMD)** is a customer deposit without a fixed contractual maturity (e.g., checking accounts, savings accounts). Unlike a 1-year fixed-rate deposit that reprices on a known date, an NMD has no contractual repricing date. Its economics change when the customer leaves, adds or withdraws balances, or when the bank changes the administered customer rate.

The **NMD Curve** models how long the balances are expected to remain stable and how sensitive their administered rates are to market conditions, using **behavioral assumptions** like deposit beta and stickiness. This is critical for FTP because:
- NMDs represent a large, stable funding source for banks.
- Their customer rates and balances adjust differently, usually more slowly than market rates, due to customer inertia.
- Regulatory requirements (NSFR, LCR) care about deposit "stickiness."

---

## Key Concepts

### 1. What Makes NMDs Different?

**Contractual vs. Behavioral Repricing:**

| Property | Fixed-Rate Deposit | NMD (Checking Account) |
|----------|-------------------|----------------------|
| Maturity | Known (1Y, 3Y, etc.) | Unknown ("forever") |
| Repricing Date | Contractual (maturity) | When customer decides or bank changes rate |
| Rate Path | Known at inception | Follows administered customer rate |
| Sensitivity to Rates | High (floating rate or refinancing risk) | Low to medium (customer stickiness) |
| FTP Complexity | Simple (use swap curve) | Complex (behavioral model needed) |

**Example:**
- A customer opens a checking account earning 0.5% (bank's administered rate).
- Market EURIBOR rises to 2.5%, and most banks raise their checking rates to 1.5%.
- This customer's rate only changes when the bank decides to raise it (or the customer notices and threatens to leave).
- The deposit doesn't "reprice" the same way a 3M EURIBOR loan reprices every 3 months.

### 2. Deposit Beta: The Core Behavioral Parameter

**Beta** measures how much of a market rate move is passed through to customer deposit rates.

- **Beta = 1.0**: Customer rate moves 100% with market rates (like a floating-rate bond).
- **Beta = 0.5**: Customer rate moves only 50% with market rates (high stickiness).
- **Beta = 0.0**: Customer rate doesn't move at all (zero sensitivity).

**Example Scenario:**

| Event | Market Rate | Retail NMD Beta | Customer Rate Change |
|-------|-------------|-----------------|----------------------|
| Today | EURIBOR 3M = 0.5% | 0.5 | Bank sets customer rate = 0.2% |
| Market rises | EURIBOR 3M = 2.5% | 0.5 | Bank raises customer rate by 0.5 × (2.5% - 0.5%) = 1.0% → new rate = 1.2% |
| Customer "feels" move | — | — | Customer notices rate went from 0.2% to 1.2%—maybe 1.0% is offered elsewhere |

**Why Beta < 1.0?**
1. **Customer stickiness**: Inertia, switching costs (time, paperwork).
2. **Relationship dynamics**: Customer might stay if overall banking relationship is good.
3. **Market power**: Bank doesn't need to match every competitor's rate move.
4. **Adverse selection**: Reducing the rate attracts only the most rate-sensitive customers (the ones most likely to leave anyway).

### 3. Deposit Maturity vs. Effective Maturity

A checking account has **no contractual maturity**, but it has an **effective (behavioral) maturity**.

**Effective maturity** = The modeled time profile over which a non-maturing deposit behaves like stable funding.

NMDs do not have a contractual repricing date in the same way a fixed-term deposit or bond does. In FTP, "repricing" is shorthand for the point at which the bank's assumed funding benefit changes because customer balances run off, customer rates are adjusted, or the bank must replace the behavioral NMD funding with market funding.

**Example:**
- Retail deposits have high beta (0.5) and slow repricing.
- Effective maturity: ~1-5 years (the stable funding benefit is expected to decay over several years).
- Wholesale deposits have high beta (0.95) and fast repricing.
- Effective maturity: ~0.25-1 year (institutional balances can move within weeks/months).

**Why This Matters for FTP:**
- If a bank funds a 10-year mortgage with an NMD segment modeled as 5-year behavioral funding, there's **duration mismatch** (interest rate risk).
- The NMD is not contractually priced for five years. The bank observes deposit stickiness and customer-rate sensitivity, then converts the expected stable portion into fixed-term FTP funding.
- If behavior differs from the model, the FTP funding profile changes: balances may run off sooner than expected, deposit rates may need to be adjusted faster, or the bank may need to replace the assumed NMD funding with market funding earlier. If balances are stickier than expected, the behavioral funding can last longer than modeled.

---

## How the NMD Curve is Built

NMD curves are **behavioral models**, not market prices. They're built from:
1. **Historical repricing data**: How did customer rates change last time rates moved?
2. **Stress tests**: How fast would deposits leave in a crisis?
3. **Peer data**: What beta do other banks assume for similar deposits?
4. **Regulatory guidance**: LCR/NSFR rules suggest run-off rates (e.g., retail stable deposits: 10% outflow in 30 days).

### The Three NMD Profiles

#### A. Retail NMD (Checking & Savings)
- **Beta**: 0.5 (slow repricing)
- **Half-life**: 2 years (takes 2 years for beta to decay to 0.25)
- **Effective maturity**: 1-5 years
- **Rationale**: Customers are sticky (automated payroll, loyalty, switching costs). Retail mass market moves slowly.

**Example Beta Decay:**
```
t=0:    beta = 0.50 (full initial response)
t=2y:   beta = 0.25 (decayed to 50%)
t=4y:   beta = 0.125 (decayed to 25% of original)
```

This models that as interest rates stay elevated, customers gradually reprend towards the new environment, but inertia keeps them from leaving immediately.

#### B. Corporate NMD (Operating Accounts)
- **Beta**: 0.7 (medium repricing)
- **Half-life**: 1 year
- **Effective maturity**: 0.5-2 years
- **Rationale**: Corporate treasurers monitor rates more actively than retail. Operating accounts reprice faster.

#### C. Wholesale NMD (Brokered, Institutional)
- **Beta**: 0.95 (fast repricing, nearly market-sensitive)
- **Half-life**: 0.25 years (3 months)
- **Effective maturity**: 0.25-1 year
- **Rationale**: Money from investors and brokers; highly rate-sensitive; can withdraw within days.

---

## FTP Application: Pricing NMD Portfolios

### Step 1: Segment Deposits by Type

From our Deutsche Bank balance sheet:
```
retail_current_accounts: €185,000m  → Retail NMD
retail_savings_accounts: €120,000m  → Retail NMD
retail_term_deposits: €80,000m      → NOT NMD (has maturity)
corporate_operating_deposits: €165,000m → Corporate NMD
corporate_term_deposits: €70,000m   → NOT NMD
financial_institution_deposits: €66,658m → Wholesale NMD
```

Total NMD: €536,658m (retail) + (corporate) + (wholesale)

### Step 2: Assign Effective Maturity

Using our behavioral assumptions:

```python
retail_effective_maturity = 2.5 years  # average of [1.0, 5.0]
corporate_effective_maturity = 1.0 year
wholesale_effective_maturity = 0.5 years
```

### Step 3: Assign to Repricing Buckets in FTP Balance Sheet

```
Retail: bucket = "0_3y" (use blended 1-3y rates)
Corporate: bucket = "0_1y" (use shorter-term rates)
Wholesale: bucket = "on_demand" or "0_3m" (most sensitive)
```

### Step 4: Price Using NMD Curve + Base Funding Curve

NMD FTP Rate = Base Funding Curve + NMD Spread Adjustment

**Example:**
```
Base Unsecured Funding Curve (1-year): 3.5% (money market rate)
NMD Spread Adjustment (retail): -100 bps (retail deposits cheaper because of stickiness)
NMD FTP Rate for Retail: 3.5% - 1.0% = 2.5%

Cost to bank: €305,000m × 2.5% = €7,625m annually
```

---

## Learning Exercise 1: Calculate Effective Maturity

### Scenario

Deutsche Bank has:
- Retail deposits: €305,000m with beta = 0.5
- Corporate deposits: €165,000m with beta = 0.7
- Wholesale deposits: €66,658m with beta = 0.95

For each segment, **calculate effective maturity** under current assumptions.

### Calculation

**Retail:**
```
Effective Maturity = Min + (Max - Min) × (1 - beta)
                   = 1.0 + (5.0 - 1.0) × (1 - 0.5)
                   = 1.0 + 4.0 × 0.5
                   = 1.0 + 2.0
                   = 3.0 years
```

**Corporate:**
```
Effective Maturity = 0.5 + (2.0 - 0.5) × (1 - 0.7)
                   = 0.5 + 1.5 × 0.3
                   = 0.5 + 0.45
                   = 0.95 ≈ 1.0 year
```

**Wholesale:**
```
Effective Maturity = 0.25 + (1.0 - 0.25) × (1 - 0.95)
                   = 0.25 + 0.75 × 0.05
                   = 0.25 + 0.0375
                   = 0.2875 ≈ 0.3 years (≈ 3.4 months)
```

### Interpretation

- **Retail deposits** (€305,000m): Effectively 3-year funding. Use the 1-3 year segment of the funding curve.
- **Corporate deposits** (€165,000m): Effectively 1-year funding. Use 1-year rates.
- **Wholesale deposits** (€66,658m): Effectively 3-month funding. Use overnight/1M rates; very sensitive to rate changes.

---

## Learning Exercise 2: Stress Scenario – Deposit Repricing Under Rate Shock

### Scenario

Current state:
- EURIBOR 1Y: 3.5%
- Deutsche Bank retail current account rate: 0.2% (administered)
- Retail deposit beta: 0.5

**Question:** If the ECB raises rates by 100 bps (EURIBOR 1Y → 4.5%), how much will Deutsche Bank need to raise the retail rate to keep deposits stable?

### Calculation (Simplified)

With beta = 0.5, the bank should raise the deposit rate by:
```
Rate Increase = 100 bps × 0.5 = 50 bps
New Retail Rate = 0.2% + 0.5% = 0.7%
```

**But this happens over time, not instantly:**
- **Month 1-3:** Raise to 0.35% (offset some rate-sensitive outflow)
- **Month 4-6:** Raise to 0.5% (more customers notice the deal elsewhere)
- **Month 12-18:** Raise to 0.7% (equilibrium)

By modeling **beta decay**, you can forecast when outflows stabilize.

### Implications

- If you don't raise deposit rates fast enough, retail deposits will flee (run-off risk).
- This is modeled in IRRBB / LCR stress tests.
- FTP should incentivize the business unit to keep competitive rates.

---

## Learning Exercise 3: Build a Repricing Ladder

Using the `compute_nmd_repricing_ladder` function:

```python
from ftp_simulation.curves import compute_nmd_repricing_ladder

# Retail deposits: €305,000m
ladder = compute_nmd_repricing_ladder(
    balance_eur_m=305_000,
    deposit_type="retail"
)

print(ladder)
```

**Output (example):**
```
  quarter  time_years  balance_eur_m  current_beta  repriced_cumulative_eur_m  unrepriced_balance_eur_m
       0        0.00      305000        0.500          152500                    152500
       4        1.00      305000        0.354          169950                    135050
       8        2.00      305000        0.250          228750                    76250
      12        3.00      305000        0.177          244990                    60010
      16        4.00      305000        0.125          268125                    36875
      20        5.00      305000        0.088          274880                    30120
```

**Reading:**
- At t=0: 50% of deposits repriced (high initial beta).
- At t=2y: 75% repriced (beta decayed to 0.25).
- At t=5y: 91% repriced (beta decayed to 0.088, very sticky remainder).

This ladder helps assign positions to repricing buckets for IRRBB calculation.

---

## Connection to Other Curves

### NMD Spread vs. Base Funding

NMD rates are typically **lower** than swap curve rates for the same bucket:

```
1-Year Funding Curve (Unsecured Term): 3.5% (money market, wholesale)
1-Year Retail NMD Rate: 2.5% (spreads favor the bank due to stickiness)
NMD Spread Benefit: -100 bps
```

Why the benefit?
- Deposits are a more stable funding source than wholesale borrowing.
- Regulatory rules (NSFR) favor deposits.
- Customer stickiness means less refinancing risk.

### Relationship to Liquidity Curves

NMDs feed into the **Liquidity Coverage Ratio (LCR)**:
- Stable retail deposits: 10% assumed outflow in 30 days (very sticky).
- Corporate deposits: 25% outflow (more flight risk).
- Wholesale deposits: 100% outflow (assumed to flee immediately).

These stress-test parameters are related to (but different from) the FTP beta/effective maturity assumptions.

---

## Interview Relevance

### Common Questions

1. **"How does your bank model NMD repricing?"**
   - Answer: Beta decay model assigning effective maturities by deposit type, informed by historical data and stress tests.

2. **"What happened to your NMD spreads when rates went negative (2021)?"**
   - Answer: Spread compressed (deposits more attractive relative to curve). We maintained positive rates for retail to protect volume.

3. **"How sensitive is your ALM to a sudden deposit runoff?"**
   - Answer: Very; we stress-test using wholesale (100%), corporate (25%), retail (10%) outflows. Our liquidity buffer covers stress.

4. **"If rates fall 200 bps, will your deposits reprice as fast as your assets?"**
   - Answer: No. Retail deposits (beta 0.5) reprice slower (sticky downward). This is material for NIM compression scenarios.

### Why It Matters

- **Deposit funding is the bank's cheapest source** (if stable).
- **NMD stickiness is a source of competitive advantage** (if you have loyal customers).
- **Regulatory arbitrage**: NSFR rewards deposit funding vs. wholesale borrowing.
- **Rate risk management**: Asymmetric repricing (deposits down, assets up) creates NIM pressure.

---

## Code Skeleton

All code is in `ftp_simulation/curves/behavioral_nmd.py`:

### Key Functions

1. `calculate_effective_maturity()` - Single portfolio calculation.
2. `decay_beta_over_time()` - Beta decay over horizon.
3. `compute_nmd_repricing_ladder()` - Full 5-year repricing schedule.
4. `estimate_loan_equivalent_maturity()` - Assign to repricing buckets.

### Example Usage

```python
from ftp_simulation.curves import (
    RETAIL_NMD,
    calculate_effective_maturity,
    compute_nmd_repricing_ladder,
)

# Get effective maturity
result = calculate_effective_maturity(
    balance_eur_m=305_000,
    deposit_type="retail",
    rate_change_pct=0.0
)
print(f"Effective maturity: {result['effective_maturity_years']:.2f} years")

# Build repricing ladder
ladder = compute_nmd_repricing_ladder(
    balance_eur_m=305_000,
    deposit_type="retail"
)
print(ladder)

# Apply to FTP balance sheet
ftp_balance_sheet['repricing_bucket'] = 'x_3y'  # For retail
```

---

## Summary Table

| Attribute | Retail | Corporate | Wholesale |
|-----------|--------|-----------|-----------|
| **Beta** | 0.5 | 0.7 | 0.95 |
| **Half-Life** | 2y | 1y | 0.25y |
| **Effective Maturity** | 3y | 1y | 3m |
| **Repricing Speed** | Slow | Medium | Fast |
| **Customer Sticky** | High | Medium | Low |
| **FTP Spread** | Tight (-100 bps) | Medium (-50 bps) | Wide (0 bps) |
| **Balance (DB)** | €305,000m | €165,000m | €66,658m |

---

## Next Steps

1. **Implement NMD calculation** in your FTP pipeline.
2. **Stress test** deposit outflows under rate scenarios.
3. **Extend** to Non-Maturity Asset (NMA) curves (e.g., mortgage prepayments).
4. **Connect** to IRRBB and EaR calculations.

