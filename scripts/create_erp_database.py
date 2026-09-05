import sqlite3
import pandas as pd
from pathlib import Path


DATABASE_DIR = Path("data/source_system")
DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = DATABASE_DIR / "erp.db"


def create_database():

    print("Creating ERP database...")

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    # -----------------------------
    # Supplier Master
    # -----------------------------

    suppliers = pd.read_csv(
        "data/sample/suppliers.csv"
    )

    suppliers.to_sql(
        "supplier_master",
        connection,
        if_exists="replace",
        index=False
    )

    # -----------------------------
    # Product Master
    # -----------------------------

    products = pd.read_csv(
        "data/sample/products.csv"
    )

    products.to_sql(
        "product_master",
        connection,
        if_exists="replace",
        index=False
    )

    # -----------------------------
    # Warehouse Master
    # -----------------------------

    warehouses = pd.read_csv(
        "data/sample/warehouses.csv"
    )

    warehouses.to_sql(
        "warehouse_master",
        connection,
        if_exists="replace",
        index=False
    )

    # -----------------------------
    # Purchase Orders
    # -----------------------------

    purchase_orders = pd.DataFrame({
        "purchase_order_id": [
            f"PO{i:07d}"
            for i in range(1, 10001)
        ],
        "supplier_id": [
            f"S{i % 100 + 1:04d}"
            for i in range(10000)
        ],
        "product_id": [
            f"P{i % 1000 + 1:05d}"
            for i in range(10000)
        ],
        "quantity": [
            10 + (i % 490)
            for i in range(10000)
        ],
        "status": [
            [
                "Created",
                "Approved",
                "Received",
                "Cancelled"
            ][i % 4]
            for i in range(10000)
        ]
    })

    purchase_orders.to_sql(
        "purchase_orders",
        connection,
        if_exists="replace",
        index=False
    )

    connection.close()

    print(
        f"ERP database created at: "
        f"{DATABASE_PATH}"
    )


if __name__ == "__main__":
    create_database()