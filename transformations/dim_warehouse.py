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
# TRANSFORM WAREHOUSE DATA
# ============================================================

def transform_warehouses():

    print("=" * 60)
    print("WAREHOUSE DIMENSION TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Read warehouse data
    # --------------------------------------------------------

    warehouses_file = RAW_DIR / "warehouses.csv"

    warehouses = pd.read_csv(
        warehouses_file
    )

    print(
        f"Warehouses loaded: {len(warehouses):,}"
    )

    # --------------------------------------------------------
    # 2. Remove duplicate warehouses
    # --------------------------------------------------------

    before = len(warehouses)

    warehouses = warehouses.drop_duplicates(
        subset=["warehouse_id"]
    )

    after = len(warehouses)

    print(
        f"Duplicate warehouses removed: "
        f"{before - after:,}"
    )

    # --------------------------------------------------------
    # 3. Clean text columns
    # --------------------------------------------------------

    text_columns = [
        "warehouse_name",
        "city",
        "state"
    ]

    for column in text_columns:

        warehouses[column] = (
            warehouses[column]
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # 4. Standardize capacity
    # --------------------------------------------------------

    warehouses["capacity"] = pd.to_numeric(
        warehouses["capacity"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 5. Create warehouse status
    # --------------------------------------------------------

    warehouses["warehouse_status"] = "ACTIVE"

    # --------------------------------------------------------
    # 6. Select warehouse columns
    # --------------------------------------------------------

    dim_warehouse = warehouses[
        [
            "warehouse_id",
            "warehouse_name",
            "city",
            "state",
            "capacity",
            "warehouse_status"
        ]
    ].copy()

    # --------------------------------------------------------
    # 7. Final validation
    # --------------------------------------------------------

    if dim_warehouse["warehouse_id"].duplicated().any():

        raise ValueError(
            "Duplicate warehouse_id found "
            "after transformation."
        )

    if dim_warehouse["warehouse_id"].isnull().any():

        raise ValueError(
            "Null warehouse_id found "
            "after transformation."
        )

    if dim_warehouse["capacity"].isnull().any():

        raise ValueError(
            "Invalid or null warehouse capacity "
            "found after transformation."
        )

    if (dim_warehouse["capacity"] < 0).any():

        raise ValueError(
            "Negative warehouse capacity "
            "found after transformation."
        )

    # --------------------------------------------------------
    # 8. Write transformed dataset
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR / "dim_warehouse.csv"
    )

    dim_warehouse.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # 9. Print summary
    # --------------------------------------------------------

    print(
        f"Transformed records: "
        f"{len(dim_warehouse):,}"
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Warehouse dimension transformation "
        "completed successfully."
    )

    return dim_warehouse


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_warehouses()