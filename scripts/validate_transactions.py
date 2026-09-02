
import pandas as pd

INPUT_FILE = "/opt/airflow/data/online_retail.csv"
VALID_FILE = "/opt/airflow/data/valid_transactions.csv"
REJECTED_FILE = "/opt/airflow/data/rejected_transactions.csv"


def validate_transactions():
    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded {len(df):,} transactions")

    # Remove exact duplicate rows
    duplicates = df.duplicated(keep="first")
    duplicate_rows = df[duplicates].copy()

    df = df[~duplicates].copy()

    # Required fields
    required_columns = [
        "InvoiceNo",
        "StockCode",
        "InvoiceDate",
        "Quantity",
        "UnitPrice",
        "Country",
    ]

    missing_required = df[required_columns].isnull().any(axis=1)

    # Negative prices are invalid for normal transaction records
    negative_price = df["UnitPrice"] < 0

    # Records that fail hard validation
    rejected = df[missing_required | negative_price].copy()

    # Valid records
    valid = df[~(missing_required | negative_price)].copy()

    # Add transaction classification
    valid["transaction_type"] = "sale"

    valid.loc[
        valid["InvoiceNo"].astype(str).str.startswith("C"),
        "transaction_type"
    ] = "return"

    valid.loc[
        valid["StockCode"].astype(str).eq("B"),
        "transaction_type"
    ] = "adjustment"

    # Save results
    valid.to_csv(VALID_FILE, index=False)
    rejected.to_csv(REJECTED_FILE, index=False)

    print(f"Duplicate rows removed: {len(duplicate_rows):,}")
    print(f"Valid transactions: {len(valid):,}")
    print(f"Rejected transactions: {len(rejected):,}")
    print(f"Valid file: {VALID_FILE}")
    print(f"Rejected file: {REJECTED_FILE}")


if __name__ == "__main__":
    validate_transactions()
