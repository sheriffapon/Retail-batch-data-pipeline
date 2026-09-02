SELECT
    stock_code,
    MAX(description) AS description,
    SUM(quantity) AS total_quantity,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(transaction_amount) AS total_sales
FROM {{ ref('fct_transactions') }}
GROUP BY stock_code
ORDER BY total_sales DESC