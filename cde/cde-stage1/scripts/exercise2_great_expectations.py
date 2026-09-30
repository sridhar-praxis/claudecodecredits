"""
exercise2_great_expectations.py
Exercise 2: Validate the orders dataset with Great Expectations.
Uses the same orders.parquet from Exercise 1 -- same dataset, new lens.
Run from inside the tutorials/data folder.
"""
import pandas as pd
import great_expectations as gx

df = pd.read_parquet("orders.parquet")
ge_df = gx.from_pandas(df)

# Rule 1: order_id must never be missing
ge_df.expect_column_values_to_not_be_null("order_id")

# Rule 2: customer_id must never be missing
ge_df.expect_column_values_to_not_be_null("customer_id")

# Rule 3: quantity must be a positive number (1 or more)
ge_df.expect_column_values_to_be_between("quantity", min_value=1, max_value=None)

# Rule 4: unit_price must be greater than zero
ge_df.expect_column_values_to_be_between("unit_price", min_value=0.01, max_value=None)

# Rule 5: category must be one of the five known categories
ge_df.expect_column_values_to_be_in_set(
    "category",
    ["Electronics", "Clothing", "Home", "Sports", "Books"]
)

# Rule 6: order_id must be unique (catches duplicate rows)
ge_df.expect_column_values_to_be_unique("order_id")

results = ge_df.validate()

print(f"Overall success: {results['success']}")
print(f"Checks run: {len(results['results'])}")
print()

for r in results["results"]:
    expectation = r["expectation_config"]["expectation_type"]
    column = r["expectation_config"]["kwargs"].get("column", "")
    status = "PASS" if r["success"] else "FAIL"
    unexpected = r["result"].get("unexpected_count", 0)
    print(f"[{status}] {expectation} on '{column}'  (unexpected values: {unexpected})")
