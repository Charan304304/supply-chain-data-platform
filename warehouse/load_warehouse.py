import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path("/opt/supply-chain")

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


# ============================================================
# DATABASE CONNECTION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://"
    "airflow:airflow@postgres/"
    "supply_chain_warehouse"
)

engine = create_engine(
    DATABASE_URL
)


# ============================================================
# TABLE DEFINITIONS
# ============================================================

TABLE_DEFINITIONS = {

    # --------------------------------------------------------
    # SUPPLIER DIMENSION
    # --------------------------------------------------------

    "dim_supplier": """
        CREATE TABLE IF NOT EXISTS dim_supplier (
            supplier_id VARCHAR(20) PRIMARY KEY,
            supplier_name VARCHAR(255) NOT NULL,
            lead_time_days INTEGER,
            reliability_score NUMERIC(10,2),
            supplier_status VARCHAR(20)
        )
    """,

    # --------------------------------------------------------
    # PRODUCT DIMENSION
    # --------------------------------------------------------

    "dim_product": """
        CREATE TABLE IF NOT EXISTS dim_product (
            product_id VARCHAR(20) PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            supplier_id VARCHAR(20),
            supplier_name VARCHAR(255),
            unit_cost NUMERIC(18,2),
            product_status VARCHAR(20),

            CONSTRAINT fk_product_supplier
                FOREIGN KEY (supplier_id)
                REFERENCES dim_supplier(supplier_id)
        )
    """,

    # --------------------------------------------------------
    # WAREHOUSE DIMENSION
    # --------------------------------------------------------

    "dim_warehouse": """
        CREATE TABLE IF NOT EXISTS dim_warehouse (
            warehouse_id VARCHAR(20) PRIMARY KEY,
            warehouse_name VARCHAR(255) NOT NULL,
            city VARCHAR(100),
            state VARCHAR(100),
            capacity NUMERIC(18,2),
            warehouse_status VARCHAR(20)
        )
    """,

    # --------------------------------------------------------
    # CUSTOMER DIMENSION
    # --------------------------------------------------------

    "dim_customer": """
        CREATE TABLE IF NOT EXISTS dim_customer (
            customer_id VARCHAR(20) PRIMARY KEY,
            customer_name VARCHAR(255) NOT NULL,
            city VARCHAR(100),
            state VARCHAR(100),
            registration_date DATE,
            customer_status VARCHAR(20)
        )
    """,

    # --------------------------------------------------------
    # DATE DIMENSION
    # --------------------------------------------------------

    "dim_date": """
        CREATE TABLE IF NOT EXISTS dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date DATE UNIQUE NOT NULL,
            year INTEGER,
            quarter INTEGER,
            month INTEGER,
            month_name VARCHAR(20),
            week INTEGER,
            day INTEGER,
            day_name VARCHAR(20),
            is_weekend BOOLEAN
        )
    """,

    # --------------------------------------------------------
    # ORDERS FACT
    # --------------------------------------------------------

    "fact_orders": """
        CREATE TABLE IF NOT EXISTS fact_orders (
            order_id VARCHAR(20) PRIMARY KEY,
            order_date_key INTEGER NOT NULL,
            customer_id VARCHAR(20) NOT NULL,
            product_id VARCHAR(20) NOT NULL,
            warehouse_id VARCHAR(20) NOT NULL,
            quantity NUMERIC(18,2),
            unit_price NUMERIC(18,2),
            total_amount NUMERIC(18,2),

            CONSTRAINT fk_orders_date
                FOREIGN KEY (order_date_key)
                REFERENCES dim_date(date_key),

            CONSTRAINT fk_orders_customer
                FOREIGN KEY (customer_id)
                REFERENCES dim_customer(customer_id),

            CONSTRAINT fk_orders_product
                FOREIGN KEY (product_id)
                REFERENCES dim_product(product_id),

            CONSTRAINT fk_orders_warehouse
                FOREIGN KEY (warehouse_id)
                REFERENCES dim_warehouse(warehouse_id)
        )
    """,

    # --------------------------------------------------------
    # INVENTORY FACT
    # --------------------------------------------------------

    "fact_inventory": """
        CREATE TABLE IF NOT EXISTS fact_inventory (
            product_id VARCHAR(20) NOT NULL,
            warehouse_id VARCHAR(20) NOT NULL,
            stock_quantity NUMERIC(18,2),
            reorder_level NUMERIC(18,2),
            unit_cost NUMERIC(18,2),
            inventory_value NUMERIC(18,2),
            low_stock_flag BOOLEAN,

            PRIMARY KEY (
                product_id,
                warehouse_id
            ),

            CONSTRAINT fk_inventory_product
                FOREIGN KEY (product_id)
                REFERENCES dim_product(product_id),

            CONSTRAINT fk_inventory_warehouse
                FOREIGN KEY (warehouse_id)
                REFERENCES dim_warehouse(warehouse_id)
        )
    """,

    # --------------------------------------------------------
    # SHIPMENTS FACT
    # --------------------------------------------------------

    "fact_shipments": """
        CREATE TABLE IF NOT EXISTS fact_shipments (
            shipment_id VARCHAR(20) PRIMARY KEY,
            order_id VARCHAR(20) NOT NULL,
            supplier_id VARCHAR(20) NOT NULL,
            warehouse_id VARCHAR(20) NOT NULL,
            dispatch_date_key INTEGER NOT NULL,
            expected_delivery_date_key INTEGER NOT NULL,
            actual_delivery_date_key INTEGER NOT NULL,
            shipping_mode VARCHAR(50),
            shipping_cost NUMERIC(18,2),
            delivery_days INTEGER,
            delay_days INTEGER,
            delivery_status VARCHAR(20),

            CONSTRAINT fk_shipments_order
                FOREIGN KEY (order_id)
                REFERENCES fact_orders(order_id),

            CONSTRAINT fk_shipments_supplier
                FOREIGN KEY (supplier_id)
                REFERENCES dim_supplier(supplier_id),

            CONSTRAINT fk_shipments_warehouse
                FOREIGN KEY (warehouse_id)
                REFERENCES dim_warehouse(warehouse_id),

            CONSTRAINT fk_shipments_dispatch_date
                FOREIGN KEY (dispatch_date_key)
                REFERENCES dim_date(date_key),

            CONSTRAINT fk_shipments_expected_date
                FOREIGN KEY (expected_delivery_date_key)
                REFERENCES dim_date(date_key),

            CONSTRAINT fk_shipments_actual_date
                FOREIGN KEY (actual_delivery_date_key)
                REFERENCES dim_date(date_key)
        )
    """,

    # --------------------------------------------------------
    # PURCHASE ORDERS FACT
    # --------------------------------------------------------

    "fact_purchase_orders": """
        CREATE TABLE IF NOT EXISTS fact_purchase_orders (
            purchase_order_id VARCHAR(20) PRIMARY KEY,
            supplier_id VARCHAR(20) NOT NULL,
            product_id VARCHAR(20) NOT NULL,
            quantity NUMERIC(18,2),
            unit_cost NUMERIC(18,2),
            purchase_order_value NUMERIC(18,2),
            status VARCHAR(20),

            CONSTRAINT fk_purchase_supplier
                FOREIGN KEY (supplier_id)
                REFERENCES dim_supplier(supplier_id),

            CONSTRAINT fk_purchase_product
                FOREIGN KEY (product_id)
                REFERENCES dim_product(product_id)
        )
    """
}


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    print("=" * 70)
    print("CREATING DATA WAREHOUSE TABLES")
    print("=" * 70)

    table_order = [
        "dim_supplier",
        "dim_product",
        "dim_warehouse",
        "dim_customer",
        "dim_date",
        "fact_orders",
        "fact_inventory",
        "fact_shipments",
        "fact_purchase_orders"
    ]

    with engine.begin() as connection:

        for table_name in table_order:

            print(
                f"Creating table: {table_name}"
            )

            connection.execute(
                text(
                    TABLE_DEFINITIONS[
                        table_name
                    ]
                )
            )

    print(
        "All warehouse tables are ready."
    )


