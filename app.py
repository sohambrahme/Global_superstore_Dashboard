import streamlit as st
import pandas as pd
import plotly.express as px
from insights import generate_insights

st.set_page_config(page_title="Global Superstore Dashboard", page_icon="🌎", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0c0f14;
        color: #ffffff;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700;
        color: #4CAF50; /* Green for positive metrics */
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        color: #aaaaaa;
        font-weight: 500;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        margin-bottom: 0rem;
        padding-bottom: 0rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #121820;
        border-right: 1px solid #1e2633;
    }
    
    /* Cards for charts */
    .stPlotlyChart {
         background-color: #161e2b;
         border-radius: 12px;
         padding: 10px;
         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Insights Card */
    .insights-card {
        background-color: #1e2633;
        border-left: 5px solid #4ECDC4;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .insights-card p {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #eeeeee;
        margin-bottom: 12px;
    }
    .insights-title {
        color: #4ECDC4;
        font-weight: bold;
        font-size: 1.3rem;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# --- Data Loading ---
@st.cache_data
def load_data():
    df = pd.read_csv('Global-Superstore.csv', encoding='latin1')
    # Preprocess Dates silently and robustly
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
    # Filter out bad dates if any
    df = df.dropna(subset=['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    df['MonthYear'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

try:
    with st.spinner("Loading Data..."):
         df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()


# --- Sidebar Filters ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
st.sidebar.title("Filters")

# Year filter
years = sorted(df['Year'].unique().tolist())
selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)

# Region filter
regions = sorted(df['Region'].unique().tolist())
selected_regions = st.sidebar.multiselect("Select Region(s)", regions, default=regions)

# Segment filter
segments = sorted(df['Segment'].unique().tolist())
selected_segments = st.sidebar.multiselect("Select Segment(s)", segments, default=segments)


# --- Apply Filters ---
filtered_df = df[
    (df['Year'].isin(selected_years if selected_years else years)) &
    (df['Region'].isin(selected_regions if selected_regions else regions)) &
    (df['Segment'].isin(selected_segments if selected_segments else segments))
]


# --- Main Content ---
st.title("GLOBAL SUPERSTORE DASHBOARD")
st.markdown("Analyze sales, profitability, and operational performance across the globe.")
st.markdown("---")

# --- KPIs ---
if filtered_df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
total_orders = filtered_df['Order ID'].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Sales", f"${total_sales:,.0f}")
with col2:
    # Color condition for profit
    p_color = "normal" if total_profit >= 0 else "inverse"
    st.metric("Total Profit", f"${total_profit:,.0f}", delta=f"{profit_margin:.1f}% Margin", delta_color=p_color)
with col3:
    st.metric("Avg Order Value", f"${total_sales/total_orders:,.0f}" if total_orders > 0 else "$0")
with col4:
    st.metric("Total Orders", f"{total_orders:,}")

st.markdown("<br>", unsafe_allow_html=True)

# --- Visualizations ---
chart_theme_config = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#eeeeee')
)

col_ch1, col_ch2 = st.columns(2)

with col_ch1:
    st.subheader("Monthly Sales Trend")
    monthly_sales = filtered_df.groupby('MonthYear')['Sales'].sum().reset_index()
    # Sort chronologically
    monthly_sales['MonthYear'] = pd.to_datetime(monthly_sales['MonthYear'])
    monthly_sales = monthly_sales.sort_values('MonthYear')
    
    fig_sales = px.area(monthly_sales, x='MonthYear', y='Sales', 
                        color_discrete_sequence=['#4ECDC4'], markers=True)
    fig_sales.update_layout(**chart_theme_config, margin=dict(l=20, r=20, t=30, b=20))
    fig_sales.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2e3643')
    fig_sales.update_xaxes(showgrid=False)
    st.plotly_chart(fig_sales, use_container_width=True)

with col_ch2:
    st.subheader("Sales by Category & Segment")
    cat_segment = filtered_df.groupby(['Category', 'Segment'])['Sales'].sum().reset_index()
    fig_cat = px.bar(cat_segment, x='Category', y='Sales', color='Segment', 
                     barmode='group', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_cat.update_layout(**chart_theme_config, margin=dict(l=20, r=20, t=30, b=20))
    fig_cat.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2e3643')
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

col_ch3, col_ch4 = st.columns([3, 2])

with col_ch3:
    st.subheader("Profitability by Region")
    region_profit = filtered_df.groupby('Region')['Profit'].sum().reset_index()
    region_profit = region_profit.sort_values(by='Profit', ascending=True)
    fig_region = px.bar(region_profit, x='Profit', y='Region', orientation='h',
                        color='Profit', color_continuous_scale='RdYlGn', text_auto='.2s')
    fig_region.update_layout(**chart_theme_config, margin=dict(l=20, r=20, t=30, b=20), coloraxis_showscale=False)
    st.plotly_chart(fig_region, use_container_width=True)

with col_ch4:
    st.subheader("Sales Distribution (Market)")
    market_sales = filtered_df.groupby('Market')['Sales'].sum().reset_index()
    fig_pie = px.pie(market_sales, values='Sales', names='Market', hole=0.6,
                     color_discrete_sequence=px.colors.qualitative.Set3)
    fig_pie.update_layout(**chart_theme_config, margin=dict(l=20, r=20, t=30, b=20))
    # Add center text
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)


# --- Automated Business Insights ---
st.markdown("---")
st.subheader("🧠 Automated Business Insights")
st.markdown("Key takeaways based on your current filter selection:")

insights_list = generate_insights(filtered_df)

# Render insights in a premium card format using HTML
insights_html = "<div class='insights-card'>"
for insight in insights_list:
    insights_html += f"<p>{insight}</p>"
insights_html += "</div>"
st.markdown(insights_html, unsafe_allow_html=True)


# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Dashboard created for Global Superstore Analytics. Data is purely for illustrative purposes.<br>
        <i>Powered by Streamlit & Plotly</i>
    </div>
    """, 
    unsafe_allow_html=True
)
