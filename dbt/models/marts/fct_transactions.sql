SELECT
    invoice_no,
    stock_code,
    description,
    customer_id,
    invoice_date,
    country,
    transaction_type,
    quantity,
    unit_price,
    transaction_amount
FROM {{ ref('stg_transactions') }}
