import os
import random
from datetime import date, timedelta

import pandas as pd

random.seed(42)

# (product_id, product_name, category, base_price in PKR)
PRODUCTS = [
    ("P001", "Samsung TV 43 inch", "Electronics", 55000),
    ("P002", "iPhone 13", "Electronics", 150000),
    ("P003", "Bluetooth Headphones", "Electronics", 6000),
    ("P004", "Laptop HP 15", "Electronics", 120000),
    ("P005", "Men Cotton Shirt", "Clothing", 2500),
    ("P006", "Women Lawn Suit", "Clothing", 4500),
    ("P007", "Jeans", "Clothing", 3500),
    ("P008", "Kids Jacket", "Clothing", 3000),
    ("P009", "Microwave Oven", "Home Appliances", 28000),
    ("P010", "Air Fryer", "Home Appliances", 15000),
    ("P011", "Washing Machine", "Home Appliances", 65000),
    ("P012", "Electric Kettle", "Home Appliances", 4500),
    ("P013", "Basmati Rice 5kg", "Grocery", 1800),
    ("P014", "Cooking Oil 5L", "Grocery", 2600),
    ("P015", "Tea Pack 950g", "Grocery", 1500),
    ("P016", "Sugar 5kg", "Grocery", 700),
]

CITIES = {
    "Karachi": "South",
    "Hyderabad": "South",
    "Lahore": "Central",
    "Faisalabad": "Central",
    "Islamabad": "North",
    "Peshawar": "North",
}

FIRST = ["Ayesha", "Ali", "Sara", "Usman", "Fatima", "Hassan", "Zainab",
         "Bilal", "Hina", "Omar", "Maryam", "Ahmed", "Noor", "Saad", "Iqra"]
LAST = ["Khan", "Ahmed", "Malik", "Sheikh", "Raza", "Siddiqui", "Hussain",
        "Qureshi", "Baig", "Ansari"]

# 300 customers
customers = []
for i in range(1, 301):
    name = f"{random.choice(FIRST)} {random.choice(LAST)}"
    customers.append((f"C{i:04d}", name))

# Some customers buy more often, so we get VIP and repeat buyers
weights = [random.choice([1, 1, 1, 2, 3, 6]) for _ in customers]

start = date(2024, 1, 1)
days = (date(2025, 12, 31) - start).days

rows = []
for n in range(1, 4001):
    cust_id, cust_name = random.choices(customers, weights=weights)[0]
    pid, pname, cat, price = random.choice(PRODUCTS)
    qty = random.randint(1, 2) if cat in ("Electronics", "Home Appliances") else random.randint(1, 5)
    city = random.choice(list(CITIES))
    rows.append({
        "transaction_id": f"T{n:06d}",
        "order_date": start + timedelta(days=random.randint(0, days)),
        "customer_id": cust_id,
        "customer_name": cust_name,
        "product_id": pid,
        "product_name": pname,
        "category": cat,
        "quantity": qty,
        "unit_price": price,
        "discount_pct": random.choice([0, 0, 5, 10, 15, 20]),
        "city": city,
        "region": CITIES[city],
        "channel": random.choice(["Online", "Store"]),
    })

df = pd.DataFrame(rows)

# ---- Intentional dirty records ----
# 1) Missing customer names (40 rows)
df.loc[df.sample(40, random_state=1).index, "customer_name"] = None

# 2) Inconsistent product names (80 rows)
idx = df.sample(80, random_state=2).index
df.loc[idx, "product_name"] = df.loc[idx, "product_name"].apply(
    lambda s: random.choice([s.lower(), s.upper(), s + " "])
)

# 3) Duplicate transactions (60 rows)
duplicates = df.sample(60, random_state=3)
df = pd.concat([df, duplicates], ignore_index=True)

# Shuffle and save as CSV
df = df.sample(frac=1, random_state=4).reset_index(drop=True)

os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/sales_raw.csv", index=False)

print("Raw file created: data/raw/sales_raw.csv")
print("Rows:", len(df))