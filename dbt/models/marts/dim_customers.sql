SELECT
    customer_id,
    country,
    MIN(invoice_date) AS first_purchase_date,
    MAX(invoice_date) AS last_purchase_date,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(transaction_amount) AS lifetime_value
FROM {{ ref('fct_transactions') }}
WHERE customer_id IS NOT NULL
GROUP BY customer_id, country