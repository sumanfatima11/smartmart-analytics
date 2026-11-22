-- KPI 1: Total Revenue, Orders, Units, AOV, Active Customers
SELECT
    ROUND(SUM(revenue), 2)                                  AS total_revenue,
    COUNT(DISTINCT transaction_id)                          AS total_orders,
    SUM(quantity)                                           AS units_sold,
    ROUND(SUM(revenue) / COUNT(DISTINCT transaction_id), 2) AS avg_order_value,
    COUNT(DISTINCT customer_id)                             AS active_customers
FROM fact_sales;

-- KPI 2: Monthly revenue
SELECT d.year_month, ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_date d ON f.order_date = d.date_id
GROUP BY d.year_month
ORDER BY d.year_month;

-- KPI 3: Top 5 products by revenue
SELECT p.product_name, ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 5;

-- KPI 4: Revenue by region
SELECT region, ROUND(SUM(revenue), 2) AS revenue
FROM fact_sales
GROUP BY region
ORDER BY revenue DESC;

-- KPI 5: Repeat customer rate
SELECT
    ROUND(100.0 * SUM(CASE WHEN orders >= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_rate_pct
FROM (
    SELECT customer_id, COUNT(*) AS orders
    FROM fact_sales
    GROUP BY customer_id
);