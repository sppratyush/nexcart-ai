import streamlit as st
import requests
import os
import time

# --- Configuration ---
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="SmartShop | AI Product Discovery",
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
    
    st.markdown("#### Price Filtering (₹)")
    price_range = st.slider(
        "Select Price Range",
        min_value=0,
        max_value=200000,
        value=(0, 200000),
        step=1000
    )
    min_price, max_price = price_range
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
    st.markdown("### 📊 Analytics Dashboard")
    try:
        stats_resp = requests.get(f"{API_URL}/stats", timeout=3)
        if stats_resp.status_code == 200:
             stats = stats_resp.json()
             st.metric("Total Products", stats.get("total_products", 0))
             st.metric("Average Price", f"₹{stats.get('avg_price', 0):,.2f}")
             
             dist = stats.get("price_distribution", {})
             if dist:
                 st.markdown("**Price Distribution**")
                 st.bar_chart(dist)
    except:
        st.warning("Analytics unavailable")

    st.markdown("---")
    st.markdown("### 🩺 System Status")
    try:
        health_resp = requests.get(f"{API_URL}/health", timeout=2)
        if health_resp.status_code == 200:
            st.success("Backend: Online 🟢")
        else:
            st.error("Backend: Error 🔴")
    except:
        st.error("Backend: Offline 🔴")

# --- Main Content ---
st.markdown("<h1>🛍️ SmartShop Discovery Engine</h1>", unsafe_allow_html=True)

query = st.text_input("What are you looking for today?", placeholder="e.g. 'Waterproof hiking boots' or 'Quiet mechanical keyboard'...")

cols = st.columns([1, 4, 1])
with cols[1]:
    search_clicked = st.button("🔍 Discover Products", use_container_width=True)

