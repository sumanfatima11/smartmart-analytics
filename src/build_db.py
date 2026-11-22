import os
import sqlite3

import pandas as pd

CLEAN_PATH = "data/clean/sales_clean.csv"
DB_PATH = "data/smartmart.db"

# ---------- 1. Load clean data ----------
df = pd.read_csv(CLEAN_PATH, parse_dates=["order_date"])
print("Clean rows loaded:", len(df))

# ---------- 2. Build the 4 tables ----------
# Customer table: one row per customer, with first order date
dim_customer = (
    df.groupby("customer_id")
    .agg(customer_name=("customer_name", "first"),
         first_order_date=("order_date", "min"))
    .reset_index()
)
dim_customer["first_order_date"] = dim_customer["first_order_date"].dt.strftime("%Y-%m-%d")

# Product table: one row per product
dim_product = (
    df[["product_id", "product_name", "category"]]
    .drop_duplicates(subset="product_id")
    .reset_index(drop=True)
)

# Date table: one row per date
dates = pd.DataFrame({"order_date": sorted(df["order_date"].unique())})
dates["order_date"] = pd.to_datetime(dates["order_date"])
dim_date = pd.DataFrame({
    "date_id": dates["order_date"].dt.strftime("%Y-%m-%d"),
    "year": dates["order_date"].dt.year,
    "quarter": dates["order_date"].dt.quarter,
    "month": dates["order_date"].dt.month,
    "month_name": dates["order_date"].dt.strftime("%B"),
    "year_month": dates["order_date"].dt.strftime("%Y-%m"),
    "day_name": dates["order_date"].dt.strftime("%A"),
})

# Sales (fact) table
fact_sales = df[[
    "transaction_id", "order_date", "customer_id", "product_id",
    "quantity", "unit_price", "discount_pct", "revenue",
    "city", "region", "channel",
]].copy()
fact_sales["order_date"] = fact_sales["order_date"].dt.strftime("%Y-%m-%d")

# ---------- 3. Save into SQLite ----------
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
dim_customer.to_sql("dim_customer", conn, index=False)
dim_product.to_sql("dim_product", conn, index=False)
dim_date.to_sql("dim_date", conn, index=False)
fact_sales.to_sql("fact_sales", conn, index=False)
conn.close()

print("Database created:", DB_PATH)
print("dim_customer rows:", len(dim_customer))
print("dim_product rows:", len(dim_product))
print("dim_date rows:", len(dim_date))
print("fact_sales rows:", len(fact_sales))