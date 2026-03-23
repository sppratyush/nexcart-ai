import traceback
from backend.recommender import get_recommender
try:
    rec = get_recommender()
    rec.recommend('budget phone')
    print("Success")
except Exception as e:
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)
