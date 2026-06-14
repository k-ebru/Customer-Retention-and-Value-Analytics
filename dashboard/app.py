"""Streamlit dashboard for the customer retention and value analysis.

Run from the project root:
    streamlit run dashboard/app.py

The app loads the cleaned data once (cached), then lets a non technical user
explore monthly revenue, cohort retention and the RFM segments interactively.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Make the project root importable when Streamlit runs from elsewhere.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src import cohort, rfm
from src.preprocessing import load_clean, summary

st.set_page_config(page_title="Customer Retention and Value", layout="wide")


@st.cache_data(show_spinner="Loading data ...")
def get_data():
    df = load_clean()
    retention, sizes = cohort.build_retention(df)
    rfm_table = rfm.compute_rfm(df)
    seg = rfm.segment_summary(rfm_table)
    return df, retention, rfm_table, seg


df, retention, rfm_table, seg = get_data()
s = summary(df)

st.title("Customer Retention and Value")
st.caption(
    f"UK online retail, {s['date_min']} to {s['date_max']}. "
    "Cohort retention and RFM segmentation."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{s['customers']:,}")
c2.metric("Orders", f"{s['invoices']:,}")
c3.metric("Revenue", f"£{s['total_revenue'] / 1e6:.1f}M")
c4.metric("Countries", s["countries"])

st.subheader("Monthly revenue")
monthly = (
    df.assign(Month=df["InvoiceDate"].dt.to_period("M").dt.to_timestamp())
    .groupby("Month")["Revenue"]
    .sum()
)
st.line_chart(monthly)

st.subheader("Cohort retention (%)")
heat = (retention.iloc[:, :13] * 100).round(0)
heat.index = heat.index.astype(str)
st.dataframe(
    heat.style.background_gradient(cmap="Blues", axis=None).format("{:.0f}", na_rep=""),
    use_container_width=True,
)

st.subheader("RFM segments")
left, right = st.columns([1, 1])
with left:
    show = seg.copy()
    show["RevenueShare"] = (show["RevenueShare"] * 100).round(1)
    show["CustomerShare"] = (show["CustomerShare"] * 100).round(1)
    show["TotalRevenue"] = show["TotalRevenue"].round(0)
    st.dataframe(
        show[["Customers", "CustomerShare", "TotalRevenue", "RevenueShare"]],
        use_container_width=True,
    )
with right:
    st.bar_chart(seg["RevenueShare"] * 100)

seg_choice = st.selectbox("Inspect a segment", sorted(rfm_table["Segment"].unique()))
sub = rfm_table[rfm_table["Segment"] == seg_choice]
st.write(
    f"**{seg_choice}**: {len(sub):,} customers, "
    f"average recency {sub['Recency'].mean():.0f} days, "
    f"average {sub['Frequency'].mean():.1f} orders, "
    f"£{sub['Monetary'].sum():,.0f} total revenue."
)
