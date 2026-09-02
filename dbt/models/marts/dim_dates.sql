WITH date_spine AS (

    SELECT
        generate_series(
            (SELECT MIN(invoice_date)::date FROM {{ ref('fct_transactions') }}),
            (SELECT MAX(invoice_date)::date FROM {{ ref('fct_transactions') }}),
            INTERVAL '1 day'
        )::date AS date_day

)

SELECT
    date_day,
    EXTRACT(YEAR FROM date_day)::int AS year,
    EXTRACT(QUARTER FROM date_day)::int AS quarter,
    EXTRACT(MONTH FROM date_day)::int AS month,
    TO_CHAR(date_day, 'Month') AS month_name,
    EXTRACT(WEEK FROM date_day)::int AS week,
    EXTRACT(DAY FROM date_day)::int AS day,
    TO_CHAR(date_day, 'Day') AS day_name
FROM date_spine