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

FACT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "facts"
)

FACT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TRANSFORM SHIPMENT DATA
# ============================================================

def transform_shipments():

    print("=" * 60)
    print("SHIPMENT FACT TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Read source data
    # --------------------------------------------------------

    shipments = pd.read_csv(
        RAW_DIR / "shipments.csv"
    )

    orders = pd.read_csv(
        FACT_DIR / "fact_orders.csv"
    )

    warehouses = pd.read_csv(
        DIM_DIR / "dim_warehouse.csv"
    )

    suppliers = pd.read_csv(
        DIM_DIR / "dim_supplier.csv"
    )

    dates = pd.read_csv(
        DIM_DIR / "dim_date.csv"
    )

    print(
        f"Shipments loaded: "
        f"{len(shipments):,}"
    )

    # --------------------------------------------------------
    # 2. Remove duplicate shipments
    # --------------------------------------------------------

    before = len(shipments)

    shipments = shipments.drop_duplicates(
        subset=["shipment_id"]
    )

    after = len(shipments)

    print(
        f"Duplicate shipments removed: "
        f"{before - after:,}"
    )

    # --------------------------------------------------------
    # 3. Clean ID columns
    # --------------------------------------------------------

    id_columns = [
        "shipment_id",
        "order_id",
        "supplier_id",
        "warehouse_id"
    ]

    for column in id_columns:

        shipments[column] = (
            shipments[column]
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # 4. Clean shipping mode
    # --------------------------------------------------------

    shipments["shipping_mode"] = (
        shipments["shipping_mode"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # 5. Convert dates
    # --------------------------------------------------------

    date_columns = [
        "dispatch_date",
        "expected_delivery_date",
        "actual_delivery_date"
    ]

    for column in date_columns:

        shipments[column] = pd.to_datetime(
            shipments[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # 6. Convert shipping cost
    # --------------------------------------------------------

    shipments["shipping_cost"] = pd.to_numeric(
        shipments["shipping_cost"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 7. Validate order references
    # --------------------------------------------------------

    valid_orders = set(
        orders["order_id"]
        .astype(str)
        .str.strip()
    )

    invalid_orders = (
        ~shipments["order_id"]
        .isin(valid_orders)
    )

    if invalid_orders.any():

        count = invalid_orders.sum()

        raise ValueError(
            f"{count:,} shipments contain "
            f"invalid order_id references."
        )

    # --------------------------------------------------------
    # 8. Validate warehouse references
    # --------------------------------------------------------

    valid_warehouses = set(
        warehouses["warehouse_id"]
        .astype(str)
        .str.strip()
    )

    invalid_warehouses = (
        ~shipments["warehouse_id"]
        .isin(valid_warehouses)
    )

    if invalid_warehouses.any():

        count = invalid_warehouses.sum()

        raise ValueError(
            f"{count:,} shipments contain "
            f"invalid warehouse_id references."
        )

    # --------------------------------------------------------
    # 9. Validate supplier references
    # --------------------------------------------------------

    valid_suppliers = set(
        suppliers["supplier_id"]
        .astype(str)
        .str.strip()
    )

    invalid_suppliers = (
        ~shipments["supplier_id"]
        .isin(valid_suppliers)
    )

    if invalid_suppliers.any():

        count = invalid_suppliers.sum()

        raise ValueError(
            f"{count:,} shipments contain "
            f"invalid supplier_id references."
        )

    # --------------------------------------------------------
    # 10. Validate shipment dates
    # --------------------------------------------------------

    if shipments["dispatch_date"].isnull().any():

        raise ValueError(
            "Invalid or null dispatch_date found."
        )

    if shipments[
        "expected_delivery_date"
    ].isnull().any():

        raise ValueError(
            "Invalid or null expected_delivery_date found."
        )

    if shipments[
        "actual_delivery_date"
    ].isnull().any():

        raise ValueError(
            "Invalid or null actual_delivery_date found."
        )

    # --------------------------------------------------------
    # 11. Validate shipping cost
    # --------------------------------------------------------

    if shipments["shipping_cost"].isnull().any():

        raise ValueError(
            "Null or invalid shipping_cost found."
        )

    if (shipments["shipping_cost"] < 0).any():

        raise ValueError(
            "Negative shipping_cost found."
        )

    # --------------------------------------------------------
    # 12. Calculate delivery days
    # --------------------------------------------------------

    shipments["delivery_days"] = (
        shipments["actual_delivery_date"]
        - shipments["dispatch_date"]
    ).dt.days

    # --------------------------------------------------------
    # 13. Calculate delay days
    # --------------------------------------------------------

    shipments["delay_days"] = (
        shipments["actual_delivery_date"]
        - shipments["expected_delivery_date"]
    ).dt.days

    # --------------------------------------------------------
    # 14. Create delivery status
    # --------------------------------------------------------

    shipments["delivery_status"] = "ON_TIME"

    shipments.loc[
        shipments["delay_days"] > 0,
        "delivery_status"
    ] = "DELAYED"

    shipments.loc[
        shipments["delay_days"] < 0,
        "delivery_status"
    ] = "EARLY"

    # --------------------------------------------------------
    # 15. Create dispatch date key
    # --------------------------------------------------------

    shipments["dispatch_date_key"] = (
        shipments["dispatch_date"]
        .dt.strftime("%Y%m%d")
    )

    shipments["dispatch_date_key"] = pd.to_numeric(
        shipments["dispatch_date_key"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 16. Create expected delivery date key
    # --------------------------------------------------------

    shipments["expected_delivery_date_key"] = (
        shipments["expected_delivery_date"]
        .dt.strftime("%Y%m%d")
    )

    shipments["expected_delivery_date_key"] = pd.to_numeric(
        shipments["expected_delivery_date_key"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 17. Create actual delivery date key
    # --------------------------------------------------------

    shipments["actual_delivery_date_key"] = (
        shipments["actual_delivery_date"]
        .dt.strftime("%Y%m%d")
    )

    shipments["actual_delivery_date_key"] = pd.to_numeric(
        shipments["actual_delivery_date_key"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 18. Validate date dimension references
    # --------------------------------------------------------

    valid_dates = set(
        pd.to_numeric(
            dates["date_key"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
    )

    date_key_columns = [
        "dispatch_date_key",
        "expected_delivery_date_key",
        "actual_delivery_date_key"
    ]

    for column in date_key_columns:

        invalid_dates = (
            ~shipments[column]
            .isin(valid_dates)
        )

        if invalid_dates.any():

            count = invalid_dates.sum()

            raise ValueError(
                f"{count:,} shipments contain "
                f"invalid {column} references."
            )

    # --------------------------------------------------------
    # 19. Final validation
    # --------------------------------------------------------

    if shipments["shipment_id"].duplicated().any():

        raise ValueError(
            "Duplicate shipment_id found "
            "after transformation."
        )

    if shipments["shipment_id"].isnull().any():

        raise ValueError(
            "Null shipment_id found."
        )

    if (shipments["delivery_days"] < 0).any():

        raise ValueError(
            "Actual delivery date cannot be "
            "before dispatch date."
        )

    # --------------------------------------------------------
    # 20. Select final fact columns
    # --------------------------------------------------------

    fact_shipments = shipments[
        [
            "shipment_id",
            "order_id",
            "supplier_id",
            "warehouse_id",
            "dispatch_date_key",
            "expected_delivery_date_key",
            "actual_delivery_date_key",
            "shipping_mode",
            "shipping_cost",
            "delivery_days",
            "delay_days",
            "delivery_status"
        ]
    ].copy()

    # --------------------------------------------------------
    # 21. Round shipping cost
    # --------------------------------------------------------

    fact_shipments["shipping_cost"] = (
        fact_shipments["shipping_cost"]
        .round(2)
    )

    # --------------------------------------------------------
    # 22. Write output
    # --------------------------------------------------------

    output_file = (
        FACT_DIR / "fact_shipments.csv"
    )

    fact_shipments.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # 23. Print summary
    # --------------------------------------------------------

    print(
        f"Transformed records: "
        f"{len(fact_shipments):,}"
    )

    print(
        f"Total shipping cost: "
        f"{fact_shipments['shipping_cost'].sum():,.2f}"
    )

    print(
        f"Average delivery days: "
        f"{fact_shipments['delivery_days'].mean():.2f}"
    )

    print(
        f"Delayed shipments: "
        f"{(fact_shipments['delivery_status'] == 'DELAYED').sum():,}"
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Shipment fact transformation "
        "completed successfully."
    )

    return fact_shipments


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_shipments()