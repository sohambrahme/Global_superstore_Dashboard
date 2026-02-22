import pandas as pd

df = pd.read_csv('Global-Superstore.csv', encoding='latin1')
print("SHAPE:", df.shape)
print("\nCOLUMNS:")
for col in df.columns:
    print(f"- {col} (Type: {df[col].dtype})")

print("\nUNIQUE VALUES FOR CATEGORICAL:")
for col in ['Category', 'Sub-Category', 'Segment', 'Region', 'Market']:
    if col in df.columns:
        print(f"{col}: {df[col].unique().tolist()}")

print("\nSAMPLE ROW:")
print(df.head(1).to_json(orient='records', indent=2))
