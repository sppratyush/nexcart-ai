import traceback
import json
from backend.recommender import get_recommender

try:
    rec = get_recommender()
    rec.recommend('budget phone')
    print("Success")
except Exception as e:
    with open('error.json', 'w') as f:
        json.dump({"trace": traceback.format_exc()}, f)
