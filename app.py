import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_functions import get_kpis, execute_query

st.set_page_config(page_title="Executive Overview | Retail Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# --- Custom Premium CSS ---
st.markdown("""
<style>
    /* Corporate color palette & Clean Layout */
    .stApp {
        background-color: #f7f9fc;
        color: #1a202c;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    h1, h2, h3 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    h1 {
        border-bottom: 2px solid #2b6cb0;
        padding-bottom: 10px;
        margin-bottom: 25px;
        color: #2b6cb0 !important;
    }

    /* KPI Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800;
        color: #2b6cb0; 
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #4a5568 !important;
        font-weight: 600;
    }

    /* Chart Containers */
    .stPlotlyChart {
         background-color: #ffffff;
         border-radius: 8px;
         padding: 15px;
         box-shadow: 0 1px 3px rgba(0,0,0,0.1);
         border: 1px solid #e2e8f0;
    }
    
    /* Insights section styling */
    .business-insight {
        background-color: #ebf8fa;
        border-left: 4px solid #319795;
        padding: 15px;
        border-radius: 4px;
        margin-top: 20px;
        color: #2d3748;
    }
    .business-insight h4 {
        margin-top: 0;
        color: #319795 !important;
    }
    .business-insight ul {
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("Executive Overview")
st.markdown("Commercial Retail Intelligence System - High-level business performance metrics.")

# --- Data Loading ---
try:
    kpis = get_kpis()
    # Monthly sales for trend
    monthly_sales_query = """
    SELECT strftime('%Y-%m', `Order Date`) as Month, SUM(Sales) as Total_Sales
    FROM fact_orders
    GROUP BY Month
    ORDER BY Month
    """
    df_monthly = execute_query(monthly_sales_query)
    
    # Profit by Region
    region_profit_query = """
    SELECT l.Region, SUM(f.Profit) as Total_Profit
    FROM fact_orders f
    JOIN dim_locations l ON f.`Location ID` = l.`Location ID`
    GROUP BY l.Region
    ORDER BY Total_Profit DESC
    """
    df_region = execute_query(region_profit_query)
    
    # Top/Bottom Products
    products_query = """
    SELECT p.`Product Name`, SUM(f.Profit) as Total_Profit
    FROM fact_orders f
    JOIN dim_products p ON f.`Product ID` = p.`Product ID`
    GROUP BY p.`Product Name`
    ORDER BY Total_Profit DESC
    """
    df_products = execute_query(products_query)
        
except Exception as e:
    st.error(f"Database Error: Ensure ETL has been run. Details: {e}")
    st.stop()


# --- KPI Section ---
if not kpis.empty:
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    
    with col1:
        st.metric("Total Sales", f"${kpis['total_sales'].iloc[0]:,.0f}")
    with col2:
        st.metric("Total Profit", f"${kpis['total_profit'].iloc[0]:,.0f}")
    with col3:
        st.metric("Profit Margin", f"{kpis['profit_margin'].iloc[0]:.1f}%")
        
    with col4:
        st.metric("Total Orders", f"{kpis['total_orders'].iloc[0]:,}")
    with col5:
        st.metric("Total Customers", f"{kpis['total_customers'].iloc[0]:,}")
    with col6:
        st.metric("Avg Order Value", f"${kpis['avg_order_value'].iloc[0]:,.2f}")

st.markdown("<hr/>", unsafe_allow_html=True)

# --- Charts Section ---
col_ch1, col_ch2 = st.columns([2, 1])

# Chart config for clean white background
chart_config = dict(plot_bgcolor='white', paper_bgcolor='white', font=dict(color='#2d3748'))

with col_ch1:
    st.subheader("Monthly Sales Trend")
    fig_trend = px.area(df_monthly, x='Month', y='Total_Sales', color_discrete_sequence=['#2b6cb0'])
    fig_trend.update_layout(**chart_config, margin=dict(l=20, r=20, t=30, b=20))
    fig_trend.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
    fig_trend.update_xaxes(showgrid=False)
    st.plotly_chart(fig_trend, use_container_width=True)

with col_ch2:
    st.subheader("Profit by Region")
    fig_region = px.bar(df_region, x='Total_Profit', y='Region', orientation='h',
                        color='Total_Profit', color_continuous_scale='Blues')
    fig_region.update_layout(**chart_config, coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_region, use_container_width=True)


col_table1, col_table2 = st.columns(2)

base_table_style = [{"selector": "th", "props": [("background-color", "#2b6cb0"), ("color", "white")]}]

with col_table1:
    st.subheader("Top 5 Products (Profit)")
    top_5 = df_products.head(5).copy()
    top_5['Total_Profit'] = top_5['Total_Profit'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(top_5, use_container_width=True, hide_index=True)

with col_table2:
    st.subheader("Bottom 5 Products (Profit)")
    bottom_5 = df_products.tail(5).sort_values(by='Total_Profit').copy()
    bottom_5['Total_Profit'] = bottom_5['Total_Profit'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(bottom_5, use_container_width=True, hide_index=True)


# --- Business Insights ---
st.markdown("""
<div class="business-insight">
    <h4>Commercial Insights & Next Steps</h4>
    <ul>
        <li><strong>Profit Margin Focus:</strong> While Total Sales represent significant volume, the overall profit margin operates tightly around 11.6%. A commercial strategy adjusting margin on high-volume, low-profit items is recommended.</li>
        <li><strong>Regional Disparities:</strong> Significant profit variance exists across regions. Investigating supply chain costs in the lowest-performing regions could unlock immediate bottom-line improvement.</li>
        <li><strong>Product Rationalisation:</strong> The bottom 5 products consistently drain profitability. A stakeholder review to assess delisting or supplier renegotiation for these specific SKUs is required.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
