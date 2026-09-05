import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path("/opt/supply-chain")

RAW_ERP_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "erp"
)

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
# TRANSFORM PURCHASE ORDERS
# ============================================================

def transform_purchase_orders():

    print("=" * 60)
    print("PURCHASE ORDER FACT TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Read ERP purchase orders
    # --------------------------------------------------------

    purchase_orders = pd.read_csv(
        RAW_ERP_DIR / "purchase_orders.csv"
    )

    print(
        f"Purchase orders loaded: "
        f"{len(purchase_orders):,}"
    )

    # --------------------------------------------------------
    # 2. Read dimensions
    # --------------------------------------------------------

    suppliers = pd.read_csv(
        DIM_DIR / "dim_supplier.csv"
    )

    products = pd.read_csv(
        DIM_DIR / "dim_product.csv"
    )

    # --------------------------------------------------------
    # 3. Remove duplicate purchase orders
    # --------------------------------------------------------

    before = len(purchase_orders)

    purchase_orders = purchase_orders.drop_duplicates(
        subset=["purchase_order_id"]
    )

    after = len(purchase_orders)

    print(
        f"Duplicate purchase orders removed: "
        f"{before - after:,}"
    )

    # --------------------------------------------------------
    # 4. Clean ID columns
    # --------------------------------------------------------

    id_columns = [
        "purchase_order_id",
        "supplier_id",
        "product_id"
    ]

    for column in id_columns:

        purchase_orders[column] = (
            purchase_orders[column]
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # 5. Clean status
    # --------------------------------------------------------

    purchase_orders["status"] = (
        purchase_orders["status"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    # --------------------------------------------------------
    # 6. Convert quantity
    # --------------------------------------------------------

    purchase_orders["quantity"] = pd.to_numeric(
        purchase_orders["quantity"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 7. Validate supplier references
    # --------------------------------------------------------

    valid_suppliers = set(
        suppliers["supplier_id"]
        .astype(str)
        .str.strip()
    )

    invalid_suppliers = (
        ~purchase_orders["supplier_id"]
        .isin(valid_suppliers)
    )

    if invalid_suppliers.any():

        count = invalid_suppliers.sum()

        raise ValueError(
            f"{count:,} purchase orders contain "
            f"invalid supplier_id references."
        )

    # --------------------------------------------------------
    # 8. Validate product references
    # --------------------------------------------------------

    valid_products = set(
        products["product_id"]
        .astype(str)
        .str.strip()
    )

    invalid_products = (
        ~purchase_orders["product_id"]
        .isin(valid_products)
    )

    if invalid_products.any():

        count = invalid_products.sum()

        raise ValueError(
            f"{count:,} purchase orders contain "
            f"invalid product_id references."
        )

    # --------------------------------------------------------
    # 9. Validate quantity
    # --------------------------------------------------------

    if purchase_orders["quantity"].isnull().any():

        raise ValueError(
            "Null or invalid purchase order "
            "quantity found."
        )

    if (purchase_orders["quantity"] <= 0).any():

        raise ValueError(
            "Purchase order quantity must be "
            "greater than zero."
        )

    # --------------------------------------------------------
    # 10. Validate status
    # --------------------------------------------------------

    valid_statuses = {
        "Created",
        "Approved",
        "Received",
        "Cancelled"
    }

    invalid_statuses = (
        ~purchase_orders["status"]
        .isin(valid_statuses)
    )

    if invalid_statuses.any():

        invalid_values = (
            purchase_orders.loc[
                invalid_statuses,
                "status"
            ]
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Invalid purchase order status values: "
            f"{invalid_values}"
        )

    # --------------------------------------------------------
    # 11. Prepare product cost lookup
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
    # 12. Join product cost
    # --------------------------------------------------------

    purchase_orders = purchase_orders.merge(
        product_costs,
        on="product_id",
        how="left",
        validate="many_to_one"
    )

    # --------------------------------------------------------
    # 13. Validate product cost
    # --------------------------------------------------------

    if purchase_orders["unit_cost"].isnull().any():

        raise ValueError(
            "Missing product unit_cost found "
            "during purchase order transformation."
        )

    if (purchase_orders["unit_cost"] < 0).any():

        raise ValueError(
            "Negative product unit_cost found."
        )

    # --------------------------------------------------------
    # 14. Calculate purchase order value
    # --------------------------------------------------------

    purchase_orders["purchase_order_value"] = (
        purchase_orders["quantity"]
        * purchase_orders["unit_cost"]
    )

    # --------------------------------------------------------
    # 15. Select final fact columns
    # --------------------------------------------------------

    fact_purchase_orders = purchase_orders[
        [
            "purchase_order_id",
            "supplier_id",
            "product_id",
            "quantity",
            "unit_cost",
            "purchase_order_value",
            "status"
        ]
    ].copy()

    # --------------------------------------------------------
    # 16. Round monetary values
    # --------------------------------------------------------

    fact_purchase_orders["unit_cost"] = (
        fact_purchase_orders["unit_cost"]
        .round(2)
    )

    fact_purchase_orders["purchase_order_value"] = (
        fact_purchase_orders["purchase_order_value"]
        .round(2)
    )

    # --------------------------------------------------------
    # 17. Final validation
    # --------------------------------------------------------

    if fact_purchase_orders[
        "purchase_order_id"
    ].duplicated().any():

        raise ValueError(
            "Duplicate purchase_order_id found "
            "after transformation."
        )

    if fact_purchase_orders[
        "purchase_order_id"
    ].isnull().any():

        raise ValueError(
            "Null purchase_order_id found."
        )

    # --------------------------------------------------------
    # 18. Write output
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR / "fact_purchase_orders.csv"
    )

    fact_purchase_orders.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # 19. Print summary
    # --------------------------------------------------------

    print(
        f"Transformed records: "
        f"{len(fact_purchase_orders):,}"
    )

    print(
        f"Total purchase order value: "
        f"{fact_purchase_orders['purchase_order_value'].sum():,.2f}"
    )

    print(
        "Purchase order status distribution:"
    )

    print(
        fact_purchase_orders["status"]
        .value_counts()
        .to_string()
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Purchase order fact transformation "
        "completed successfully."
    )

    return fact_purchase_orders


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_purchase_orders()