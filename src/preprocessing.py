"""Loading and cleaning for the Online Retail II dataset.

The raw file has two sheets (2009-2010 and 2010-2011) of UK online retail
transactions. Cleaning keeps only rows that represent a real, attributable
sale so that retention and customer value are measured honestly.
"""

import pandas as pd

DEFAULT_PATH = "data/online_retail_II.xlsx"


def load_raw(path: str = DEFAULT_PATH) -> pd.DataFrame:
    """Read and concatenate both sheets of the workbook into one frame."""
    sheets = pd.read_excel(path, sheet_name=None)
    df = pd.concat(sheets.values(), ignore_index=True)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the cleaning rules and add a Revenue column.

    Rules:
      * Drop rows with no Customer ID (cannot be attributed to a customer).
      * Remove cancellations, whose invoice numbers start with 'C'.
      * Keep only positive quantity and price (returns and adjustments out).
      * Revenue = Quantity * Price.
    """
    df = df.rename(columns={"Customer ID": "CustomerID"}).copy()
    df["Invoice"] = df["Invoice"].astype(str)

    df = df.dropna(subset=["CustomerID"])
    df = df[~df["Invoice"].str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

    # Online Retail II has exact duplicate line items in the raw file. Drop
    # them so revenue is not double counted.
    df = df.drop_duplicates()

    df["CustomerID"] = df["CustomerID"].astype(int)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Revenue"] = df["Quantity"] * df["Price"]
    return df.reset_index(drop=True)


def load_clean(path: str = DEFAULT_PATH) -> pd.DataFrame:
    """Convenience wrapper: load then clean."""
    return clean(load_raw(path))


def summary(df: pd.DataFrame) -> dict:
    """Return headline counts used in the README and dashboard."""
    return {
        "rows": len(df),
        "customers": int(df["CustomerID"].nunique()),
        "invoices": int(df["Invoice"].nunique()),
        "countries": int(df["Country"].nunique()),
        "total_revenue": float(df["Revenue"].sum()),
        "date_min": df["InvoiceDate"].min().date().isoformat(),
        "date_max": df["InvoiceDate"].max().date().isoformat(),
    }
