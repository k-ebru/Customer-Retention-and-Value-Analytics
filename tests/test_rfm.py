"""Tests for RFM scoring and segmentation."""

import pandas as pd

from src.rfm import compute_rfm, _segment, segment_summary


def _make_df(n_customers=200):
    rng = pd.Series(range(n_customers))
    return pd.DataFrame({
        "CustomerID": rng,
        "Invoice": [f"INV{i}" for i in rng],
        "InvoiceDate": pd.to_datetime("2011-01-01") + pd.to_timedelta(rng % 30, unit="D"),
        "Revenue": (rng + 1) * 1.5,
    })


def test_compute_rfm_has_all_columns():
    df = _make_df()
    rfm = compute_rfm(df)
    for col in ["Recency", "Frequency", "Monetary", "R", "F", "M", "RFM_Score", "Segment"]:
        assert col in rfm.columns


def test_scores_are_between_1_and_5():
    rfm = compute_rfm(_make_df())
    for col in ["R", "F", "M"]:
        assert rfm[col].min() >= 1
        assert rfm[col].max() <= 5


def test_qcut_does_not_crash_with_tied_recency():
    # All customers bought on the same day. qcut needs rank() here or it
    # raises "Bin edges must be unique".
    df = pd.DataFrame({
        "CustomerID": range(50),
        "Invoice": [f"I{i}" for i in range(50)],
        "InvoiceDate": pd.to_datetime(["2011-01-15"] * 50),
        "Revenue": [10.0] * 50,
    })
    rfm = compute_rfm(df)
    assert len(rfm) == 50
    assert set(rfm["R"].unique()).issubset({1, 2, 3, 4, 5})


def test_segment_labels_are_known():
    rfm = compute_rfm(_make_df())
    allowed = {"Champions", "Loyal", "At Risk", "Lost / Hibernating",
               "New / Promising", "Needs Attention"}
    assert set(rfm["Segment"].unique()).issubset(allowed)


def test_segment_rules_directly():
    # Champion: high recency, high frequency
    assert _segment(pd.Series({"R": 5, "F": 5})) == "Champions"
    # New: high recency, low frequency
    assert _segment(pd.Series({"R": 5, "F": 1})) == "New / Promising"
    # At Risk: low recency, high frequency
    assert _segment(pd.Series({"R": 1, "F": 5})) == "At Risk"
    # Lost: low on both
    assert _segment(pd.Series({"R": 1, "F": 1})) == "Lost / Hibernating"


def test_segment_summary_shares_sum_to_one():
    rfm = compute_rfm(_make_df())
    seg = segment_summary(rfm)
    assert abs(seg["RevenueShare"].sum() - 1.0) < 1e-9
    assert abs(seg["CustomerShare"].sum() - 1.0) < 1e-9