# ============================================================
# CLEAR EXISTING DATA
# ============================================================

def clear_warehouse():

    print("=" * 70)
    print("CLEARING EXISTING WAREHOUSE DATA")
    print("=" * 70)

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    fact_shipments,
                    fact_inventory,
                    fact_purchase_orders,
                    fact_orders,
                    dim_product,
                    dim_customer,
                    dim_warehouse,
                    dim_date,
                    dim_supplier
                CASCADE
                """
            )
        )

    print(
        "Existing warehouse data cleared successfully."
    )


# ============================================================
# LOAD TABLE
# ============================================================

def load_table(
    table_name,
    file_path,
    chunksize=10000
):

    print(
        f"\nLoading {table_name}..."
    )

    print(
        f"Source file: {file_path}"
    )

    dataframe = pd.read_csv(
        file_path
    )

    total_records = len(dataframe)

    print(
        f"Records to load: {total_records:,}"
    )

    # --------------------------------------------------------
    # Small tables
    # --------------------------------------------------------

    if total_records <= chunksize:

        dataframe.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False,
            method="multi",
        )

        print(
            f"{table_name}: "
            f"{total_records:,} records loaded."
        )

        return

    # --------------------------------------------------------
    # Large tables
    # --------------------------------------------------------

    total_chunks = (
        (total_records + chunksize - 1)
        // chunksize
    )

    print(
        f"Using chunked loading: "
        f"{total_chunks} chunks "
        f"of up to {chunksize:,} records."
    )

    for chunk_number, start in enumerate(
        range(
            0,
            total_records,
            chunksize
        ),
        start=1
    ):

        end = min(
            start + chunksize,
            total_records
        )

        chunk = dataframe.iloc[
            start:end
        ]

        print(
            f"Loading chunk "
            f"{chunk_number}/{total_chunks}: "
            f"records {start + 1:,}-"
            f"{end:,}"
        )

        chunk.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False,
            method="multi",
        )

        print(
            f"Chunk {chunk_number}/{total_chunks} "
            f"completed."
        )

    print(
        f"{table_name}: "
        f"{total_records:,} records loaded successfully."
    )


# ============================================================
# VALIDATE ROW COUNTS
# ============================================================

def validate_row_counts(
    expected_counts
):

    print("\n" + "=" * 70)
    print("WAREHOUSE ROW COUNT VALIDATION")
    print("=" * 70)

    validation_failed = False

    with engine.connect() as connection:

        for table_name, expected in expected_counts.items():

            result = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM {table_name}
                    """
                )
            )

            actual = result.scalar()

            if actual == expected:

                status = "PASS"

            else:

                status = "FAIL"

                validation_failed = True

            print(
                f"{table_name:<25}"
                f"{actual:>10,} "
                f"(expected {expected:,}) "
                f"{status}"
            )

    if validation_failed:

        raise RuntimeError(
            "Warehouse row count validation failed."
        )

    print(
        "\nAll warehouse row count validations passed."
    )


