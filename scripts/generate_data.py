from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

fake = Faker("en_IN")

# Reproducibility
random.seed(42)
Faker.seed(42)

# Output directory
OUTPUT_DIR = Path("data/sample")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_suppliers(n=100):
    suppliers = []

    for i in range(1, n + 1):
        suppliers.append({
            "supplier_id": f"S{i:04d}",
            "supplier_name": fake.company(),
            "location": fake.city(),
            "country": "India",
            "lead_time_days": random.randint(2, 15),
            "reliability_score": round(random.uniform(0.70, 0.99), 2)
        })

    return pd.DataFrame(suppliers)
def generate_warehouses(n=10):
    warehouses = []

    for i in range(1, n + 1):
        warehouses.append({
            "warehouse_id": f"W{i:03d}",
            "warehouse_name": f"Warehouse {i}",
            "city": fake.city(),
            "state": fake.state(),
            "capacity": random.randint(5000, 50000)
        })

    return pd.DataFrame(warehouses)
def generate_products(n=1000, supplier_count=100):
    categories = [
        "Electronics",
        "Furniture",
        "Clothing",
        "Appliances",
        "Automotive",
        "Grocery",
        "Industrial"
    ]

    products = []

    for i in range(1, n + 1):
        products.append({
            "product_id": f"P{i:05d}",
            "product_name": fake.catch_phrase(),
            "category": random.choice(categories),
            "supplier_id": f"S{random.randint(1, supplier_count):04d}",
            "unit_cost": round(random.uniform(100, 50000), 2)
        })

    return pd.DataFrame(products)
def generate_customers(n=10000):
    customers = []

    for i in range(1, n + 1):
        customers.append({
            "customer_id": f"C{i:06d}",
            "customer_name": fake.name(),
            "city": fake.city(),
            "state": fake.state(),
            "registration_date": fake.date_between(
                start_date="-5y",
                end_date="today"
            )
        })

    return pd.DataFrame(customers)
def generate_inventory(products, warehouses):
    inventory = []

    for _, product in products.iterrows():
        warehouse = random.choice(warehouses["warehouse_id"].tolist())

        stock = random.randint(0, 1000)
        reorder_level = random.randint(50, 300)
        safety_stock = random.randint(20, 150)

        inventory.append({
            "inventory_id": f"I{len(inventory)+1:07d}",
            "product_id": product["product_id"],
            "warehouse_id": warehouse,
            "stock_quantity": stock,
            "reorder_level": reorder_level,
            "safety_stock": safety_stock,
            "inventory_date": datetime.now().date()
        })

    return pd.DataFrame(inventory)
def generate_orders(n, customers, products, warehouses):
    orders = []

    statuses = [
        "Pending",
        "Processing",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    priorities = [
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    customer_ids = customers["customer_id"].tolist()
    product_ids = products["product_id"].tolist()
    warehouse_ids = warehouses["warehouse_id"].tolist()

    for i in range(1, n + 1):

        quantity = random.randint(1, 20)
        unit_price = round(random.uniform(100, 50000), 2)

        order_date = fake.date_between(
            start_date="-1y",
            end_date="today"
        )

        orders.append({
            "order_id": f"O{i:08d}",
            "customer_id": random.choice(customer_ids),
            "product_id": random.choice(product_ids),
            "warehouse_id": random.choice(warehouse_ids),
            "order_date": order_date,
            "quantity": quantity,
            "unit_price": unit_price,
            "status": random.choice(statuses),
            "priority": random.choice(priorities)
        })

    return pd.DataFrame(orders)
def generate_shipments(orders, suppliers):
    shipments = []

    shipping_modes = [
        "Road",
        "Rail",
        "Air",
        "Sea"
    ]

    for i, (_, order) in enumerate(orders.iterrows(), start=1):

        if order["status"] in ["Cancelled", "Pending"]:
            continue

        dispatch_date = pd.to_datetime(order["order_date"]) + timedelta(
            days=random.randint(1, 5)
        )

        expected_delivery = dispatch_date + timedelta(
            days=random.randint(2, 10)
        )

        actual_delivery = expected_delivery + timedelta(
            days=random.randint(-2, 7)
        )

        shipments.append({
            "shipment_id": f"SH{i:08d}",
            "order_id": order["order_id"],
            "supplier_id": random.choice(
                suppliers["supplier_id"].tolist()
            ),
            "warehouse_id": order["warehouse_id"],
            "dispatch_date": dispatch_date.date(),
            "expected_delivery_date": expected_delivery.date(),
            "actual_delivery_date": actual_delivery.date(),
            "shipping_mode": random.choice(shipping_modes),
            "shipping_cost": round(random.uniform(500, 20000), 2)
        })

    return pd.DataFrame(shipments)
if __name__ == "__main__":

    print("Generating supply chain data...")

    suppliers = generate_suppliers(100)
    warehouses = generate_warehouses(10)
    products = generate_products(1000, 100)
    customers = generate_customers(10000)
    inventory = generate_inventory(products, warehouses)
    orders = generate_orders(
        100000,
        customers,
        products,
        warehouses
    )
    shipments = generate_shipments(orders, suppliers)

    suppliers.to_csv(
        OUTPUT_DIR / "suppliers.csv",
        index=False
    )

    warehouses.to_csv(
        OUTPUT_DIR / "warehouses.csv",
        index=False
    )

    products.to_csv(
        OUTPUT_DIR / "products.csv",
        index=False
    )

    customers.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False
    )

    inventory.to_csv(
        OUTPUT_DIR / "inventory.csv",
        index=False
    )

    orders.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False
    )

    shipments.to_csv(
        OUTPUT_DIR / "shipments.csv",
        index=False
    )

    print("Data generation completed!")