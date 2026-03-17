from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.recommender import get_recommender
import os

app = FastAPI(
    title="NexCart Product Discovery API",
    description="Enhanced Backend API with Real-time ML Updates",
    version="1.1.0"
)

class ItemAddRequest(BaseModel):
    name: str
    description: str
    id: Optional[str] = None

class RecommendationRequest(BaseModel):
    query: str
    top_k: int = 5
    semantic_weight: float = 0.7

class SimilarItemResult(BaseModel):
    id: str
    name: str

class RecommendationResult(BaseModel):
    id: str
    name: str
    description: str
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
    data_path = os.getenv("DATA_PATH", "data/raw/amazon_electronics.csv")
    print(f"Initializing Recommender with {data_path}...")
    _ = get_recommender(data_path)
    print("NexCart Engine Ready.")

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
            semantic_weight=request.semantic_weight
        )
        return RecommendationResponse(query=request.query, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/items")
def add_item(item: ItemAddRequest):
    try:
        recommender = get_recommender()
        success = recommender.add_product({
            "name": item.name,
            "description": item.description,
            "id": item.id
        })
        return {"status": "success", "message": f"Product '{item.name}' added and indexed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
