# 🚀 NexCart Product Recommendation System

Welcome to the **NexCart AI Product Discovery Engine**, a comprehensive rewrite of the product recommendation system, transforming it into an industrial-grade, scalable Machine Learning architecture!

## 🌟 What's New?
We've completely overhauled the project to simulate a real-world tech-stack used by top e-commerce platforms. 

1. **Microservices Architecture**:
   - **Backend** (`FastAPI`): High-performance RESTful API powering our recommendation algorithm.
   - **Frontend** (`Streamlit`): Beautiful, glass-morphism aesthetic UI designed for a premium user experience.

2. **Advanced ML Engine (Hybrid Search)**:
   - **Semantic Search**: Powered by `SentenceTransformers` and `FAISS` for extremely fast, billion-scale dense vector retrieval. 
   - **Lexical Search**: Powered by `BM25`, ensuring exact keyword string matches are correctly prioritized.
   - You can dynamically adjust the sliding weight between semantic vs lexical search in the UI.

3. **Cloud-Native & MLOps Ready**:
   - Packaged with **Docker** and **Docker Compose** to instantly spin up the API and UI anywhere.
   - Modularized project structure following best practices.
   - Comprehensive unit testing via `pytest`.

---

## 🏗️ Project Structure
```text
.
├── backend/
│   ├── main.py            # FastAPI service exposing endpoints
│   └── recommender.py     # Hybrid ML Engine (FAISS + BM25)
├── frontend/
│   ├── app.py             # Streamlit Premium UI
│   └── assets/
│       └── style.css      # Custom UI Styling
├── data/
│   └── raw/               # Product datasets
├── notebooks/             # Data exploration and prototyping
├── tests/                 # Pytest test cases
├── Dockerfile             # Unified Container Definition
├── docker-compose.yml     # Container Orchestrator
└── requirements.txt       # Unified Python dependencies
```

---

## ⚡ Quick Start

### 1. The Easy Way (Docker Compose)
Don't want to install anything on your machine? Just run:
```bash
docker-compose up --build
```
- UI available at: `http://localhost:8501`
- API available at: `http://localhost:8000/docs`

### 2. The Manual Way (Local Execution)
Install the dependencies:
```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate 
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

**Terminal 1: Start Backend**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2: Start Frontend**
```bash
streamlit run frontend/app.py
```

---

## 🧪 Running Tests
```bash
pytest tests/
```

## 🛠️ Technology Stack
* **Python 3.9+**
* **SentenceTransformers** (`all-MiniLM-L6-v2`)
* **FAISS** (Facebook AI Similarity Search)
* **BM25Okapi** (Ranking Algorithm)
* **FastAPI** & **Uvicorn**
* **Streamlit** (with Custom CSS injections)
* **Docker**
