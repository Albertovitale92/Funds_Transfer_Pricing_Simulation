from __future__ import annotations

import pandas as pd
import pytest

from ftp_simulation.balance_sheet.loader import load_balance_sheet
from ftp_simulation.balance_sheet.validation import BalanceSheetValidationError, calculate_totals, validate_balance_sheet


SAMPLE_PATH = "data/static/deutsche_bank_balance_sheet_sample.csv"


def test_sample_balance_sheet_loads_and_reconciles() -> None:
    data = load_balance_sheet(SAMPLE_PATH)

    totals = calculate_totals(data)

    assert len(data) == 59
    assert totals.asset_detail_sum == totals.total_assets
    assert totals.liability_detail_sum == totals.total_liabilities
    assert totals.total_liabilities + totals.total_equity == totals.total_liabilities_and_equity


def test_rejects_invalid_side() -> None:
    data = pd.read_csv(SAMPLE_PATH)
    data.loc[data["raw_portfolio"] == "corporate_term_loans", "side"] = "asset_liability"

    with pytest.raises(BalanceSheetValidationError):
        validate_balance_sheet(data)


def test_rejects_broken_asset_total() -> None:
    data = pd.read_csv(SAMPLE_PATH)
    data.loc[data["raw_portfolio"] == "corporate_term_loans", "amount_eur_m"] += 1

    with pytest.raises(BalanceSheetValidationError, match="Asset detail rows"):
        validate_balance_sheet(data)


def test_rejects_missing_control_row() -> None:
    data = pd.read_csv(SAMPLE_PATH)
    data = data[data["raw_portfolio"] != "total_equity"]

    with pytest.raises(BalanceSheetValidationError, match="Missing required control raw portfolio rows"):
        validate_balance_sheet(data)


def test_rejects_multiple_as_of_dates() -> None:
    data = pd.read_csv(SAMPLE_PATH)
    data.loc[data["raw_portfolio"] == "corporate_term_loans", "as_of_date"] = "2026-04-30"

    with pytest.raises(BalanceSheetValidationError, match="exactly one as_of_date"):
        validate_balance_sheet(data)
