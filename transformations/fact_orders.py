import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path("/opt/supply-chain")

RAW_DIR = PROJECT_ROOT / "data" / "raw"

DIM_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "dimensions"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "facts"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TRANSFORM ORDERS
# ============================================================

def transform_orders():

    print("=" * 60)
    print("ORDER FACT TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Read source data
    # --------------------------------------------------------

    orders = pd.read_csv(
        RAW_DIR / "orders.csv"
    )

    customers = pd.read_csv(
        DIM_DIR / "dim_customer.csv"
    )

    products = pd.read_csv(
        DIM_DIR / "dim_product.csv"
    )

    warehouses = pd.read_csv(
        DIM_DIR / "dim_warehouse.csv"
    )

    dates = pd.read_csv(
        DIM_DIR / "dim_date.csv"
    )

    print(
        f"Orders loaded: {len(orders):,}"
    )

    # --------------------------------------------------------
    # 2. Remove duplicate orders
    # --------------------------------------------------------

    before = len(orders)

    orders = orders.drop_duplicates(
        subset=["order_id"]
    )

    after = len(orders)

    print(
        f"Duplicate orders removed: "
        f"{before - after:,}"
    )

    # --------------------------------------------------------
    # 3. Clean and standardize fields
    # --------------------------------------------------------

    orders["order_id"] = (
        orders["order_id"]
        .astype(str)
        .str.strip()
    )

    orders["customer_id"] = (
        orders["customer_id"]
        .astype(str)
        .str.strip()
    )

    orders["product_id"] = (
        orders["product_id"]
        .astype(str)
        .str.strip()
    )

    orders["warehouse_id"] = (
        orders["warehouse_id"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # 4. Convert order date
    # --------------------------------------------------------

    orders["order_date"] = pd.to_datetime(
        orders["order_date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 5. Convert numeric fields
    # --------------------------------------------------------

    orders["quantity"] = pd.to_numeric(
        orders["quantity"],
        errors="coerce"
    )

    orders["unit_price"] = pd.to_numeric(
        orders["unit_price"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 6. Create total amount
    # --------------------------------------------------------

    orders["total_amount"] = (
        orders["quantity"]
        * orders["unit_price"]
    )

    # --------------------------------------------------------
    # 7. Create date key
    # --------------------------------------------------------

    orders["order_date_key"] = (
        orders["order_date"]
        .dt.strftime("%Y%m%d")
    )

    orders["order_date_key"] = pd.to_numeric(
        orders["order_date_key"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 8. Validate customer references
    # --------------------------------------------------------

    valid_customers = set(
        customers["customer_id"]
        .astype(str)
        .str.strip()
    )

    invalid_customers = (
        ~orders["customer_id"]
        .isin(valid_customers)
    )

    if invalid_customers.any():

        count = invalid_customers.sum()

        raise ValueError(
            f"{count:,} orders contain "
            f"invalid customer_id references."
        )

    # --------------------------------------------------------
    # 9. Validate product references
    # --------------------------------------------------------

    valid_products = set(
        products["product_id"]
        .astype(str)
        .str.strip()
    )

    invalid_products = (
        ~orders["product_id"]
        .isin(valid_products)
    )

    if invalid_products.any():

        count = invalid_products.sum()

        raise ValueError(
            f"{count:,} orders contain "
            f"invalid product_id references."
        )

    # --------------------------------------------------------
    # 10. Validate warehouse references
    # --------------------------------------------------------

    valid_warehouses = set(
        warehouses["warehouse_id"]
        .astype(str)
        .str.strip()
    )

    invalid_warehouses = (
        ~orders["warehouse_id"]
        .isin(valid_warehouses)
    )

    if invalid_warehouses.any():

        count = invalid_warehouses.sum()

        raise ValueError(
            f"{count:,} orders contain "
            f"invalid warehouse_id references."
        )

    # --------------------------------------------------------
    # 11. Validate date references
    # --------------------------------------------------------

    valid_dates = set(
        pd.to_numeric(
            dates["date_key"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
    )

    invalid_dates = (
        ~orders["order_date_key"]
        .isin(valid_dates)
    )

    if invalid_dates.any():

        count = invalid_dates.sum()

        raise ValueError(
            f"{count:,} orders contain "
            f"invalid order date references."
        )

    # --------------------------------------------------------
    # 12. Validate quantity
    # --------------------------------------------------------

    if orders["quantity"].isnull().any():

        raise ValueError(
            "Null or invalid quantity found."
        )

    if (orders["quantity"] <= 0).any():

        raise ValueError(
            "Order quantity must be greater than zero."
        )

    # --------------------------------------------------------
    # 13. Validate unit price
    # --------------------------------------------------------

    if orders["unit_price"].isnull().any():

        raise ValueError(
            "Null or invalid unit_price found."
        )

    if (orders["unit_price"] < 0).any():

        raise ValueError(
            "Negative unit_price found."
        )

    # --------------------------------------------------------
    # 14. Validate order date
    # --------------------------------------------------------

    if orders["order_date"].isnull().any():

        raise ValueError(
            "Invalid or null order_date found."
        )

    # --------------------------------------------------------
    # 15. Select final fact columns
    # --------------------------------------------------------

    fact_orders = orders[
        [
            "order_id",
            "order_date_key",
            "customer_id",
            "product_id",
            "warehouse_id",
            "quantity",
            "unit_price",
            "total_amount"
        ]
    ].copy()

    # --------------------------------------------------------
    # 16. Round monetary values
    # --------------------------------------------------------

    fact_orders["unit_price"] = (
        fact_orders["unit_price"]
        .round(2)
    )

    fact_orders["total_amount"] = (
        fact_orders["total_amount"]
        .round(2)
    )

    # --------------------------------------------------------
    # 17. Final validation
    # --------------------------------------------------------

    if fact_orders["order_id"].duplicated().any():

        raise ValueError(
            "Duplicate order_id found "
            "after transformation."
        )

    if fact_orders["order_id"].isnull().any():

        raise ValueError(
            "Null order_id found."
        )

    # --------------------------------------------------------
    # 18. Write output
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR / "fact_orders.csv"
    )

    fact_orders.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # 19. Print summary
    # --------------------------------------------------------

    print(
        f"Transformed records: "
        f"{len(fact_orders):,}"
    )

    print(
        f"Total order value: "
        f"{fact_orders['total_amount'].sum():,.2f}"
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Order fact transformation "
        "completed successfully."
    )

    return fact_orders


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_orders()