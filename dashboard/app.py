import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output

# ------------------------------
# Helper Function to Load Data from SQLite
# ------------------------------
def load_data(query):
    """Connects to the SQLite database, executes the query, and returns a DataFrame."""
    conn = sqlite3.connect('ecommerce_advanced.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ------------------------------
# Load Data from the Database
# ------------------------------
# Monthly Revenue Data
df_revenue = load_data("SELECT * FROM monthly_revenue")
# Customer Segmentation Features
df_customers = load_data("SELECT * FROM customer_features")
# Product Performance Metrics
df_products = load_data("SELECT * FROM product_performance")

# ------------------------------
# Create Plotly Figures for Each Analysis
# ------------------------------

# 1. Revenue Overview: Monthly Revenue Trend (Line Chart)
fig_revenue = px.line(
    df_revenue, 
    x='order_month', 
    y='total_revenue', 
    markers=True, 
    title='Monthly Revenue Trend'
)
fig_revenue.update_layout(xaxis_title='Month', yaxis_title='Total Revenue')

# Revenue Growth Rate (Bar Chart)
fig_growth = px.bar(
    df_revenue, 
    x='order_month', 
    y='revenue_growth_rate', 
    title='Monthly Revenue Growth Rate (%)'
)
fig_growth.update_layout(xaxis_title='Month', yaxis_title='Growth Rate (%)')

# 2. Customer Segmentation: Scatter Plot of Order Frequency vs Total Spent
fig_customers = px.scatter(
    df_customers, 
    x='order_frequency', 
    y='total_spent', 
    color='recency_days',
    size='total_spent', 
    hover_data=['customer_id'],
    title='Customer Segmentation: Order Frequency vs Total Spent'
)
fig_customers.update_layout(xaxis_title='Order Frequency', yaxis_title='Total Spent ($)')

# 3. Product Performance: Bar Chart of Total Sales by Product Category
fig_products = px.bar(
    df_products, 
    x='product_category_name', 
    y='total_sales', 
    color='order_count',
    title='Product Performance by Category'
)
fig_products.update_layout(xaxis_title='Product Category', yaxis_title='Total Sales ($)')

# ------------------------------
# Create the Dash App with Bootstrap for Styling
# ------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "E-commerce Advanced Analytics Dashboard"

# ------------------------------
# Layout: Navigation Bar, Tabs, and Content Container
# ------------------------------
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="E-commerce Advanced Analytics Dashboard",
        brand_href="#",
        color="primary",
        dark=True,
        className="mb-4"
    ),
    dbc.Tabs([
        dbc.Tab(label='Revenue Overview', tab_id='tab-revenue'),
        dbc.Tab(label='Customer Segmentation', tab_id='tab-customers'),
        dbc.Tab(label='Product Performance', tab_id='tab-products')
    ], id='tabs', active_tab='tab-revenue', className="mb-4"),
    html.Div(id='tab-content', className="p-4")
], fluid=True)

# ------------------------------
# Callback to Update Tab Content Based on Active Tab
# ------------------------------
@app.callback(Output('tab-content', 'children'),
              Input('tabs', 'active_tab'))
def render_tab_content(active_tab):
    if active_tab == 'tab-revenue':
        return html.Div([
            html.H3("Monthly Revenue & Growth"),
            dcc.Graph(figure=fig_revenue),
            dcc.Graph(figure=fig_growth)
        ])
    elif active_tab == 'tab-customers':
        return html.Div([
            html.H3("Customer Segmentation"),
            dcc.Graph(figure=fig_customers)
        ])
    elif active_tab == 'tab-products':
        return html.Div([
            html.H3("Product Performance by Category"),
            dcc.Graph(figure=fig_products)
        ])
    return html.Div("No tab selected")

# ------------------------------
# Run the App
# ------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
