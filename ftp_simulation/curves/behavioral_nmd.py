"""Behavioral non-maturity deposit (NMD) curve utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class NMDAssumptions:
    """Assumptions for non-maturity deposit repricing behavior."""

    deposit_type: str  # "retail", "corporate", "wholesale"
    beta: float  # Repricing sensitivity (0 = no repricing, 1 = full repricing)
    half_life_years: float  # Time for beta to decay to 0.5
    min_maturity_years: float  # Effective minimum maturity
    max_maturity_years: float  # Effective maximum maturity
    notes: str = ""

    def __repr__(self) -> str:
        return (
            f"NMDAssumptions(type={self.deposit_type!r}, beta={self.beta}, "
            f"half_life={self.half_life_years}y, range=[{self.min_maturity_years}y, {self.max_maturity_years}y])"
        )


# Standard NMD behavioral profiles
RETAIL_NMD = NMDAssumptions(
    deposit_type="retail",
    beta=0.5,
    half_life_years=2.0,
    min_maturity_years=1.0,
    max_maturity_years=5.0,
    notes="Stable retail deposits; slow repricing due to switching costs and inertia.",
)

CORPORATE_NMD = NMDAssumptions(
    deposit_type="corporate",
    beta=0.7,
    half_life_years=1.0,
    min_maturity_years=0.5,
    max_maturity_years=2.0,
    notes="Corporate operational deposits; faster repricing; intermediate stickiness.",
)

WHOLESALE_NMD = NMDAssumptions(
    deposit_type="wholesale",
    beta=0.95,
    half_life_years=0.25,
    min_maturity_years=0.25,
    max_maturity_years=1.0,
    notes="Wholesale fragile deposits; reprices quickly with market conditions.",
)


def calculate_effective_maturity(
    balance_eur_m: float,
    deposit_type: str = "retail",
    rate_change_pct: float = 0.0,
) -> dict[str, float]:
    """Calculate effective maturity of an NMD portfolio under assumptions.

    Effective maturity reflects when deposits are expected to reprice on average,
    accounting for customer stickiness and behavioral decay over time.

    Args:
        balance_eur_m: Balance in EUR millions.
        deposit_type: One of "retail", "corporate", "wholesale".
        rate_change_pct: Hypothetical rate change (%) to test behavioral response.

    Returns:
        Dictionary with effective maturity and related metrics.
    """
    if deposit_type == "retail":
        assumptions = RETAIL_NMD
    elif deposit_type == "corporate":
        assumptions = CORPORATE_NMD
    elif deposit_type == "wholesale":
        assumptions = WHOLESALE_NMD
    else:
        raise ValueError(f"Unknown deposit_type: {deposit_type!r}")

    # Effective maturity = min + (max - min) * (1 - initial_beta)
    # This reflects the range of repricing times weighted by stickiness
    effective_maturity = assumptions.min_maturity_years + (
        assumptions.max_maturity_years - assumptions.min_maturity_years
    ) * (1 - assumptions.beta)

    # Behavioral adjustment: if rates are rising, deposits flee faster (shorter maturity)
    # If rates are falling, deposits stick around longer (longer maturity)
    behavioral_adjustment = 0.0
    if rate_change_pct > 0:
        # Rising rates: deposits reprice faster (become shorter)
        behavioral_adjustment = -0.1 * assumptions.beta  # Up to 10% reduction in maturity
    elif rate_change_pct < 0:
        # Falling rates: deposits reprice slower (become longer)
        behavioral_adjustment = 0.1 * (1 - assumptions.beta)  # Up to 10% extension

    adjusted_effective_maturity = effective_maturity + behavioral_adjustment

    return {
        "deposit_type": deposit_type,
        "balance_eur_m": balance_eur_m,
        "beta": assumptions.beta,
        "min_maturity_years": assumptions.min_maturity_years,
        "max_maturity_years": assumptions.max_maturity_years,
        "effective_maturity_years": effective_maturity,
        "rate_change_pct": rate_change_pct,
        "behavioral_adjustment": behavioral_adjustment,
        "adjusted_effective_maturity_years": adjusted_effective_maturity,
    }


def decay_beta_over_time(
    initial_beta: float,
    time_years: float,
    half_life_years: float = 2.0,
) -> float:
    """Calculate beta decay using exponential half-life model.

    Beta represents the sensitivity of deposit repricing to market rate changes.
    Over time, beta decays (deposits become stickier) as customers internalize
    the new rate environment.

    Args:
        initial_beta: Starting beta (e.g., 0.5 for retail).
        time_years: Time elapsed (years).
        half_life_years: Time for beta to decay to half its value.

    Returns:
        Beta value at `time_years`.
    """
    if time_years < 0:
        raise ValueError("time_years must be non-negative")
    if half_life_years <= 0:
        raise ValueError("half_life_years must be positive")

    decay_factor = 0.5 ** (time_years / half_life_years)
    return initial_beta * decay_factor


def compute_nmd_repricing_ladder(
    balance_eur_m: float,
    deposit_type: str = "retail",
    initial_beta: float | None = None,
) -> pd.DataFrame:
    """Build a repricing ladder for NMD balances over time.

    This models how an NMD portfolio reprices over 5 years based on behavioral
    assumptions. Used for IRRBB and duration calculations.

    Args:
        balance_eur_m: Total NMD balance in EUR millions.
        deposit_type: One of "retail", "corporate", "wholesale".
        initial_beta: Override initial beta (if None, use profile default).

    Returns:
        DataFrame with repricing schedule (time, balance, beta, repriced_amount).
    """
    if deposit_type == "retail":
        assumptions = RETAIL_NMD
    elif deposit_type == "corporate":
        assumptions = CORPORATE_NMD
    elif deposit_type == "wholesale":
        assumptions = WHOLESALE_NMD
    else:
        raise ValueError(f"Unknown deposit_type: {deposit_type!r}")

    beta = initial_beta if initial_beta is not None else assumptions.beta
    rows = []

    # Model repricing over 5 years, quarterly
    for quarter in range(0, 21):  # 5 years * 4 quarters
        time_years = quarter / 4.0
        current_beta = decay_beta_over_time(beta, time_years, assumptions.half_life_years)

        # Repricing happens when beta decays; cumulative repricing increases
        repriced_amount = balance_eur_m * (1.0 - current_beta)

        rows.append(
            {
                "quarter": quarter,
                "time_years": time_years,
                "balance_eur_m": balance_eur_m,
                "current_beta": current_beta,
                "repriced_cumulative_eur_m": repriced_amount,
                "unreppriced_balance_eur_m": balance_eur_m - repriced_amount,
            }
        )

    return pd.DataFrame(rows)


def estimate_loan_equivalent_maturity(
    portfolio_df: pd.DataFrame,
    deposit_type: str = "retail",
) -> float:
    """Estimate equivalent maturity for an NMD portfolio using beta decay.

    This is used to assign the NMD portfolio to repricing buckets in the
    FTP balance sheet.

    Args:
        portfolio_df: DataFrame with repricing ladder from `compute_nmd_repricing_ladder`.
        deposit_type: Deposit type (used for naming only).

    Returns:
        Estimated equivalent maturity in years.
    """
    if portfolio_df.empty:
        return 0.0

    # Find the time at which 50% of balance has repriced
    half_repriced = portfolio_df[
        portfolio_df["repriced_cumulative_eur_m"] >= portfolio_df["balance_eur_m"].iloc[0] / 2
    ]

    if half_repriced.empty:
        # If not 50% repriced in 5 years, use the max
        return portfolio_df["time_years"].max()

    return half_repriced["time_years"].iloc[0]

