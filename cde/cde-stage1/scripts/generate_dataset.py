"""
generate_dataset.py
Creates the toy 'orders' dataset used across Exercises 1-3 in Stage 1.
Deliberately includes a few dirty rows so the Great Expectations exercise
(Exercise 2) has real problems to catch, not a dataset that always passes.
"""
import pandas as pd
import numpy as np

np.random.seed(42)

N = 500
regions = ["North", "South", "East", "West"]
categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
products = {
    "Electronics": ["Headphones", "Laptop Stand", "USB Cable", "Webcam"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Socks"],
    "Home": ["Lamp", "Cushion", "Mug", "Candle"],
    "Sports": ["Yoga Mat", "Water Bottle", "Resistance Band", "Cap"],
    "Books": ["Notebook", "Novel", "Cookbook", "Planner"],
}

rows = []
for i in range(1, N + 1):
    category = np.random.choice(categories)
    product = np.random.choice(products[category])
    region = np.random.choice(regions)
    order_date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=int(np.random.randint(0, 240)))
    quantity = int(np.random.randint(1, 6))
    unit_price = round(float(np.random.uniform(5, 150)), 2)

    rows.append({
        "order_id": f"ORD{i:05d}",
        "customer_id": f"CUST{np.random.randint(1, 120):04d}",
        "order_date": order_date,
        "category": category,
        "product": product,
        "region": region,
        "quantity": quantity,
        "unit_price": unit_price,
    })

df = pd.DataFrame(rows)

# --- Deliberately inject data-quality problems for the GE exercise ---
# 1) A few missing customer_id values
df.loc[[10, 55, 200], "customer_id"] = None

# 2) A couple of negative quantities (data entry error)
df.loc[[30, 175], "quantity"] = -1

# 3) One zero unit_price (looks like a pricing bug)
df.loc[88, "unit_price"] = 0.0

# 4) One exact duplicate row (same order_id appearing twice)
dup_row = df.loc[300].copy()
dup_row_df = pd.DataFrame([dup_row])
df = pd.concat([df, dup_row_df], ignore_index=True)

# 5) One category value outside the allowed set (typo-like)
df.loc[400, "category"] = "Electroncis"

df.to_parquet("orders.parquet", index=False)
print(f"Wrote orders.parquet with {len(df)} rows (including deliberately dirty rows).")
print(df.head(10).to_string())
