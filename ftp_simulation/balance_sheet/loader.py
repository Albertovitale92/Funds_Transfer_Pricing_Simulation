"""CSV loader for balance-sheet input data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ftp_simulation.balance_sheet.validation import validate_balance_sheet

DEFAULT_BALANCE_SHEET_PATH = Path("data/static/deutsche_bank_balance_sheet_sample.csv")


def load_balance_sheet(path: str | Path = DEFAULT_BALANCE_SHEET_PATH, *, validate: bool = True) -> pd.DataFrame:
    """Load a balance-sheet CSV and optionally validate it for FTP simulation use."""
    data = pd.read_csv(path)
    if validate:
        return validate_balance_sheet(data)
    return data
