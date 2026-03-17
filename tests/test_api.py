import requests
import json

try:
    resp = requests.post("http://localhost:8000/recommend", json={"query": "phones", "top_k": 5})
    if resp.status_code == 200:
        results = resp.json()["results"]
        print(f"Server returned {len(results)} results.")
        for r in results:
            print(f"- {r['name']} (Rating: {r['rating']}, Trending: {r['is_trending']})")
            if 'similar_items' in r:
                sim_names = [s['name'] for s in r['similar_items']]
                print(f"  Similar: {', '.join(sim_names)}")
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"Connection failed: {e}")
