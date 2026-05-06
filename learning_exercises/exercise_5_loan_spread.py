# Learning Exercise 5: Decompose Loan Spread
# ============================================
#
# Objective: Break down EURIBOR + X into components (liquidity, credit, term premiums).
#
# What to implement:
# - Loan spread decomposition
# - Risk-adjusted pricing
# - FTP rate calculation for loans
#
# Data Sources:
# - Loan pricing: EURIBOR + spread observations
# - Credit ratings: BBB, A, AA ratings
# - Market data: CDS spreads, bond yields
#
# Hints:
# 1. Loan spread = base_rate + credit_spread + liquidity_premium + term_premium
# 2. Credit spread from CDS or bond yields
# 3. Liquidity premium: 10-30 bps for loans vs. bonds
# 4. Test with different credit qualities
#
# Expected Output:
# - Spread decomposition breakdown
# - FTP rate for the loan
# - RAROC calculation
#
# Self-Assessment:
# - Why do loans trade at wider spreads than bonds?
# - How does credit quality affect FTP?
# - What happens to spreads during crises?

def decompose_loan_spread(
    euribor_rate: float,
    total_spread: float,
    credit_rating: str = "BBB",
    loan_type: str = "corporate"
) -> dict[str, float]:
    """Decompose loan spread into components.

    Args:
        euribor_rate: Base EURIBOR rate
        total_spread: Total spread over EURIBOR
        credit_rating: Credit rating (AAA, AA, A, BBB, etc.)
        loan_type: Type of loan

    Returns:
        Dictionary with spread components
    """
    # Typical credit spreads (bps)
    credit_spreads = {
        "AAA": 10,
        "AA": 20,
        "A": 40,
        "BBB": 80,
        "BB": 200,
    }

    # TODO: Estimate credit spread from rating
    # TODO: Allocate liquidity premium (20-50 bps)
    # TODO: Allocate term premium (10-30 bps)
    # TODO: Calculate residual (other factors)

    return {
        "base_rate": euribor_rate,
        "total_spread": total_spread,
        "credit_spread": 0.0,  # TODO
        "liquidity_premium": 0.0,  # TODO
        "term_premium": 0.0,  # TODO
        "other_factors": 0.0,  # TODO
        "ftp_rate": 0.0,  # TODO: base + components
    }


def calculate_loan_raroc(
    loan_balance: float,
    ftp_rate: float,
    expected_loss: float,
    capital_requirement: float,
    cost_of_capital: float = 0.10
) -> dict[str, float]:
    """Calculate RAROC for loan pricing.

    Args:
        loan_balance: Loan amount
        ftp_rate: FTP rate for the loan
        expected_loss: Expected credit loss
        capital_requirement: Regulatory capital (%)
        cost_of_capital: Cost of equity

    Returns:
        RAROC analysis
    """
    # TODO: Calculate expected revenue
    # TODO: Calculate capital charge
    # TODO: Calculate RAROC = (revenue - losses) / capital
    # TODO: Determine if pricing is adequate

    return {
        "expected_revenue": 0.0,  # TODO
        "capital_charge": 0.0,  # TODO
        "expected_loss": expected_loss,
        "raroc": 0.0,  # TODO
        "pricing_adequate": False,  # TODO
    }


# Test with sample data
if __name__ == "__main__":
    # Sample corporate loan: EURIBOR + 2.5%
    decomposition = decompose_loan_spread(
        euribor_rate=0.035,
        total_spread=0.025,
        credit_rating="BBB"
    )
    print(f"Spread decomposition: {decomposition}")

    # RAROC calculation
    raroc = calculate_loan_raroc(
        loan_balance=10_000_000,
        ftp_rate=decomposition["ftp_rate"],
        expected_loss=50_000,  # 0.5% EL
        capital_requirement=0.08  # 8% RWA
    )
    print(f"RAROC analysis: {raroc}")
