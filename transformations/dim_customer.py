import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path("/opt/supply-chain")

RAW_DIR = PROJECT_ROOT / "data" / "raw"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "dimensions"
)


# Make sure output directory exists
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TRANSFORM CUSTOMER DATA
# ============================================================

def transform_customers():

    print("=" * 60)
    print("CUSTOMER DIMENSION TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Read customer data
    # --------------------------------------------------------

    customers_file = RAW_DIR / "customers.csv"

    customers = pd.read_csv(
        customers_file
    )

    print(
        f"Customers loaded: "
        f"{len(customers):,}"
    )

    # --------------------------------------------------------
    # 2. Remove duplicate customers
    # --------------------------------------------------------

    before = len(customers)

    customers = customers.drop_duplicates(
        subset=["customer_id"]
    )

    after = len(customers)

    print(
        f"Duplicate customers removed: "
        f"{before - after:,}"
    )

    # --------------------------------------------------------
    # 3. Clean text columns
    # --------------------------------------------------------

    text_columns = [
        "customer_name",
        "city",
        "state"
    ]

    for column in text_columns:

        customers[column] = (
            customers[column]
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # 4. Standardize registration date
    # --------------------------------------------------------

    customers["registration_date"] = pd.to_datetime(
        customers["registration_date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 5. Create customer status
    # --------------------------------------------------------

    customers["customer_status"] = "ACTIVE"

    # --------------------------------------------------------
    # 6. Select final dimension columns
    # --------------------------------------------------------

    dim_customer = customers[
        [
            "customer_id",
            "customer_name",
            "city",
            "state",
            "registration_date",
            "customer_status"
        ]
    ].copy()

    # --------------------------------------------------------
    # 7. Final validation
    # --------------------------------------------------------

    if dim_customer["customer_id"].duplicated().any():

        raise ValueError(
            "Duplicate customer_id found "
            "after transformation."
        )

    if dim_customer["customer_id"].isnull().any():

        raise ValueError(
            "Null customer_id found "
            "after transformation."
        )

    if dim_customer["customer_name"].isnull().any():

        raise ValueError(
            "Null customer_name found "
            "after transformation."
        )

    if dim_customer["registration_date"].isnull().any():

        raise ValueError(
            "Invalid or null registration_date "
            "found after transformation."
        )

    # --------------------------------------------------------
    # 8. Write transformed dataset
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR / "dim_customer.csv"
    )

    dim_customer.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # 9. Print summary
    # --------------------------------------------------------

    print(
        f"Transformed records: "
        f"{len(dim_customer):,}"
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Customer dimension transformation "
        "completed successfully."
    )

    return dim_customer


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_customers()