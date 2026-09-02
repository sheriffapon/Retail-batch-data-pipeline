SELECT
    invoice_no,
    stock_code,
    description,
    quantity,
    invoice_date,
    unit_price,
    customer_id,
    country,
    transaction_type,

    quantity * unit_price AS transaction_amount

FROM {{ source('raw', 'transactions') }}