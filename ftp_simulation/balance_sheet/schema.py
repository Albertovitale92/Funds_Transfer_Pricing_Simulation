"""Schema definitions for FTP balance-sheet input data."""

from __future__ import annotations

import pandera.pandas as pa

REQUIRED_COLUMNS = [
    "as_of_date",
    "source_institution",
    "source_report",
    "source_url",
    "public_report_line",
    "raw_portfolio",
    "statement_line",
    "side",
    "business_line",
    "product_type",
    "currency",
    "amount_eur_m",
    "contractual_maturity_bucket",
    "rate_type",
    "interest_rate_index",
    "contractual_repricing_frequency",
    "fixed_rate_period_bucket",
    "amortization_profile",
    "behavioral_profile",
    "valuation_basis",
    "secured_unsecured",
    "counterparty_type",
    "behavioral_hint",
    "is_control_row",
    "notes",
]

ALLOWED_SIDES = {
    "asset",
    "liability",
    "equity",
    "liability_and_equity",
}

CONTROL_RAW_PORTFOLIOS = {
    "total_assets": "asset",
    "total_liabilities": "liability",
    "total_equity": "equity",
    "total_liabilities_and_equity": "liability_and_equity",
}

BALANCE_SHEET_SCHEMA = pa.DataFrameSchema(
    {
        "as_of_date": pa.Column(pa.DateTime, nullable=False, coerce=True),
        "source_institution": pa.Column(str, nullable=False),
        "source_report": pa.Column(str, nullable=False),
        "source_url": pa.Column(str, nullable=False),
        "public_report_line": pa.Column(str, nullable=False),
        "raw_portfolio": pa.Column(str, nullable=False, unique=True),
        "statement_line": pa.Column(str, nullable=False),
        "side": pa.Column(str, pa.Check.isin(ALLOWED_SIDES), nullable=False),
        "business_line": pa.Column(str, nullable=False),
        "product_type": pa.Column(str, nullable=False),
        "currency": pa.Column(str, nullable=False),
        "amount_eur_m": pa.Column(float, pa.Check.ge(0), nullable=False, coerce=True),
        "contractual_maturity_bucket": pa.Column(str, nullable=False),
        "rate_type": pa.Column(str, nullable=False),
        "interest_rate_index": pa.Column(str, nullable=False),
        "contractual_repricing_frequency": pa.Column(str, nullable=False),
        "fixed_rate_period_bucket": pa.Column(str, nullable=False),
        "amortization_profile": pa.Column(str, nullable=False),
        "behavioral_profile": pa.Column(str, nullable=False),
        "valuation_basis": pa.Column(str, nullable=False),
        "secured_unsecured": pa.Column(str, nullable=False),
        "counterparty_type": pa.Column(str, nullable=False),
        "behavioral_hint": pa.Column(str, nullable=False),
        "is_control_row": pa.Column(bool, nullable=False, coerce=True),
        "notes": pa.Column(str, nullable=True),
    },
    checks=[
        pa.Check(lambda df: set(REQUIRED_COLUMNS).issubset(df.columns), error="Missing required balance-sheet columns."),
    ],
    strict=True,
    coerce=True,
)
