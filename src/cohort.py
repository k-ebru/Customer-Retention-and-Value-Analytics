"""Monthly cohort retention.

A customer's cohort is the calendar month of their first purchase. For every
later month we measure what share of that cohort came back and bought again.
This separates one-time buyers from customers who form a lasting relationship.
"""

import pandas as pd


def _months_between(later: pd.Series, earlier: pd.Series) -> pd.Series:
    return (later.dt.year - earlier.dt.year) * 12 + (later.dt.month - earlier.dt.month)


def build_retention(df: pd.DataFrame):
    """Return (retention, cohort_sizes).

    retention: DataFrame indexed by cohort month, columns are months since
    acquisition, values are the fraction of the cohort active that month.
    cohort_sizes: Series of the number of customers acquired in each cohort.
    """
    df = df.copy()
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M")
    df["CohortMonth"] = df.groupby("CustomerID")["InvoiceMonth"].transform("min")

    df["CohortIndex"] = _months_between(
        df["InvoiceMonth"].dt.to_timestamp(), df["CohortMonth"].dt.to_timestamp()
    )

    counts = (
        df.groupby(["CohortMonth", "CohortIndex"])["CustomerID"]
        .nunique()
        .reset_index()
    )
    pivot = counts.pivot(index="CohortMonth", columns="CohortIndex", values="CustomerID")
    cohort_sizes = pivot.iloc[:, 0]
    retention = pivot.divide(cohort_sizes, axis=0)
    return retention, cohort_sizes


def average_retention(retention: pd.DataFrame, months) -> dict:
    """Average retention across cohorts at the requested month offsets."""
    out = {}
    for m in months:
        if m in retention.columns:
            out[m] = float(retention[m].mean(skipna=True))
    return out
