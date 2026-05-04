from __future__ import annotations

import pandas as pd
import pytest

from ftp_simulation.balance_sheet.loader import load_balance_sheet
from ftp_simulation.balance_sheet.repricing import (
    derive_repricing_buckets,
    load_repricing_rules,
    validate_repricing_rules,
)
from ftp_simulation.balance_sheet.validation import BalanceSheetValidationError


BALANCE_SHEET_PATH = "data/static/deutsche_bank_balance_sheet_sample.csv"
REPRICING_RULES_PATH = "data/static/repricing_rules_sample.csv"


def test_raw_balance_sheet_does_not_store_repricing_bucket() -> None:
    raw_data = pd.read_csv(BALANCE_SHEET_PATH)

    assert "repricing_bucket" not in raw_data.columns


def test_repricing_rules_derive_bucket_for_every_balance_sheet_row() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    rules = load_repricing_rules(REPRICING_RULES_PATH)

    derived = derive_repricing_buckets(balance_sheet, rules)

    assert len(derived) == len(balance_sheet)
    assert derived["repricing_bucket"].notna().all()
    assert derived["repricing_rule_id"].notna().all()
    assert set(balance_sheet["raw_portfolio"]) == set(derived["raw_portfolio"])


def test_repricing_rule_can_be_challenged_without_changing_raw_balance_sheet() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    rules = pd.read_csv(REPRICING_RULES_PATH)
    rules.loc[rules["rule_id"] == "fixed_3y_5y", "repricing_bucket"] = "5y_plus"

    derived = derive_repricing_buckets(balance_sheet, rules)
    mortgage = derived.loc[derived["raw_portfolio"] == "residential_mortgages_fixed"].iloc[0]

    assert mortgage["repricing_bucket"] == "5y_plus"
    assert mortgage["repricing_mapping_method"] == "duration_proxy"


def test_repricing_derivation_rejects_unmapped_rows() -> None:
    balance_sheet = load_balance_sheet(BALANCE_SHEET_PATH)
    rules = pd.read_csv(REPRICING_RULES_PATH)
    rules = rules[rules["rule_id"] != "fixed_3y_5y"]

    with pytest.raises(BalanceSheetValidationError, match="No repricing rule matched"):
        derive_repricing_buckets(balance_sheet, validate_repricing_rules(rules))
