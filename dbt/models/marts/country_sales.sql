SELECT
    country,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(transaction_amount) AS total_sales
FROM {{ ref('fct_transactions') }}
GROUP BY country
ORDER BY total_sales DESC