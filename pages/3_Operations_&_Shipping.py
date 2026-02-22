import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_functions import execute_query

st.set_page_config(page_title="Operations & Shipping", page_icon="🚚", layout="wide")

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

st.title("Operations & Shipping")
st.markdown("Analyzing logistics efficiency, shipping costs, and regional bottlenecks.")

try:
    # We must calculate Shipping Days dynamically because SQLite date math can be tricky.
    query = """
    SELECT 
        f.`Order ID`, 
        f.`Order Date`, 
        f.`Ship Date`, 
        f.`Ship Mode`, 
        f.`Shipping Cost`, 
        l.Region, 
        l.Market
    FROM fact_orders f
    JOIN dim_locations l ON f.`Location ID` = l.`Location ID`
    """
    df_ops = execute_query(query)
    
    # Calculate Shipping Days
    df_ops['Order Date'] = pd.to_datetime(df_ops['Order Date'])
    df_ops['Ship Date'] = pd.to_datetime(df_ops['Ship Date'])
    df_ops['Shipping Days'] = (df_ops['Ship Date'] - df_ops['Order Date']).dt.days
    
    # Drop negative or absurd days if any exist due to data entry errors
    df_ops = df_ops[(df_ops['Shipping Days'] >= 0) & (df_ops['Shipping Days'] <= 30)]

except Exception as e:
    st.error(f"Error loading operations data: {e}")
    st.stop()


# --- Top Level Metrics ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Avg Shipping Days", f"{df_ops['Shipping Days'].mean():.1f}")
with col2:
    st.metric("Total Shipping Cost", f"${df_ops['Shipping Cost'].sum():,.0f}")
with col3:
    st.metric("Avg Shipping Cost per Order", f"${df_ops['Shipping Cost'].mean():.2f}")


st.markdown("---")

col_ch1, col_ch2 = st.columns(2)
chart_config = dict(plot_bgcolor='white', paper_bgcolor='white', font=dict(color='#2d3748'))

with col_ch1:
    st.subheader("Shipping Performance by Region")
    reg_perf = df_ops.groupby('Region')['Shipping Days'].mean().reset_index().sort_values('Shipping Days')
    fig_reg = px.bar(reg_perf, x='Shipping Days', y='Region', orientation='h', color='Shipping Days',
                     color_continuous_scale='Reds')
    fig_reg.update_layout(**chart_config, coloraxis_showscale=False, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_reg, use_container_width=True)

with col_ch2:
    st.subheader("Volume vs Cost by Ship Mode")
    mode_perf = df_ops.groupby('Ship Mode').agg({'Order ID': 'count', 'Shipping Cost': 'sum'}).reset_index()
    fig_mode = px.scatter(mode_perf, x='Order ID', y='Shipping Cost', size='Shipping Cost', color='Ship Mode',
                           hover_name='Ship Mode', size_max=60)
    fig_mode.update_layout(**chart_config, xaxis_title="Order Volume", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_mode, use_container_width=True)


# --- Business Insights ---
st.markdown("""
<div class="insight-box">
    <h4>Route & Bottleneck Insights</h4>
    <ul>
        <li><strong>SLA Monitoring:</strong> Keep a close eye on the regions at the top of the horizontal bar chart. Extended shipping days impact customer retention (Recency in RFM) and increase the likelihood of chargebacks.</li>
        <li><strong>Logistics Expense:</strong> Analyze the 'Volume vs Cost by Ship Mode' scatter. If High-Cost classes (e.g., Same Day/First Class) aren't yielding proportional lifetime value from those customers, we must renegotiate carrier tariffs or adjust pricing tiers to offset.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
