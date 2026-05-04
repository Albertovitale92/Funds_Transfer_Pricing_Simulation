from __future__ import annotations

import pandas as pd
import pytest

from ftp_simulation.balance_sheet.loader import load_balance_sheet
from ftp_simulation.balance_sheet.segmentation import (
    load_segmentation,
    map_balance_sheet_to_ftp_categories,
    summarize_by_ftp_category,
    validate_segmentation,
)
from ftp_simulation.balance_sheet.validation import BalanceSheetValidationError, calculate_totals


BALANCE_SHEET_PATH = "data/static/deutsche_bank_balance_sheet_sample.csv"
SEGMENTATION_PATH = "data/static/portfolio_segmentation_sample.csv"


def test_sample_segmentation_covers_every_non_control_raw_portfolio() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    segmentation = load_segmentation(SEGMENTATION_PATH)

    validated = validate_segmentation(segmentation, balance_sheet)
    raw_detail_count = (~balance_sheet["is_control_row"]).sum()

    assert len(validated) == raw_detail_count


def test_segmentation_rejects_unknown_raw_portfolio() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    segmentation = pd.read_csv(SEGMENTATION_PATH)
    segmentation.loc[0, "raw_portfolio"] = "unknown_raw_portfolio"

    with pytest.raises(BalanceSheetValidationError, match="missing FTP mapping"):
        validate_segmentation(segmentation, balance_sheet)


def test_segmentation_rejects_missing_raw_portfolio_mapping() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    segmentation = pd.read_csv(SEGMENTATION_PATH)
    segmentation = segmentation[segmentation["raw_portfolio"] != "corporate_term_loans"]

    with pytest.raises(BalanceSheetValidationError, match="missing FTP mapping"):
        validate_segmentation(segmentation, balance_sheet)


def test_segmentation_rejects_funding_role_inconsistent_with_side() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    segmentation = pd.read_csv(SEGMENTATION_PATH)
    segmentation.loc[segmentation["raw_portfolio"] == "corporate_term_loans", "funding_role"] = (
        "liability_provides_funding"
    )

    with pytest.raises(BalanceSheetValidationError, match="funding_role is inconsistent"):
        validate_segmentation(segmentation, balance_sheet)


def test_mapping_preserves_balance_sheet_totals() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    segmentation = load_segmentation(SEGMENTATION_PATH)

    mapped = map_balance_sheet_to_ftp_categories(balance_sheet, segmentation)
    totals = calculate_totals(balance_sheet)

    assert mapped.loc[mapped["side"] == "asset", "amount_eur_m"].sum() == pytest.approx(totals.total_assets)
    assert mapped.loc[mapped["side"] == "liability", "amount_eur_m"].sum() == pytest.approx(totals.total_liabilities)


def test_summarize_by_ftp_category_keeps_asset_and_liability_balances() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    segmentation = load_segmentation(SEGMENTATION_PATH)

    mapped = map_balance_sheet_to_ftp_categories(balance_sheet, segmentation)
    summary = summarize_by_ftp_category(mapped)

    assert {"side", "ftp_category", "amount_eur_m"} == set(summary.columns)
    assert summary.loc[summary["side"] == "asset", "amount_eur_m"].sum() == pytest.approx(
        mapped.loc[mapped["side"] == "asset", "amount_eur_m"].sum()
    )
    assert summary.loc[summary["side"] == "liability", "amount_eur_m"].sum() == pytest.approx(
        mapped.loc[mapped["side"] == "liability", "amount_eur_m"].sum()
    )
