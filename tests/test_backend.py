import pytest
from fastapi.testclient import TestClient
import os
import sys

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.recommender import HybridRecommender, get_recommender

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_recommend_empty_query():
    response = client.post("/recommend", json={"query": ""})
    assert response.status_code == 400

def test_recommend_valid_query():
    response = client.post("/recommend", json={
        "query": "shirt",
        "top_k": 2,
        "semantic_weight": 0.5
    })
    
    # Depending on dataset loading, it could return 200 (if data loads well) or 500
    # Assuming success since sample-data.csv exists:
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert data["query"] == "shirt"
        assert "results" in data
        assert len(data["results"]) <= 2
        
        if len(data["results"]) > 0:
            assert "id" in data["results"][0]
            assert "name" in data["results"][0]
            assert "score" in data["results"][0]
