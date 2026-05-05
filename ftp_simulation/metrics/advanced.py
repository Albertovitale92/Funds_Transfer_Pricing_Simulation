"""Advanced FTP, value, and IRRBB metrics."""

from __future__ import annotations


def calculate_shareholder_value_added(
    nopat: float,
    wacc: float,
    allocated_capital: float,
) -> float:
    """Calculate SVA as NOPAT minus the cost of allocated capital."""
    raise NotImplementedError


def explain_marginal_vs_average_ftp() -> dict[str, float]:
    """Compare marginal and average FTP effects for portfolio changes."""
    raise NotImplementedError


def explain_ftp_pnl() -> dict[str, float]:
    """Explain FTP P&L by volume, rate, mix, and curve-shift effects."""
    raise NotImplementedError


def calculate_product_irr(cash_flows: list[float]) -> float:
    """Calculate product IRR for instruments with multiple cash flows."""
    raise NotImplementedError


def calculate_economic_value_of_equity() -> float:
    """Calculate EVE for IRRBB economic-value sensitivity."""
    raise NotImplementedError
