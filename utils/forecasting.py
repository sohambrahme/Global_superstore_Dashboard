import pandas as pd
import streamlit as st
from prophet import Prophet
from utils.db_functions import execute_query

@st.cache_data(ttl=3600)
def generate_forecast(periods=3):
    """
    Generates a monthly sales forecast using Prophet for the next `periods` months.
    Returns the historical data, forecast data, and MAPE (Backtest).
    """
    # 1. Fetch Monthly Sales Data
    query = """
    SELECT strftime('%Y-%m-01', `Order Date`) as ds, SUM(Sales) as y
    FROM fact_orders
    GROUP BY ds
    ORDER BY ds
    """
    df = execute_query(query)
    df['ds'] = pd.to_datetime(df['ds'])
    
    # Needs at least 12 months for a meaningful forecast
    if len(df) < 12:
        return df, None, 0
    
    # 2. Backtest (MAPE) configuration
    # Train on all but the last 3 months to calculate MAPE
    train = df.iloc[:-3]
    test = df.iloc[-3:]
    
    m_backtest = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    # Suppress cmdstanpy logging if possible
    import logging
    logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
    
    m_backtest.fit(train)
    future_test = m_backtest.make_future_dataframe(periods=3, freq='M')
    forecast_test = m_backtest.predict(future_test)
    
    # Calculate MAPE
    predictions = forecast_test.iloc[-3:]['yhat'].values
    actuals = test['y'].values
    mape = (abs((actuals - predictions) / actuals).mean()) * 100
    
    # 3. Final Forecast on full dataset
    m_final = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m_final.fit(df)
    future_final = m_final.make_future_dataframe(periods=periods, freq='M')
    forecast_final = m_final.predict(future_final)
    
    return df, forecast_final, mape
