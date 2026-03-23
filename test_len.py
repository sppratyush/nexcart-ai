import pickle
import pandas as pd
df = pickle.load(open('p:/product/product/data/models/processed_data.pkl', 'rb'))
with open('len.txt', 'w') as f:
    f.write(f"Rows: {len(df)}\n")
    f.write(f"Columns: {list(df.columns)}\n")
