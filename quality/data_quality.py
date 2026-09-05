import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path("/opt/supply-chain")

RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "data" / "quality_reports"


REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# GENERIC CHECKS
# ============================================================

def check_required_columns(df, required_columns):

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    return missing_columns


def check_nulls(df, columns):

    results = {}

    for column in columns:

        results[column] = int(
            df[column].isnull().sum()
        )

    return results


def check_duplicates(df, column):

    return int(
        df[column].duplicated().sum()
    )


def check_numeric_range(
    df,
    column,
    minimum=None,
    maximum=None
):

    invalid_count = 0

    if minimum is not None:

        invalid_count += (
            df[column] < minimum
        ).sum()

    if maximum is not None:

        invalid_count += (
            df[column] > maximum
        ).sum()

    return int(invalid_count)


# ============================================================
# SUPPLIER VALIDATION
# ============================================================

def validate_suppliers():

    file = RAW_DIR / "suppliers.csv"

    df = pd.read_csv(file)

    results = {}

    results["row_count"] = len(df)

    results["missing_supplier_id"] = int(
        df["supplier_id"].isnull().sum()
    )

    results["duplicate_supplier_id"] = check_duplicates(
        df,
        "supplier_id"
    )

    results["missing_supplier_name"] = int(
        df["supplier_name"].isnull().sum()
    )

    results["invalid_lead_time"] = check_numeric_range(
        df,
        "lead_time_days",
        minimum=1
    )

    results["invalid_reliability"] = check_numeric_range(
        df,
        "reliability_score",
        minimum=0,
        maximum=1
    )

    return results


# ============================================================
# PRODUCT VALIDATION
# ============================================================

def validate_products():

    file = RAW_DIR / "products.csv"

    df = pd.read_csv(file)

    suppliers = pd.read_csv(
        RAW_DIR / "suppliers.csv"
    )

    results = {}

    results["row_count"] = len(df)

    results["duplicate_product_id"] = check_duplicates(
        df,
        "product_id"
    )

    results["missing_product_name"] = int(
        df["product_name"].isnull().sum()
    )

    results["invalid_unit_cost"] = check_numeric_range(
        df,
        "unit_cost",
        minimum=0
    )

    results["invalid_supplier_reference"] = int(
        (~df["supplier_id"].isin(
            suppliers["supplier_id"]
        )).sum()
    )

    return results


# ============================================================
# INVENTORY VALIDATION
# ============================================================

def validate_inventory():

    file = RAW_DIR / "inventory.csv"

    df = pd.read_csv(file)

    products = pd.read_csv(
        RAW_DIR / "products.csv"
    )

    warehouses = pd.read_csv(
        RAW_DIR / "warehouses.csv"
    )

    results = {}

    results["row_count"] = len(df)

    results["duplicate_inventory_id"] = check_duplicates(
        df,
        "inventory_id"
    )

    results["invalid_stock"] = check_numeric_range(
        df,
        "stock_quantity",
        minimum=0
    )

    results["invalid_product_reference"] = int(
        (~df["product_id"].isin(
            products["product_id"]
        )).sum()
    )

    results["invalid_warehouse_reference"] = int(
        (~df["warehouse_id"].isin(
            warehouses["warehouse_id"]
        )).sum()
    )

    return results


# ============================================================
# ORDER VALIDATION
# ============================================================

def validate_orders():

    file = RAW_DIR / "orders.csv"

    df = pd.read_csv(file)

    customers = pd.read_csv(
        RAW_DIR / "customers.csv"
    )

    products = pd.read_csv(
        RAW_DIR / "products.csv"
    )

    warehouses = pd.read_csv(
        RAW_DIR / "warehouses.csv"
    )

    results = {}

    results["row_count"] = len(df)

    results["duplicate_order_id"] = check_duplicates(
        df,
        "order_id"
    )

    results["invalid_quantity"] = check_numeric_range(
        df,
        "quantity",
        minimum=1
    )

    results["invalid_unit_price"] = check_numeric_range(
        df,
        "unit_price",
        minimum=0
    )

    results["invalid_customer_reference"] = int(
        (~df["customer_id"].isin(
            customers["customer_id"]
        )).sum()
    )

    results["invalid_product_reference"] = int(
        (~df["product_id"].isin(
            products["product_id"]
        )).sum()
    )

    results["invalid_warehouse_reference"] = int(
        (~df["warehouse_id"].isin(
            warehouses["warehouse_id"]
        )).sum()
    )

    return results


# ============================================================
# SHIPMENT VALIDATION
# ============================================================

def validate_shipments():

    file = RAW_DIR / "shipments.csv"

    df = pd.read_csv(file)

    orders = pd.read_csv(
        RAW_DIR / "orders.csv"
    )

    results = {}

    results["row_count"] = len(df)

    results["duplicate_shipment_id"] = check_duplicates(
        df,
        "shipment_id"
    )

    results["invalid_shipping_cost"] = check_numeric_range(
        df,
        "shipping_cost",
        minimum=0
    )

    results["invalid_order_reference"] = int(
        (~df["order_id"].isin(
            orders["order_id"]
        )).sum()
    )

    return results


# ============================================================
# RUN ALL QUALITY CHECKS
# ============================================================

def run_quality_checks():

    report = {

        "suppliers": validate_suppliers(),

        "products": validate_products(),

        "inventory": validate_inventory(),

        "orders": validate_orders(),

        "shipments": validate_shipments()

    }

    return report


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    report = run_quality_checks()

    print("\n")

    print("=" * 70)
    print("SUPPLY CHAIN DATA QUALITY REPORT")
    print("=" * 70)

    for dataset, checks in report.items():

        print(f"\n[{dataset.upper()}]")

        for check, value in checks.items():

            if value == 0:

                status = "PASS"

            else:

                status = "FAIL"

            print(
                f"{check:<40} "
                f"{status:<6} "
                f"{value}"
            )