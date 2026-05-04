from __future__ import annotations

import pandas as pd
import pytest

from ftp_simulation.balance_sheet.loader import load_balance_sheet
from ftp_simulation.balance_sheet.repricing import load_repricing_rules
from ftp_simulation.balance_sheet.segmentation import load_segmentation, prepare_ftp_balance_sheet
from ftp_simulation.balance_sheet.validation import calculate_totals


BALANCE_SHEET_PATH = "data/static/deutsche_bank_balance_sheet_sample.csv"
REPRICING_RULES_PATH = "data/static/repricing_rules_sample.csv"
SEGMENTATION_PATH = "data/static/portfolio_segmentation_sample.csv"


def test_prepare_ftp_balance_sheet_adds_repricing_and_segmentation_fields() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    repricing_rules = load_repricing_rules(REPRICING_RULES_PATH)
    segmentation = load_segmentation(SEGMENTATION_PATH)

    prepared = prepare_ftp_balance_sheet(balance_sheet, repricing_rules, segmentation)

    assert not prepared["is_control_row"].any()
    assert len(prepared) == (~balance_sheet["is_control_row"]).sum()
    assert {
        "repricing_bucket",
        "repricing_rule_id",
        "repricing_mapping_method",
        "ftp_category",
        "ftp_model_portfolio",
        "ftp_curve",
        "behavioral_model",
        "liquidity_treatment",
        "funding_role",
    }.issubset(prepared.columns)
    assert prepared["repricing_bucket"].notna().all()
    assert prepared["ftp_category"].notna().all()


def test_prepare_ftp_balance_sheet_preserves_detail_totals() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    repricing_rules = load_repricing_rules(REPRICING_RULES_PATH)
    segmentation = load_segmentation(SEGMENTATION_PATH)

    prepared = prepare_ftp_balance_sheet(balance_sheet, repricing_rules, segmentation)
    totals = calculate_totals(balance_sheet)

    assert prepared.loc[prepared["side"] == "asset", "amount_eur_m"].sum() == pytest.approx(totals.total_assets)
    assert prepared.loc[prepared["side"] == "liability", "amount_eur_m"].sum() == pytest.approx(
        totals.total_liabilities
    )


def test_prepare_ftp_balance_sheet_uses_changed_repricing_rules() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    repricing_rules = pd.read_csv(REPRICING_RULES_PATH)
    segmentation = load_segmentation(SEGMENTATION_PATH)
    repricing_rules.loc[repricing_rules["rule_id"] == "fixed_3y_5y", "repricing_bucket"] = "5y_plus"

    prepared = prepare_ftp_balance_sheet(balance_sheet, repricing_rules, segmentation)
    mortgage = prepared.loc[prepared["raw_portfolio"] == "residential_mortgages_fixed"].iloc[0]

    assert mortgage["repricing_bucket"] == "5y_plus"
    assert mortgage["ftp_category"] == "residential_mortgages"
