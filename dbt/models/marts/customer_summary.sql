SELECT
    customer_id,

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

    AVG(
        CASE
            WHEN transaction_type = 'sale'
            THEN transaction_amount
        END
    ) AS average_transaction_value

FROM {{ ref('fct_transactions') }}

WHERE customer_id IS NOT NULL

GROUP BY customer_id