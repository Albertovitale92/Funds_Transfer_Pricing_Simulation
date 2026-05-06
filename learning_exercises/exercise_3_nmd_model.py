# Learning Exercise 3: Build Your Own NMD Model
# ============================================
#
# Objective: Estimate deposit beta from historical data (how fast deposits reprice).
#
# What to implement:
# - Analyze historical deposit rate changes vs. market rate changes
# - Calculate beta coefficient (repricing sensitivity)
# - Build decay model for effective maturity
#
# Data Sources:
# - Historical deposit rates: Use sample time series or generate synthetic
# - Market rates: ESTR or EURIBOR historical data
# - Deposit volumes: Sample balance data
#
# Hints:
# 1. Beta = correlation(deposit_rate_change, market_rate_change)
# 2. Effective maturity = integral of decay function
# 3. Test with different deposit types (retail vs. corporate)
# 4. Use regression: deposit_rate = alpha + beta * market_rate + error
#
# Expected Output:
# - Beta coefficient estimate
# - Effective maturity calculation
# - Repricing lag analysis
#
# Self-Assessment:
# - Why do retail deposits have lower beta than corporate?
# - How does beta affect FTP pricing?
# - What happens during rate shock scenarios?

import pandas as pd
import numpy as np


def estimate_deposit_beta(deposit_rates: list[float], market_rates: list[float]) -> float:
    """Estimate deposit beta from historical rate changes.

    Args:
        deposit_rates: Time series of deposit rates
        market_rates: Time series of market rates

    Returns:
        Beta coefficient (0-1, where 1 = full repricing)
    """
    # TODO: Calculate rate changes
    # TODO: Run regression or correlation
    # TODO: Return beta estimate

    return 0.0  # TODO


def calculate_effective_maturity_from_beta(beta: float, time_horizon: int = 60) -> float:
    """Calculate effective maturity using beta decay model.

    Args:
        beta: Estimated beta coefficient
        time_horizon: Months to simulate

    Returns:
        Effective maturity in months
    """
    # TODO: Implement beta decay over time
    # TODO: Calculate present value weighted average maturity
    # TODO: Return effective maturity

    return 0.0  # TODO


# Test with sample data
if __name__ == "__main__":
    # Sample historical data (synthetic)
    deposit_rates = [0.01, 0.015, 0.02, 0.025, 0.03]  # Increasing over time
    market_rates = [0.01, 0.02, 0.03, 0.04, 0.05]     # Market moves

    beta = estimate_deposit_beta(deposit_rates, market_rates)
    print(f"Estimated beta: {beta}")

    effective_maturity = calculate_effective_maturity_from_beta(beta)
    print(f"Effective maturity: {effective_maturity} months")
