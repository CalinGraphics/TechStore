"""In-memory storage helpers used as a fallback layer when Supabase is not available."""
from typing import Dict, List

# In-memory storage (only populated at runtime, nu există date hardcodate la pornire)
USER_FAVORITES: Dict[str, List[str]] = {}  # user_id -> list of product_ids
ORDERS: List[dict] = []  # List of orders

# Date demo (folosite ca fallback dacă Supabase nu este configurat)
# Notă: parolele sunt în clar doar pentru mod demo local; în DB ele se stochează hash-uit.
HARDCODED_USERS: List[dict] = [
    {
        "id": "1",
        "username": "admin",
        "password": "admin123",
        "role": "admin",
        "profile": {
            "age_group": "26-35",
            "budget_range": "high",
            "interests": ["laptops", "gaming", "audio"],
            "preferred_brands": ["Apple", "Dell", "Sony", "Samsung"],
        },
    },
    {
        "id": "2",
        "username": "user",
        "password": "pass123",
        "role": "user",
        "profile": {
            "age_group": "18-25",
            "budget_range": "medium",
            "interests": ["smartphones", "audio", "fitness"],
            "preferred_brands": ["Samsung", "Xiaomi", "Sony"],
        },
    },
]

HARDCODED_PRODUCTS: List[dict] = [
    {
        "id": "p1",
        "name": "Laptop Dell XPS 13",
        "category": "laptops",
        "brand": "Dell",
        "price": 6499.0,
        "description": "Ultrabook premium cu ecran luminos și autonomie mare.",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
        "specs": {"cpu": "Intel Core i7", "ram": "16GB", "storage": "512GB SSD", "display": "13.4\" FHD"},
        "stock": 8,
        "supplier": "Dell Romania",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["ultrabook", "office", "portable"],
    },
    {
        "id": "p2",
        "name": "MacBook Air M2",
        "category": "laptops",
        "brand": "Apple",
        "price": 6999.0,
        "description": "Laptop ușor și rapid, excelent pentru productivitate.",
        "image_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4",
        "specs": {"cpu": "Apple M2", "ram": "8GB", "storage": "256GB SSD", "display": "13.6\" Liquid Retina"},
        "stock": 10,
        "supplier": "Apple Partner",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["mac", "portable", "student"],
    },
    {
        "id": "p3",
        "name": "Samsung Galaxy S24",
        "category": "smartphones",
        "brand": "Samsung",
        "price": 4599.0,
        "description": "Smartphone flagship cu cameră excelentă și ecran AMOLED.",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
        "specs": {"display": "6.2\" AMOLED", "camera": "50MP", "battery": "4000mAh", "storage": "256GB"},
        "stock": 14,
        "supplier": "Samsung Store",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["android", "flagship", "camera"],
    },
    {
        "id": "p4",
        "name": "Xiaomi Redmi Note 13",
        "category": "smartphones",
        "brand": "Xiaomi",
        "price": 1299.0,
        "description": "Raport preț/performanță foarte bun, baterie mare.",
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5",
        "specs": {"display": "6.67\" OLED", "camera": "108MP", "battery": "5000mAh", "storage": "128GB"},
        "stock": 25,
        "supplier": "Xiaomi Distributor",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["budget", "battery", "oled"],
    },
    {
        "id": "p5",
        "name": "Sony WH-1000XM5",
        "category": "audio",
        "brand": "Sony",
        "price": 1799.0,
        "description": "Căști cu anulare activă a zgomotului și sunet premium.",
        "image_url": "https://images.unsplash.com/photo-1518441902117-f0a2b4f7d4b7",
        "specs": {"type": "over-ear", "anc": True, "battery": "30h"},
        "stock": 12,
        "supplier": "Sony Audio",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["anc", "wireless", "premium"],
    },
    {
        "id": "p6",
        "name": "Apple AirPods Pro",
        "category": "audio",
        "brand": "Apple",
        "price": 1299.0,
        "description": "In-ear cu ANC și integrare excelentă în ecosistem.",
        "image_url": "https://images.unsplash.com/photo-1588423771073-b8903fbb85b5",
        "specs": {"type": "in-ear", "anc": True, "charging": "wireless"},
        "stock": 30,
        "supplier": "Apple Partner",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["anc", "in-ear", "wireless"],
    },
    {
        "id": "p7",
        "name": "PlayStation 5",
        "category": "gaming",
        "brand": "Sony",
        "price": 2799.0,
        "description": "Consolă next-gen pentru gaming 4K și exclusivități.",
        "image_url": "https://images.unsplash.com/photo-1606813902914-1c3cfa3dfe2f",
        "specs": {"resolution": "4K", "storage": "825GB SSD"},
        "stock": 7,
        "supplier": "Game Retail",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["console", "4k", "exclusive"],
    },
    {
        "id": "p8",
        "name": "Nintendo Switch OLED",
        "category": "gaming",
        "brand": "Nintendo",
        "price": 1599.0,
        "description": "Consolă hibrid cu ecran OLED și portabilitate.",
        "image_url": "https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf",
        "specs": {"display": "7\" OLED", "mode": "handheld/docked"},
        "stock": 11,
        "supplier": "Game Retail",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["portable", "oled", "family"],
    },
    {
        "id": "p9",
        "name": "Garmin Forerunner 255",
        "category": "fitness",
        "brand": "Garmin",
        "price": 1499.0,
        "description": "Ceas sport cu GPS, puls și antrenamente inteligente.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
        "specs": {"gps": True, "battery": "14 days", "metrics": "HR, VO2max"},
        "stock": 9,
        "supplier": "Garmin Store",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["gps", "running", "health"],
    },
    {
        "id": "p10",
        "name": "Samsung Galaxy Watch 6",
        "category": "fitness",
        "brand": "Samsung",
        "price": 1199.0,
        "description": "Smartwatch cu monitorizare sănătate și notificări.",
        "image_url": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3",
        "specs": {"health": "ECG/SpO2", "water": "5ATM"},
        "stock": 18,
        "supplier": "Samsung Store",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["smartwatch", "health", "android"],
    },
    {
        "id": "p11",
        "name": "iPad 10th Gen",
        "category": "tablets",
        "brand": "Apple",
        "price": 2499.0,
        "description": "Tablet versatil pentru studiu, media și productivitate.",
        "image_url": "https://images.unsplash.com/photo-1542751110-97427bbecf23",
        "specs": {"display": "10.9\"", "storage": "64GB", "chip": "A14 Bionic"},
        "stock": 6,
        "supplier": "Apple Partner",
        "delivery_method": "Curier",
        "is_active": True,
        "tags": ["tablet", "study", "media"],
    },
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


__all__ = [
    "USER_FAVORITES",
    "ORDERS",
    "HARDCODED_USERS",
    "HARDCODED_PRODUCTS",
    "refresh_product_status",
    "ensure_product_tags",
]