import pandas as pd
from pathlib import Path


SOURCE_DIR = Path("data/sample")
OUTPUT_DIR = Path("data/raw")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_bad_data():
    print("Creating raw datasets with intentional data issues...")

    # -------------------------
    # Suppliers
    # -------------------------
    suppliers = pd.read_csv(SOURCE_DIR / "suppliers.csv")

    # Missing supplier name
    suppliers.loc[2, "supplier_name"] = None

    # Invalid lead time
    suppliers.loc[5, "lead_time_days"] = -3

    suppliers.to_csv(
        OUTPUT_DIR / "suppliers.csv",
        index=False
    )

    # -------------------------
    # Products
    # -------------------------
    products = pd.read_csv(SOURCE_DIR / "products.csv")

    # Invalid supplier reference
    products.loc[10, "supplier_id"] = "S9999"

    # Negative product cost
    products.loc[20, "unit_cost"] = -500

    products.to_csv(
        OUTPUT_DIR / "products.csv",
        index=False
    )

    # -------------------------
    # Inventory
    # -------------------------
    inventory = pd.read_csv(SOURCE_DIR / "inventory.csv")

    # Negative stock
    inventory.loc[15, "stock_quantity"] = -100

    # Invalid product reference
    inventory.loc[25, "product_id"] = "P99999"

    inventory.to_csv(
        OUTPUT_DIR / "inventory.csv",
        index=False
    )

    # -------------------------
    # Orders
    # -------------------------
    orders = pd.read_csv(SOURCE_DIR / "orders.csv")

    # Negative quantity
    orders.loc[100, "quantity"] = -5

    # Invalid customer
    orders.loc[200, "customer_id"] = "C999999"

    # Duplicate order
    orders.loc[300] = orders.loc[299]

    orders.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False
    )

    # -------------------------
    # Shipments
    # -------------------------
    shipments = pd.read_csv(SOURCE_DIR / "shipments.csv")

    # Negative shipping cost
    shipments.loc[10, "shipping_cost"] = -1000

    # Invalid order reference
    shipments.loc[20, "order_id"] = "O99999999"

    shipments.to_csv(
        OUTPUT_DIR / "shipments.csv",
        index=False
    )

    # -------------------------
    # Warehouses
    # -------------------------
    warehouses = pd.read_csv(
        SOURCE_DIR / "warehouses.csv"
    )

    # Invalid capacity
    warehouses.loc[2, "capacity"] = -500

    warehouses.to_csv(
        OUTPUT_DIR / "warehouses.csv",
        index=False
    )

    # -------------------------
    # Customers
    # -------------------------
    customers = pd.read_csv(
        SOURCE_DIR / "customers.csv"
    )

    # Missing customer name
    customers.loc[5, "customer_name"] = None

    customers.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False
    )

    print("Raw datasets created successfully.")


if __name__ == "__main__":
    create_bad_data()