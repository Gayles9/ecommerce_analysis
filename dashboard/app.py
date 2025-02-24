import streamlit as st 
import pandas as pd 
import sqlite3
import altair as alt 

# Function to load data from the database
@st.cache_data
def load_data(query):
    conn = sqlite3.connect('ecommerce.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("E-commerce Sales Analysis Dashboard")

# Monthly Revenue Chart
revenue_query = '''
SELECT 
    strftime('%Y-%m', o.order_purchase_timestamp) AS month, 
    SUM(oi.price) AS monthly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;
'''
df_revenue = load_data(revenue_query)

st.subheader("Monthly Revenue Trend")
chart = alt.Chart(df_revenue).mark_line(point=True).encode(
    x='month:T',
    y='monthly_revenue:Q'
).properties(width=700, height=400)
st.altair_chart(chart, use_container_width=True)

# Best-Selling Products Chart
best_sellers_query = '''
SELECT 
    oi.product_id, 
    p.product_category_name, 
    SUM(oi.price) AS total_sales,
    COUNT(oi.order_id) AS orders_count
FROM order_items AS oi
JOIN products AS p ON oi.product_id = p.product_id
GROUP BY oi.product_id
ORDER BY total_sales DESC
LIMIT 10;
'''
df_best = load_data(best_sellers_query)
st.subheader("Top 10 Best-Selling Products")
st.dataframe(df_best)
