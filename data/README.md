# Data

This project uses the **Online Retail II** dataset: real online retail
transactions from a UK based retailer, December 2009 to December 2011.

The file is about 45 MB and is not committed to the repository. Download it
once before running the analysis.

## Download

Source: UCI Machine Learning Repository, Online Retail II.

```bash
curl -L -o data/online_retail_II.zip \
  "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
unzip data/online_retail_II.zip -d data/
```

This produces `data/online_retail_II.xlsx`, which the pipeline reads directly.

## Schema

One row is one line item on an invoice.

| Column      | Meaning                                        |
|-------------|------------------------------------------------|
| Invoice     | Invoice number (a leading `C` marks a cancellation) |
| StockCode   | Product code                                   |
| Description | Product name                                   |
| Quantity    | Units on the line                              |
| InvoiceDate | Timestamp of the invoice                       |
| Price       | Unit price in GBP                              |
| Customer ID | Customer identifier (missing for some rows)    |
| Country     | Customer country                               |

The workbook has two sheets (2009-2010 and 2010-2011) which the pipeline
concatenates.
