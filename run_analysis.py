"""End to end analysis: clean the data, build cohort retention and RFM
segments, save all figures, and write a segment summary CSV.

Run:
    python run_analysis.py
"""

import os

import pandas as pd

from src import cohort, plotting, rfm
from src.preprocessing import load_clean, summary

FIG_DIR = "figures"
OUT_DIR = "outputs"


def main() -> None:
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Loading and cleaning ...")
    df = load_clean()
    s = summary(df)
    print(
        f"  {s['rows']:,} rows | {s['customers']:,} customers | "
        f"{s['invoices']:,} invoices | GBP {s['total_revenue']:,.0f} | "
        f"{s['date_min']} to {s['date_max']}"
    )

    print("Cohort retention ...")
    retention, sizes = cohort.build_retention(df)
    avg = cohort.average_retention(retention, [1, 3, 6, 12])
    for m, v in avg.items():
        print(f"  month {m:>2}: {v * 100:4.1f}%")
    plotting.plot_monthly_revenue(df, f"{FIG_DIR}/monthly_revenue.png")
    plotting.plot_cohort_heatmap(retention, f"{FIG_DIR}/cohort_retention.png")

    print("RFM segmentation ...")
    rfm_table = rfm.compute_rfm(df)
    seg = rfm.segment_summary(rfm_table)
    plotting.plot_segment_revenue(seg, f"{FIG_DIR}/segment_revenue.png")
    plotting.plot_segment_scatter(rfm_table, f"{FIG_DIR}/segment_scatter.png")

    rfm_table.to_csv(f"{OUT_DIR}/rfm_customers.csv")
    seg.to_csv(f"{OUT_DIR}/segment_summary.csv")

    pd.set_option("display.width", 200)
    print("\nSegment summary:")
    show = seg.copy()
    show["RevenueShare"] = (show["RevenueShare"] * 100).round(1)
    show["CustomerShare"] = (show["CustomerShare"] * 100).round(1)
    print(show.round(1).to_string())
    print(f"\nFigures saved to {FIG_DIR}/, tables to {OUT_DIR}/")


if __name__ == "__main__":
    main()
