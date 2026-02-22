import pandas as pd
import sqlite3
import os

def run_etl():
    print("Starting ETL Process...")
    data_path = 'data/Global-Superstore.csv'
    db_path = 'data/retail_warehouse.db'

    if not os.path.exists(data_path):
        print(f"Error: Could not find {data_path}")
        return

    # 1. Extract
    print(f"Extracting data from {data_path}...")
    df = pd.read_csv(data_path, encoding='latin1')
    
    # Preprocess basic issues
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
    
    # Drop rows without dates
    df = df.dropna(subset=['Order Date'])

    # 2. Transform into Star Schema
    print("Transforming data into Dimensional Schema...")

    # DIM CUSTOMERS
    dim_customers = df[['Customer ID', 'Customer Name', 'Segment']].drop_duplicates().reset_index(drop=True)

    # DIM PRODUCTS
    dim_products = df[['Product ID', 'Product Name', 'Category', 'Sub-Category']].drop_duplicates().reset_index(drop=True)

    # DIM LOCATIONS (We'll use a surrogate key for Location ID to handle granularity)
    dim_locations = df[['City', 'State', 'Country', 'Region', 'Market']].drop_duplicates().reset_index(drop=True)
    dim_locations['Location ID'] = dim_locations.index + 1

    # FACT ORDERS
    # Merge Location ID back into the main dataframe
    fact_orders = df.merge(dim_locations, on=['City', 'State', 'Country', 'Region', 'Market'], how='left')
    
    # Select columns for fact table
    fact_cols = [
        'Row ID', 'Order ID', 'Order Date', 'Ship Date', 'Ship Mode',
        'Customer ID', 'Product ID', 'Location ID', 
        'Sales', 'Quantity', 'Discount', 'Profit', 'Shipping Cost', 'Order Priority'
    ]
    fact_orders = fact_orders[fact_cols]

    # Clean text anomalies in Product ID (Sometimes there are extra spaces)
    dim_products['Product ID'] = dim_products['Product ID'].str.strip()
    fact_orders['Product ID'] = fact_orders['Product ID'].str.strip()

    # 3. Load
    print(f"Loading data into {db_path}...")
    # Remove old DB if exists to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    
    dim_customers.to_sql('dim_customers', conn, index=False, if_exists='replace')
    dim_products.to_sql('dim_products', conn, index=False, if_exists='replace')
    dim_locations.to_sql('dim_locations', conn, index=False, if_exists='replace')
    fact_orders.to_sql('fact_orders', conn, index=False, if_exists='replace')

    print("Creating Indices for performance...")
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_fact_date ON fact_orders('Order Date')")
    cursor.execute("CREATE INDEX idx_fact_cust ON fact_orders('Customer ID')")
    cursor.execute("CREATE INDEX idx_fact_prod ON fact_orders('Product ID')")
    cursor.execute("CREATE INDEX idx_fact_loc ON fact_orders('Location ID')")
    conn.commit()

    # Integrity check
    print("\nDatabase Row Counts:")
    for table in ['dim_customers', 'dim_products', 'dim_locations', 'fact_orders']:
        count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn).iloc[0]['count']
        print(f"{table}: {count} rows")

    conn.close()
    print("\nETL COMPLETE successfully.")

if __name__ == "__main__":
    run_etl()
