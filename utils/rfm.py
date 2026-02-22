import pandas as pd
import streamlit as st
from utils.db_functions import execute_query

@st.cache_data(ttl=3600)
def calculate_rfm():
    """Calculates Recency, Frequency, and Monetary value for each customer."""
    # First, we need the max date in the dataset to act as "today" for recency
    max_date_query = "SELECT MAX(`Order Date`) as max_date FROM fact_orders"
    df_max = execute_query(max_date_query)
    current_date = pd.to_datetime(df_max['max_date'].iloc[0])

    # Get raw customer data
    query = """
    SELECT 
        c.`Customer ID`,
        c.`Customer Name`,
        MAX(f.`Order Date`) as last_order_date,
        COUNT(DISTINCT f.`Order ID`) as frequency,
        SUM(f.Sales) as monetary
    FROM fact_orders f
    JOIN dim_customers c ON f.`Customer ID` = c.`Customer ID`
    GROUP BY c.`Customer ID`, c.`Customer Name`
    """
    df_rfm = execute_query(query)
    
    # Calculate Recency in days
    df_rfm['last_order_date'] = pd.to_datetime(df_rfm['last_order_date'])
    df_rfm['recency'] = (current_date - df_rfm['last_order_date']).dt.days

    # Segmentation Logic
    # We will use simple quantiles (1 to 4) where 4 is best.
    # Recency: Lower is better (so reverse quantile)
    # Frequency & Monetary: Higher is better
    
    r_labels = range(4, 0, -1)
    f_labels = range(1, 5)
    m_labels = range(1, 5)

    try:
        df_rfm['R'] = pd.qcut(df_rfm['recency'], q=4, labels=r_labels)
    except ValueError: # handle non-unique bin edges
        df_rfm['R'] = pd.qcut(df_rfm['recency'].rank(method='first'), q=4, labels=r_labels)
        
    try:
        df_rfm['F'] = pd.qcut(df_rfm['frequency'], q=4, labels=f_labels)
    except ValueError:
        df_rfm['F'] = pd.qcut(df_rfm['frequency'].rank(method='first'), q=4, labels=f_labels)
        
    try:
        df_rfm['M'] = pd.qcut(df_rfm['monetary'], q=4, labels=m_labels)
    except ValueError:
        df_rfm['M'] = pd.qcut(df_rfm['monetary'].rank(method='first'), q=4, labels=m_labels)

    # Combine RFM scores
    df_rfm['RFM_Score'] = df_rfm['R'].astype(str) + df_rfm['F'].astype(str) + df_rfm['M'].astype(str)

    # Segment Mapping Function
    def map_segment(row):
        r, f = int(row['R']), int(row['F'])
        if r >= 4 and f >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Hibernating'
        else:
            return 'Potential/Other'

    df_rfm['Segment'] = df_rfm.apply(map_segment, axis=1)
    
    return df_rfm
