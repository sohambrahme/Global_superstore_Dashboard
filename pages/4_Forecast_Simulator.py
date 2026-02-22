import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.forecasting import generate_forecast
from utils.db_functions import execute_query

st.set_page_config(page_title="Forecast & Scenario Simulator", page_icon="🔮", layout="wide")

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

st.title("Forecast & What-if Scenario Simulator")
st.markdown("Time-series projection and discount impact simulation module.")

# --- Forecasting ---
st.subheader("1. Monthly Sales Forecast (Next 3 Months)")
st.caption("Forecast generated using Facebook Prophet with yearly seasonality components.")

try:
    with st.spinner("Generating Forecast..."):
        df_hist, df_forecast, mape = generate_forecast(periods=3)
        
    if df_forecast is not None:
        col_metric, col_chart = st.columns([1, 3])
        
        with col_metric:
            st.metric("Model Backtest Error (MAPE)", f"{mape:.1f}%", help="Mean Absolute Percentage Error on the last 3 months holdout set.")
            future_only = df_forecast.iloc[-3:]
            projected_total = future_only['yhat'].sum()
            st.metric("Projected 3-Mo Revenue", f"${projected_total:,.0f}")
            
        with col_chart:
            # Prepare data for plotting
            hist_plot = df_hist[['ds', 'y']].copy()
            hist_plot['Type'] = 'Actuals'
            hist_plot.rename(columns={'y': 'Sales'}, inplace=True)
            
            future_plot = df_forecast[['ds', 'yhat']].iloc[-3:].copy()
            future_plot['Type'] = 'Forecast'
            future_plot.rename(columns={'yhat': 'Sales'}, inplace=True)
            
            plot_df = pd.concat([hist_plot, future_plot])
            
            fig_fcst = px.line(plot_df, x='ds', y='Sales', color='Type', 
                               color_discrete_map={'Actuals': '#2b6cb0', 'Forecast': '#ed8936'},
                               markers=True)
            
            # Add confidence intervals
            fig_fcst.add_trace(go.Scatter(
                name='Upper Bound',
                x=df_forecast['ds'].iloc[-3:],
                y=df_forecast['yhat_upper'].iloc[-3:],
                mode='lines',
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False
            ))
            fig_fcst.add_trace(go.Scatter(
                name='Lower Bound',
                x=df_forecast['ds'].iloc[-3:],
                y=df_forecast['yhat_lower'].iloc[-3:],
                marker=dict(color="#444"),
                line=dict(width=0),
                mode='lines',
                fillcolor='rgba(237, 137, 54, 0.2)',
                fill='tonexty',
                showlegend=False
            ))
            
            fig_fcst.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_fcst, use_container_width=True)
            
except Exception as e:
    st.error(f"Error during forecasting: {e}")


st.markdown("---")

# --- What-IF Simulator ---
st.subheader("2. Margin Impact Scenario Simulator")
st.markdown("Adjust the global discount rate to simulate the potential impact on Total Profit.")

# Fetch base metrics for simulation
try:
    base_query = "SELECT SUM(Sales) as Base_Sales, SUM(Profit) as Base_Profit, AVG(Discount) as Base_Discount FROM fact_orders"
    df_base = execute_query(base_query)
    curr_sales = df_base['Base_Sales'].iloc[0]
    curr_profit = df_base['Base_Profit'].iloc[0]
    curr_disc = df_base['Base_Discount'].iloc[0]
except Exception as e:
    st.error('Error fetching base scenario.')
    st.stop()

# Scenario Inputs
sim_discount = st.slider("Simulated Average Discount %", min_value=0.0, max_value=80.0, value=float(curr_disc*100), step=1.0)

# Simple simulation math (Assumes inelastic demand for simplicity - in reality, volume would shift)
sim_disc_ratio = (sim_discount / 100)
# Re-gross the sales
gross_sales_estimate = curr_sales / (1 - curr_disc)
# Calculate new metrics
sim_sales = gross_sales_estimate * (1 - sim_disc_ratio)
# Assume profit changes $1 for $1 with discount changes (simplistic approach for demo)
profit_difference = sim_sales - curr_sales
sim_profit = curr_profit + profit_difference
sim_margin = (sim_profit / sim_sales) * 100

col_sim1, col_sim2, col_sim3 = st.columns(3)

with col_sim1:
    st.metric("Simulated Revenue", f"${sim_sales:,.0f}", delta=f"${sim_sales - curr_sales:,.0f} vs Baseline")
with col_sim2:
    st.metric("Simulated Profit", f"${sim_profit:,.0f}", delta=f"${sim_profit - curr_profit:,.0f} vs Baseline")
with col_sim3:
    st.metric("Simulated Profit Margin", f"{sim_margin:.1f}%", delta=f"{sim_margin - (curr_profit/curr_sales)*100:.1f}%")

st.caption("ℹ️ *Disclaimer: This simplistic scenario assumes perfectly inelastic demand. In reality, reducing discounts may reduce `Volume` (total orders), altering the gross sales estimate.*")


# --- Business Insights ---
st.markdown("""
<div class="insight-box">
    <h4>Strategic Simulation Insight</h4>
    <ul>
        <li><strong>Forecasting Utility:</strong> The time-series model provides a baseline expectation to align inventory planning and staffing, especially in peak sales seasons towards year-end.</li>
        <li><strong>Discount Sensitivity:</strong> The simulator highlights the enormous leverage that discounting has on absolute profit. Even a 200 bps (2%) reduction in the average discount policy across the business can flow directly to the bottom line, demonstrating that tight discount governance is often more powerful than pure volume growth.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
