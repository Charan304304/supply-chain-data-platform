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
# TRANSFORM PRODUCT DATA
# ============================================================

def transform_products():

    print("=" * 60)
    print("PRODUCT DIMENSION TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Read source data
    # --------------------------------------------------------

    products_file = RAW_DIR / "products.csv"
    suppliers_file = RAW_DIR / "suppliers.csv"

    products = pd.read_csv(
        products_file
    )

    suppliers = pd.read_csv(
        suppliers_file
    )

    print(
        f"Products loaded: {len(products):,}"
    )

    print(
        f"Suppliers loaded: {len(suppliers):,}"
    )


    # --------------------------------------------------------
    # 2. Remove duplicate products
    # --------------------------------------------------------

    before = len(products)

    products = products.drop_duplicates(
        subset=["product_id"]
    )

    after = len(products)

    print(
        f"Duplicate products removed: "
        f"{before - after:,}"
    )


    # --------------------------------------------------------
    # 3. Clean product names
    # --------------------------------------------------------

    products["product_name"] = (
        products["product_name"]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # 4. Standardize category
    # --------------------------------------------------------

    products["category"] = (
        products["category"]
        .astype(str)
        .str.strip()
        .str.title()
    )


    # --------------------------------------------------------
    # 5. Standardize unit cost
    # --------------------------------------------------------

    products["unit_cost"] = pd.to_numeric(
        products["unit_cost"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # 6. Join supplier information
    # --------------------------------------------------------

    supplier_lookup = suppliers[
        [
            "supplier_id",
            "supplier_name"
        ]
    ].drop_duplicates(
        subset=["supplier_id"]
    )

    products = products.merge(
        supplier_lookup,
        on="supplier_id",
        how="left"
    )


    # --------------------------------------------------------
    # 7. Create derived product status
    # --------------------------------------------------------

    products["product_status"] = "ACTIVE"


    # --------------------------------------------------------
    # 8. Select warehouse-friendly columns
    # --------------------------------------------------------

    dim_product = products[
        [
            "product_id",
            "product_name",
            "category",
            "supplier_id",
            "supplier_name",
            "unit_cost",
            "product_status"
        ]
    ].copy()


    # --------------------------------------------------------
    # 9. Final validation
    # --------------------------------------------------------

    if dim_product["product_id"].duplicated().any():

        raise ValueError(
            "Duplicate product_id found "
            "after transformation."
        )


    if dim_product["product_id"].isnull().any():

        raise ValueError(
            "Null product_id found "
            "after transformation."
        )


    # --------------------------------------------------------
    # 10. Write transformed dataset
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR / "dim_product.csv"
    )

    dim_product.to_csv(
        output_file,
        index=False
    )


    print(
        f"Transformed records: "
        f"{len(dim_product):,}"
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Product dimension transformation "
        "completed successfully."
    )

    return dim_product


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_products()