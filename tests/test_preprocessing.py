"""Tests for the cleaning step.

Each test builds a tiny DataFrame that targets one cleaning rule, so a
failure points straight at the rule that broke.
"""

import pandas as pd

from src.preprocessing import clean


def _raw(rows):
    cols = ["Invoice", "StockCode", "Description", "Quantity",
            "InvoiceDate", "Price", "Customer ID", "Country"]
    return pd.DataFrame(rows, columns=cols)


def test_drops_missing_customer_id():
    df = _raw([
        ["536365", "85123A", "WHITE HEART", 6, "2010-12-01 08:26", 2.55, 17850, "UK"],
        ["536366", "71053",  "WHITE METAL", 6, "2010-12-01 08:28", 3.39, None,  "UK"],
    ])
    out = clean(df)
    assert len(out) == 1
    assert out["CustomerID"].iloc[0] == 17850


def test_drops_cancellations():
    df = _raw([
        ["536365",  "A", "x", 1, "2010-12-01", 1.0, 1, "UK"],
        ["C536365", "A", "x", 1, "2010-12-01", 1.0, 1, "UK"],
    ])
    out = clean(df)
    assert len(out) == 1
    assert not out["Invoice"].str.startswith("C").any()


def test_drops_non_positive_quantity_or_price():
    df = _raw([
        ["1", "A", "x",  1, "2010-12-01", 1.0, 1, "UK"],
        ["2", "A", "x",  0, "2010-12-01", 1.0, 1, "UK"],
        ["3", "A", "x",  1, "2010-12-01", 0.0, 1, "UK"],
        ["4", "A", "x", -2, "2010-12-01", 1.0, 1, "UK"],
    ])
    out = clean(df)
    assert len(out) == 1


def test_drops_duplicate_rows():
    df = _raw([
        ["1", "A", "x", 1, "2010-12-01", 1.0, 1, "UK"],
        ["1", "A", "x", 1, "2010-12-01", 1.0, 1, "UK"],
    ])
    out = clean(df)
    assert len(out) == 1


def test_revenue_column():
    df = _raw([
        ["1", "A", "x", 3, "2010-12-01", 2.5, 1, "UK"],
    ])
    out = clean(df)
    assert out["Revenue"].iloc[0] == 7.5
