from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.recommender import get_recommender
import os

app = FastAPI(
    title="SmartShop Product Discovery API",
    description="Enhanced Backend API with Real-time ML Updates",
    version="1.1.0"
)



class RecommendationRequest(BaseModel):
    query: str
    top_k: int = 5
    semantic_weight: float = 0.7
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class SimilarItemResult(BaseModel):
    id: str
    name: str

class RecommendationResult(BaseModel):
    id: str
    name: str
    description: str
    price: float
    amazon_price: float
    flipkart_price: float
    price_available: bool
    price_source: str
    tags: List[str]
    score: float
    rating: float
    is_trending: bool
    is_best_seller: bool
    amazon_url: str
    flipkart_url: str
    similar_items: List[SimilarItemResult]

class RecommendationResponse(BaseModel):
    query: str
    results: List[RecommendationResult]

@app.on_event("startup")
async def startup_event():
    data_path = os.getenv("DATA_PATH", "data/raw/catalog.csv")
    print(f"Initializing Recommender with {data_path}...")
    _ = get_recommender(data_path)
    print("SmartShop Engine Ready.")

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "multi-qa-mpnet-base-dot-v1"}

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        recommender = get_recommender()
        results = recommender.recommend(
            query=request.query, 
            top_k=request.top_k, 
            semantic_weight=request.semantic_weight,
            min_price=request.min_price,
            max_price=request.max_price
        )
        return RecommendationResponse(query=request.query, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def stats():
    recommender = get_recommender()
    df = recommender.df
    if df is None or df.empty:
         return {"total_products": 0, "avg_price": 0, "price_distribution": {}}
    
    # Calculate stats
    total_products = len(df)
    avg_price = float(df['price'].mean()) if 'price' in df.columns else 0.0
    
    dist = {"Under ₹10k": 0, "₹10k - ₹30k": 0, "₹30k - ₹80k": 0, "Above ₹80k": 0}
    if 'price' in df.columns:
        dist["Under ₹10k"] = int(len(df[df['price'] < 10000]))
        dist["₹10k - ₹30k"] = int(len(df[(df['price'] >= 10000) & (df['price'] < 30000)]))
        dist["₹30k - ₹80k"] = int(len(df[(df['price'] >= 30000) & (df['price'] < 80000)]))
        dist["Above ₹80k"] = int(len(df[df['price'] >= 80000]))

    return {
        "total_products": total_products,
        "avg_price": avg_price,
        "price_distribution": dist
    }

