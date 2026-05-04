"""Mapping granular balance-sheet rows into FTP-modelable portfolios."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.errors
import pandera.pandas as pa

from ftp_simulation.balance_sheet.repricing import derive_repricing_buckets
from ftp_simulation.balance_sheet.validation import BalanceSheetValidationError, validate_balance_sheet

DEFAULT_SEGMENTATION_PATH = Path("data/static/portfolio_segmentation_sample.csv")

SEGMENTATION_SCHEMA = pa.DataFrameSchema(
    {
        "raw_portfolio": pa.Column(str, nullable=False, unique=True),
        "ftp_category": pa.Column(str, nullable=False),
        "ftp_model_portfolio": pa.Column(str, nullable=False),
        "ftp_curve": pa.Column(str, nullable=False),
        "behavioral_model": pa.Column(str, nullable=False),
        "liquidity_treatment": pa.Column(str, nullable=False),
        "funding_role": pa.Column(
            str,
            pa.Check.isin({"asset_uses_funding", "liability_provides_funding"}),
            nullable=False,
        ),
        "notes": pa.Column(str, nullable=True),
    },
    strict=True,
    coerce=True,
)


def load_segmentation(path: str | Path = DEFAULT_SEGMENTATION_PATH, *, validate: bool = True) -> pd.DataFrame:
    """Load raw-portfolio to FTP-model mapping assumptions."""
    data = pd.read_csv(path)
    if validate:
        return validate_segmentation(data)
    return data


def validate_segmentation(segmentation: pd.DataFrame, balance_sheet: pd.DataFrame | None = None) -> pd.DataFrame:
    """Validate segmentation mapping and, if supplied, full raw-row coverage."""
    try:
        validated = SEGMENTATION_SCHEMA.validate(segmentation, lazy=True)
    except pandera.errors.SchemaErrors as exc:
        raise BalanceSheetValidationError(str(exc)) from exc

    if balance_sheet is not None:
        valid_balance_sheet = validate_balance_sheet(balance_sheet)
        _validate_mapping_coverage(validated, valid_balance_sheet)
        _validate_funding_role_consistency(validated, valid_balance_sheet)

    return validated


def map_balance_sheet_to_ftp_categories(balance_sheet: pd.DataFrame, segmentation: pd.DataFrame) -> pd.DataFrame:
    """Attach FTP category, curve, and behavioral model fields to granular balance-sheet rows."""
    valid_balance_sheet = validate_balance_sheet(balance_sheet)
    valid_segmentation = validate_segmentation(segmentation, valid_balance_sheet)
    detail_rows = valid_balance_sheet[~valid_balance_sheet["is_control_row"]].copy()

    mapped = detail_rows.merge(valid_segmentation, on="raw_portfolio", how="left", validate="one_to_one")
    if mapped["ftp_category"].isna().any():
        missing = sorted(mapped.loc[mapped["ftp_category"].isna(), "raw_portfolio"].unique())
        raise BalanceSheetValidationError(f"Balance-sheet raw portfolios missing FTP mapping: {missing}.")

    return mapped


def prepare_ftp_balance_sheet(
    balance_sheet: pd.DataFrame,
    repricing_rules: pd.DataFrame,
    segmentation: pd.DataFrame,
) -> pd.DataFrame:
    """Return detail rows enriched with derived repricing buckets and FTP segmentation assumptions."""
    valid_balance_sheet = validate_balance_sheet(balance_sheet)
    repriced_balance_sheet = derive_repricing_buckets(valid_balance_sheet, repricing_rules)
    valid_segmentation = validate_segmentation(segmentation, valid_balance_sheet)
    detail_rows = repriced_balance_sheet[~repriced_balance_sheet["is_control_row"]].copy()

    prepared = detail_rows.merge(valid_segmentation, on="raw_portfolio", how="left", validate="one_to_one")
    if prepared["ftp_category"].isna().any():
        missing = sorted(prepared.loc[prepared["ftp_category"].isna(), "raw_portfolio"].unique())
        raise BalanceSheetValidationError(f"Balance-sheet raw portfolios missing FTP mapping: {missing}.")

    return prepared


def summarize_by_ftp_category(mapped_balance_sheet: pd.DataFrame) -> pd.DataFrame:
    """Aggregate mapped balance-sheet balances by FTP category and side."""
    return (
        mapped_balance_sheet.groupby(["side", "ftp_category"], as_index=False)["amount_eur_m"]
        .sum()
        .sort_values(["side", "ftp_category"])
        .reset_index(drop=True)
    )


def _validate_mapping_coverage(segmentation: pd.DataFrame, balance_sheet: pd.DataFrame) -> None:
    raw_portfolios = set(balance_sheet.loc[~balance_sheet["is_control_row"], "raw_portfolio"])
    mapped_portfolios = set(segmentation["raw_portfolio"])

    missing = sorted(raw_portfolios - mapped_portfolios)
    if missing:
        raise BalanceSheetValidationError(f"Balance-sheet raw portfolios missing FTP mapping: {missing}.")

    unknown = sorted(mapped_portfolios - raw_portfolios)
    if unknown:
        raise BalanceSheetValidationError(f"Segmentation references unknown raw portfolios: {unknown}.")


def _validate_funding_role_consistency(segmentation: pd.DataFrame, balance_sheet: pd.DataFrame) -> None:
    detail_rows = balance_sheet.loc[~balance_sheet["is_control_row"], ["raw_portfolio", "side"]]
    mapped = detail_rows.merge(segmentation[["raw_portfolio", "funding_role"]], on="raw_portfolio", validate="one_to_one")

    invalid_asset_roles = mapped.loc[
        (mapped["side"] == "asset") & (mapped["funding_role"] != "asset_uses_funding"),
        "raw_portfolio",
    ]
    invalid_liability_roles = mapped.loc[
        (mapped["side"] == "liability") & (mapped["funding_role"] != "liability_provides_funding"),
        "raw_portfolio",
    ]

    invalid = sorted(set(invalid_asset_roles).union(invalid_liability_roles))
    if invalid:
        raise BalanceSheetValidationError(f"Segmentation funding_role is inconsistent with balance-sheet side: {invalid}.")
