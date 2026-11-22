import os

import pandas as pd

RAW_PATH = "data/raw/sales_raw.csv"
CLEAN_PATH = "data/clean/sales_clean.csv"

REQUIRED_COLUMNS = [
    "transaction_id", "order_date", "customer_id", "customer_name",
    "product_id", "product_name", "category", "quantity", "unit_price",
    "discount_pct", "city", "region", "channel",
]

# ---------- 1. Load ----------
df = pd.read_csv(RAW_PATH)
print("Rows loaded:", len(df))

# ---------- 2. Validate columns ----------
missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")
print("All 13 required columns found.")

# ---------- 3. Remove duplicate transactions ----------
before = len(df)
df = df.drop_duplicates(subset="transaction_id", keep="first")
print("Duplicates removed:", before - len(df))

# ---------- 4. Fix data types ----------
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
for col in ["quantity", "unit_price", "discount_pct"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------- 5. Drop invalid rows ----------
before = len(df)
df = df.dropna(subset=["transaction_id", "order_date", "customer_id",
                       "product_id", "quantity", "unit_price"])
df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]
df = df[df["discount_pct"].between(0, 100)]
print("Invalid rows removed:", before - len(df))

# ---------- 6. Fix product names ----------
# Use the correct name from the product master (product_id -> most common clean name)
df["product_name"] = df["product_name"].str.strip()
correct_names = (
    df.groupby("product_id")["product_name"]
    .agg(lambda s: s[s != s.str.lower()][s != s.str.upper()].mode().iloc[0]
         if len(s[s != s.str.lower()][s != s.str.upper()]) > 0 else s.mode().iloc[0])
)
df["product_name"] = df["product_id"].map(correct_names)

# ---------- 7. Missing customer names ----------
missing_names = df["customer_name"].isna().sum()
df["customer_name"] = df["customer_name"].fillna("Unknown Customer")
print("Missing customer names filled:", missing_names)

# ---------- 8. Calculated column ----------
df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)

# ---------- 9. Save ----------
os.makedirs("data/clean", exist_ok=True)
df.to_csv(CLEAN_PATH, index=False)

print("-" * 40)
print("Clean file created:", CLEAN_PATH)
print("Final rows:", len(df))
print("Total revenue:", round(df["revenue"].sum(), 2))