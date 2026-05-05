"""Core FTP metrics.

These functions intentionally define the first calculation surface without
committing to final input schemas. They should later be wired to prepared FTP
balance-sheet rows, FTP curve assumptions, and scenario outputs.
"""

from __future__ import annotations


def calculate_net_interest_margin(
    interest_income: float,
    interest_expense: float,
    earning_assets: float,
) -> float:
    """Calculate NIM as (interest income - interest expense) / earning assets."""
    raise NotImplementedError


def calculate_ftp_spread(product_rate: float, ftp_rate: float) -> float:
    """Calculate FTP spread as product rate minus FTP rate."""
    raise NotImplementedError


def calculate_liquidity_premium(ftp_rate: float, base_curve_rate: float) -> float:
    """Calculate liquidity premium as FTP rate minus base curve rate."""
    raise NotImplementedError


def calculate_capital_charge(rwa: float, cost_of_capital: float) -> float:
    """Calculate RWA-based capital charge."""
    raise NotImplementedError


def calculate_net_product_margin(
    product_revenue: float,
    ftp_cost: float,
    capital_charge: float,
) -> float:
    """Calculate net product margin after FTP cost and capital charge."""
    raise NotImplementedError
