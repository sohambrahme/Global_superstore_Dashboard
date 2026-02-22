import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_functions import execute_query

st.set_page_config(page_title="Sales & Profitability", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f7f9fc; color: #1a202c; font-family: 'Inter', sans-serif;}
    h1, h2, h3 { color: #2b6cb0 !important; font-weight: 700 !important; }
    h1 { border-bottom: 2px solid #2b6cb0; padding-bottom: 10px; margin-bottom: 25px; }
    .stPlotlyChart { background-color: #ffffff; border-radius: 8px; padding: 15px; border: 1px solid #e2e8f0; }
    .insight-box { background-color: #ebf8fa; border-left: 4px solid #319795; padding: 15px; border-radius: 4px; color: #2d3748; }
    .insight-box h4 { margin-top: 0; color: #319795 !important; }
</style>
""", unsafe_allow_html=True)

st.title("Sales & Profitability Deep Dive")

# --- Fetch Data ---
try:
    scatter_query = """
    SELECT 
        `Order ID`, 
        SUM(Sales) as Total_Sales, 
        SUM(Profit) as Total_Profit, 
        AVG(Discount) as Avg_Discount,
        `Ship Mode`
    FROM fact_orders
    GROUP BY `Order ID`, `Ship Mode`
    HAVING Total_Sales > 0
    """
    df_scatter = execute_query(scatter_query)
    
    cat_query = """
    SELECT 
        p.Category, 
        p.`Sub-Category`, 
        SUM(f.Sales) as Sales, 
        SUM(f.Profit) as Profit,
        (SUM(f.Profit) / SUM(f.Sales)) * 100 as Profit_Margin
    FROM fact_orders f
    JOIN dim_products p ON f.`Product ID` = p.`Product ID`
    GROUP BY p.Category, p.`Sub-Category`
    """
    df_cat = execute_query(cat_query)
    
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()


# --- Charts ---
col1, col2 = st.columns(2)
chart_config = dict(plot_bgcolor='white', paper_bgcolor='white', font=dict(color='#2d3748'))

with col1:
    st.subheader("Sales vs Profit by Order (Discount Impact)")
    # Sample down if too large for browser performance
    if len(df_scatter) > 10000:
        df_scatter = df_scatter.sample(10000)
    
    fig_scatter = px.scatter(df_scatter, x='Total_Sales', y='Total_Profit', 
                             color='Avg_Discount', color_continuous_scale='RdYlGn_r',
                             hover_data=['Order ID', 'Ship Mode'], opacity=0.7)
    fig_scatter.update_layout(**chart_config, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("Category Performance & Margin")
    df_cat_sorted = df_cat.sort_values(by='Sales', ascending=False)
    fig_bar = px.bar(df_cat_sorted, x='Sub-Category', y='Sales', color='Profit_Margin',
                     color_continuous_scale='RdYlGn', text_auto='.2s')
    fig_bar.update_layout(**chart_config, margin=dict(l=20, r=20, t=30, b=20), coloraxis_showscale=True)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

st.subheader("Sub-category Financials")
st.dataframe(df_cat.sort_values(by='Profit', ascending=False).style.format({
    'Sales': '${:,.2f}',
    'Profit': '${:,.2f}',
    'Profit_Margin': '{:.1f}%'
}), use_container_width=True)


# --- Business Insights ---
st.markdown("""
<div class="insight-box">
    <h4>Commercial Recommendations</h4>
    <ul>
        <li><strong>Discount Elasticity:</strong> The scatter plot illustrates that higher discounts (red dots) strongly correlate with negative profit outcomes, even on high-sales-value orders. Discount governance policies must be tightened.</li>
        <li><strong>Category Strengths:</strong> Certain Sub-Categories like Copiers drive exceptional margin. We recommend heavy marketing push into these high-margin items to subsidise loss-leading categories if necessary.</li>
        <li><strong>Margin Degradation:</strong> Tables and Fasteners run at alarmingly low or negative margins. Pricing strategy review for these specific categories is urgently required.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
