import sqlite3
import pandas as pd
import streamlit as st
import os

DB_PATH = 'data/retail_warehouse.db'

@st.cache_data(ttl=3600)
def execute_query(query: str, params=()) -> pd.DataFrame:
    """Executes a SQL query against the SQLite database and returns a DataFrame.
    Uses st.cache_data to ensure high performance on repeated queries.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Please run the ETL script first.")
        
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
    return df

@st.cache_data(ttl=3600)
def get_kpis():
    """Fetches high-level KPIs for the Executive Overview"""
    query = """
    SELECT 
        SUM(Sales) as total_sales,
        SUM(Profit) as total_profit,
        (SUM(Profit) / SUM(Sales)) * 100 as profit_margin,
        COUNT(DISTINCT `Order ID`) as total_orders,
        COUNT(DISTINCT `Customer ID`) as total_customers,
        SUM(Sales) / COUNT(DISTINCT `Order ID`) as avg_order_value
    FROM fact_orders
    """
    return execute_query(query)
