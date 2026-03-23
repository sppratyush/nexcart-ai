import streamlit as st
import requests
import os
import time

# --- Configuration ---
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="NexCart | AI Product Discovery",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Custom CSS ---
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ⚙️ Search Settings")
    top_k = st.slider("Number of Results", min_value=1, max_value=20, value=6)
    st.markdown("#### Hybrid Search Focus")
    st.markdown("<small>Adjust the blend between exact keyword matching (BM25) and semantic vector search (SentenceTransformers).</small>", unsafe_allow_html=True)
    
    semantic_weight = st.slider(
        "Semantic Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="1.0 = Pure Semantic Search, 0.0 = Pure Lexical Search"
    )
    
    st.markdown("---")
    st.markdown("### ⚡ Real-time Product Sync")
    with st.expander("Add New Product to Index"):
        new_name = st.text_input("Product Name")
        new_desc = st.text_area("Description")
        if st.button("🚀 Index Product"):
            if new_name and new_desc:
                try:
                    sync_resp = requests.post(
                        f"{API_URL}/items",
                        json={"name": new_name, "description": new_desc}
                    )
                    if sync_resp.status_code == 200:
                        st.success("Product indexed and searchable!")
                    else:
                        st.error(f"Sync failed: {sync_resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Name and Description required.")

    st.markdown("---")
    st.markdown("### 📊 System Status")
    try:
        health_resp = requests.get(f"{API_URL}/health", timeout=2)
        if health_resp.status_code == 200:
            st.success("Backend: Online 🟢")
        else:
            st.error("Backend: Error 🔴")
    except:
        st.error("Backend: Offline 🔴")

# --- Main Content ---
st.markdown("<h1>🛍️ NexCart Discovery Engine</h1>", unsafe_allow_html=True)

query = st.text_input("What are you looking for today?", placeholder="e.g. 'Waterproof hiking boots' or 'Quiet mechanical keyboard'...")

cols = st.columns([1, 4, 1])
with cols[1]:
    search_clicked = st.button("🔍 Discover Products", use_container_width=True)

if search_clicked or query:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Analyzing semantic space and fetching top matches..."):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{API_URL}/recommend",
                    json={
                        "query": query,
                        "top_k": top_k,
                        "semantic_weight": semantic_weight
                    },
                    timeout=10
                )
                ellapsed = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    all_results = data.get("results", [])
                    # Filter out padding items with absolute match scores below 0.60
                    results = [r for r in all_results if float(r.get('score', 0)) >= 0.60]
                    
                    st.markdown(f"<p style='color: #94a3b8; margin-top: 1rem;'>Found {len(results)} highly-relevant results in {ellapsed:.3f} seconds.</p>", unsafe_allow_html=True)
                    
                    if not results:
                        st.info("No relevant products found.")
                    else:
                        # Render results in a grid
                        for i in range(0, len(results), 2):
                            col1, col2 = st.columns(2)
                            
                            # Item 1
                            item1 = results[i]
                            with col1:
                                # Convert similar items to a badge string
                                sim_html = ""
                                if "similar_items" in item1:
                                    sim_names = [f"<span class='sim-badge'>{s['name'][:30]}...</span>" for s in item1["similar_items"]]
                                    sim_html = f"<div class='sim-section'><b>Similar:</b> {' '.join(sim_names)}</div>"
                                    
                                # Metdata badges
                                badges_html = ""
                                if item1.get('is_trending'):
                                    badges_html += "<span style='background: #ec4899; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 5px;'>🔥 Trending</span>"
                                if item1.get('is_best_seller'):
                                    badges_html += "<span style='background: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 5px;'>🏆 Best Seller</span>"
                                
                                rating_html = f"<span style='color: #f59e0b;'>★ {item1.get('rating', 0.0)}</span>"
                                    
                                st.markdown(f"""
                                <div class="product-card">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                        <div class="product-title">{item1['name']}</div>
                                        <div>{rating_html}</div>
                                    </div>
                                    <div style="margin-bottom: 0.8rem;">{badges_html}</div>
                                    <div class="product-desc">{str(item1['description'])[:200]}...</div>
                                    <div class="product-score">Match Score: {item1['score']:.2f}</div>
                                    {sim_html}
                                    <div style="margin-top: 1rem; display: flex; gap: 10px;">
                                        <a href="{item1.get('amazon_url', '#')}" target="_blank" style="text-decoration: none;">
                                            <button style="background: #f59e0b; color: #fff; border:none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">🛒 Amazon</button>
                                        </a>
                                        <a href="{item1.get('flipkart_url', '#')}" target="_blank" style="text-decoration: none;">
                                            <button style="background: #3b82f6; color: #fff; border:none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">🛒 Flipkart</button>
                                        </a>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            # Item 2
                            if i + 1 < len(results):
                                item2 = results[i+1]
                                with col2:
                                    sim_html = ""
                                    if "similar_items" in item2:
                                        sim_names = [f"<span class='sim-badge'>{s['name'][:30]}...</span>" for s in item2["similar_items"]]
                                        sim_html = f"<div class='sim-section'><b>Similar:</b> {' '.join(sim_names)}</div>"
                                        
                                    # Metdata badges
                                    badges_html2 = ""
                                    if item2.get('is_trending'):
                                        badges_html2 += "<span style='background: #ec4899; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 5px;'>🔥 Trending</span>"
                                    if item2.get('is_best_seller'):
                                        badges_html2 += "<span style='background: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 5px;'>🏆 Best Seller</span>"
                                    
                                    rating_html2 = f"<span style='color: #f59e0b;'>★ {item2.get('rating', 0.0)}</span>"

                                    st.markdown(f"""
                                    <div class="product-card">
                                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                            <div class="product-title">{item2['name']}</div>
                                            <div>{rating_html2}</div>
                                        </div>
                                        <div style="margin-bottom: 0.8rem;">{badges_html2}</div>
                                        <div class="product-desc">{str(item2['description'])[:200]}...</div>
                                        <div class="product-score">Match Score: {item2['score']:.2f}</div>
                                        {sim_html}
                                        <div style="margin-top: 1rem; display: flex; gap: 10px;">
                                            <a href="{item2.get('amazon_url', '#')}" target="_blank" style="text-decoration: none;">
                                                <button style="background: #f59e0b; color: #fff; border:none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">🛒 Amazon</button>
                                            </a>
                                            <a href="{item2.get('flipkart_url', '#')}" target="_blank" style="text-decoration: none;">
                                                <button style="background: #3b82f6; color: #fff; border:none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">🛒 Flipkart</button>
                                            </a>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Error from server: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot connect to the backend ML Engine. Please ensure the FastAPI server is running.")
            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")
