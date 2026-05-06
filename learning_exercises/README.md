# Learning Exercises: Treasury FTP Hands-On Practice
# ===================================================

This folder contains **DIY learning exercises** to build Treasury FTP knowledge step-by-step. Each exercise focuses on a core concept with skeleton code, data sources, and hints.

## How to Use

1. **Choose an exercise** that interests you
2. **Read the hints** and understand the objective
3. **Implement the TODOs** in the skeleton code
4. **Test with sample data** provided
5. **Answer self-assessment questions** to verify learning

## Exercise List

### 1. ECB Corridor Calculation (`exercise_1_ecb_corridor.py`)
**Concept**: How ECB interest rate corridor guides overnight funding costs
**Data**: Administered ECB rates (DFR, MRO, MLF)
**Output**: Corridor width, ESTR trading range, funding implications

### 2. Mortgage Prepayment Model (`exercise_2_mortgage_prepayment.py`)
**Concept**: Option-adjusted spreads for mortgages (PSA curves)
**Data**: Mortgage rates, refinancing costs, PSA assumptions
**Output**: Prepayment schedule, effective duration, FTP adjustment

### 3. Build Your Own NMD Model (`exercise_3_nmd_model.py`)
**Concept**: Estimating deposit beta from historical data
**Data**: Time series of deposit rates vs. market rates
**Output**: Beta coefficient, effective maturity, repricing analysis

### 4. Liquidity Stress Scenario (`exercise_4_liquidity_stress.py`)
**Concept**: LCR outflows under stress (deposit flight)
**Data**: Deposit balances, regulatory outflow assumptions
**Output**: 30-day outflows, LCR ratio, liquidity gap

### 5. Decompose Loan Spread (`exercise_5_loan_spread.py`)
**Concept**: Breaking down EURIBOR + X into risk components
**Data**: Loan pricing, credit ratings, market spreads
**Output**: Spread decomposition, RAROC calculation

### 6. Rate Shock Scenario (`exercise_6_rate_shock.py`)
**Concept**: IRRBB sensitivity (interest rate risk in banking book)
**Data**: Balance sheet by repricing bucket, rate scenarios
**Output**: Income impact, EVE sensitivity, duration gap

## Data Sources

### Internal (No External APIs Needed)
- **ECB Rates**: Use hypothetical values (DFR=4.5%, MRO=4.75%, MLF=5.0%)
- **Balance Sheet**: Reference `data/static/deutsche_bank_balance_sheet_sample.csv`
- **Sample Data**: Provided in each exercise script

### External (For Advanced Practice)
- **Historical Rates**: ECB Statistical Data Warehouse
- **CDS Spreads**: Bloomberg or Markit
- **Bond Yields**: ECB yield curves

## Learning Objectives

Each exercise teaches:
- **Technical Skills**: Python implementation, financial math
- **Treasury Concepts**: FTP pricing, risk management
- **Interview Prep**: Common questions and frameworks

## Self-Assessment Framework

After each exercise, ask yourself:
1. **Can I explain the concept** to a colleague?
2. **Do I understand the data sources** and assumptions?
3. **Can I apply it** to the Deutsche Bank balance sheet?
4. **What happens** under different scenarios?

## Integration with Main Project

Once implemented, exercises can be:
- Moved to `ftp_simulation/curves/` as production code
- Added to `tests/` with proper test cases
- Connected to the main FTP pipeline in Steps 4-7

## Next Steps

- Start with **Exercise 1** (ECB Corridor) - foundational concept
- Progress through exercises in order
- Implement 2-3 exercises to build comprehensive knowledge
- Use completed exercises in FTP charge logic (Step 5)

Happy learning! 🎓
