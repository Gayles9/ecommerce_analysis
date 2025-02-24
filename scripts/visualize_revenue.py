import sqlite3
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 

# connect to the database
conn = sqlite3.connect('ecommerce.db')


# query monthly revenue 
query = '''
SELECT 
    strftime('%Y-%m', o.order_purchase_timestamp) AS month, 
    SUM(oi.price) AS monthly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;
'''

df_revenue =  pd.read_sql_query(query, conn)
conn.close()

# create a line plot for mothly revenue
plt.figure(figsize=(12,6))
sns.lineplot(data=df_revenue, x='month', y='monthly_revenue', marker ='o')
plt.xticks(rotation=45) 
plt.title('Monthly Revenue Trend')
plt.xlabel('Month')
plt.ylabel('Revenue')
plt.tight_layout()
plt.show()
