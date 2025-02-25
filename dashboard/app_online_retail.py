import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime
from prophet import Prophet

# ------------------------------
# Helper Function: Load Data from SQLite
# ------------------------------
def load_data(query):
    conn = sqlite3.connect('ecommerce_advanced.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ------------------------------
# Load Data from the Database
# ------------------------------
df_revenue = load_data("SELECT * FROM monthly_revenue")
df_customers = load_data("SELECT * FROM customer_features")
df_products = load_data("SELECT * FROM product_performance")
df_top_products = df_products.sort_values(by='TotalSales', ascending=False).head(10)
df_orders = load_data("SELECT * FROM order_values")

# ------------------------------
# Compute Overall Summary Metrics (Static)
# ------------------------------
total_revenue_value = df_orders['OrderValue'].sum()
total_orders_value = df_orders.shape[0]
avg_order_value_value = df_orders['OrderValue'].mean()
unique_customers_value = load_data("SELECT COUNT(DISTINCT CustomerID) as count FROM customer_features").iloc[0]['count']

# ------------------------------
# Create Figures for the Summary Tab
# ------------------------------
fig_order_hist = px.histogram(df_orders, x='OrderValue', nbins=50, title="Distribution of Order Values")
fig_order_hist.update_layout(
    xaxis_title="Order Value ($)", yaxis_title="Count",
    paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
    font=dict(color='white')
)

# ------------------------------
# Process Revenue Data
# ------------------------------
# Convert InvoiceMonth (e.g., "2017-08") to a datetime object (using the first day of the month)
df_revenue['InvoiceMonth_dt'] = pd.to_datetime(df_revenue['InvoiceMonth'] + '-01')
df_revenue = df_revenue.sort_values('InvoiceMonth_dt')

# Create Revenue Trend Figure
fig_revenue = px.line(
    df_revenue, x='InvoiceMonth_dt', y='TotalRevenue', markers=True,
    title="Monthly Revenue Trend"
)
fig_revenue.update_layout(
    xaxis_title="Month", yaxis_title="Total Revenue ($)",
    paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
    font=dict(color='white')
)

# Create Revenue Growth Rate Figure
fig_growth = px.bar(
    df_revenue, x='InvoiceMonth_dt', y='RevenueGrowthRate',
    title="Monthly Revenue Growth Rate (%)"
)
fig_growth.update_layout(
    xaxis_title="Month", yaxis_title="Growth Rate (%)",
    paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
    font=dict(color='white')
)

# ------------------------------
# Create Customer Segmentation Figure
# ------------------------------
fig_customers = px.scatter(
    df_customers, x='OrderFrequency', y='TotalSpent', color='RecencyDays',
    size='TotalSpent', hover_data=['CustomerID'],
    title="Customer Segmentation: Order Frequency vs Total Spent"
)
fig_customers.update_layout(
    xaxis_title="Order Frequency", yaxis_title="Total Spent ($)",
    paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
    font=dict(color='white')
)

# ------------------------------
# Create Products Figure (Top 10 Products)
# ------------------------------
fig_products = px.bar(
    df_top_products, x='Description', y='TotalSales', color='OrderCount',
    title="Top 10 Products by Total Sales"
)
fig_products.update_layout(
    xaxis_title="Product Description", yaxis_title="Total Sales ($)",
    xaxis_tickangle=-45,
    paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
    font=dict(color='white')
)

# ------------------------------
# Forecasting with Prophet (Next 6 Months)
# ------------------------------
df_forecast = df_revenue[['InvoiceMonth_dt', 'TotalRevenue']].rename(
    columns={'InvoiceMonth_dt': 'ds', 'TotalRevenue': 'y'}
)
model = Prophet(seasonality_mode='multiplicative')
model.fit(df_forecast)
future = model.make_future_dataframe(periods=6, freq='M')
forecast = model.predict(future)
fig_forecast = px.line(forecast, x='ds', y='yhat', title="Revenue Forecast for Next 6 Months")
fig_forecast.update_layout(
    xaxis_title="Month", yaxis_title="Forecasted Revenue ($)",
    paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
    font=dict(color='white')
)

# ------------------------------
# Correlation Analysis: Heatmap of Customer Features
# ------------------------------
corr_matrix = df_customers[['TotalSpent', 'OrderFrequency', 'RecencyDays']].corr()
fig_corr = px.imshow(corr_matrix, text_auto=True, title="Correlation Matrix: Customer Features", color_continuous_scale='RdBu_r')
fig_corr.update_layout(
    paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
    font=dict(color='white')
)

# ------------------------------
# Data Dictionary / Methodology Markdown
# ------------------------------
data_dictionary_md = """
### Data Dictionary & Methodology

**Summary Metrics:**
- **Total Revenue:** Sum of all order values.
- **Total Orders:** Number of unique invoices.
- **Average Order Value (AOV):** Average value per order.
- **Unique Customers:** Count of distinct customers.

**Revenue Metrics:**
- **Monthly Revenue:** Total revenue aggregated by month.
- **Revenue Growth Rate:** Percentage change in monthly revenue compared to the previous month.

**Customer Segmentation:**
- **Total Spent:** Total amount spent by a customer.
- **Order Frequency:** Number of orders placed by a customer.
- **Recency Days:** Number of days since the customer's last order.

**Product Performance:**
- **Total Sales:** Total revenue generated by a product.
- **Order Count:** Number of orders that include the product.

**Forecasting:**
- **Revenue Forecast:** Predicted revenue for the next 6 months using the Prophet model.

**Methodology:**
1. Data was cleaned by removing orders with negative or zero quantity and missing CustomerIDs.
2. Advanced metrics were computed and aggregated from the Online Retail dataset.
3. Forecasting was performed using Facebook's Prophet with multiplicative seasonality.
"""

# ------------------------------
# Create the Dash App with DARKLY Theme (Dark Background)
# ------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Online Retail Advanced Analytics Dashboard"

# ------------------------------
# Define the Layout with 7 Tabs
# ------------------------------
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Online Retail Analytics",
        brand_href="#",
        color="dark",
        dark=True,
        style={"fontFamily": "Helvetica, Arial, sans-serif"}
    ),
    dbc.Tabs(
        id="tabs",
        active_tab="tab-summary",
        children=[
            dbc.Tab(label="Summary", tab_id="tab-summary",
                    tab_style={"backgroundColor": "#2C2C2C", "border": "none"},
                    label_style={"color": "white", "fontWeight": "bold"}),
            dbc.Tab(label="Revenue", tab_id="tab-revenue",
                    tab_style={"backgroundColor": "#2C2C2C", "border": "none"},
                    label_style={"color": "white", "fontWeight": "bold"}),
            dbc.Tab(label="Customers", tab_id="tab-customers",
                    tab_style={"backgroundColor": "#2C2C2C", "border": "none"},
                    label_style={"color": "white", "fontWeight": "bold"}),
            dbc.Tab(label="Products", tab_id="tab-products",
                    tab_style={"backgroundColor": "#2C2C2C", "border": "none"},
                    label_style={"color": "white", "fontWeight": "bold"}),
            dbc.Tab(label="Forecasting", tab_id="tab-forecasting",
                    tab_style={"backgroundColor": "#2C2C2C", "border": "none"},
                    label_style={"color": "white", "fontWeight": "bold"}),
            dbc.Tab(label="Correlation", tab_id="tab-correlation",
                    tab_style={"backgroundColor": "#2C2C2C", "border": "none"},
                    label_style={"color": "white", "fontWeight": "bold"}),
            dbc.Tab(label="Data Dictionary", tab_id="tab-dictionary",
                    tab_style={"backgroundColor": "#2C2C2C", "border": "none"},
                    label_style={"color": "white", "fontWeight": "bold"})
        ],
        style={"marginBottom": "20px"}
    ),
    html.Div(id="tab-content", className="p-4", style={"fontFamily": "Helvetica, Arial, sans-serif"})
], fluid=True, style={"backgroundColor": "#000000", "minHeight": "100vh", "color": "white"})

