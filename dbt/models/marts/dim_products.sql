SELECT DISTINCT
    stock_code,
    description
FROM {{ ref('stg_transactions') }}