# ============================================================
# MAIN WAREHOUSE LOAD
# ============================================================

def load_warehouse():

    print("=" * 70)
    print("SUPPLY CHAIN DATA WAREHOUSE LOAD")
    print("=" * 70)

    # --------------------------------------------------------
    # STEP 1: Create tables
    # --------------------------------------------------------

    create_tables()

    # --------------------------------------------------------
    # STEP 2: Clear previous data
    # --------------------------------------------------------

    clear_warehouse()

    # --------------------------------------------------------
    # STEP 3: Load dimensions first
    # --------------------------------------------------------

    dimension_tables = [

        "dim_supplier",
        "dim_product",
        "dim_warehouse",
        "dim_customer",
        "dim_date"

    ]

    print("\n" + "=" * 70)
    print("LOADING DIMENSION TABLES")
    print("=" * 70)

    for table_name in dimension_tables:

        load_table(
            table_name,
            DIM_DIR / f"{table_name}.csv"
        )

    # --------------------------------------------------------
    # STEP 4: Load facts
    # --------------------------------------------------------

    fact_tables = [

        "fact_orders",
        "fact_inventory",
        "fact_shipments",
        "fact_purchase_orders"

    ]

    print("\n" + "=" * 70)
    print("LOADING FACT TABLES")
    print("=" * 70)

    for table_name in fact_tables:

        load_table(
            table_name,
            FACT_DIR / f"{table_name}.csv"
        )

    # --------------------------------------------------------
    # STEP 5: Validate warehouse
    # --------------------------------------------------------

    expected_counts = {

        "dim_supplier": 100,

        "dim_product": 1000,

        "dim_warehouse": 10,

        "dim_customer": 10000,

        "dim_date": 2557,

        "fact_orders": 100000,

        "fact_inventory": 1000,

        "fact_shipments": 59953,

        "fact_purchase_orders": 10000

    }

    validate_row_counts(
        expected_counts
    )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("WAREHOUSE LOAD COMPLETED SUCCESSFULLY")
    print("=" * 70)


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    load_warehouse()