# ------------------------------
# Callback to Render Tab Content Based on Active Tab
# ------------------------------
@app.callback(Output("tab-content", "children"), [Input("tabs", "active_tab")])
def render_tab_content(active_tab):
    if active_tab == "tab-summary":
        summary_cards = dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Total Revenue", className="card-title"),
                        html.H2(f"${total_revenue_value:,.2f}", className="card-text")
                    ]),
                    style={"backgroundColor": "#2C2C2C", "border": "none"}
                ), md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Total Orders", className="card-title"),
                        html.H2(f"{total_orders_value:,}", className="card-text")
                    ]),
                    style={"backgroundColor": "#2C2C2C", "border": "none"}
                ), md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Average Order Value", className="card-title"),
                        html.H2(f"${avg_order_value_value:,.2f}", className="card-text")
                    ]),
                    style={"backgroundColor": "#2C2C2C", "border": "none"}
                ), md=3
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Unique Customers", className="card-title"),
                        html.H2(f"{unique_customers_value:,}", className="card-text")
                    ]),
                    style={"backgroundColor": "#2C2C2C", "border": "none"}
                ), md=3
            )
        ], className="mb-4")
        return html.Div([
            html.H3("Key Summary Metrics", style={"textAlign": "center"}),
            summary_cards,
            dbc.Card(
                dbc.CardBody([
                    html.H3("Order Value Distribution", style={"textAlign": "center"}),
                    dcc.Graph(figure=fig_order_hist)
                ]),
                style={"backgroundColor": "#2C2C2C", "border": "none"}
            )
        ])
    elif active_tab == "tab-revenue":
        return html.Div([
            html.H3("Revenue Analysis", style={"textAlign": "center"}),
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Select Date Range:", style={"textAlign": "center"}),
                            dcc.DatePickerRange(
                                id="revenue-date-picker",
                                min_date_allowed=df_revenue['InvoiceMonth_dt'].min(),
                                max_date_allowed=df_revenue['InvoiceMonth_dt'].max(),
                                start_date=df_revenue['InvoiceMonth_dt'].min(),
                                end_date=df_revenue['InvoiceMonth_dt'].max(),
                                display_format='YYYY-MM'
                            )
                        ]),
                        style={"backgroundColor": "#2C2C2C", "border": "none"}
                    ), md=12
                )
            ], className="mb-4"),
            dbc.Card(
                dbc.CardBody([
                    html.H3("Monthly Revenue Trend", style={"textAlign": "center"}),
                    dcc.Graph(id="graph-revenue", figure=fig_revenue)
                ]),
                className="mb-4",
                style={"backgroundColor": "#2C2C2C", "border": "none"}
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H3("Revenue Growth Rate", style={"textAlign": "center"}),
                    dcc.Graph(id="graph-growth", figure=fig_growth)
                ]),
                style={"backgroundColor": "#2C2C2C", "border": "none"}
            )
        ])
    elif active_tab == "tab-customers":
        return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.H3("Customer Segmentation", style={"textAlign": "center"}),
                    dcc.Graph(figure=fig_customers)
                ]),
                style={"backgroundColor": "#2C2C2C", "border": "none"}
            )
        ])
    elif active_tab == "tab-products":
        return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.H3("Top 10 Products by Total Sales", style={"textAlign": "center"}),
                    dcc.Graph(figure=fig_products)
                ]),
                style={"backgroundColor": "#2C2C2C", "border": "none"}
            )
        ])
    elif active_tab == "tab-forecasting":
        return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.H3("Revenue Forecast", style={"textAlign": "center"}),
                    dcc.Graph(figure=fig_forecast)
                ]),
                style={"backgroundColor": "#2C2C2C", "border": "none"}
            )
        ])
    elif active_tab == "tab-correlation":
        return html.Div([
            dbc.Card(
                dbc.CardBody([
                    html.H3("Correlation Analysis", style={"textAlign": "center"}),
                    dcc.Graph(figure=fig_corr)
                ]),
                style={"backgroundColor": "#2C2C2C", "border": "none"}
            )
        ])
    elif active_tab == "tab-dictionary":
        return html.Div([
            dbc.Card(
                dbc.CardBody([dcc.Markdown(data_dictionary_md)]),
                style={"backgroundColor": "#2C2C2C", "border": "none"}
            )
        ])
    return html.Div("No tab selected", style={"textAlign": "center"})

