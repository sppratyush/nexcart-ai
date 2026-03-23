import json
from backend.recommender import get_recommender

rec = get_recommender()

queries = [
    "budget phone",
    "gaming keyboard",
    "noise canceling headphone",
    "office laptop",
    "smartwatch"
]

output = []

for q in queries:
    results = rec.recommend(q, top_k=8, semantic_weight=0.7)
    output.append(f"\\n=== Query: '{q}' ===")
    for i, r in enumerate(results):
        status = "[PASS]" if r['score'] > 0.65 else "[DROP]"
        output.append(f"{i+1}. {r['name']:<40} | Score: {r['score']:.4f} {status}")

with open("eval_results.txt", "w", encoding="utf-8") as f:
    f.write("\\n".join(output))
    
print("Evaluation complete. Results written to eval_results.txt")
