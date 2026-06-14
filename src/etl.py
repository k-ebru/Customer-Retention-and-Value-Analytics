"""Small ETL script.

Reads the raw Online Retail II workbook, applies the cleaning rules in
preprocessing.clean, and writes the result to Parquet for fast reloads.

Run:
    python -m src.etl --input data/online_retail_II.xlsx \
                      --output data/online_retail_II_clean.parquet
"""

import argparse
from pathlib import Path

from src.preprocessing import clean, load_raw, summary


def parse_args():
    p = argparse.ArgumentParser(description="Clean Online Retail II to Parquet.")
    p.add_argument("--input", default="data/online_retail_II.xlsx",
                   help="Path to the raw .xlsx workbook.")
    p.add_argument("--output", default="data/online_retail_II_clean.parquet",
                   help="Path to write the cleaned Parquet file.")
    return p.parse_args()


def main():
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading  {in_path}")
    raw = load_raw(str(in_path))
    print(f"  raw rows: {len(raw):,}")

    print("Cleaning ...")
    df = clean(raw)
    s = summary(df)
    print(
        f"  clean rows: {s['rows']:,} | customers: {s['customers']:,} | "
        f"invoices: {s['invoices']:,} | revenue: GBP {s['total_revenue']:,.0f}"
    )

    # StockCode mixes ints and strings in the raw file, which breaks parquet.
    # Cast to string so the schema is consistent.
    df["StockCode"] = df["StockCode"].astype(str)

    print(f"Writing  {out_path}")
    df.to_parquet(out_path, index=False)
    print("Done.")


if __name__ == "__main__":
    main()
