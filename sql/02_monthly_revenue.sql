/*
Monthly revenue and active customers.

A simple health check: how much money comes in each month and how many
distinct customers are active. Average order value is revenue per invoice.
*/

SELECT
    DATE_TRUNC('month', invoice_date)        AS month,
    COUNT(DISTINCT customer_id)              AS active_customers,
    COUNT(DISTINCT invoice)                  AS orders,
    SUM(revenue)                             AS revenue,
    SUM(revenue) / COUNT(DISTINCT invoice)   AS avg_order_value
FROM transactions
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY month;
