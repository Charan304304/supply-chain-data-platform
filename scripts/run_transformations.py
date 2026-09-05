import sys
from pathlib import Path


# ============================================================
# ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

PROJECT_ROOT = Path("/opt/supply-chain")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT TRANSFORMATION MODULES
# ============================================================

from transformations.dim_supplier import transform_suppliers
from transformations.dim_product import transform_products
from transformations.dim_warehouse import transform_warehouses
from transformations.dim_customer import transform_customers
from transformations.dim_date import transform_date

from transformations.fact_orders import transform_orders
from transformations.fact_inventory import transform_inventory
from transformations.fact_shipments import transform_shipments
from transformations.fact_purchase_orders import (
    transform_purchase_orders
)


# ============================================================
# RUN ALL TRANSFORMATIONS
# ============================================================

def run_all_transformations():

    print("=" * 70)
    print("SUPPLY CHAIN DATA PLATFORM")
    print("TRANSFORMATION PIPELINE")
    print("=" * 70)

    # ========================================================
    # DIMENSIONS
    # ========================================================

    print("\n[1/9] Transforming supplier dimension...")
    transform_suppliers()

    print("\n[2/9] Transforming product dimension...")
    transform_products()

    print("\n[3/9] Transforming warehouse dimension...")
    transform_warehouses()

    print("\n[4/9] Transforming customer dimension...")
    transform_customers()

    print("\n[5/9] Transforming date dimension...")
    transform_date()

    # ========================================================
    # FACTS
    # ========================================================

    print("\n[6/9] Transforming orders fact...")
    transform_orders()

    print("\n[7/9] Transforming inventory fact...")
    transform_inventory()

    print("\n[8/9] Transforming shipments fact...")
    transform_shipments()

    print("\n[9/9] Transforming purchase orders fact...")
    transform_purchase_orders()

    # ========================================================
    # COMPLETE
    # ========================================================

    print("\n" + "=" * 70)
    print("ALL TRANSFORMATIONS COMPLETED SUCCESSFULLY")
    print("=" * 70)


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    run_all_transformations()