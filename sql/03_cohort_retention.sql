/*
Monthly cohort retention in SQL.

A customer's cohort is the month of their first purchase. For each later
activity month we count how many of that cohort were active, then divide by
the original cohort size to get a retention rate.
*/

WITH customer_cohort AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(invoice_date)) AS cohort_month
    FROM transactions
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT
        t.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', t.invoice_date) AS activity_month
    FROM transactions t
    JOIN customer_cohort c ON t.customer_id = c.customer_id
),
cohort_offsets AS (
    SELECT
        cohort_month,
        -- whole months between cohort month and activity month
        (EXTRACT(YEAR  FROM activity_month) - EXTRACT(YEAR  FROM cohort_month)) * 12
      + (EXTRACT(MONTH FROM activity_month) - EXTRACT(MONTH FROM cohort_month)) AS month_index,
        customer_id
    FROM activity
),
cohort_counts AS (
    SELECT
        cohort_month,
        month_index,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM cohort_offsets
    GROUP BY cohort_month, month_index
),
cohort_size AS (
    SELECT cohort_month, active_customers AS size
    FROM cohort_counts
    WHERE month_index = 0
)
SELECT
    cc.cohort_month,
    cc.month_index,
    cc.active_customers,
    cs.size                                              AS cohort_size,
    ROUND(100.0 * cc.active_customers / cs.size, 1)      AS retention_pct
FROM cohort_counts cc
JOIN cohort_size cs ON cc.cohort_month = cs.cohort_month
ORDER BY cc.cohort_month, cc.month_index;
