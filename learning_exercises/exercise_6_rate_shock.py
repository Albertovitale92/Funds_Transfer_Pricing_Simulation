# Learning Exercise 6: Rate Shock Scenario
# ============================================
#
# Objective: Calculate IRRBB sensitivity (interest rate risk in banking book).
#
# What to implement:
# - Parallel rate shock (+/- 100 bps)
# - Interest income sensitivity
# - Economic value of equity (EVE) change
#
# Data Sources:
# - Balance sheet: Assets and liabilities by repricing bucket
# - Rate scenarios: Base case, +100 bps, -100 bps
# - Behavioral assumptions: NMD beta, prepayment models
#
# Hints:
# 1. IRRBB = Duration assets - Duration liabilities
# 2. Income sensitivity = sum(cash_flows * rate_change * duration)
# 3. EVE change = PV assets - PV liabilities under shock
# 4. Test with different shock sizes (+50, +200 bps)
#
# Expected Output:
# - Income impact over 1-5 years
# - EVE sensitivity
# - IRRBB gap analysis
#
# Self-Assessment:
# - Why is IRRBB important for banks?
# - How do behavioral models affect sensitivity?
# - What happens if assets reprice faster than liabilities?

import pandas as pd


def calculate_irrb_income_sensitivity(
    balance_sheet: pd.DataFrame,
    rate_shock: float,
    time_horizon: int = 12
) -> dict[str, float]:
    """Calculate IRRBB income sensitivity to rate shock.

    Args:
        balance_sheet: DataFrame with amount, repricing_bucket, side
        rate_shock: Rate shock in decimal (0.01 = +100 bps)
        time_horizon: Months to project

    Returns:
        Income sensitivity analysis
    """
    # TODO: Group by repricing bucket
    # TODO: Calculate repricing impact by bucket
    # TODO: Sum income changes over horizon
    # TODO: Return sensitivity metrics

    return {
        "rate_shock_bps": rate_shock * 10000,
        "income_impact_year1": 0.0,  # TODO
        "income_impact_year2": 0.0,  # TODO
        "cumulative_impact": 0.0,  # TODO
    }


def calculate_eve_sensitivity(
    assets_pv: float,
    liabilities_pv: float,
    rate_shock: float,
    asset_duration: float,
    liability_duration: float
) -> dict[str, float]:
    """Calculate EVE sensitivity to rate shock.

    Args:
        assets_pv: Present value of assets
        liabilities_pv: Present value of liabilities
        rate_shock: Rate shock in decimal
        asset_duration: Modified duration of assets
        liability_duration: Modified duration of liabilities

    Returns:
        EVE sensitivity analysis
    """
    eve_base = assets_pv - liabilities_pv

    # TODO: Calculate PV change using duration
    # TODO: Calculate new EVE
    # TODO: Calculate EVE change

    return {
        "eve_base": eve_base,
        "eve_shock": 0.0,  # TODO
        "eve_change": 0.0,  # TODO
        "eve_change_percent": 0.0,  # TODO
    }


# Test with sample data
if __name__ == "__main__":
    # Sample balance sheet (simplified)
    balance_data = {
        "portfolio": ["retail_deposits", "corporate_loans", "wholesale_deposits"],
        "amount_m": [305_000, 155_000, 66_658],
        "repricing_bucket": ["3M", "1Y", "1M"],
        "side": ["liability", "asset", "liability"],
    }
    balance_sheet = pd.DataFrame(balance_data)

    # +100 bps shock
    income_sensitivity = calculate_irrb_income_sensitivity(
        balance_sheet, rate_shock=0.01, time_horizon=12
    )
    print(f"Income sensitivity: {income_sensitivity}")

    # EVE calculation (simplified)
    eve = calculate_eve_sensitivity(
        assets_pv=1_500_000_000_000,  # €1.5T assets
        liabilities_pv=1_400_000_000_000,  # €1.4T liabilities
        rate_shock=0.01,
        asset_duration=2.5,
        liability_duration=1.8
    )
    print(f"EVE sensitivity: {eve}")
