/*
RFM scoring and segmentation in SQL.

Recency, frequency and monetary value are computed per customer, each scored
1 to 5 with NTILE, then mapped to the same business segments used in the
Python analysis. The final SELECT rolls the customers up to one row per
segment with revenue and customer shares.
*/

WITH customer_rfm AS (
    SELECT
        customer_id,
        -- recency: days since last purchase relative to the latest date in the data
        (SELECT MAX(invoice_date) FROM transactions)::date - MAX(invoice_date)::date AS recency,
        COUNT(DISTINCT invoice) AS frequency,
        SUM(revenue)            AS monetary
    FROM transactions
    GROUP BY customer_id
),
scored AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        -- recency reversed: most recent buyers get the highest score
        6 - NTILE(5) OVER (ORDER BY recency)            AS r,
        NTILE(5) OVER (ORDER BY frequency)              AS f,
        NTILE(5) OVER (ORDER BY monetary)               AS m
    FROM customer_rfm
),
segmented AS (
    SELECT
        *,
        CASE
            WHEN r >= 4 AND f >= 4 THEN 'Champions'
            WHEN r >= 3 AND f >= 3 THEN 'Loyal'
            WHEN r >= 4 AND f <= 2 THEN 'New / Promising'
            WHEN r <= 2 AND f >= 3 THEN 'At Risk'
            WHEN r <= 2 AND f <= 2 THEN 'Lost / Hibernating'
            ELSE 'Needs Attention'
        END AS segment
    FROM scored
)
SELECT
    segment,
    COUNT(*)                                                   AS customers,
    ROUND(AVG(recency), 1)                                     AS avg_recency,
    ROUND(AVG(frequency), 1)                                   AS avg_frequency,
    ROUND(SUM(monetary), 0)                                    AS total_revenue,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1) AS revenue_pct,
    ROUND(100.0 * COUNT(*)      / SUM(COUNT(*))      OVER (), 1) AS customer_pct
FROM segmented
GROUP BY segment
ORDER BY total_revenue DESC;
