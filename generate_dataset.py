import csv
import os

products = [
    # ---- PANTS ----
    ("PANT-001", "Slim Fit Premium Denim", "Dark wash stretch denim jeans featuring a slim taper fit and reinforced stitching for durability.", "Pants", 4.6, 1, 1, "mens slim fit dark wash denim jeans", 4999),
    ("PANT-002", "Classic Khaki Chinos", "Versatile flat-front chino pants made from breathable cotton twill, perfect for business casual.", "Pants", 4.4, 0, 1, "mens khaki chino pants business casual", 3599),
    ("PANT-003", "Tech Cargo Trousers", "Water-resistant cargo pants with multiple hidden zipper pockets and an articulating knee design.", "Pants", 4.7, 1, 0, "techwear water resistant cargo pants men", 5999),
    ("PANT-004", "Relaxed Fit Lounge Joggers", "Ultra-soft fleece joggers with an elastic drawstring waist for ultimate weekend comfort.", "Pants", 4.8, 0, 1, "mens soft fleece lounge joggers sweatpants", 2599),
    ("PANT-005", "Tailored Wool Trousers", "Elegant high-waisted wool blend trousers, tailored for a sharp, formal silhouette.", "Pants", 4.5, 0, 0, "mens formal wool blend dress trousers", 7999),
    ("PANT-006", "Corduroy Straight Leg Pants", "Vintage-inspired thick corduroy pants available in earthy autumn tones.", "Pants", 4.3, 1, 0, "vintage straight leg corduroy pants", 4299),
    ("PANT-007", "Lightweight Linen Drawstring", "Breezy summer linen pants with a relaxed wide leg and comfortable drawstring closure.", "Pants", 4.5, 0, 0, "mens summer lightweight linen pants", 3899),
    ("PANT-008", "Athletic Track Pants", "Performance track pants with moisture-wicking fabric and side snap buttons.", "Pants", 4.2, 0, 0, "performance athletic sports track pants", 2999),
    ("PANT-009", "Distressed Vintage Jeans", "Light blue extensively distressed denim jeans for a rugged, lived-in aesthetic.", "Pants", 4.4, 1, 0, "distressed ripped light blue denim jeans", 5499),
    ("PANT-010", "Utility Workwear Pants", "Heavy-duty canvas double-knee work pants built to withstand tough environments.", "Pants", 4.8, 0, 1, "heavy duty canvas workwear pants double knee", 6500),

    # ---- SHIRTS ----
    ("SHRT-001", "Crisp White Oxford", "Essential classic white Oxford button-down shirt, featuring a tailored fit and premium cotton.", "Shirts", 4.7, 0, 1, "mens classic white oxford button down shirt", 2999),
    ("SHRT-002", "Casual Flannel Overshirt", "Heavyweight plaid flannel shirt meant to be layered over tees for autumn weather.", "Shirts", 4.8, 1, 1, "heavyweight plaid flannel overshirt layering", 3499),
    ("SHRT-003", "Performance Pique Polo", "Moisture-wicking athletic polo shirt ideal for golf or active office environments.", "Shirts", 4.5, 0, 0, "performance moisture wicking golf polo shirt", 2499),
    ("SHRT-004", "Silk Camp Collar Shirt", "Luxurious silk-blend short sleeve shirt with an open camp collar and a subtle geometric pattern.", "Shirts", 4.6, 1, 0, "luxury silk short sleeve camp collar shirt", 5999),
    ("SHRT-005", "Heavyweight Cotton T-Shirt", "Premium heavyweight structured t-shirt that holds its shape wash after wash.", "Shirts", 4.9, 0, 1, "premium heavyweight structured cotton t shirt", 1299),
    ("SHRT-006", "Linen Button-Up", "Breathable, lightly textured pure linen shirt perfect for beach vacations.", "Shirts", 4.4, 0, 0, "pure breathable linen beach button up shirt", 3299),
    ("SHRT-007", "Denim Western Shirt", "Rugged denim shirt with pearl snap buttons and traditional western yoke detailing.", "Shirts", 4.7, 1, 0, "rugged denim western snap button shirt", 4599),
    ("SHRT-008", "Floral Hawaiian Shirt", "Vibrant tropical floral print short sleeve shirt made from lightweight viscose rayon.", "Shirts", 4.3, 0, 0, "tropical floral print hawaiian rayon shirt", 2799),
    ("SHRT-009", "Merino Wool Sweater Shirt", "A unique hybrid long-sleeve knit shirt made from temperature-regulating merino wool.", "Shirts", 4.8, 0, 0, "temperature regulating merino wool knit shirt", 6599),
    ("SHRT-010", "Striped Breton Top", "Classic French-inspired long sleeve boat neck shirt featuring navy and white horizontal stripes.", "Shirts", 4.5, 0, 0, "classic french horizontal striped breton shirt", 2199),

    # ---- HOME FURNITURE ----
    ("FURN-001", "Mid-Century Modern Sofa", "Sleek velvet 3-seater sofa with tufted cushions and tapered wooden legs.", "Furniture", 4.7, 1, 1, "mid century modern velvet 3 seater sofa", 45000),
    ("FURN-002", "Ergonomic Mesh Office Chair", "Premium office chair with adjustable lumbar support, 3D armrests, and a breathable mesh back.", "Furniture", 4.8, 0, 1, "premium ergonomic mesh office desk chair lumbar", 22000),
    ("FURN-003", "Solid Walnut Coffee Table", "Minimalist low-profile coffee table crafted from beautiful solid walnut wood.", "Furniture", 4.6, 0, 0, "minimalist solid walnut wood low coffee table", 15000),
    ("FURN-004", "Industrial Bookshelf", "Tall 5-tier shelving unit combining rustic reclaimed wood shelves with a black iron pipe frame.", "Furniture", 4.5, 0, 0, "industrial rustic wood black iron pipe bookshelf", 18500),
    ("FURN-005", "Upholstered Platform Bed Frame", "Queen-size bed frame featuring a padded, tufted headboard and sturdy wooden slats.", "Furniture", 4.7, 1, 0, "queen size bed frame tufted upholstered headboard", 32000),
    ("FURN-006", "Marble Top Dining Table", "Elegant circular dining table featuring a heavy genuine marble top and a brass pedestal base.", "Furniture", 4.9, 0, 0, "elegant circular genuine marble top dining table", 55000),
    ("FURN-007", "Leather Accent Recliner", "Plush genuine leather recliner chair with push-back mechanism and ergonomic padding.", "Furniture", 4.6, 0, 0, "plush genuine leather push back recliner chair", 28000),
    ("FURN-008", "Rattan Pattern TV Stand", "Boho-chic entertainment center console featuring woven rattan doors and hidden cable management.", "Furniture", 4.4, 1, 0, "boho rattan woven tv stand entertainment console", 21000),
    ("FURN-009", "Minimalist Floating Nightstand", "Wall-mounted wooden bedside table with a seamlessly integrated drawer for a clean look.", "Furniture", 4.3, 0, 0, "minimalist wall mounted floating wooden nightstand", 4500),
    ("FURN-010", "Velvet Ottoman Pouf", "Round, deeply tufted velvet footrest ottoman that doubles as extra seating.", "Furniture", 4.5, 0, 1, "round tufted velvet footrest ottoman pouf seat", 3500)
]

def main():
    os.makedirs("p:/product/product/data/raw", exist_ok=True)
    with open("p:/product/product/data/raw/catalog.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["uniq_id", "product_name", "product_description", "category", "rating", "is_trending", "is_best_seller", "search_term", "price"])
        for p in products:
            writer.writerow(p)

    print("Catalog dataset (Shirts, Pants, Furniture) generated successfully -> catalog.csv")

if __name__ == "__main__":
    main()
