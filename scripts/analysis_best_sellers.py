import sqlite3
import pandas as pd

#Connecting the database
conn = sqlite3.connect('ecommerce.db')

#Query: Join order_items with products to compute total sales per product.
query = '''
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

df_best_selling = pd.read_sql_query(query, conn)
print("Top 10 Best-Selling Products:")
print(df_best_selling)

conn.close()