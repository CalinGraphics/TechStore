"""Hardcoded data for fallback when database is not available."""
from typing import Dict, List

# In-memory storage (fallback if Supabase not available)
USER_FAVORITES: Dict[str, List[str]] = {}  # user_id -> list of product_ids
ORDERS: List[dict] = []  # List of orders

HARDCODED_USERS = [
    {
        "id": "user-1",
        "username": "Elvis_Marcu",
        "password": "pass123",
        "role": "user",
        "profile": {
            "age_group": "26-35",
            "interests": ["laptops", "gaming", "photography"],
            "budget_range": "high",
            "preferred_brands": ["Apple", "Dell", "Asus"]
        }
    },
    {
        "id": "user-2",
        "username": "robert_escrocul",
        "password": "pass123",
        "role": "user",
        "profile": {
            "age_group": "18-25",
            "interests": ["smartphones", "fitness", "photography"],
            "budget_range": "medium",
            "preferred_brands": ["Samsung", "Google", "Apple"]
        }
    },
    {
        "id": "user-3",
        "username": "carastefania31",
        "password": "pass123",
        "role": "user",
        "profile": {
            "age_group": "18-25",
            "interests": ["gaming", "laptops", "audio"],
            "budget_range": "high",
            "preferred_brands": ["Asus", "Razer", "Sony"]
        }
    },
    {
        "id": "admin-1",
        "username": "admin",
        "password": "admin123",
        "role": "admin",
        "profile": {
            "age_group": "26-35",
            "interests": ["laptops", "smartphones", "gaming"],
            "budget_range": "high",
            "preferred_brands": ["Apple", "Samsung", "Dell"]
        }
    }
]

