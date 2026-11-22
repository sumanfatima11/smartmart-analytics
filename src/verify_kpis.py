import sqlite3

import pandas as pd

DB_PATH = "data/smartmart.db"
CLEAN_PATH = "data/clean/sales_clean.csv"
SQL_PATH = "sql/kpi_queries.sql"

# ---------- 1. Run the SQL queries ----------
conn = sqlite3.connect(DB_PATH)
with open(SQL_PATH, encoding="utf-8") as f:
    queries = [q.strip() for q in f.read().split(";") if q.strip()]

sql_kpi = pd.read_sql_query(queries[0], conn)
sql_repeat = pd.read_sql_query(queries[4], conn)
sql_region = pd.read_sql_query(queries[3], conn)
conn.close()

# ---------- 2. Calculate the same KPIs with pandas ----------
df = pd.read_csv(CLEAN_PATH)

pd_revenue = round(df["revenue"].sum(), 2)
pd_orders = df["transaction_id"].nunique()
pd_units = int(df["quantity"].sum())
pd_aov = round(pd_revenue / pd_orders, 2)
pd_customers = df["customer_id"].nunique()

orders_per_customer = df.groupby("customer_id").size()
pd_repeat = round(100 * (orders_per_customer >= 2).sum() / len(orders_per_customer), 2)

pd_region = df.groupby("region")["revenue"].sum().round(2).sort_values(ascending=False)

# ---------- 3. Compare ----------
def check(name, sql_value, pandas_value):
    status = "PASS" if abs(float(sql_value) - float(pandas_value)) < 0.01 else "FAIL"
    print(f"{name:<18} SQL={sql_value:<15} Pandas={pandas_value:<15} {status}")

check("Total Revenue", sql_kpi["total_revenue"][0], pd_revenue)
check("Total Orders", sql_kpi["total_orders"][0], pd_orders)
check("Units Sold", sql_kpi["units_sold"][0], pd_units)
check("Avg Order Value", sql_kpi["avg_order_value"][0], pd_aov)
check("Active Customers", sql_kpi["active_customers"][0], pd_customers)
check("Repeat Rate %", sql_repeat["repeat_rate_pct"][0], pd_repeat)

for _, row in sql_region.iterrows():
    check(f"Region {row['region']}", row["revenue"], pd_region[row["region"]])