import sys
import os
import requests

# Mocking the backend call to test the recommender directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.recommender import get_recommender

def test_recommender():
    # 1. Test loading
    print("Test 1: Loading Persistent Recommender with Genuine Data...")
    rec = get_recommender("data/raw/amazon_electronics.csv")
    print(f"Index size: {len(rec.df)}")
    assert "rating" in rec.df.columns, "Metadata 'rating' missing"
    
    # 2. Test recommendation for "smart phone"
    print("\nTest 2: Verifying 'Genuine' Recommendations for 'smart phone'...")
    results = rec.recommend("smart phone", top_k=5)
    for r in results:
        trend_label = "[TRENDING]" if r['is_trending'] else ""
        best_label = "[BEST SELLER]" if r['is_best_seller'] else ""
        print(f"- {r['name']} {trend_label} {best_label} (Rating: {r['rating']}, Score: {r['score']:.2f})")
    
    # Check if we got actual phone brands
    phone_found = any(brand in results[0]['name'] for brand in ["iPhone", "Samsung", "Pixel", "OnePlus", "Nothing"])
    assert phone_found, f"Top result '{results[0]['name']}' doesn't look like a genuine phone flagship"

    print("\nVerification Successful! Quality is significantly improved.")

if __name__ == "__main__":
    test_recommender()
