"""Business validation for balance-sheet data used by the FTP simulator."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import pandera.errors

from ftp_simulation.balance_sheet.schema import BALANCE_SHEET_SCHEMA, CONTROL_RAW_PORTFOLIOS


class BalanceSheetValidationError(ValueError):
    """Raised when balance-sheet data fails FTP business validation."""


@dataclass(frozen=True)
class BalanceSheetTotals:
    asset_detail_sum: float
    total_assets: float
    liability_detail_sum: float
    total_liabilities: float
    total_equity: float
    total_liabilities_and_equity: float


def validate_balance_sheet(data: pd.DataFrame) -> pd.DataFrame:
    """Validate schema and accounting controls for an FTP balance-sheet sample."""
    try:
        validated = BALANCE_SHEET_SCHEMA.validate(data, lazy=True)
    except pandera.errors.SchemaErrors as exc:
        raise BalanceSheetValidationError(str(exc)) from exc

    _validate_single_as_of_date(validated)
    _validate_control_rows(validated)
    totals = calculate_totals(validated)
    _validate_reconciliation(totals)
    return validated


def calculate_totals(data: pd.DataFrame) -> BalanceSheetTotals:
    """Return detail and control totals needed for reconciliation checks."""
    controls = data.set_index("raw_portfolio")["amount_eur_m"]

    asset_detail_sum = data.loc[
        (data["side"] == "asset") & (~data["is_control_row"]),
        "amount_eur_m",
    ].sum()
    liability_detail_sum = data.loc[
        (data["side"] == "liability") & (~data["is_control_row"]),
        "amount_eur_m",
    ].sum()

    return BalanceSheetTotals(
        asset_detail_sum=float(asset_detail_sum),
        total_assets=float(controls["total_assets"]),
        liability_detail_sum=float(liability_detail_sum),
        total_liabilities=float(controls["total_liabilities"]),
        total_equity=float(controls["total_equity"]),
        total_liabilities_and_equity=float(controls["total_liabilities_and_equity"]),
    )


def _validate_single_as_of_date(data: pd.DataFrame) -> None:
    if data["as_of_date"].nunique() != 1:
        raise BalanceSheetValidationError("Balance-sheet file must contain exactly one as_of_date.")


def _validate_control_rows(data: pd.DataFrame) -> None:
    portfolios = set(data["raw_portfolio"])
    missing = sorted(set(CONTROL_RAW_PORTFOLIOS) - portfolios)
    if missing:
        raise BalanceSheetValidationError(f"Missing required control raw portfolio rows: {missing}.")

    for portfolio, expected_side in CONTROL_RAW_PORTFOLIOS.items():
        row = data.loc[data["raw_portfolio"] == portfolio].iloc[0]
        actual_side = row["side"]
        if actual_side != expected_side:
            raise BalanceSheetValidationError(
                f"Control raw portfolio {portfolio!r} must have side {expected_side!r}, got {actual_side!r}."
            )
        if not row["is_control_row"]:
            raise BalanceSheetValidationError(f"Control raw portfolio {portfolio!r} must set is_control_row=true.")


def _validate_reconciliation(totals: BalanceSheetTotals) -> None:
    _assert_close(totals.asset_detail_sum, totals.total_assets, "Asset detail rows do not reconcile to total_assets.")
    _assert_close(
        totals.liability_detail_sum,
        totals.total_liabilities,
        "Liability detail rows do not reconcile to total_liabilities.",
    )
    _assert_close(
        totals.total_liabilities + totals.total_equity,
        totals.total_liabilities_and_equity,
        "Total liabilities plus total equity does not reconcile to total_liabilities_and_equity.",
    )
    _assert_close(
        totals.total_assets,
        totals.total_liabilities_and_equity,
        "Total assets does not reconcile to total liabilities and equity.",
    )


def _assert_close(actual: float, expected: float, message: str, tolerance: float = 0.001) -> None:
    if abs(actual - expected) > tolerance:
        raise BalanceSheetValidationError(f"{message} Actual={actual:.3f}, expected={expected:.3f}.")
