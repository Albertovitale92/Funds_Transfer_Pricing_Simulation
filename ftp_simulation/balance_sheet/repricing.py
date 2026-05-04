"""Configurable repricing-bucket derivation for balance-sheet rows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.errors
import pandera.pandas as pa

from ftp_simulation.balance_sheet.validation import BalanceSheetValidationError, validate_balance_sheet

DEFAULT_REPRICING_RULES_PATH = Path("data/static/repricing_rules_sample.csv")
WILDCARD = "*"

RULE_MATCH_COLUMNS = [
    "raw_portfolio",
    "side",
    "product_type",
    "rate_type",
    "interest_rate_index",
    "contractual_repricing_frequency",
    "fixed_rate_period_bucket",
    "amortization_profile",
    "behavioral_profile",
    "valuation_basis",
    "contractual_maturity_bucket",
]

REPRICING_RULES_SCHEMA = pa.DataFrameSchema(
    {
        "rule_id": pa.Column(str, nullable=False, unique=True),
        "priority": pa.Column(int, pa.Check.ge(0), nullable=False, coerce=True),
        **{column: pa.Column(str, nullable=False) for column in RULE_MATCH_COLUMNS},
        "repricing_bucket": pa.Column(str, nullable=False),
        "mapping_method": pa.Column(str, nullable=False),
        "notes": pa.Column(str, nullable=True),
    },
    strict=True,
    coerce=True,
)


def load_repricing_rules(path: str | Path = DEFAULT_REPRICING_RULES_PATH, *, validate: bool = True) -> pd.DataFrame:
    """Load editable assumptions used to derive repricing buckets."""
    data = pd.read_csv(path)
    if validate:
        return validate_repricing_rules(data)
    return data


def validate_repricing_rules(rules: pd.DataFrame) -> pd.DataFrame:
    """Validate the repricing-rule table."""
    try:
        return REPRICING_RULES_SCHEMA.validate(rules, lazy=True).sort_values("priority").reset_index(drop=True)
    except pandera.errors.SchemaErrors as exc:
        raise BalanceSheetValidationError(str(exc)) from exc


def derive_repricing_buckets(balance_sheet: pd.DataFrame, rules: pd.DataFrame) -> pd.DataFrame:
    """Attach derived repricing buckets using the first matching rule by priority."""
    valid_balance_sheet = validate_balance_sheet(balance_sheet)
    valid_rules = validate_repricing_rules(rules)

    derived_rows = []
    for _, row in valid_balance_sheet.iterrows():
        rule = _find_first_matching_rule(row, valid_rules)
        if rule is None:
            raise BalanceSheetValidationError(
                f"No repricing rule matched raw portfolio {row['raw_portfolio']!r}."
            )

        derived = row.copy()
        derived["repricing_bucket"] = rule["repricing_bucket"]
        derived["repricing_rule_id"] = rule["rule_id"]
        derived["repricing_mapping_method"] = rule["mapping_method"]
        derived_rows.append(derived)

    return pd.DataFrame(derived_rows).reset_index(drop=True)


def _find_first_matching_rule(row: pd.Series, rules: pd.DataFrame) -> pd.Series | None:
    for _, rule in rules.iterrows():
        if all(rule[column] == WILDCARD or rule[column] == row[column] for column in RULE_MATCH_COLUMNS):
            return rule
    return None
