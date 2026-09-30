"""
fix_dirty_rows.py
Exercise 3 helper: simulates someone fixing data-quality issues in the
orders dataset. Run this AFTER the first `dvc add` + commit, to create
a new version of the data for DVC to track.

Run from the tutorials\\ folder (not tutorials\\data\\) -- this matches
Exercise 3, Step 6 in the Lab Guide: python scripts\\fix_dirty_rows.py
"""
import pandas as pd

df = pd.read_parquet("data/orders.parquet")

# Fix: fill missing customer_id with a placeholder
df["customer_id"] = df["customer_id"].fillna("UNKNOWN")

# Fix: negative quantities -> make positive (assume sign error)
df.loc[df["quantity"] < 0, "quantity"] = df.loc[df["quantity"] < 0, "quantity"].abs()

# Fix: zero unit_price -> drop those rows (bad record, no safe fix)
df = df[df["unit_price"] > 0]

# Fix: typo'd category
df["category"] = df["category"].replace("Electroncis", "Electronics")

# Fix: drop exact duplicate order_id rows, keep first occurrence
df = df.drop_duplicates(subset="order_id", keep="first")

df.to_parquet("data/orders.parquet", index=False)
print(f"Fixed dataset written. New row count: {len(df)}")
