import os
import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

DB_PATH = "data/smartmart.db"
CLEAN_PATH = "data/clean/sales_clean.csv"
RAW_PATH = "data/raw/sales_raw.csv"

st.set_page_config(page_title="SmartMart Analytics", page_icon="🛒", layout="wide")

PALETTE = ["#7C6CF0", "#2DD4BF", "#F472B6", "#FBBF24", "#38BDF8", "#FB923C"]

custom = go.layout.Template(pio.templates["plotly_dark"])
custom.layout.update(
    colorway=PALETTE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Segoe UI, sans-serif", size=13),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)
custom.layout.xaxis.update(gridcolor="rgba(255,255,255,0.07)")
custom.layout.yaxis.update(gridcolor="rgba(255,255,255,0.07)")
pio.templates["smartmart"] = custom
pio.templates.default = "smartmart"

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(160deg, #0F0C29 0%, #1B1840 45%, #0F2A3F 100%);
    }
    .hero {
        background: linear-gradient(90deg, #7C6CF0 0%, #F472B6 55%, #FB923C 100%);
        padding: 22px 28px;
        border-radius: 16px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(124, 108, 240, 0.35);
    }
    .hero h1 { color: white; margin: 0; font-size: 2rem; }
    .hero p { color: rgba(255,255,255,0.9); margin: 4px 0 0 0; }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-left: 5px solid #7C6CF0;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    div[data-testid="stMetricLabel"] { opacity: 0.8; }
    div[data-testid="stMetricValue"] { font-weight: 700; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B1840 0%, #12263A 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    button[data-baseweb="tab"] { font-size: 1rem; font-weight: 600; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #F472B6; }
    h2, h3 { color: #E9E7FF; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Load data ----------
@st.cache_data
def load_data():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT f.*, p.product_name, p.category, c.customer_name
            FROM fact_sales f
            JOIN dim_product p ON f.product_id = p.product_id
            JOIN dim_customer c ON f.customer_id = c.customer_id
        """
        data = pd.read_sql_query(query, conn, parse_dates=["order_date"])
        conn.close()
    elif os.path.exists(CLEAN_PATH):
        data = pd.read_csv(CLEAN_PATH, parse_dates=["order_date"])
    else:
        return None
    data["year_month"] = data["order_date"].dt.to_period("M").astype(str)
    data["weekday"] = data["order_date"].dt.day_name()
    return data


@st.cache_data
def load_quality():
    if not (os.path.exists(RAW_PATH) and os.path.exists(CLEAN_PATH)):
        return None
    raw = pd.read_csv(RAW_PATH)
    clean = pd.read_csv(CLEAN_PATH)
    return {
        "Raw rows": len(raw),
        "Duplicate rows removed": int(raw.duplicated(subset="transaction_id").sum()),
        "Missing customer names": int(raw["customer_name"].isna().sum()),
        "Messy product names": int(raw["product_name"].nunique() - clean["product_name"].nunique()),
        "Clean rows": len(clean),
    }


df = load_data()
if df is None:
    st.error("Data not found. Run the data scripts first (generate, clean, build_db).")
    st.stop()

st.markdown(
    """
    <div class="hero">
        <h1>🛒 SmartMart Retail Analytics</h1>
        <p>Sales, customers, products and regions in one dashboard | Python + SQLite + Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
min_d = df["order_date"].min().date()
max_d = df["order_date"].max().date()

preset = st.sidebar.selectbox(
    "Quick period",
    ["All time", "Last 30 days", "Last 90 days", "Last 12 months", "Year 2024", "Year 2025", "Custom"],
)
if preset == "Custom":
    picked = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
    if len(picked) != 2:
        st.warning("Please select both a start date and an end date.")
        st.stop()
    start, end = pd.to_datetime(picked[0]), pd.to_datetime(picked[1])
else:
    end = pd.to_datetime(max_d)
    start = pd.to_datetime(min_d)
    if preset == "Last 30 days":
        start = end - pd.Timedelta(days=29)
    elif preset == "Last 90 days":
        start = end - pd.Timedelta(days=89)
    elif preset == "Last 12 months":
        start = end - pd.DateOffset(years=1) + pd.Timedelta(days=1)
    elif preset == "Year 2024":
        start, end = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")
    elif preset == "Year 2025":
        start, end = pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")

categories = st.sidebar.multiselect(
    "Category", sorted(df["category"].unique()), default=sorted(df["category"].unique()))
regions = st.sidebar.multiselect(
    "Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
city_options = sorted(df[df["region"].isin(regions)]["city"].unique())
cities = st.sidebar.multiselect("City", city_options, default=city_options)
channels = st.sidebar.multiselect(
    "Channel", sorted(df["channel"].unique()), default=sorted(df["channel"].unique()))
top_n = st.sidebar.slider("Top N products", 3, 16, 10)

base = df[
    df["category"].isin(categories)
    & df["region"].isin(regions)
    & df["city"].isin(cities)
    & df["channel"].isin(channels)
]
fdf = base[(base["order_date"] >= start) & (base["order_date"] <= end)]

st.sidebar.info(f"Period: {start.date()} to {end.date()}\n\nRows selected: {len(fdf):,}")

if fdf.empty:
    st.warning("No data matches the selected filters. Please change the filters.")
    st.stop()

# ---------- Previous period (for KPI change) ----------
span = (end - start) + pd.Timedelta(days=1)
prev = base[(base["order_date"] >= start - span) & (base["order_date"] < start)]


def pct_change(now, before):
    if before == 0:
        return None
    return f"{(now - before) / before * 100:+.1f}%"


revenue = fdf["revenue"].sum()
orders = fdf["transaction_id"].nunique()
units = int(fdf["quantity"].sum())
aov = revenue / orders
customers = fdf["customer_id"].nunique()
orders_per_cust = fdf.groupby("customer_id")["transaction_id"].nunique()
repeat_rate = (orders_per_cust >= 2).mean() * 100

p_rev = prev["revenue"].sum()
p_orders = prev["transaction_id"].nunique()
p_units = int(prev["quantity"].sum())
p_aov = p_rev / p_orders if p_orders else 0
p_cust = prev["customer_id"].nunique()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Revenue", f"{revenue:,.0f}", pct_change(revenue, p_rev))
k2.metric("Total Orders", f"{orders:,}", pct_change(orders, p_orders))
k3.metric("Units Sold", f"{units:,}", pct_change(units, p_units))
k4.metric("Avg Order Value", f"{aov:,.0f}", pct_change(aov, p_aov))
k5.metric("Active Customers", f"{customers:,}", pct_change(customers, p_cust))
k6.metric("Repeat Rate", f"{repeat_rate:.1f}%")
st.caption("Green/red change = compared with the previous period of the same length.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📈 Overview", "📦 Products", "👥 Customers", "🗺️ Regions", "🧹 Data Quality", "⬇️ Export"])

# ---------- Tab 1: Overview ----------
with tab1:
    level = st.radio("View by", ["Daily", "Monthly", "Yearly"], index=1, horizontal=True)
    freq = {"Daily": "D", "Monthly": "MS", "Yearly": "YS"}[level]
    trend = fdf.set_index("order_date")["revenue"].resample(freq).sum().reset_index()
    fig = px.line(trend, x="order_date", y="revenue", markers=(level != "Daily"),
                  labels={"order_date": "Date", "revenue": "Revenue"})
    if level == "Daily" and len(trend) > 7:
        trend["7-day average"] = trend["revenue"].rolling(7).mean()
        fig.add_scatter(x=trend["order_date"], y=trend["7-day average"],
                        mode="lines", name="7-day average")
    st.plotly_chart(fig)

    if level == "Monthly" and len(trend) > 1:
        trend["growth_pct"] = trend["revenue"].pct_change() * 100
        st.write("Monthly growth %")
        st.plotly_chart(px.bar(trend.dropna(), x="order_date", y="growth_pct",
                               labels={"order_date": "Month", "growth_pct": "Growth %"}))

    c1, c2 = st.columns(2)
    with c1:
        st.write("Revenue by category")
        cat = fdf.groupby("category")["revenue"].sum().reset_index()
        st.plotly_chart(px.pie(cat, names="category", values="revenue", hole=0.45))
    with c2:
        st.write("Online vs Store")
        ch = fdf.groupby("channel")["revenue"].sum().reset_index()
        st.plotly_chart(px.pie(ch, names="channel", values="revenue", hole=0.45))

    st.write("Revenue heatmap: weekday vs month")
    heat = fdf.groupby(["weekday", "year_month"])["revenue"].sum().reset_index()
    heat_pivot = heat.pivot(index="weekday", columns="year_month", values="revenue").reindex(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    st.plotly_chart(px.imshow(heat_pivot, aspect="auto", color_continuous_scale="Purp"))

# ---------- Tab 2: Products ----------
with tab2:
    prod = fdf.groupby(["product_name", "category"]).agg(
        revenue=("revenue", "sum"), units=("quantity", "sum"),
        orders=("transaction_id", "nunique")).reset_index()
    prod["revenue_share_%"] = (prod["revenue"] / prod["revenue"].sum() * 100).round(2)
    prod = prod.sort_values("revenue", ascending=False)

    left, right = st.columns(2)
    with left:
        st.write(f"Top {top_n} products by revenue")
        st.plotly_chart(px.bar(prod.head(top_n), x="revenue", y="product_name",
                               color="category", orientation="h")
                        .update_yaxes(autorange="reversed"))
    with right:
        st.write("Bottom 5 products (underperforming)")
        st.plotly_chart(px.bar(prod.tail(5), x="revenue", y="product_name",
                               color="category", orientation="h")
                        .update_yaxes(autorange="reversed"))
    st.write("Full product table")
    st.dataframe(prod, hide_index=True)

# ---------- Tab 3: Customers ----------
with tab3:
    cust = fdf.groupby(["customer_id", "customer_name"]).agg(
        orders=("transaction_id", "nunique"),
        total_spend=("revenue", "sum"),
        last_order=("order_date", "max"),
    ).reset_index()
    cust["days_since_last_order"] = (end - cust["last_order"]).dt.days
    vip_cutoff = cust["total_spend"].quantile(0.80)

    def segment(row):
        if row["total_spend"] >= vip_cutoff:
            return "VIP"
        if row["orders"] >= 2:
            return "Regular"
        return "New"

    cust["segment"] = cust.apply(segment, axis=1)
    cust["at_risk"] = cust["days_since_last_order"] > 90

    a, b, c = st.columns(3)
    a.metric("VIP customers", int((cust["segment"] == "VIP").sum()))
    b.metric("New (1 order)", int((cust["segment"] == "New").sum()))
    c.metric("At risk (no order 90+ days)", int(cust["at_risk"].sum()))

    s1, s2 = st.columns([1, 2])
    with s1:
        seg = cust["segment"].value_counts().reset_index()
        seg.columns = ["segment", "customers"]
        st.plotly_chart(px.pie(seg, names="segment", values="customers", hole=0.45))
    with s2:
        st.write("Top 10 customers by spend")
        st.dataframe(cust.sort_values("total_spend", ascending=False).head(10)
                     .drop(columns=["last_order"]), hide_index=True)

    seg_pick = st.selectbox("Show customers of segment", ["All", "VIP", "Regular", "New"])
    shown = cust if seg_pick == "All" else cust[cust["segment"] == seg_pick]
    st.dataframe(shown.sort_values("total_spend", ascending=False).drop(columns=["last_order"]),
                 hide_index=True)

    first_order = df.groupby("customer_id")["order_date"].min().rename("first_order")
    m = fdf.merge(first_order, on="customer_id")
    m["month"] = m["order_date"].dt.to_period("M").astype(str)
    is_new = m["order_date"].dt.to_period("M") == m["first_order"].dt.to_period("M")
    m["type"] = is_new.map({True: "New", False: "Repeat"})
    nv = m.groupby(["month", "type"])["customer_id"].nunique().reset_index()
    st.write("New vs Repeat customers per month")
    st.plotly_chart(px.bar(nv, x="month", y="customer_id", color="type", barmode="stack",
                           labels={"customer_id": "Customers"}))

# ---------- Tab 4: Regions ----------
with tab4:
    r1, r2 = st.columns(2)
    with r1:
        st.write("Revenue by region")
        reg = fdf.groupby("region")["revenue"].sum().sort_values(ascending=False).reset_index()
        st.plotly_chart(px.bar(reg, x="region", y="revenue", color="region"))
    with r2:
        st.write("Revenue by city")
        cty = fdf.groupby("city")["revenue"].sum().sort_values(ascending=False).reset_index()
        st.plotly_chart(px.bar(cty, x="city", y="revenue", color="city"))
    st.write("City vs category (revenue)")
    cc = fdf.groupby(["city", "category"])["revenue"].sum().reset_index()
    st.plotly_chart(px.bar(cc, x="city", y="revenue", color="category", barmode="stack"))

# ---------- Tab 5: Data quality ----------
with tab5:
    st.write("What the cleaning script fixed (raw file vs clean file)")
    q = load_quality()
    if q is None:
        st.info("Raw or clean CSV file not found in the data folder.")
    else:
        cols = st.columns(len(q))
        for col, (name, value) in zip(cols, q.items()):
            col.metric(name, f"{value:,}")
    st.write("Cloud resource usage (free tier)")
    size_kb = os.path.getsize(CLEAN_PATH) / 1024 if os.path.exists(CLEAN_PATH) else 0
    u1, u2, u3 = st.columns(3)
    u1.metric("Rows in app", f"{len(df):,}")
    u2.metric("Clean CSV size", f"{size_kb:,.0f} KB")
    u3.metric("Memory used by data", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:,.1f} MB")

# ---------- Tab 6: Export ----------
with tab6:
    e1, e2, e3 = st.columns(3)
    e1.download_button("Filtered sales (CSV)", fdf.to_csv(index=False).encode("utf-8"),
                       "smartmart_filtered_sales.csv", "text/csv")
    seg_export = cust.drop(columns=["last_order"])
    e2.download_button("Customer segments (CSV)", seg_export.to_csv(index=False).encode("utf-8"),
                       "smartmart_customer_segments.csv", "text/csv")
    e3.download_button("Product summary (CSV)", prod.to_csv(index=False).encode("utf-8"),
                       "smartmart_product_summary.csv", "text/csv")
    st.dataframe(fdf.head(100), hide_index=True)
    st.caption("Preview of the first 100 filtered rows.")