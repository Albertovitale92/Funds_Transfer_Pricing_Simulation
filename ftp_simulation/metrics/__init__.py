"""FTP metric calculation skeletons."""

from ftp_simulation.metrics.advanced import (
    calculate_economic_value_of_equity,
    calculate_product_irr,
    calculate_shareholder_value_added,
    explain_marginal_vs_average_ftp,
    explain_ftp_pnl,
)
from ftp_simulation.metrics.core import (
    calculate_capital_charge,
    calculate_ftp_spread,
    calculate_liquidity_premium,
    calculate_net_interest_margin,
    calculate_net_product_margin,
)
from ftp_simulation.metrics.intermediate import (
    calculate_behavioral_maturity_adjustment,
    calculate_duration_gap,
    calculate_earnings_at_risk,
    calculate_simplified_lcr,
    decompose_transfer_pricing_rate,
)

__all__ = [
    "calculate_behavioral_maturity_adjustment",
    "calculate_capital_charge",
    "calculate_duration_gap",
    "calculate_earnings_at_risk",
    "calculate_economic_value_of_equity",
    "calculate_ftp_spread",
    "calculate_liquidity_premium",
    "calculate_net_interest_margin",
    "calculate_net_product_margin",
    "calculate_product_irr",
    "calculate_shareholder_value_added",
    "calculate_simplified_lcr",
    "decompose_transfer_pricing_rate",
    "explain_marginal_vs_average_ftp",
    "explain_ftp_pnl",
]
