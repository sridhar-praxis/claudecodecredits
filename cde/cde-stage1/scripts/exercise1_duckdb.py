"""
exercise1_duckdb.py
Exercise 1: Query the orders dataset with DuckDB.
Run from inside the tutorials/data folder (where orders.parquet lives).
"""
import duckdb

con = duckdb.connect()

print("=== Total rows in orders.parquet ===")
result = con.execute("SELECT COUNT(*) AS row_count FROM 'orders.parquet'").fetchdf()
print(result)

print("\n=== Total revenue by region ===")
result = con.execute("""
    SELECT region,
           ROUND(SUM(quantity * unit_price), 2) AS total_revenue
    FROM 'orders.parquet'
    GROUP BY region
    ORDER BY total_revenue DESC
""").fetchdf()
print(result)

print("\n=== Top 5 products by units sold ===")
result = con.execute("""
    SELECT product,
           SUM(quantity) AS total_units
    FROM 'orders.parquet'
    GROUP BY product
    ORDER BY total_units DESC
    LIMIT 5
""").fetchdf()
print(result)

print("\n=== Orders with suspicious values (negative quantity or zero price) ===")
result = con.execute("""
    SELECT order_id, customer_id, quantity, unit_price
    FROM 'orders.parquet'
    WHERE quantity < 0 OR unit_price = 0
""").fetchdf()
print(result)

con.close()
