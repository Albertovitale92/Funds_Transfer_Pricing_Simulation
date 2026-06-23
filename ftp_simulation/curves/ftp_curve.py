"""Construction and quotation of decomposed FTP curves."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd


Side = Literal["asset", "liability"]
ProductType = Literal["corporate_loan", "retail_mortgage", "retail_nmd", "corporate_nmd", "wholesale_deposit"]
CounterpartyType = Literal["sovereign", "bank", "corporate", "retail", "secured_mortgage", "wholesale"]


DEFAULT_TARGET_CAPITAL_RATIO = 0.13
DEFAULT_COST_OF_CAPITAL = 0.10


@dataclass(frozen=True)
class ProductFTPRequest:
    """Input needed to quote an FTP rate for one product portfolio."""

    product_name: str
    product_type: ProductType
    side: Side
    balance_eur_m: float
    maturity_years: float
    repricing_years: float | None = None
    deposit_beta: float | None = None
    counterparty_type: CounterpartyType | None = None
    risk_weight_override: float | None = None


def build_sample_market_inputs() -> pd.DataFrame:
    """Create sample FTP inputs by tenor.

    Rates are decimals. For example, 0.035 means 3.50%.
    """
    return pd.DataFrame(
        {
            "tenor": ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "10Y"],
            "maturity_years": [1 / 12, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0],
            "base_curve_rate": [0.0300, 0.0305, 0.0310, 0.0320, 0.0330, 0.0340, 0.0350, 0.0365],
            "bank_funding_spread": [0.0010, 0.0012, 0.0015, 0.0020, 0.0030, 0.0040, 0.0055, 0.0075],
            "liquidity_premium": [0.0005, 0.0007, 0.0010, 0.0015, 0.0022, 0.0030, 0.0040, 0.0060],
        }
    )


def interpolate_curve_component(curve: pd.DataFrame, maturity_years: float, column: str) -> float:
    """Linearly interpolate one curve component at the required maturity."""
    ordered = curve.sort_values("maturity_years")
    tenor_index = pd.Index(ordered["maturity_years"])
    values = ordered[column].to_numpy()

    if maturity_years < tenor_index[0] or maturity_years > tenor_index[-1]:
        raise ValueError(
            f"maturity_years={maturity_years} is outside available curve range "
            f"{tenor_index[0]:.2f}-{tenor_index[-1]:.2f}"
        )

    interpolation_index = tenor_index.union(pd.Index([maturity_years]))
    return float(pd.Series(values, index=tenor_index).reindex(interpolation_index).interpolate().loc[maturity_years])


def construct_ftp_curve(market_inputs: pd.DataFrame) -> pd.DataFrame:
    """Construct an all-in Treasury FTP curve by tenor."""
    curve = market_inputs.copy()
    curve["all_in_ftp_rate"] = (
        curve["base_curve_rate"] + curve["bank_funding_spread"] + curve["liquidity_premium"]
    )
    curve["base_curve_bps"] = curve["base_curve_rate"] * 10_000
    curve["funding_spread_bps"] = curve["bank_funding_spread"] * 10_000
    curve["liquidity_premium_bps"] = curve["liquidity_premium"] * 10_000
    curve["all_in_ftp_bps"] = curve["all_in_ftp_rate"] * 10_000
    return curve


def build_sample_risk_weight_factors() -> pd.DataFrame:
    """Create simplified regulatory capital factors by product and counterparty.

    Risk weights are simplified modelling assumptions, not a CRR calculator.
    """
    return pd.DataFrame(
        {
            "product_type": [
                "corporate_loan",
                "corporate_loan",
                "retail_mortgage",
                "retail_nmd",
                "corporate_nmd",
                "wholesale_deposit",
            ],
            "counterparty_type": [
                "corporate",
                "bank",
                "secured_mortgage",
                "retail",
                "corporate",
                "wholesale",
            ],
            "base_risk_weight": [1.00, 0.50, 0.35, 0.00, 0.00, 0.00],
            "short_maturity_multiplier": [0.90, 0.85, 1.00, 1.00, 1.00, 1.00],
            "long_maturity_multiplier": [1.15, 1.10, 1.05, 1.00, 1.00, 1.00],
        }
    )


def load_risk_weight_factors(path: str = "data/static/regulatory_capital_risk_weights_sample.csv") -> pd.DataFrame:
    """Load simplified regulatory capital factors from CSV."""
    return pd.read_csv(path)


def lookup_risk_weight(product: ProductFTPRequest, risk_weight_factors: pd.DataFrame | None = None) -> float:
    """Return a simplified risk weight for the product quote."""
    if product.risk_weight_override is not None:
        return product.risk_weight_override

    if product.counterparty_type is None:
        return 0.0

    factors = build_sample_risk_weight_factors() if risk_weight_factors is None else risk_weight_factors
    matches = factors[
        (factors["product_type"] == product.product_type)
        & (factors["counterparty_type"] == product.counterparty_type)
    ]
    if matches.empty:
        return 0.0

    row = matches.iloc[0]
    multiplier = 1.0
    if product.maturity_years <= 1.0:
        multiplier = row["short_maturity_multiplier"]
    elif product.maturity_years >= 5.0:
        multiplier = row["long_maturity_multiplier"]

    return float(row["base_risk_weight"] * multiplier)


def regulatory_capital_spread(
    product: ProductFTPRequest,
    risk_weight_factors: pd.DataFrame | None = None,
    target_capital_ratio: float = DEFAULT_TARGET_CAPITAL_RATIO,
    cost_of_capital: float = DEFAULT_COST_OF_CAPITAL,
) -> float:
    """Calculate a simplified annual capital spread.

    Spread = risk weight * target capital ratio * cost of capital.
    """
    risk_weight = lookup_risk_weight(product, risk_weight_factors)
    return risk_weight * target_capital_ratio * cost_of_capital


def product_behavior_adjustment(product: ProductFTPRequest, base_rate: float) -> float:
    """Return product-specific FTP adjustment.

    Positive values increase the FTP rate; negative values reduce it.
    """
    if product.product_type == "retail_mortgage":
        return 0.0015

    if product.product_type == "corporate_loan":
        return 0.0008

    if product.product_type in {"retail_nmd", "corporate_nmd"}:
        beta = product.deposit_beta if product.deposit_beta is not None else 0.5
        return -(1 - beta) * base_rate

    if product.product_type == "wholesale_deposit":
        return 0.0000

    raise ValueError(f"Unsupported product_type: {product.product_type}")


def quote_product_ftp_rate(
    product: ProductFTPRequest,
    ftp_curve: pd.DataFrame,
    risk_weight_factors: pd.DataFrame | None = None,
    target_capital_ratio: float = DEFAULT_TARGET_CAPITAL_RATIO,
    cost_of_capital: float = DEFAULT_COST_OF_CAPITAL,
) -> dict[str, float | str]:
    """Quote an FTP rate and decompose the result."""
    pricing_maturity = product.repricing_years or product.maturity_years

    base_rate = interpolate_curve_component(ftp_curve, pricing_maturity, "base_curve_rate")
    funding_spread = interpolate_curve_component(ftp_curve, pricing_maturity, "bank_funding_spread")
    liquidity_premium = interpolate_curve_component(ftp_curve, pricing_maturity, "liquidity_premium")
    behavior_adjustment = product_behavior_adjustment(product, base_rate)
    capital_spread = regulatory_capital_spread(
        product,
        risk_weight_factors=risk_weight_factors,
        target_capital_ratio=target_capital_ratio,
        cost_of_capital=cost_of_capital,
    )

    all_in_rate = base_rate + funding_spread + liquidity_premium + behavior_adjustment + capital_spread
    annual_ftp_amount_eur_m = product.balance_eur_m * all_in_rate

    return {
        "product_name": product.product_name,
        "side": product.side,
        "pricing_maturity_years": pricing_maturity,
        "base_curve_rate": base_rate,
        "bank_funding_spread": funding_spread,
        "liquidity_premium": liquidity_premium,
        "behavior_adjustment": behavior_adjustment,
        "risk_weight": lookup_risk_weight(product, risk_weight_factors),
        "regulatory_capital_spread": capital_spread,
        "all_in_ftp_rate": all_in_rate,
        "all_in_ftp_bps": all_in_rate * 10_000,
        "annual_ftp_amount_eur_m": annual_ftp_amount_eur_m,
    }


def explain_ftp_quote(quote: dict[str, float | str]) -> str:
    """Create a concise business explanation of the FTP quote."""
    direction = "charge" if quote["side"] == "asset" else "credit"
    return (
        f"{quote['product_name']} receives an FTP {direction} of "
        f"{quote['all_in_ftp_rate']:.2%}. This is built from a "
        f"{quote['base_curve_rate']:.2%} base curve, "
        f"{quote['bank_funding_spread']:.2%} bank funding spread, "
        f"{quote['liquidity_premium']:.2%} liquidity premium, and "
        f"{quote['behavior_adjustment']:.2%} product behavior adjustment, plus "
        f"{quote['regulatory_capital_spread']:.2%} regulatory capital spread."
    )
