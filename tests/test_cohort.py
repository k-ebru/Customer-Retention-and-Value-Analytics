"""Tests for cohort retention.

The setup creates two customers with very different repeat patterns, so the
retention matrix is small enough to check by hand.
"""

import pandas as pd

from src.cohort import build_retention, _months_between


def _frame(rows):
    df = pd.DataFrame(rows, columns=["CustomerID", "Invoice", "InvoiceDate", "Revenue"])
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df


def test_months_between_basic():
    later = pd.Series(pd.to_datetime(["2010-03-15", "2011-01-01"]))
    earlier = pd.Series(pd.to_datetime(["2010-01-20", "2010-12-31"]))
    out = _months_between(later, earlier)
    assert list(out) == [2, 1]


def test_single_cohort_full_retention():
    # One customer bought every month for three months
    df = _frame([
        (1, "a", "2010-01-15", 10),
        (1, "b", "2010-02-15", 10),
        (1, "c", "2010-03-15", 10),
    ])
    retention, sizes = build_retention(df)
    assert sizes.iloc[0] == 1
    assert retention.iloc[0, 0] == 1.0
    assert retention.iloc[0, 1] == 1.0
    assert retention.iloc[0, 2] == 1.0


def test_retention_fraction():
    # Two customers acquired in Jan, only one comes back in Feb
    df = _frame([
        (1, "a", "2010-01-10", 5),
        (1, "b", "2010-02-10", 5),
        (2, "c", "2010-01-20", 5),
    ])
    retention, sizes = build_retention(df)
    assert sizes.iloc[0] == 2
    assert retention.iloc[0, 0] == 1.0
    assert retention.iloc[0, 1] == 0.5