# ------------------------------
# Callback to Update Revenue Graphs Based on Date Range
# ------------------------------
@app.callback(
    [Output("graph-revenue", "figure"), Output("graph-growth", "figure")],
    [Input("revenue-date-picker", "start_date"), Input("revenue-date-picker", "end_date")]
)
def update_revenue_graphs(start_date, end_date):
    mask = (df_revenue['InvoiceMonth_dt'] >= pd.to_datetime(start_date)) & (df_revenue['InvoiceMonth_dt'] <= pd.to_datetime(end_date))
    filtered = df_revenue.loc[mask]
    fig_rev = px.line(filtered, x='InvoiceMonth_dt', y='TotalRevenue', markers=True, title="Monthly Revenue Trend")
    fig_rev.update_layout(
        xaxis_title="Month", yaxis_title="Total Revenue ($)",
        paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
        font=dict(color='white')
    )
    fig_gro = px.bar(filtered, x='InvoiceMonth_dt', y='RevenueGrowthRate', title="Monthly Revenue Growth Rate (%)")
    fig_gro.update_layout(
        xaxis_title="Month", yaxis_title="Growth Rate (%)",
        paper_bgcolor="#2C2C2C", plot_bgcolor="#2C2C2C",
        font=dict(color='white')
    )
    return fig_rev, fig_gro

# ------------------------------
# Run the App
# ------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)


