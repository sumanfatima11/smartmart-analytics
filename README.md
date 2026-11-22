# SmartMart Retail Analytics Dashboard

A free-tier analytics project for a retail company (Electronics, Clothing, Home Appliances, Grocery) selling through stores and online. Built with Python, SQLite, Streamlit, GitHub and Streamlit Community Cloud. No paid services are used.

**Live app:** https://smartmart-analytics-kbjt69jp2vqjjvqeyfgaqz.streamlit.app/
**Repository:** https://github.com/sumanfatima11/smartmart-analytics

## 1. Business problems solved

| Problem | Solution in the dashboard |
|---|---|
| Limited sales visibility | Daily, monthly and yearly trend charts, monthly growth % |
| Poor customer insights | VIP / Regular / New segments, New vs Repeat chart, at-risk customers |
| Product performance issues | Top N and bottom 5 products, product table with revenue share |
| Regional performance gaps | Revenue by region and city, city vs category chart |
| Manual reporting | Filters, KPI cards and one-click CSV export |
| Data quality problems | Cleaning script plus a Data Quality tab |
| Infrastructure cost | Only free tools: GitHub, Streamlit Community Cloud, SQLite |

## 2. Data dictionary

The data is synthetic (4,000 transactions plus 60 intentional duplicates), stored as CSV.

| Column | Meaning |
|---|---|
| transaction_id | Unique order line ID |
| order_date | Date of sale (2024-01-01 to 2025-12-31) |
| customer_id, customer_name | Customer |
| product_id, product_name, category | Product |
| quantity, unit_price, discount_pct | Sale values |
| city, region, channel | Location and Online/Store |
| revenue (calculated) | quantity x unit_price x (1 - discount_pct / 100) |

## 3. KPI definitions

| KPI | Definition |
|---|---|
| Total Revenue | SUM(revenue) |
| Total Orders | COUNT(DISTINCT transaction_id) |
| Units Sold | SUM(quantity) |
| Average Order Value | Total Revenue / Total Orders |
| Active Customers | COUNT(DISTINCT customer_id) |
| Repeat Rate | Customers with 2 or more orders / Active Customers x 100 |
| VIP | Total spend in the top 20% |
| Regular | 2 or more orders (not VIP) |
| New | Only 1 order |
| At risk | No order in the last 90 days of the selected period |

## 4. Project structure

```
smartmart-analytics/
├── app.py                  Streamlit dashboard
├── requirements.txt
├── .streamlit/config.toml  Colour theme
├── data/
│   ├── raw/sales_raw.csv       Dirty data (4,060 rows)
│   ├── clean/sales_clean.csv   Clean data (4,000 rows)
│   └── smartmart.db            SQLite database
├── src/
│   ├── generate_data.py    Creates the raw CSV
│   ├── clean_data.py       Validates and cleans the data
│   ├── build_db.py         Builds the 4 tables
│   └── verify_kpis.py      Compares SQL and pandas KPIs
└── sql/kpi_queries.sql     KPI SQL queries
```

## 5. How to run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/generate_data.py
python src/clean_data.py
python src/build_db.py
python src/verify_kpis.py
streamlit run app.py
```

## 6. Data pipeline

1. **Generate:** 4,000 transactions with intentional problems (60 duplicates, 40 missing customer names, 80 messy product names).
2. **Clean:** check 13 required columns, remove duplicate transaction_id, fix data types, drop invalid rows, standardise product names, fill missing names with "Unknown Customer", add `revenue`.
3. **Tables:** `fact_sales`, `dim_customer` (300 rows), `dim_product` (16 rows), `dim_date` (731 rows) in SQLite.
4. **Verify:** SQL results are compared with pandas results.

## 7. Deployment steps

1. Create a GitHub repository (public) named `smartmart-analytics`.
2. In the project folder: `git init`, `git add .`, `git commit`, `git branch -M main`, `git remote add origin <repo-url>`, `git push -u origin main`.
3. Open share.streamlit.io and sign in with GitHub.
4. Click **Create app**, choose the repository, branch `main`, main file `app.py`.
5. Click **Deploy** and wait a few minutes.
6. Open the public URL in an Incognito window to confirm it works without login.

Every `git push` to `main` updates the live app automatically.

## 8. Testing results

| Test | What was checked | Result |
|---|---|---|
| Data validation | 13 required columns found; 60 duplicates removed; 40 missing names filled; 16 unique product names after cleaning | Pass |
| KPI accuracy | SQL and pandas match for revenue, orders, units, AOV, customers, repeat rate and 3 regions (9 of 9) | Pass |
| Cross-check | 2024 revenue 80,176,195 + 2025 revenue 83,533,870 = 163,710,065 (all-time) | Pass |
| Filter behaviour | Quick period, category, region, city and channel update KPIs and charts | Pass |
| Error handling | Empty filter result shows a warning; missing database falls back to the clean CSV; incomplete date range shows a warning | Pass |
| Public URL | App opens in Incognito without login | Pass |

## 9. Free-tier limits and resource usage

| Service | Limit (approximate, may change) |
|---|---|
| Streamlit Community Cloud | Resources per app: up to 2 CPU cores, about 2.7 GB memory (as per Streamlit docs, February 2024) |
| App sleep | Apps with no traffic for 12 hours go to sleep; visiting wakes them |
| GitHub | Free public repository; a single file must stay under 100 MB |
| SQLite | Runs inside the app, no server and no cost |

This project uses very little: 4,000 rows, a clean CSV of a few hundred KB, and a small database. See the **Data Quality** tab in the app for live rows, file size and memory used. Check the official Streamlit documentation for the latest limits.

**Limitations and future work:** the data is synthetic; for larger data move to a free cloud database (for example Supabase or Neon); add automatic daily data refresh with GitHub Actions.
