# Learning Exercise 2: Mortgage Prepayment Model
# ============================================
#
# Objective: Understand how mortgage prepayments affect FTP pricing (option-adjusted spreads).
#
# What to implement:
# - PSA (Public Securities Association) prepayment curve
# - Calculate prepayment-adjusted duration
# - Estimate refinancing behavior under rate scenarios
#
# Data Sources:
# - Historical mortgage rates: Use sample data or generate synthetic
# - Prepayment assumptions: PSA standard curves (100 PSA = 6% annual prepayment)
# - Rate scenarios: Current mortgage rate vs. market rates
#
# Hints:
# 1. PSA curve: Prepayment rate = PSA_factor * (age/30) for first 30 months
# 2. Refinancing trigger: When market rate < mortgage rate - refinancing cost
# 3. Option-adjusted spread: Additional yield for prepayment risk
# 4. Test with different PSA speeds (50 PSA, 200 PSA)
#
# Expected Output:
# - Prepayment schedule over time
# - Effective duration with prepayments
# - FTP adjustment for prepayment risk
#
# Self-Assessment:
# - Why do mortgages have embedded options?
# - How does PSA speed affect duration?
# - What happens to FTP when rates fall?

def calculate_psa_prepayment_schedule(principal: float, psa_speed: float = 100) -> list[float]:
    """Calculate prepayment schedule using PSA model.

    Args:
        principal: Initial mortgage principal
        psa_speed: PSA speed (100 = standard)

    Returns:
        List of prepayment amounts by month
    """
    # TODO: Implement PSA prepayment curve
    # TODO: Calculate monthly prepayment rate
    # TODO: Return prepayment schedule

    return []  # TODO


def estimate_refinancing_behavior(current_rate: float, market_rate: float, refinancing_cost: float = 0.02) -> dict:
    """Estimate refinancing likelihood.

    Args:
        current_rate: Borrower's mortgage rate
        market_rate: Current market mortgage rate
        refinancing_cost: Transaction costs (2% typical)

    Returns:
        Dictionary with refinancing analysis
    """
    # TODO: Calculate rate incentive
    # TODO: Determine if refinancing is economical
    # TODO: Estimate prepayment speed increase

    return {
        "rate_incentive": 0.0,  # TODO
        "refinancing_likely": False,  # TODO
        "estimated_prepayment_speed": 0,  # TODO
    }


# Test with sample data
if __name__ == "__main__":
    # Sample €100M mortgage portfolio
    prepayments = calculate_psa_prepayment_schedule(100_000_000, psa_speed=100)
    print(f"Monthly prepayments: {prepayments[:12]}...")  # First year

    refinance = estimate_refinancing_behavior(current_rate=0.035, market_rate=0.030)
    print(f"Refinancing analysis: {refinance}")
