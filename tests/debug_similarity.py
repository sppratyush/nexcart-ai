import sys
import os
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.recommender import get_recommender

def debug_similarity():
    rec = get_recommender("data/raw/amazon_electronics.csv")
    query = "Nothing Phone"
    results = rec.recommend(query, top_k=3)
    
    print(f"Results for query: '{query}'")
    for r in results:
        print(f"\nProduct: {r['name']}")
        base_name = r['name'].split(' (')[0].lower()
        print(f"Base Name: '{base_name}'")
        if 'similar_items' in r:
            for s in r['similar_items']:
                s_base = s['name'].split(' (')[0].lower()
                print(f"  - Similar: {s['name']} (Base: {s_base})")
                if s_base == base_name:
                    print("    !!! ERROR: Same base name found in similar items !!!")

if __name__ == "__main__":
    debug_similarity()
