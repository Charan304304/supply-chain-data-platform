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
# TRANSFORM INVENTORY DATA
# ============================================================

def transform_inventory():

    print("=" * 60)
    print("INVENTORY FACT TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Read source data
    # --------------------------------------------------------

    inventory = pd.read_csv(
        RAW_DIR / "inventory.csv"
    )

    products = pd.read_csv(
        DIM_DIR / "dim_product.csv"
    )

    warehouses = pd.read_csv(
        DIM_DIR / "dim_warehouse.csv"
    )

    print(
        f"Inventory records loaded: "
        f"{len(inventory):,}"
    )

    # --------------------------------------------------------
    # 2. Remove duplicate inventory records
    # --------------------------------------------------------

    before = len(inventory)

    inventory = inventory.drop_duplicates(
        subset=["product_id", "warehouse_id"]
    )

    after = len(inventory)

    print(
        f"Duplicate inventory records removed: "
        f"{before - after:,}"
    )

    # --------------------------------------------------------
    # 3. Clean ID columns
    # --------------------------------------------------------

    inventory["product_id"] = (
        inventory["product_id"]
        .astype(str)
        .str.strip()
    )

    inventory["warehouse_id"] = (
        inventory["warehouse_id"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # 4. Convert numeric columns
    # --------------------------------------------------------

    inventory["stock_quantity"] = pd.to_numeric(
        inventory["stock_quantity"],
        errors="coerce"
    )

    inventory["reorder_level"] = pd.to_numeric(
        inventory["reorder_level"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 5. Validate product references
    # --------------------------------------------------------

    valid_products = set(
        products["product_id"]
        .astype(str)
        .str.strip()
    )

    invalid_products = (
        ~inventory["product_id"]
        .isin(valid_products)
    )

    if invalid_products.any():

        count = invalid_products.sum()

        raise ValueError(
            f"{count:,} inventory records contain "
            f"invalid product_id references."
        )

    # --------------------------------------------------------
    # 6. Validate warehouse references
    # --------------------------------------------------------

    valid_warehouses = set(
        warehouses["warehouse_id"]
        .astype(str)
        .str.strip()
    )

    invalid_warehouses = (
        ~inventory["warehouse_id"]
        .isin(valid_warehouses)
    )

    if invalid_warehouses.any():

        count = invalid_warehouses.sum()

        raise ValueError(
            f"{count:,} inventory records contain "
            f"invalid warehouse_id references."
        )

    # --------------------------------------------------------
    # 7. Validate stock quantity
    # --------------------------------------------------------

    if inventory["stock_quantity"].isnull().any():

        raise ValueError(
            "Null or invalid stock_quantity found."
        )

    if (inventory["stock_quantity"] < 0).any():

        raise ValueError(
            "Negative stock_quantity found."
        )

    # --------------------------------------------------------
    # 8. Validate reorder level
    # --------------------------------------------------------

    if inventory["reorder_level"].isnull().any():

        raise ValueError(
            "Null or invalid reorder_level found."
        )

    if (inventory["reorder_level"] < 0).any():

        raise ValueError(
            "Negative reorder_level found."
        )

    # --------------------------------------------------------
    # 9. Prepare product cost lookup
    # --------------------------------------------------------

    product_costs = products[
        [
            "product_id",
            "unit_cost"
        ]
    ].copy()

    product_costs["product_id"] = (
        product_costs["product_id"]
        .astype(str)
        .str.strip()
    )

    product_costs["unit_cost"] = pd.to_numeric(
        product_costs["unit_cost"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 10. Join product cost
    # --------------------------------------------------------

    inventory = inventory.merge(
        product_costs,
        on="product_id",
        how="left",
        validate="many_to_one"
    )

    # --------------------------------------------------------
    # 11. Validate product cost
    # --------------------------------------------------------

    if inventory["unit_cost"].isnull().any():

        raise ValueError(
            "Missing product unit_cost found "
            "during inventory transformation."
        )

    if (inventory["unit_cost"] < 0).any():

        raise ValueError(
            "Negative product unit_cost found."
        )

    # --------------------------------------------------------
    # 12. Calculate inventory value
    # --------------------------------------------------------

    inventory["inventory_value"] = (
        inventory["stock_quantity"]
        * inventory["unit_cost"]
    )

    # --------------------------------------------------------
    # 13. Create low-stock indicator
    # --------------------------------------------------------

    inventory["low_stock_flag"] = (
        inventory["stock_quantity"]
        <= inventory["reorder_level"]
    )

    # --------------------------------------------------------
    # 14. Select final fact columns
    # --------------------------------------------------------

    fact_inventory = inventory[
        [
            "product_id",
            "warehouse_id",
            "stock_quantity",
            "reorder_level",
            "unit_cost",
            "inventory_value",
            "low_stock_flag"
        ]
    ].copy()

    # --------------------------------------------------------
    # 15. Round monetary values
    # --------------------------------------------------------

    fact_inventory["unit_cost"] = (
        fact_inventory["unit_cost"]
        .round(2)
    )

    fact_inventory["inventory_value"] = (
        fact_inventory["inventory_value"]
        .round(2)
    )

    # --------------------------------------------------------
    # 16. Final validation
    # --------------------------------------------------------

    if fact_inventory[
        ["product_id", "warehouse_id"]
    ].duplicated().any():

        raise ValueError(
            "Duplicate product_id + warehouse_id "
            "combination found after transformation."
        )

    # --------------------------------------------------------
    # 17. Write output
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR / "fact_inventory.csv"
    )

    fact_inventory.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # 18. Print summary
    # --------------------------------------------------------

    print(
        f"Transformed records: "
        f"{len(fact_inventory):,}"
    )

    print(
        f"Total inventory value: "
        f"{fact_inventory['inventory_value'].sum():,.2f}"
    )

    print(
        f"Low-stock records: "
        f"{fact_inventory['low_stock_flag'].sum():,}"
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Inventory fact transformation "
        "completed successfully."
    )

    return fact_inventory


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_inventory()