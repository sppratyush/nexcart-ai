import json
from backend.recommender import get_recommender

rec = get_recommender()

queries = [
    "budget phone",
    "premium phone",
    "gaming keyboard",
    "headphone",
    "earbuds",
    "office laptop",
    "smartwatch"
]

output = []

for q in queries:
    results = rec.recommend(q, top_k=20, semantic_weight=0.7)
    valid_count = sum(1 for r in results if r['score'] >= 0.60)
    output.append(f"\\n=== Query: '{q}' ===")
    output.append(f"Valid results (score >= 0.60): {valid_count}")
    for i, r in enumerate(results[:15]):  # show top 15
        status = "[PASS]" if r['score'] >= 0.60 else "[DROP]"
        output.append(f"{i+1}. {r['name']:<40} | Score: {r['score']:.4f} {status}")

with open("eval_results_final.txt", "w", encoding="utf-8") as f:
    f.write("\\n".join(output))
    
print("Final evaluation complete.")
