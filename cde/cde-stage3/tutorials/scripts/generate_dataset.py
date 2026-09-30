"""
Generate the Stage 3 dataset: a folder of order-event JSON files.

This simulates an upstream system (a checkout service) dropping one small
JSON file per order into a local "incoming" folder. Exercise 1 uploads this
whole folder to S3 (via LocalStack) exactly as-is.

Run from tutorials\\data (per the Lab Guide):  python ..\\scripts\\generate_dataset.py
Output goes to data\\orders_incoming\\.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)  # same dataset every time this is run

REGIONS = ["North", "South", "East", "West"]
CATEGORIES = ["Electronics", "Clothing", "Home", "Sports", "Books"]
PRODUCTS = {
    "Electronics": ["Headphones", "Charger", "Webcam", "Speaker"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Socks"],
    "Home": ["Mug", "Lamp", "Pillow", "Towel"],
    "Sports": ["Yoga Mat", "Water Bottle", "Resistance Band", "Cap"],
    "Books": ["Notebook", "Planner", "Cookbook", "Novel"],
}
PAYMENT_METHODS = ["credit_card", "debit_card", "upi", "wallet"]
SHIPPING_METHODS = ["standard", "express"]
STATUSES = ["placed", "shipped", "delivered", "cancelled"]
# Weighted so "placed" dominates, matching a realistic snapshot of recent orders
STATUS_WEIGHTS = [0.45, 0.25, 0.25, 0.05]

NUM_ORDERS = 60
BASE_TIME = datetime(2026, 9, 1, 8, 0, 0)


def make_order(order_num: int) -> dict:
    category = random.choice(CATEGORIES)
    product = random.choice(PRODUCTS[category])
    order_time = BASE_TIME + timedelta(minutes=random.randint(0, 60 * 24 * 5))

    return {
        "order_id": f"ORD{order_num:05d}",
        "customer_id": f"CUST{random.randint(1, 25):04d}",
        "order_timestamp": order_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "region": random.choice(REGIONS),
        "category": category,
        "product": product,
        "quantity": random.randint(1, 5),
        "unit_price": round(random.uniform(9.99, 199.99), 2),
        "payment_method": random.choice(PAYMENT_METHODS),
        "shipping_method": random.choice(SHIPPING_METHODS),
        "status": random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0],
    }


def main():
    out_dir = Path("orders_incoming")
    out_dir.mkdir(exist_ok=True)

    # Clear out any previous run so re-running this script is idempotent
    for old_file in out_dir.glob("order_*.json"):
        old_file.unlink()

    for i in range(1, NUM_ORDERS + 1):
        order = make_order(i)
        file_path = out_dir / f"order_{i:04d}.json"
        with open(file_path, "w") as f:
            json.dump(order, f, indent=2)

    print(f"Wrote {NUM_ORDERS} order files to {out_dir}\\")
    print("\nSample order (order_0001.json):")
    with open(out_dir / "order_0001.json") as f:
        print(f.read())


if __name__ == "__main__":
    main()
