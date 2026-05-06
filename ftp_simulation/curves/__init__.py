"""FTP curve management and application to balance-sheet portfolios."""

from __future__ import annotations

import pandas as pd
import pandera.pandas as pa

from ftp_simulation.curves.behavioral_nmd import (
    NMDAssumptions,
    RETAIL_NMD,
    CORPORATE_NMD,
    WHOLESALE_NMD,
    calculate_effective_maturity,
    decay_beta_over_time,
    compute_nmd_repricing_ladder,
    estimate_loan_equivalent_maturity,
)


CURVE_TAXONOMY_SCHEMA = pa.DataFrameSchema(
    {
        "curve_name": pa.Column(str, nullable=False, unique=True),
        "curve_type": pa.Column(str, nullable=False),
        "currency": pa.Column(str, nullable=False),
        "base_rate_type": pa.Column(str, nullable=False),
        "maturity_range": pa.Column(str, nullable=False),
        "liquidity_premium": pa.Column(str, nullable=False),
        "credit_spread": pa.Column(str, nullable=False),
        "behavioral_model": pa.Column(str, nullable=True),
        "regulatory_component": pa.Column(str, nullable=True),
        "usage": pa.Column(str, nullable=False),
        "data_source": pa.Column(str, nullable=False),
        "update_frequency": pa.Column(str, nullable=False),
        "learning_objective": pa.Column(str, nullable=False),
        "interview_relevance": pa.Column(str, nullable=False),
        "implementation_status": pa.Column(str, nullable=False),
        "remarks": pa.Column(str, nullable=True),
    },
    strict=True,
    coerce=True,
)


def load_curve_taxonomy(path: str | pd.DataFrame = "data/static/ftp_curve_taxonomy.csv") -> pd.DataFrame:
    """Load FTP curve taxonomy from CSV.

    Args:
        path: Path to CSV file or a pre-loaded DataFrame.

    Returns:
        Validated curve taxonomy DataFrame.
    """
    if isinstance(path, pd.DataFrame):
        data = path.copy()
    else:
        data = pd.read_csv(path)

    return CURVE_TAXONOMY_SCHEMA.validate(data, lazy=True)


def summarize_curve_taxonomy(taxonomy: pd.DataFrame) -> dict[str, list]:
    """Summarize curve taxonomy by implementation status and type.

    Args:
        taxonomy: Loaded curve taxonomy DataFrame.

    Returns:
        Dictionary with summary counts and lists.
    """
    return {
        "total_curves": len(taxonomy),
        "by_type": taxonomy["curve_type"].value_counts().to_dict(),
        "by_status": taxonomy["implementation_status"].value_counts().to_dict(),
        "by_currency": taxonomy["currency"].value_counts().to_dict(),
    }


__all__ = [
    "load_curve_taxonomy",
    "summarize_curve_taxonomy",
    "NMDAssumptions",
    "RETAIL_NMD",
    "CORPORATE_NMD",
    "WHOLESALE_NMD",
    "calculate_effective_maturity",
    "decay_beta_over_time",
    "compute_nmd_repricing_ladder",
    "estimate_loan_equivalent_maturity",
]
