# Learning Exercise 1: ECB Corridor Calculation
# ============================================
#
# Objective: Understand how the ECB interest rate corridor guides overnight funding costs.
#
# What to implement:
# - Function to calculate corridor width between DFR (floor) and MLF (ceiling)
# - Estimate ESTR trading range within the corridor
# - Explain funding implications for banks
#
# Data Sources:
# - ECB rates: Use hypothetical values (DFR=4.5%, MRO=4.75%, MLF=5.0%)
# - No external data needed - rates are administered by ECB
#
# Hints:
# 1. Corridor width = MLF - DFR (in bps: multiply by 10000)
# 2. ESTR typically trades 3-10 bps inside the corridor
# 3. Banks won't lend below DFR or borrow above MLF
# 4. Test with different corridor widths (narrow: 25bps, wide: 200bps)
#
# Expected Output:
# - Dictionary with rates, width, ESTR range, implications
#
# Self-Assessment:
# - Can you explain why ECB uses a corridor?
# - How does corridor width affect interbank liquidity?
# - What happens if MLF = DFR (zero corridor)?

def calculate_ecb_corridor(dfr: float, mro: float, mlf: float) -> dict:
    """Calculate ECB interest rate corridor and implications.

    Args:
        dfr: Deposit facility rate (floor)
        mro: Main refinancing operations rate (central)
        mlf: Marginal lending facility rate (ceiling)

    Returns:
        Dictionary with corridor analysis
    """
    # TODO: Implement corridor width calculation
    # TODO: Estimate ESTR trading range
    # TODO: Generate funding implications text

    return {
        "dfr": dfr,
        "mro": mro,
        "mlf": mlf,
        "corridor_width_bps": 0.0,  # TODO
        "est_interbank_range": "0.000 - 0.000",  # TODO
        "funding_implications": "TODO: Explain implications",  # TODO
    }


# Test with sample data
if __name__ == "__main__":
    result = calculate_ecb_corridor(dfr=0.045, mro=0.0475, mlf=0.050)
    print("ECB Corridor Analysis:")
    for key, value in result.items():
        print(f"{key}: {value}")
