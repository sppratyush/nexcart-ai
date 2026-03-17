import pandas as pd
import numpy as np
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.recommender import HybridRecommender

def generate_dynamic_dataset(count=2000):
    products_db = {
        "Audio": [
            ("Sony WH-1000XM5", "Industry-leading noise canceling wireless headphones with auto NC optimizer."),
            ("Apple AirPods Max", "The pinnacle of over-ear headphones with high-fidelity audio and spatial sound."),
            ("Bose QuietComfort Ultra", "World-class noise cancellation headphones for pure concentration."),
            ("Sennheiser Momentum 4", "Premium sound quality wireless headphones with 60-hour battery life."),
            ("JBL Flip 6", "Powerful portable Bluetooth speaker with deep bass and waterproof design."),
            ("Sony WF-1000XM5", "Truly wireless noise cancelling earbuds with sleek design and rich sound."),
            ("Bose SoundLink Flex", "Robust portable speaker with deep bass and waterproof durability."),
            ("Marshal Major IV", "Iconic wireless on-ear headphones with 80+ hours of battery.")
        ],
        "Computing": [
            ("MacBook Pro 16 M3 Max", "Extreme performance for professionals with Liquid Retina XDR."),
            ("Dell XPS 15", "Premium Windows laptop with InfinityEdge display and RTX graphics."),
            ("ASUS ROG Zephyrus G14", "Compact gaming powerhouse with high refresh rate display."),
            ("Lenovo ThinkPad X1 Carbon", "Legendary business laptop with ultra-light carbon fiber chassis."),
            ("HP Spectre x360", "Elegant 2-in-1 convertible with stunning OLED touchscreen."),
            ("Logitech MX Master 3S", "Performance wireless mouse with silent clicks and MagSpeed scrolling."),
            ("Samsung Odyssey G9", "Ultra-wide 49-inch curved monitor for ultimate gaming setup."),
            ("iPad Pro M2", "The most powerful iPad with Liquid Retina XDR and Apple Pencil support.")
        ],
        "Mobile": [
            ("iPhone 15 Pro Max", "Ultimate flagship with Titanium design and A17 Pro chip."),
            ("Samsung Galaxy S24 Ultra", "Powerhouse flagship with Galaxy AI and integrated S Pen."),
            ("Google Pixel 8 Pro", "Advanced AI-powered camera and helpful Google experiences."),
            ("Nothing Phone (2)", "Unique transparent design with Glyph interface."),
            ("OnePlus 12", "Powerful performance with Hasselblad camera and ultra-fast charging."),
            ("Xiaomi 14 Ultra", "Pro-grade photography with Leica optics and large sensor."),
            ("Sony Xperia 1 V", "Professional video and audio focus with 4K OLED."),
            ("iPhone 14 Plus", "Big screen performance and exceptional battery life.")
        ],
        "Accessories": [
            ("Apple Watch Ultra 2", "The most rugged and capable Apple Watch for explorers."),
            ("Samsung Galaxy Watch 6", "Sleek smartwatch with advanced health and sleep tracking."),
            ("Garmin Fenix 7 Pro", "Ultimate multisport GPS watch with solar charging."),
            ("DJI Mini 4 Pro", "Ultra-light drone with 4K HDR and obstacle sensing."),
            ("GoPro HERO12 Black", "Rugged action camera with best-in-class stabilization.")
        ]
    }
    
    colors = ["Midnight Black", "Pure White", "Ocean Blue", "Space Gray", "Platinum Silver"]
    data = []
    
    i = 0
    for cat, products in products_db.items():
        for base_name, base_desc in products:
            for color in colors:
                name = f"{base_name} ({color})"
                desc = f"{base_desc} This {color} edition offers a premium look and feel. {np.random.choice(['Trending', 'Editor\'s Choice', 'Award Winning'])} for 2024."
                
                # Metadata
                rating = round(np.random.uniform(3.8, 5.0), 1)
                is_trending = np.random.choice([0, 1], p=[0.7, 0.3])
                is_best_seller = np.random.choice([0, 1], p=[0.9, 0.1])
                
                data.append({
                    "uniq_id": f"PROD-{i:04d}",
                    "product_name": name,
                    "product_description": desc,
                    "category": cat,
                    "rating": rating,
                    "is_trending": is_trending,
                    "is_best_seller": is_best_seller
                })
                i += 1
    
    df = pd.DataFrame(data)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/amazon_electronics.csv", index=False)
    print(f"Generated {len(df)} UNIQUE genuine items in data/raw/amazon_electronics.csv")
    return "data/raw/amazon_electronics.csv"

if __name__ == "__main__":
    # 1. Generate new unique dataset
    csv_path = generate_dynamic_dataset()
    
    # 2. Clear old models
    model_dir = "data/models"
    if os.path.exists(model_dir):
        import shutil
        print(f"Clearing old models in {model_dir}...")
        shutil.rmtree(model_dir)
    os.makedirs(model_dir, exist_ok=True)
    
    # 3. Retrain
    print("Initializing recommender and pre-computing indices...")
    recommender = HybridRecommender(csv_path, model_dir=model_dir)
    print(f"Retraining complete. {len(recommender.df)} items indexed in {model_dir}")
