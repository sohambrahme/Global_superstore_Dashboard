import pandas as pd
df = pd.read_csv('Global-Superstore.csv', encoding='latin1')
print("Total rows:", len(df))
print("Order Date format examples:", df['Order Date'].head(5).tolist())

df_dt = pd.to_datetime(df['Order Date'], format='%d-%m-%Y', errors='coerce')
print("After parsing with %d-%m-%Y, valid rows:", df_dt.notna().sum())

df_dt2 = pd.to_datetime(df['Order Date'], errors='coerce')
print("After parsing with default inferred, valid rows:", df_dt2.notna().sum())
