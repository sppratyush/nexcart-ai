import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from backend.recommender import HybridRecommender

try:
    print("Starting Standalone Recommender Test...")
    data_path = "data/raw/amazon_electronics.csv"
    rec = HybridRecommender(data_path, model_dir="data/models")
    print("Recommender Initialized successfully!")
    
    query = "phones"
    results = rec.recommend(query)
    print(f"\nResults for '{query}':")
    for r in results:
        print(f"\n- {r['name']}")
        if 'similar_items' in r:
            sims = [item['name'] for item in r['similar_items']]
            print(f"  Final Similar: {', '.join(sims)}")
            
            # Debug raw candidates
            item_emb = rec.model.encode([r['name']], convert_to_numpy=True)
            import faiss
            faiss.normalize_L2(item_emb)
            _, sim_indices = rec.faiss_index.search(item_emb, 10)
            print("  Raw Candidates:")
            for s_idx in sim_indices[0]:
                if s_idx != -1:
                    print(f"    * {rec.df.iloc[s_idx][rec.name_col]}")
except Exception as e:
    print(f"CRASH DETECTED: {e}")
    import traceback
    traceback.print_exc()
