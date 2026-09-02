import os
import time
from io import StringIO

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()


CSV_FILE = "/opt/airflow/data/valid_transactions.csv"

DB_CONFIG = {
    "host": "batch-postgres",
    "port": 5432,
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


def load_transactions():
    start_time = time.time()

    print("Reading validated CSV...")

    df = pd.read_csv(CSV_FILE)

    rows_read = len(df)

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    df["transaction_type"] = "sale"

    df.loc[
        df["InvoiceNo"].astype(str).str.startswith("C"),
        "transaction_type"
    ] = "return"

    df.loc[
        df["StockCode"].astype(str).eq("B"),
        "transaction_type"
    ] = "adjustment"

    df = df.rename(
        columns={
            "InvoiceNo": "invoice_no",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "UnitPrice": "unit_price",
            "CustomerID": "customer_id",
            "Country": "country",
        }
    )

    print(f"Rows to load: {rows_read:,}")

    conn = psycopg2.connect(**DB_CONFIG)

    cursor = conn.cursor()

    run_id = None

    try:
        cursor.execute("""
            INSERT INTO raw.batch_runs (
                rows_read,
                status
            )
            VALUES (%s, 'RUNNING')
            RETURNING run_id;
        """, (rows_read,))

        run_id = cursor.fetchone()[0]

        conn.commit()

        print(f"Batch run started: {run_id}")

        print("Creating temporary staging table...")

        cursor.execute("""
            CREATE TEMP TABLE transactions_load
            (LIKE raw.transactions)
            ON COMMIT DROP;
        """)

        buffer = StringIO()

        df.to_csv(
            buffer,
            index=False,
            header=False
        )

        buffer.seek(0)

        print("Loading data into staging table...")

        cursor.copy_expert(
            """
            COPY transactions_load (
                invoice_no,
                stock_code,
                description,
                quantity,
                invoice_date,
                unit_price,
                customer_id,
                country,
                transaction_type
            )
            FROM STDIN
            WITH CSV
            """,
            buffer,
        )

        rows_staged = cursor.rowcount

        print(f"Rows staged: {rows_staged:,}")

        print("Removing duplicates from staging data...")

        cursor.execute("""
            DELETE FROM transactions_load
            WHERE ctid NOT IN (
                SELECT MIN(ctid)
                FROM transactions_load
                GROUP BY
                    invoice_no,
                    stock_code,
                    customer_id,
                    invoice_date
            );
        """)

        duplicates_removed = cursor.rowcount

        print(
            f"Duplicates removed: "
            f"{duplicates_removed:,}"
        )

        cursor.execute("""
            UPDATE raw.batch_runs
            SET
                rows_staged = %s,
                duplicates_removed = %s
            WHERE run_id = %s;
        """, (
            rows_staged,
            duplicates_removed,
            run_id,
        ))

        print("Loading new transactions...")

        cursor.execute("""
            INSERT INTO raw.transactions (
                invoice_no,
                stock_code,
                description,
                quantity,
                invoice_date,
                unit_price,
                customer_id,
                country,
                transaction_type
            )
            SELECT
                s.invoice_no,
                s.stock_code,
                s.description,
                s.quantity,
                s.invoice_date,
                s.unit_price,
                s.customer_id,
                s.country,
                s.transaction_type
            FROM transactions_load s
            ON CONFLICT (
                invoice_no,
                stock_code,
                customer_id,
                invoice_date
            ) DO NOTHING;
        """)

        inserted_rows = cursor.rowcount

        cursor.execute("""
            UPDATE raw.batch_runs
            SET
                rows_inserted = %s,
                finished_at = NOW(),
                status = 'SUCCESS'
            WHERE run_id = %s;
        """, (
            inserted_rows,
            run_id,
        ))

        conn.commit()

        duration = time.time() - start_time

        print()
        print("----------------------------------------")
        print("Batch Load Summary")
        print("----------------------------------------")
        print(f"Run ID:               {run_id}")
        print(f"Rows read:            {rows_read:,}")
        print(f"Rows staged:          {rows_staged:,}")
        print(f"Duplicates removed:   {duplicates_removed:,}")
        print(f"Rows inserted:        {inserted_rows:,}")
        print(f"Duration:             {duration:.2f} seconds")
        print("Status:               SUCCESS")
        print("----------------------------------------")

    except Exception as e:
        conn.rollback()

        if run_id is not None:
            try:
                cursor.execute("""
                    UPDATE raw.batch_runs
                    SET
                        finished_at = NOW(),
                        status = 'FAILED',
                        error_message = %s
                    WHERE run_id = %s;
                """, (
                    str(e),
                    run_id,
                ))

                conn.commit()

            except Exception:
                conn.rollback()

        print()
        print("----------------------------------------")
        print("BATCH LOAD FAILED")
        print("----------------------------------------")
        print(f"Run ID: {run_id}")
        print(f"Error: {e}")
        print("----------------------------------------")

        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_transactions()