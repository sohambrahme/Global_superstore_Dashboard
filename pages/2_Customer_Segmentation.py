import streamlit as st
import pandas as pd
import plotly.express as px
from utils.rfm import calculate_rfm

st.set_page_config(page_title="Customer Segmentation", page_icon="👥", layout="wide")

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

st.title("Customer Segmentation (RFM Analysis)")
st.markdown("Evaluating customer quality based on Recency, Frequency, and Monetary value.")

try:
    with st.spinner("Calculating RFM Scores..."):
        df_rfm = calculate_rfm()
except Exception as e:
    st.error(f"Error calculating RFM: {e}")
    st.stop()

# --- Segment Metrics ---
segment_stats = df_rfm.groupby('Segment').agg({
    'Customer ID': 'count',
    'monetary': 'sum',
    'recency': 'mean',
    'frequency': 'mean'
}).rename(columns={'Customer ID': 'Customers', 'monetary': 'Total Revenue', 'recency': 'Avg Recency', 'frequency': 'Avg Frequency'})
segment_stats['Revenue %'] = (segment_stats['Total Revenue'] / segment_stats['Total Revenue'].sum()) * 100
segment_stats = segment_stats.reset_index()

col1, col2 = st.columns([1, 1])
chart_config = dict(plot_bgcolor='white', paper_bgcolor='white', font=dict(color='#2d3748'))

with col1:
    st.subheader("Customer Base Distribution")
    fig_pie_cust = px.pie(segment_stats, values='Customers', names='Segment', hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie_cust.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie_cust.update_layout(**chart_config, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_pie_cust, use_container_width=True)

with col2:
    st.subheader("Revenue Contribution by Segment")
    fig_pie_rev = px.pie(segment_stats, values='Total Revenue', names='Segment', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set2)
    fig_pie_rev.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie_rev.update_layout(**chart_config, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_pie_rev, use_container_width=True)

st.markdown("---")

st.subheader("Segment Analytics Table")
st.dataframe(segment_stats.style.format({
    'Total Revenue': '${:,.0f}',
    'Avg Recency': '{:.1f} days',
    'Avg Frequency': '{:.1f} orders',
    'Revenue %': '{:.1f}%'
}), use_container_width=True, hide_index=True)


# --- Business Insights ---
st.markdown("""
<div class="insight-box">
    <h4>Commercial Targeting Priorities</h4>
    <ul>
        <li><strong>Protect 'Champions':</strong> The Champions segment likely drives a disproportionate amount of revenue. Dedicated account management and exclusive loyalty rewards should be implemented to retain them.</li>
        <li><strong>Re-activate 'At Risk':</strong> The 'At Risk' segment represents past high-value customers whose recency has dropped. Targeted CRM campaigns with personalized discounts can stimulate re-engagement.</li>
        <li><strong>Cost Management for 'Hibernating':</strong> Limit marketing spend on hibernating customers. Rely on low-cost automated emails rather than expensive targeted acquisition channels for this group.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
