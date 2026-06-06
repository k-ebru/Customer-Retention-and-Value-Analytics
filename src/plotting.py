"""Figure generation for the README and dashboard."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({"figure.dpi": 110, "font.size": 10})


def plot_monthly_revenue(df: pd.DataFrame, path: str) -> None:
    monthly = (
        df.assign(Month=df["InvoiceDate"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month")["Revenue"]
        .sum()
    )
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(monthly.index, monthly.values / 1e6, marker="o", color="#2b6cb0")
    ax.set_title("Monthly Revenue")
    ax.set_ylabel("Revenue (GBP millions)")
    ax.set_xlabel("Month")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_cohort_heatmap(retention: pd.DataFrame, path: str, max_index: int = 12) -> None:
    data = retention.iloc[:, : max_index + 1] * 100
    fig, ax = plt.subplots(figsize=(11, 7))
    im = ax.imshow(data.values, aspect="auto", cmap="Blues", vmin=0, vmax=50)

    ax.set_xticks(range(data.shape[1]))
    ax.set_xticklabels(data.columns)
    ax.set_yticks(range(data.shape[0]))
    ax.set_yticklabels([str(p) for p in data.index])
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("Acquisition cohort")
    ax.set_title("Monthly Cohort Retention (%)")

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        color="white" if v > 25 else "black", fontsize=7)
    fig.colorbar(im, ax=ax, label="Retention (%)")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_segment_revenue(summary: pd.DataFrame, path: str) -> None:
    s = summary.sort_values("TotalRevenue")
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(s.index, s["RevenueShare"] * 100, color="#2f855a")
    ax.set_xlabel("Share of total revenue (%)")
    ax.set_title("Revenue Share by Customer Segment")
    for bar, pct, cust in zip(bars, s["RevenueShare"] * 100, s["CustomerShare"] * 100):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{pct:.0f}% rev / {cust:.0f}% cust", va="center", fontsize=8)
    ax.set_xlim(0, max(s["RevenueShare"] * 100) + 12)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_segment_scatter(rfm: pd.DataFrame, path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    segments = rfm["Segment"].unique()
    cmap = plt.get_cmap("tab10")
    for i, seg in enumerate(sorted(segments)):
        sub = rfm[rfm["Segment"] == seg]
        ax.scatter(sub["Recency"], sub["Frequency"], s=14, alpha=0.5,
                   color=cmap(i), label=seg)
    ax.set_xlabel("Recency (days since last purchase)")
    ax.set_ylabel("Frequency (number of invoices)")
    ax.set_yscale("log")
    ax.set_title("Customer Segments by Recency and Frequency")
    ax.legend(fontsize=8, markerscale=1.5)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
