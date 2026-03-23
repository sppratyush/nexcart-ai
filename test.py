import json
from backend.recommender import get_recommender
rec = get_recommender()
results = rec.recommend('budget phone', top_k=10, semantic_weight=0.7)
output = []
for r in results:
    output.append(f"{r['name']} - Score: {r['score']:.4f}")
    
with open('results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
