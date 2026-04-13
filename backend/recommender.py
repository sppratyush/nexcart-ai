import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import re
import urllib.parse
import pickle
from datetime import datetime

class HybridRecommender:
    def __init__(self, data_path: str, model_name: str = "multi-qa-mpnet-base-dot-v1", model_dir: str = "data/models"):
        self.data_path = data_path
        self.model_name = model_name
        self.model_dir = model_dir
        
        # Ensure model directory exists
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
            
        self.model = SentenceTransformer(self.model_name)
        
        self.df = None
        self.bm25 = None
        self.faiss_index = None
        
        self.load_data()
        
        # Try to load existing indices, otherwise build from scratch
        if not self.load_indices():
            print("No existing indices found or load failed. Building from scratch...")
            self.build_indices()
            self.save_indices()
        else:
            print(f"Existing indices loaded successfully (Size: {len(self.df)}).")

    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text) # More aggressive cleaning
        text = re.sub(r'\s+', ' ', text).strip()
        return text.lower()

    def load_data(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
            
        self.df = pd.read_csv(self.data_path, encoding="latin1")
        self.df.columns = self.df.columns.str.lower().str.strip()
        
        name_candidates = ['name', 'product_name', 'title']
        desc_candidates = ['description', 'desc', 'details', 'product_description']
        id_candidates = ['id', 'product_id', 'uniq_id']
        
        self.name_col = next((c for c in name_candidates if c in self.df.columns), None)
        self.desc_col = next((c for c in desc_candidates if c in self.df.columns), None)
        self.id_col = next((c for c in id_candidates if c in self.df.columns), None)
        
        if self.name_col is None and self.desc_col is not None:
             self.df['name'] = self.df[self.desc_col].apply(lambda x: str(x)[:50] + "..." if isinstance(x, str) else "Unnamed Product")
             self.name_col = 'name'
             
        if self.name_col is None or self.desc_col is None:
            # Create dummy if everything fails
            if self.df.empty:
                raise ValueError("Dataset is empty and no valid columns found.")
            self.name_col = self.df.columns[0]
            self.desc_col = self.df.columns[1] if len(self.df.columns) > 1 else self.df.columns[0]

        if self.id_col is None:
            self.df['id'] = range(1, len(self.df) + 1)
            self.id_col = 'id'

        self.df = self.df.fillna("")
        if 'price' in self.df.columns:
            self.df['price'] = pd.to_numeric(self.df['price'], errors='coerce').fillna(0.0)
        else:
            self.df['price'] = 0.0

        self.df['clean_desc'] = self.df[self.desc_col].apply(self.clean_text)
        self.df['clean_name'] = self.df[self.name_col].apply(self.clean_text)
        self.df['combined'] = self.df['clean_name'] + " " + self.df['clean_desc']

    def build_indices(self):
        texts = self.df['combined'].tolist()
        
        # 1. semantic FAISS
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        d = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(d)
        faiss.normalize_L2(embeddings)
        self.faiss_index.add(embeddings)
        
        # 2. lexical BM25
        tokenized_corpus = [text.split() for text in texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def save_indices(self):
        faiss_path = os.path.join(self.model_dir, "faiss.index")
        bm25_path = os.path.join(self.model_dir, "bm25.pkl")
        df_path = os.path.join(self.model_dir, "processed_data.pkl")
        
        faiss.write_index(self.faiss_index, faiss_path)
        with open(bm25_path, "wb") as f:
            pickle.dump(self.bm25, f)
        with open(df_path, "wb") as f:
            pickle.dump(self.df, f)
        print(f"Indices saved to {self.model_dir}")

    def load_indices(self) -> bool:
        faiss_path = os.path.join(self.model_dir, "faiss.index")
        bm25_path = os.path.join(self.model_dir, "bm25.pkl")
        df_path = os.path.join(self.model_dir, "processed_data.pkl")
        
        if all(os.path.exists(p) for p in [faiss_path, bm25_path, df_path]):
            try:
                self.faiss_index = faiss.read_index(faiss_path)
                with open(bm25_path, "rb") as f:
                    self.bm25 = pickle.load(f)
                with open(df_path, "rb") as f:
                    self.df = pickle.load(f)
                return True
            except Exception as e:
                print(f"Error loading indices: {e}")
                return False
        return False


    def recommend(self, query: str, top_k: int = 5, semantic_weight: float = 0.7, min_price: float = None, max_price: float = None):
        clean_query = self.clean_text(query)
        
        if not clean_query:
            # Catalog Browse Mode: No query sent, so we return all items sorted by trending/rating.
            # We assign a default score of 1.0 to ensure they pass frontend filters.
            hybrid_scores = np.ones(len(self.df))
            
            # Apply boosts for ratings and status to naturally sort the catalog
            if 'rating' in self.df.columns:
                hybrid_scores += self.df['rating'].astype(float) / 5.0 * 0.1
            if 'is_trending' in self.df.columns:
                hybrid_scores += self.df['is_trending'].astype(float) * 0.1
            if 'is_best_seller' in self.df.columns:
                hybrid_scores += self.df['is_best_seller'].astype(float) * 0.1
            
            hybrid_scores = np.clip(hybrid_scores, 0.0, 1.0)
        else:
            # 1. Semantic
            query_emb = self.model.encode([clean_query], convert_to_numpy=True)
            faiss.normalize_L2(query_emb)
            distances, indices = self.faiss_index.search(query_emb, min(len(self.df), 200)) # Increased search space
            
            semantic_scores = np.zeros(len(self.df))
            for i, idx in enumerate(indices[0]):
                if idx != -1:
                    semantic_scores[idx] = distances[0][i]
                
            semantic_scores = np.clip(semantic_scores, 0.0, 1.0)
    
            # 2. Lexical
            tokenized_query = clean_query.split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            bm25_scores = np.clip(bm25_scores / 10.0, 0.0, 1.0)
    
            # 3. Hybrid Base Score
            hybrid_scores = (semantic_scores * semantic_weight) + (bm25_scores * (1.0 - semantic_weight))
    
            # 4. Metadata Boosting
            # Apply boosts for ratings and status
            if 'rating' in self.df.columns:
                # Rating boost: up to 0.1
                rating_boost = self.df['rating'].astype(float) / 5.0 * 0.1
                hybrid_scores += rating_boost.values
                
            if 'is_trending' in self.df.columns:
                # Trending boost: 0.1
                trending_boost = self.df['is_trending'].astype(float) * 0.1
                hybrid_scores += trending_boost.values
                
            if 'is_best_seller' in self.df.columns:
                # Best seller boost: 0.1
                best_seller_boost = self.df['is_best_seller'].astype(float) * 0.1
                hybrid_scores += best_seller_boost.values
    
            # Normalize final scores to [0, 1] clipping
            hybrid_scores = np.clip(hybrid_scores, 0.0, 1.0)

        # Apply Hard Filtering for Price bounds
        if min_price is not None or max_price is not None:
             valid_indices = np.ones(len(self.df), dtype=bool)
             if 'price' in self.df.columns:
                 prices = self.df['price'].values
                 if min_price is not None:
                     valid_indices &= (prices >= min_price)
                 if max_price is not None:
                     valid_indices &= (prices <= max_price)
             
             # Zero out scores for invalid items
             hybrid_scores[~valid_indices] = -1.0

        # 5. Result Selection with De-duplication
        # Get more than enough to filter
        top_indices = np.argsort(hybrid_scores)[::-1]
        top_indices = [idx for idx in top_indices if hybrid_scores[idx] > 0][:top_k * 4]
        
        results = []
        seen_main_base_names = set()
        
        for idx in top_indices:
            row = self.df.iloc[idx]
            name = row[self.name_col]
            base_name = name.split(' (')[0].lower()
            
            if base_name in seen_main_base_names:
                continue
                
            seen_main_base_names.add(base_name)
            
            search_query = str(row['search_term']) if 'search_term' in self.df.columns and pd.notna(row.get('search_term')) else base_name
            amazon_url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(search_query)}"
            flipkart_url = f"https://www.flipkart.com/search?q={urllib.parse.quote_plus(search_query)}"
            
            # Similar items (Semantic only)
            item_emb = self.model.encode([row['combined']], convert_to_numpy=True)
            faiss.normalize_L2(item_emb)
            _, sim_indices = self.faiss_index.search(item_emb, 20)
            
            similar_items = []
            seen_sim_base_names = {base_name} # Exclude current product's base name
            
            for sim_idx in sim_indices[0]:
                if sim_idx == -1 or sim_idx == idx:
                    continue
                    
                sim_row = self.df.iloc[sim_idx]
                sim_name = sim_row[self.name_col]
                sim_base_name = sim_name.split(' (')[0].lower()
                
                if sim_base_name not in seen_sim_base_names and len(similar_items) < 3:
                    similar_items.append({
                        "id": str(sim_row[self.id_col]),
                        "name": sim_name
                    })
                    seen_sim_base_names.add(sim_base_name)
            
            # Pricing and Mock values
            price = float(row.get('price', 0.0))
            price_available = (price > 0)
            price_source = "Demo Data"

            if price_available:
                # We do not simulate fake prices anymore to avoid mismatched data.
                # If we get a live API, we will populate these.
                amazon_price = 0.0
                flipkart_price = 0.0
            else:
                amazon_price = 0.0
                flipkart_price = 0.0

            # Tags Logic
            tags = []
            rating = float(row.get('rating', 0))
            if rating >= 4.7:
                 tags.append("Top Rated")
            if price >= 80000:
                 tags.append("Premium Choice")
            if 0 < price <= 20000 and rating >= 4.0:
                 tags.append("Best Budget")
            if float(hybrid_scores[idx]) > 0.8 and price > 0 and price <= 30000:
                 tags.append("Best Value")

            results.append({
                "id": str(row[self.id_col]),
                "name": name,
                "description": row[self.desc_col],
                "price": price,
                "amazon_price": amazon_price,
                "flipkart_price": flipkart_price,
                "price_available": price_available,
                "price_source": price_source,
                "tags": tags,
                "score": float(hybrid_scores[idx]),
                "rating": rating,
                "is_trending": bool(row.get('is_trending', False)),
                "is_best_seller": bool(row.get('is_best_seller', False)),
                "amazon_url": amazon_url,
                "flipkart_url": flipkart_url,
                "similar_items": similar_items
            })
            
            if len(results) >= top_k:
                break
            
        return results

# Singleton instance
_recommender = None

def get_recommender(data_path="data/raw/catalog.csv"):
    global _recommender
    if _recommender is None:
        _recommender = HybridRecommender(data_path)
    return _recommender