HARDCODED_PRODUCTS = [
    {
        "id": "prod-1",
        "name": "MacBook Pro 16\"",
        "category": "laptops",
        "brand": "Apple",
        "price": 2499.99,
        "description": "Laptop profesional de înaltă performanță cu procesor M3 Pro",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500",
        "specs": {
            "processor": "Apple M3 Pro",
            "ram": "32GB",
            "storage": "1TB SSD",
            "display": "16.2 inch Liquid Retina XDR"
        },
        "stock": 15,
        "supplier": "Apple Distribution",
        "delivery_method": "Curier rapid (1-2 zile)",
        "is_active": True,
        "tags": ["laptops", "gaming", "photography"]
    },
    {
        "id": "prod-2",
        "name": "iPhone 15 Pro Max",
        "category": "smartphones",
        "brand": "Apple",
        "price": 1299.99,
        "description": "Ultimul flagship iPhone cu cameră titanium și A17 Pro chip",
        "image_url": "https://s.yimg.com/ny/api/res/1.2/H66pNnkm00C22H089VH_Cw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTI0MDA7aD0xNjAw/https://s.yimg.com/os/creatr-uploaded-images/2023-09/be674c30-56ee-11ee-b7fc-ab167c852b72",
        "specs": {
            "processor": "A17 Pro",
            "camera": "48MP Main + 12MP Ultra Wide",
            "storage": "256GB",
            "display": "6.7 inch Super Retina XDR"
        },
        "stock": 25,
        "supplier": "Apple Distribution",
        "delivery_method": "Curier rapid (1-2 zile)",
        "is_active": True,
        "tags": ["smartphones", "photography"]
    },
    {
        "id": "prod-3",
        "name": "Samsung Galaxy S24 Ultra",
        "category": "smartphones",
        "brand": "Samsung",
        "price": 1199.99,
        "description": "Smartphone premium cu S Pen și AI features",
        "image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500",
        "specs": {
            "processor": "Snapdragon 8 Gen 3",
            "camera": "200MP Main + 50MP Telephoto",
            "storage": "512GB",
            "display": "6.8 inch Dynamic AMOLED 2X"
        },
        "stock": 20,
        "supplier": "Samsung Electronics",
        "delivery_method": "Curier standard (3-5 zile)",
        "is_active": True,
        "tags": ["smartphones", "gaming"]
    },
    {
        "id": "prod-4",
        "name": "Dell XPS 15",
        "category": "laptops",
        "brand": "Dell",
        "price": 1799.99,
        "description": "Laptop ultraperformant pentru creatori de conținut",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500",
        "specs": {
            "processor": "Intel Core i9-13900H",
            "ram": "32GB DDR5",
            "storage": "1TB NVMe SSD",
            "display": "15.6 inch OLED 4K"
        },
        "stock": 12,
        "supplier": "Dell Technologies",
        "delivery_method": "Curier rapid (1-2 zile)",
        "is_active": True,
        "tags": ["laptops"]
    },
    {
        "id": "prod-5",
        "name": "Asus ROG Zephyrus G16",
        "category": "gaming",
        "brand": "Asus",
        "price": 2299.99,
        "description": "Laptop gaming de top cu RTX 4090",
        "image_url": "https://images.unsplash.com/photo-1603481588273-2f908a9a7a1b?w=500",
        "specs": {
            "processor": "Intel Core i9-14900HX",
            "gpu": "NVIDIA RTX 4090",
            "ram": "32GB DDR5",
            "storage": "2TB SSD"
        },
        "stock": 8,
        "supplier": "ASUS Romania",
        "delivery_method": "Curier rapid (1-2 zile)",
        "is_active": True,
        "tags": ["gaming", "laptops"]
    },
    {
        "id": "prod-6",
        "name": "Sony WH-1000XM5",
        "category": "audio",
        "brand": "Sony",
        "price": 399.99,
        "description": "Căști premium cu noise cancelling de top",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500",
        "specs": {
            "type": "Over-ear",
            "noise_cancelling": "Industry-leading ANC",
            "battery": "30 hours",
            "connectivity": "Bluetooth 5.2"
        },
        "stock": 30,
        "supplier": "Sony Europe",
        "delivery_method": "Curier standard (3-5 zile)",
        "is_active": True,
        "tags": ["audio"]
    },
    {
        "id": "prod-7",
        "name": "Apple Watch Series 9",
        "category": "fitness",
        "brand": "Apple",
        "price": 429.99,
        "description": "Smartwatch pentru sănătate și fitness",
        "image_url": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500",
        "specs": {
            "display": "Always-On Retina",
            "features": "ECG, Blood Oxygen, Temperature",
            "battery": "18 hours",
            "water_resistance": "50m"
        },
        "stock": 40,
        "supplier": "Apple Distribution",
        "delivery_method": "Curier rapid (1-2 zile)",
        "is_active": True,
        "tags": ["wearables", "fitness"]
    },
    {
        "id": "prod-8",
        "name": "Google Pixel 8 Pro",
        "category": "smartphones",
        "brand": "Google",
        "price": 999.99,
        "description": "Smartphone cu cele mai bune fotografii AI",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500",
        "specs": {
            "processor": "Google Tensor G3",
            "camera": "50MP Main + AI Magic Eraser",
            "storage": "256GB",
            "display": "6.7 inch LTPO OLED"
        },
        "stock": 18,
        "supplier": "Google Store",
        "delivery_method": "Curier standard (3-5 zile)",
        "is_active": True,
        "tags": ["smartphones"]
    },
    {
        "id": "prod-9",
        "name": "iPad Pro 12.9\"",
        "category": "tablets",
        "brand": "Apple",
        "price": 1099.99,
        "description": "Tabletă premium pentru productivitate și creativitate",
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500",
        "specs": {
            "processor": "Apple M2",
            "display": "12.9 inch Liquid Retina XDR",
            "storage": "512GB",
            "features": "Apple Pencil & Magic Keyboard support"
        },
        "stock": 22,
        "supplier": "Apple Distribution",
        "delivery_method": "Curier rapid (1-2 zile)",
        "is_active": True,
        "tags": ["tablets"]
    },
    {
        "id": "prod-10",
        "name": "Samsung Galaxy Watch 6",
        "category": "fitness",
        "brand": "Samsung",
        "price": 349.99,
        "description": "Smartwatch elegant cu monitorizare completă a sănătății",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "specs": {
            "display": "1.5 inch Super AMOLED",
            "features": "Heart Rate, Sleep, Body Composition",
            "battery": "40 hours",
            "water_resistance": "5ATM + IP68"
        },
        "stock": 35,
        "supplier": "Samsung Electronics",
        "delivery_method": "Curier standard (3-5 zile)",
        "is_active": True,
        "tags": ["wearables", "fitness"]
    }
]


def refresh_product_status(product: dict):
    """Refresh product status based on stock."""
    stock = product.get("stock", 0)
    if stock <= 0:
        product["stock"] = 0
        product["is_active"] = False
    else:
        if "is_active" not in product or product["is_active"] is None:
            product["is_active"] = True


def ensure_product_tags(product: dict):
    """Ensure product has tags."""
    if not product.get("tags"):
        product["tags"] = [product.get("category", "")]


# Initialize products
for product in HARDCODED_PRODUCTS:
    refresh_product_status(product)
    ensure_product_tags(product)

