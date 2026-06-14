"""RFM scoring and customer segmentation.

For each customer we compute:
  * Recency   - days since their last purchase (lower is better)
  * Frequency - number of distinct invoices (higher is better)
  * Monetary  - total revenue (higher is better)

Each dimension is scored 1 to 5 by quintile, then customers are grouped into
business readable segments so the analysis can drive an action, not just a
number.
"""

import pandas as pd


def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """Return a per-customer RFM table with scores and a segment label."""
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
        Frequency=("Invoice", "nunique"),
        Monetary=("Revenue", "sum"),
    )

    # Quintile scores. Recency is reversed: recent buyers score highest.
    # rank(method="first") breaks ties so every dimension splits into 5 bins
    # even when many customers share the same value (common with Recency).
    rfm["R"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_Score"] = rfm[["R", "F", "M"]].sum(axis=1)
    rfm["Segment"] = rfm.apply(_segment, axis=1)
    return rfm


def _segment(row) -> str:
    r, f = row["R"], row["F"]
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / Promising"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f <= 2:
        return "Lost / Hibernating"
    return "Needs Attention"


def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the RFM table to one row per segment with revenue shares."""
    summary = rfm.groupby("Segment").agg(
        Customers=("Monetary", "size"),
        AvgRecency=("Recency", "mean"),
        AvgFrequency=("Frequency", "mean"),
        AvgMonetary=("Monetary", "mean"),
        TotalRevenue=("Monetary", "sum"),
    )
    summary["RevenueShare"] = summary["TotalRevenue"] / summary["TotalRevenue"].sum()
    summary["CustomerShare"] = summary["Customers"] / summary["Customers"].sum()
    return summary.sort_values("TotalRevenue", ascending=False)
