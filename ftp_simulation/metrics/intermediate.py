"""Intermediate Treasury FTP metrics."""

from __future__ import annotations


def decompose_transfer_pricing_rate(
    base_rate: float,
    liquidity_premium: float,
    term_premium: float,
    credit_spread: float,
    behavioral_adjustment: float,
) -> dict[str, float]:
    """Decompose the FTP rate into explicit Treasury building blocks."""
    raise NotImplementedError


def calculate_behavioral_maturity_adjustment(decay_rate: float) -> float:
    """Estimate effective maturity for non-maturity deposits from a decay rate."""
    raise NotImplementedError


def calculate_duration_gap(duration_assets: float, duration_liabilities: float) -> float:
    """Calculate asset-liability duration mismatch."""
    raise NotImplementedError


def calculate_earnings_at_risk(
    base_net_interest_income: float,
    shocked_net_interest_income: float,
) -> float:
    """Calculate EaR as shocked NII minus base NII."""
    raise NotImplementedError


def calculate_simplified_lcr(hqla: float, net_outflows: float) -> float:
    """Calculate simplified LCR as HQLA divided by net outflows."""
    raise NotImplementedError
