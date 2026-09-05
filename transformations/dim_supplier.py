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

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TRANSFORM SUPPLIER DATA
# ============================================================

def transform_suppliers():

    print("=" * 60)
    print("SUPPLIER DIMENSION TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Read supplier data
    # --------------------------------------------------------

    suppliers_file = RAW_DIR / "suppliers.csv"

    suppliers = pd.read_csv(
        suppliers_file
    )

    print(
        f"Suppliers loaded: {len(suppliers):,}"
    )


    # --------------------------------------------------------
    # 2. Remove duplicate suppliers
    # --------------------------------------------------------

    before = len(suppliers)

    suppliers = suppliers.drop_duplicates(
        subset=["supplier_id"]
    )

    after = len(suppliers)

    print(
        f"Duplicate suppliers removed: "
        f"{before - after:,}"
    )


    # --------------------------------------------------------
    # 3. Clean supplier name
    # --------------------------------------------------------

    suppliers["supplier_name"] = (
        suppliers["supplier_name"]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # 4. Standardize lead time
    # --------------------------------------------------------

    suppliers["lead_time_days"] = pd.to_numeric(
        suppliers["lead_time_days"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # 5. Standardize reliability score
    # --------------------------------------------------------

    suppliers["reliability_score"] = pd.to_numeric(
        suppliers["reliability_score"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # 6. Create supplier status
    # --------------------------------------------------------

    suppliers["supplier_status"] = "ACTIVE"


    # --------------------------------------------------------
    # 7. Select warehouse columns
    # --------------------------------------------------------

    dim_supplier = suppliers[
        [
            "supplier_id",
            "supplier_name",
            "lead_time_days",
            "reliability_score",
            "supplier_status"
        ]
    ].copy()


    # --------------------------------------------------------
    # 8. Final validation
    # --------------------------------------------------------

    if dim_supplier["supplier_id"].duplicated().any():

        raise ValueError(
            "Duplicate supplier_id found "
            "after transformation."
        )


    if dim_supplier["supplier_id"].isnull().any():

        raise ValueError(
            "Null supplier_id found "
            "after transformation."
        )


    # --------------------------------------------------------
    # 9. Write transformed dataset
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR / "dim_supplier.csv"
    )

    dim_supplier.to_csv(
        output_file,
        index=False
    )


    print(
        f"Transformed records: "
        f"{len(dim_supplier):,}"
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Supplier dimension transformation "
        "completed successfully."
    )

    return dim_supplier


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_suppliers()