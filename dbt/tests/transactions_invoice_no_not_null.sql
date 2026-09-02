SELECT *
FROM {{ source('raw', 'transactions') }}
WHERE invoice_no IS NULL