if search_clicked or query:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        # Smart Suggestion Messages
        q_lower = query.lower()
        if len(q_lower.split()) < 2 and not any(k in q_lower for k in ['budget', 'premium', 'high-end', 'cheap']):
            st.info("💡 **Hint:** Try using keywords like 'budget', 'premium', or specified categories for better results.")
        elif 'budget' in q_lower or 'cheap' in q_lower or 'under' in q_lower:
            st.success("🎯 **Smart Filter:** We see you're looking for value! Prioritizing budget-friendly options.")
            
        with st.spinner("Analyzing semantic space and fetching top matches..."):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{API_URL}/recommend",
                    json={
                        "query": query,
                        "top_k": top_k,
                        "semantic_weight": semantic_weight,
                        "min_price": min_price,
                        "max_price": max_price
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
                        st.warning("Try broader terms, adjusting the price range, or include budget/category keywords.")
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
                                
                                # Smart Tags
                                for tag in item1.get('tags', []):
                                    badges_html += f"<span style='background: #8b5cf6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 5px;'>✨ {tag}</span>"

                                rating_html = f"<span style='color: #f59e0b;'>★ {item1.get('rating', 0.0)}</span>"
                                
                                border_style = "border: 2px solid #10b981;" if i == 0 else ""
                                match_text = "<div style='color: #10b981; font-size: 0.8rem; margin-bottom: 5px;'><b>⭐ BEST MATCH</b></div>" if i == 0 else ""
                                
                                price_available = item1.get('price_available', False)
                                price_source = item1.get('price_source', 'Live API')
                                
                                if price_available:
                                    amazon_price = item1.get('amazon_price', 0)
                                    flipkart_price = item1.get('flipkart_price', 0)
                                    price_label = "System Base Price (Demo)" if price_source == "Demo Data" else "Live Price"
                                    price_str = f"₹{item1.get('price', 0):,.2f}<br><span style='font-size: 0.7rem; font-weight: normal; color: #64748b;'>{price_label}</span>"

                                    if amazon_price > 0 and flipkart_price > 0:
                                        amz_best = " (Best Price ✅)" if amazon_price <= flipkart_price else ""
                                        flp_best = " (Best Price ✅)" if flipkart_price < amazon_price else ""
                                        amz_text = f"🛒 Amazon: ₹{amazon_price:,.2f}{amz_best}"
                                        flp_text = f"🛒 Flipkart: ₹{flipkart_price:,.2f}{flp_best}"
                                    else:
                                        amz_text = "🛒 Check Amazon Price"
                                        flp_text = "🛒 Check Flipkart Price"

                                    button_html = f"""<div style="margin-top: 1rem; border-top: 1px dashed #cbd5e1; padding-top: 0.8rem;">
<div style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Check exact prices via official links:</div>
<div style="display: flex; gap: 10px;">
    <a href="{item1.get('amazon_url', '#')}" target="_blank" style="text-decoration: none; flex: 1;">
        <button style="width: 100%; background: #f59e0b; color: #fff; border:none; padding: 5px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">{amz_text}</button>
    </a>
    <a href="{item1.get('flipkart_url', '#')}" target="_blank" style="text-decoration: none; flex: 1;">
        <button style="width: 100%; background: #3b82f6; color: #fff; border:none; padding: 5px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">{flp_text}</button>
    </a>
</div>
</div>"""
                                else:
                                    price_str = "<span style='font-size: 0.8rem; font-weight: normal; color: #ef4444;'>Price not available currently</span>"
                                    button_html = ""
                                    
                                st.markdown(f"""<div class="product-card" style="{border_style}">
{match_text}
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
    <div class="product-title">{item1['name']}</div>
    <div style="text-align: right;">
        <div>{rating_html}</div>
        <div style="font-size: 1.1rem; font-weight: bold; color: #1e293b;">{price_str}</div>
    </div>
</div>
<div style="margin-bottom: 0.8rem; display: flex; flex-wrap: wrap; gap: 4px;">{badges_html}</div>
<div class="product-desc">{str(item1['description'])[:200]}...</div>
<div class="product-score">Match Score: {item1['score']:.2f}</div>
{sim_html}
{button_html}
</div>""", unsafe_allow_html=True)

                                
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
                                    
                                    # Smart Tags
                                    for tag in item2.get('tags', []):
                                        badges_html2 += f"<span style='background: #8b5cf6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 5px;'>✨ {tag}</span>"
                                    
                                    rating_html2 = f"<span style='color: #f59e0b;'>★ {item2.get('rating', 0.0)}</span>"

                                    price_available2 = item2.get('price_available', False)
                                    price_source2 = item2.get('price_source', 'Live API')
                                    
                                    if price_available2:
                                        amazon_price2 = item2.get('amazon_price', 0)
                                        flipkart_price2 = item2.get('flipkart_price', 0)
                                        price_label2 = "System Base Price (Demo)" if price_source2 == "Demo Data" else "Live Price"
                                        price_str2 = f"₹{item2.get('price', 0):,.2f}<br><span style='font-size: 0.7rem; font-weight: normal; color: #64748b;'>{price_label2}</span>"

                                        if amazon_price2 > 0 and flipkart_price2 > 0:
                                            amz_best2 = " (Best Price ✅)" if amazon_price2 <= flipkart_price2 else ""
                                            flp_best2 = " (Best Price ✅)" if flipkart_price2 < amazon_price2 else ""
                                            amz_text2 = f"🛒 Amazon: ₹{amazon_price2:,.2f}{amz_best2}"
                                            flp_text2 = f"🛒 Flipkart: ₹{flipkart_price2:,.2f}{flp_best2}"
                                        else:
                                            amz_text2 = "🛒 Check Amazon Price"
                                            flp_text2 = "🛒 Check Flipkart Price"

                                        button_html2 = f"""<div style="margin-top: 1rem; border-top: 1px dashed #cbd5e1; padding-top: 0.8rem;">
<div style="font-size: 0.8rem; color: #64748b; margin-bottom: 5px;">Check exact prices via official links:</div>
<div style="display: flex; gap: 10px;">
    <a href="{item2.get('amazon_url', '#')}" target="_blank" style="text-decoration: none; flex: 1;">
        <button style="width: 100%; background: #f59e0b; color: #fff; border:none; padding: 5px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">{amz_text2}</button>
    </a>
    <a href="{item2.get('flipkart_url', '#')}" target="_blank" style="text-decoration: none; flex: 1;">
        <button style="width: 100%; background: #3b82f6; color: #fff; border:none; padding: 5px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">{flp_text2}</button>
    </a>
</div>
</div>"""
                                    else:
                                        price_str2 = "<span style='font-size: 0.8rem; font-weight: normal; color: #ef4444;'>Price not available currently</span>"
                                        button_html2 = ""

                                    st.markdown(f"""<div class="product-card">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
    <div class="product-title">{item2['name']}</div>
    <div style="text-align: right;">
        <div>{rating_html2}</div>
        <div style="font-size: 1.1rem; font-weight: bold; color: #1e293b;">{price_str2}</div>
    </div>
</div>
<div style="margin-bottom: 0.8rem; display: flex; flex-wrap: wrap; gap: 4px;">{badges_html2}</div>
<div class="product-desc">{str(item2['description'])[:200]}...</div>
<div class="product-score">Match Score: {item2['score']:.2f}</div>
{sim_html}
{button_html2}
</div>""", unsafe_allow_html=True)

                else:
                    st.error(f"Error from server: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot connect to the backend ML Engine. Please ensure the FastAPI server is running.")
            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")
