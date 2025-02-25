import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

# ------------------------------
# Step 1: Load Data from XLSX
# ------------------------------
data_path = 'data/Online_Retail.xlsx'

# Read the Excel file into a DataFrame
df = pd.read_excel(data_path, engine='openpyxl')
print("Loaded dataset shape:", df.shape)
print("Columns found:", df.columns.tolist())

# ------------------------------
# Step 2: Data Cleaning & Date Conversion
# ------------------------------
# Ensure required columns exist
required_columns = ['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID']
for col in required_columns:
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in the dataset.")

# Convert InvoiceDate to datetime
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')

# Drop rows where CustomerID is missing (necessary for customer-level analysis)
df = df.dropna(subset=['CustomerID'])
df['CustomerID'] = df['CustomerID'].astype(str)  # Ensure CustomerID is a string

# Remove rows with negative or zero Quantity (likely returns or errors)
df = df[df['Quantity'] > 0]

# Create a TotalPrice column (Quantity * UnitPrice)
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

# ------------------------------
# Step 3: Advanced Metrics Computation
# ------------------------------

# 3.1 Revenue Metrics: Calculate Monthly Revenue and Growth Rate
df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')
monthly_revenue = df.groupby('InvoiceMonth')['TotalPrice'].sum().reset_index()
monthly_revenue.columns = ['InvoiceMonth', 'TotalRevenue']
monthly_revenue['InvoiceMonth'] = monthly_revenue['InvoiceMonth'].astype(str)
monthly_revenue['RevenueGrowthRate'] = monthly_revenue['TotalRevenue'].pct_change() * 100

print("\nMonthly Revenue Metrics:")
print(monthly_revenue.head())

# 3.2 Average Order Value (AOV)
order_values = df.groupby('InvoiceNo')['TotalPrice'].sum().reset_index().rename(columns={'TotalPrice': 'OrderValue'})
average_order_value = order_values['OrderValue'].mean()
print("\nAverage Order Value (AOV): ${:.2f}".format(average_order_value))

# 3.3 Customer Segmentation Features
customer_spending = df.groupby('CustomerID')['TotalPrice'].sum().reset_index().rename(columns={'TotalPrice': 'TotalSpent'})
customer_orders = df.groupby('CustomerID')['InvoiceNo'].nunique().reset_index().rename(columns={'InvoiceNo': 'OrderFrequency'})

reference_date = df['InvoiceDate'].max()
customer_last_order = df.groupby('CustomerID')['InvoiceDate'].max().reset_index().rename(columns={'InvoiceDate': 'LastOrderDate'})
customer_last_order['RecencyDays'] = (reference_date - customer_last_order['LastOrderDate']).dt.days

customer_features = pd.merge(customer_spending, customer_orders, on='CustomerID')
customer_features = pd.merge(customer_features, customer_last_order[['CustomerID', 'RecencyDays']], on='CustomerID')

print("\nCustomer Segmentation Features (first 5 rows):")
print(customer_features.head())

# 3.4 Product Performance Metrics: Sales by Product Description
product_performance = df.groupby('Description')['TotalPrice'].sum().reset_index().rename(columns={'TotalPrice': 'TotalSales'})
orders_per_product = df.groupby('Description')['InvoiceNo'].nunique().reset_index().rename(columns={'InvoiceNo': 'OrderCount'})
product_performance = pd.merge(product_performance, orders_per_product, on='Description')

print("\nProduct Performance Metrics (first 5 rows):")
print(product_performance.head())

# ------------------------------
# Step 4: Save Enhanced DataFrames to SQLite Database
# ------------------------------
conn = sqlite3.connect('ecommerce_advanced.db')

monthly_revenue.to_sql('monthly_revenue', conn, if_exists='replace', index=False)
order_values.to_sql('order_values', conn, if_exists='replace', index=False)
customer_features.to_sql('customer_features', conn, if_exists='replace', index=False)
product_performance.to_sql('product_performance', conn, if_exists='replace', index=False)

conn.close()
print("\nEnhanced data saved to 'ecommerce_advanced.db'.")


