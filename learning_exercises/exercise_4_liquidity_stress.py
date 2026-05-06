# Learning Exercise 4: Liquidity Stress Scenario
# ============================================
#
# Objective: Calculate LCR outflows under stress (how deposits flee during crisis).
#
# What to implement:
# - LCR outflow rates by deposit type
# - Stress-adjusted beta decay
# - High-quality liquid assets (HQLA) buffer calculation
#
# Data Sources:
# - Deposit balances: From balance sheet data
# - LCR assumptions: Regulatory guidelines (retail stable: 5-10%, wholesale: 75-90%)
# - HQLA assets: Central bank reserves, government bonds
#
# Hints:
# 1. LCR = HQLA / Net Outflows over 30 days
# 2. Outflow rates: Retail deposits (3-10%), corporate (10-25%), wholesale (75-100%)
# 3. Stress beta: Increase decay rate during crisis
# 4. Test with different stress scenarios (mild, severe)
#
# Expected Output:
# - 30-day outflow projection
# - LCR ratio calculation
# - Liquidity gap analysis
#
# Self-Assessment:
# - Why are retail deposits more stable than wholesale?
# - How does LCR affect FTP pricing?
# - What happens if LCR falls below 100%?

def calculate_lcr_outflows(deposit_balances: dict[str, float], stress_level: str = "normal") -> dict[str, float]:
    """Calculate LCR outflows by deposit type.

    Args:
        deposit_balances: Dict of deposit_type -> balance
        stress_level: "normal", "mild_stress", "severe_stress"

    Returns:
        Dictionary with outflow amounts by type
    """
    # LCR outflow assumptions (%)
    outflow_rates = {
        "normal": {"retail": 0.05, "corporate": 0.10, "wholesale": 0.75},
        "mild_stress": {"retail": 0.08, "corporate": 0.15, "wholesale": 0.85},
        "severe_stress": {"retail": 0.10, "corporate": 0.25, "wholesale": 1.00},
    }

    rates = outflow_rates.get(stress_level, outflow_rates["normal"])

    # TODO: Calculate outflows for each deposit type
    # TODO: Sum total outflows
    # TODO: Return detailed breakdown

    return {
        "retail_outflow": 0.0,  # TODO
        "corporate_outflow": 0.0,  # TODO
        "wholesale_outflow": 0.0,  # TODO
        "total_outflow": 0.0,  # TODO
    }


def calculate_lcr_ratio(hqla_balance: float, outflows: dict[str, float], inflows: float = 0.0) -> dict[str, float]:
    """Calculate LCR ratio.

    Args:
        hqla_balance: High-quality liquid assets
        outflows: Outflow amounts
        inflows: Expected inflows (reduce net outflows)

    Returns:
        LCR ratio and components
    """
    net_outflows = outflows["total_outflow"] - inflows

    # TODO: Calculate LCR ratio = HQLA / Net Outflows
    # TODO: Handle division by zero
    # TODO: Return ratio and components

    return {
        "hqla": hqla_balance,
        "net_outflows": net_outflows,
        "lcr_ratio": 0.0,  # TODO
        "lcr_percent": 0.0,  # TODO
    }


# Test with sample data
if __name__ == "__main__":
    # Sample deposit balances (€M)
    deposits = {
        "retail": 305_000,
        "corporate": 165_000,
        "wholesale": 66_658,
    }

    outflows = calculate_lcr_outflows(deposits, stress_level="severe_stress")
    print(f"LCR outflows: {outflows}")

    # Assume €130B HQLA (central bank reserves)
    lcr = calculate_lcr_ratio(hqla_balance=130_000, outflows=outflows)
    print(f"LCR ratio: {lcr['lcr_percent']:.1f}%")
