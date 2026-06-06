/*
Schema for the cleaned Online Retail II transactions.

One row is one line item on an invoice. The Python pipeline writes the cleaned
data; these queries show how the same retention and value analysis would be
reproduced directly in a relational warehouse.
*/

CREATE TABLE transactions (
    invoice       VARCHAR(16),
    stock_code    VARCHAR(16),
    description   TEXT,
    quantity      INTEGER,
    invoice_date  TIMESTAMP,
    price         NUMERIC(10, 2),
    customer_id   INTEGER,
    country       VARCHAR(64),
    revenue       NUMERIC(12, 2)   -- quantity * price, positive sales only
);

-- Helpful indexes for the customer-level aggregations below.
CREATE INDEX idx_tx_customer ON transactions (customer_id);
CREATE INDEX idx_tx_date     ON transactions (invoice_date);
