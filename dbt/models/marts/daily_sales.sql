SELECT
    DATE(invoice_date) AS sales_date,

    COUNT(*) AS transaction_count,

    COUNT(DISTINCT invoice_no) AS order_count,

    SUM(
        CASE
            WHEN transaction_type = 'sale'
            THEN transaction_amount
            ELSE 0
        END
    ) AS total_sales,

    SUM(
        CASE
            WHEN transaction_type = 'return'
            THEN ABS(transaction_amount)
            ELSE 0
        END
    ) AS total_returns,

    SUM(transaction_amount) AS net_revenue,

    SUM(
        CASE
            WHEN transaction_type = 'sale'
            THEN quantity
            ELSE 0
        END
    ) AS units_sold

FROM {{ ref('fct_transactions') }}

GROUP BY DATE(invoice_date)

ORDER BY sales_date