from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Union
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Supabase connection
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
supabase: Optional[Client] = None

logger = logging.getLogger(__name__)

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Connected to Supabase")
    except Exception as e:
        logger.warning(f"Failed to connect to Supabase: {e}")
        supabase = None
else:
    logger.warning("Supabase credentials not found, using in-memory storage")
    supabase = None

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello World!"}


api_router = APIRouter(prefix="/api")


class UserProfile(BaseModel):
    age_group: str
    interests: List[str]
    budget_range: str
    preferred_brands: List[str]

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    role: str = "user"
    profile: UserProfile

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: str
    username: str
    role: str
    profile: UserProfile

class RegisterRequest(BaseModel):
    username: str
    password: str
    age_group: str
    budget_range: str
    interests: List[str]
    preferred_brands: List[str] = []
    role: Optional[str] = None

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    brand: str
    price: float
    description: str
    image_url: str
    specs: dict
    stock: int = 0
    supplier: str = ""
    delivery_method: str = ""
    is_active: bool = True
    tags: Optional[List[str]] = None

class ProductMatch(BaseModel):
    product: Product
    score: float
    breakdown: Dict[str, Dict[str, Union[str, bool, float]]]
    match_reasons: List[str]


class Recommendation(BaseModel):
    products: List[Product]
    reason: str
    product_matches: Optional[List[ProductMatch]] = None
    user_profile: UserProfile

class ProductCreate(BaseModel):
    name: str
    category: str
    brand: str
    price: float
    description: str
    image_url: str
    specs: dict
    stock: int = 0
    supplier: str = ""
    delivery_method: str = ""
    is_active: bool = True
    tags: Optional[List[str]] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    specs: Optional[dict] = None
    stock: Optional[int] = None
    supplier: Optional[str] = None
    delivery_method: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None


class ProfileUpdate(BaseModel):
    age_group: str
    budget_range: str
    interests: List[str]
    preferred_brands: List[str]
    username: Optional[str] = None


class TransactionItem(BaseModel):
    product_id: str
    quantity: int


class TransactionRequest(BaseModel):
    items: List[TransactionItem]
    shipping_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    payment_method: Optional[str] = None
    full_name: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None


class ShippingInfo(BaseModel):
    full_name: str
    address: str
    city: str
    postal_code: str
    country: str
    phone: str
    email: str


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[OrderItem]
    total_amount: float
    shipping_info: Optional[ShippingInfo] = None
    status: str = "pending"  # pending, confirmed, shipped, delivered, cancelled
    created_at: str
    updated_at: str


# In-memory storage (fallback if Supabase not available)
USER_FAVORITES: Dict[str, List[str]] = {}  # user_id -> list of product_ids
ORDERS: List[dict] = []  # List of orders

# Database helper functions
async def get_products_from_db(active_only: bool = True, category: Optional[str] = None) -> List[dict]:
    """Get products from Supabase or fallback to hardcoded"""
    if supabase:
        try:
            query = supabase.table("products").select("*")
            if active_only:
                query = query.eq("is_active", True).gt("stock", 0)
            if category:
                query = query.eq("category", category)
            response = query.execute()
            return [dict(row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching products from DB: {e}")
            return HARDCODED_PRODUCTS
    return HARDCODED_PRODUCTS

async def get_product_by_id_from_db(product_id: str) -> Optional[dict]:
    """Get a single product by ID from Supabase or fallback"""
    if supabase:
        try:
            response = supabase.table("products").select("*").eq("id", product_id).execute()
            if response.data:
                return dict(response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error fetching product from DB: {e}")
            # Fallback to hardcoded
            return next((p for p in HARDCODED_PRODUCTS if p["id"] == product_id), None)
    return next((p for p in HARDCODED_PRODUCTS if p["id"] == product_id), None)

async def create_product_in_db(product_data: dict) -> dict:
    """Create a product in Supabase"""
    if supabase:
        try:
            response = supabase.table("products").insert(product_data).execute()
            return dict(response.data[0])
        except Exception as e:
            logger.error(f"Error creating product in DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")
    # Fallback: add to hardcoded list
    HARDCODED_PRODUCTS.append(product_data)
    return product_data

async def update_product_in_db(product_id: str, product_data: dict) -> dict:
    """Update a product in Supabase"""
    if supabase:
        try:
            response = supabase.table("products").update(product_data).eq("id", product_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Product not found")
            return dict(response.data[0])
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating product in DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")
    # Fallback: update in hardcoded list
    product_index = next((i for i, p in enumerate(HARDCODED_PRODUCTS) if p["id"] == product_id), None)
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    HARDCODED_PRODUCTS[product_index].update(product_data)
    return HARDCODED_PRODUCTS[product_index]

async def delete_product_from_db(product_id: str) -> None:
    """Delete a product from Supabase"""
    if supabase:
        try:
            response = supabase.table("products").delete().eq("id", product_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Product not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting product from DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")
    # Fallback: remove from hardcoded list
    product_index = next((i for i, p in enumerate(HARDCODED_PRODUCTS) if p["id"] == product_id), None)
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    HARDCODED_PRODUCTS.pop(product_index)

async def get_favorites_from_db(user_id: str) -> List[str]:
    """Get favorite product IDs for a user from Supabase"""
    if supabase:
        try:
            response = supabase.table("favorites").select("product_id").eq("user_id", user_id).execute()
            return [item["product_id"] for item in response.data]
        except Exception as e:
            logger.error(f"Error fetching favorites from DB: {e}")
            return USER_FAVORITES.get(user_id, [])
    return USER_FAVORITES.get(user_id, [])

async def add_favorite_to_db(user_id: str, product_id: str) -> None:
    """Add a favorite to Supabase"""
    if supabase:
        try:
            logger.info(f"Adding favorite: user={user_id}, product={product_id}")
            response = supabase.table("favorites").insert({"user_id": user_id, "product_id": product_id}).execute()
            logger.info(f"Successfully added favorite: {response.data}")
        except Exception as e:
            logger.error(f"Error adding favorite to DB: {e}", exc_info=True)
            # Check if it's a duplicate error - ignore duplicates
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                logger.info("Favorite already exists, ignoring")
                return
            raise HTTPException(status_code=500, detail=f"Error adding favorite: {str(e)}")
    else:
        # Fallback
        logger.warning("Supabase not available, using fallback storage for favorites")
        if user_id not in USER_FAVORITES:
            USER_FAVORITES[user_id] = []
        if product_id not in USER_FAVORITES[user_id]:
            USER_FAVORITES[user_id].append(product_id)

async def remove_favorite_from_db(user_id: str, product_id: str) -> None:
    """Remove a favorite from Supabase"""
    if supabase:
        try:
            response = supabase.table("favorites").delete().eq("user_id", user_id).eq("product_id", product_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Favorite not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing favorite from DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error removing favorite: {str(e)}")
    else:
        # Fallback
        if user_id in USER_FAVORITES and product_id in USER_FAVORITES[user_id]:
            USER_FAVORITES[user_id].remove(product_id)

async def create_order_in_db(order_data: dict) -> dict:
    """Create an order in Supabase"""
    if supabase:
        try:
            # Insert order
            order_items = order_data.pop("items", [])
            response = supabase.table("orders").insert(order_data).execute()
            created_order = dict(response.data[0])
            order_id = created_order["id"]
            
            # Insert order items
            if order_items:
                items_to_insert = [
                    {
                        "order_id": order_id,
                        "product_id": item["product_id"],
                        "product_name": item["product_name"],
                        "quantity": item["quantity"],
                        "price": item["price"]
                    }
                    for item in order_items
                ]
                supabase.table("order_items").insert(items_to_insert).execute()
                created_order["items"] = order_items
            
            return created_order
        except Exception as e:
            logger.error(f"Error creating order in DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")
    # Fallback
    ORDERS.append(order_data)
    return order_data

async def get_orders_from_db(user_id: str) -> List[dict]:
    """Get orders for a user from Supabase"""
    if supabase:
        try:
            response = supabase.table("orders").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            orders = [dict(order) for order in response.data]
            
            # Fetch order items for each order
            for order in orders:
                items_response = supabase.table("order_items").select("*").eq("order_id", order["id"]).execute()
                order["items"] = [dict(item) for item in items_response.data]
            
            return orders
        except Exception as e:
            logger.error(f"Error fetching orders from DB: {e}")
            return [o for o in ORDERS if o.get("user_id") == user_id]
    return [o for o in ORDERS if o.get("user_id") == user_id]

async def get_order_by_id_from_db(user_id: str, order_id: str) -> Optional[dict]:
    """Get a single order by ID from Supabase"""
    if supabase:
        try:
            response = supabase.table("orders").select("*").eq("id", order_id).eq("user_id", user_id).execute()
            if not response.data:
                return None
            order = dict(response.data[0])
            
            # Fetch order items
            items_response = supabase.table("order_items").select("*").eq("order_id", order_id).execute()
            order["items"] = [dict(item) for item in items_response.data]
            
            return order
        except Exception as e:
            logger.error(f"Error fetching order from DB: {e}")
            return next((o for o in ORDERS if o.get("id") == order_id and o.get("user_id") == user_id), None)
    return next((o for o in ORDERS if o.get("id") == order_id and o.get("user_id") == user_id), None)

def get_products_list():
    """Legacy function, kept for compatibility"""
    return HARDCODED_PRODUCTS


def refresh_product_status(product: dict):
    stock = product.get("stock", 0)
    if stock <= 0:
        product["stock"] = 0
        product["is_active"] = False
    else:
        if "is_active" not in product or product["is_active"] is None:
            product["is_active"] = True

def ensure_product_tags(product: dict):
    if not product.get("tags"):
        product["tags"] = [product.get("category", "")]


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

for product in HARDCODED_PRODUCTS:
    refresh_product_status(product)
    ensure_product_tags(product)


def get_budget_bucket(price: float) -> str:
    if price < 500:
        return "low"
    if price <= 1200:
        return "medium"
    return "high"


BUDGET_ORDER = {"low": 0, "medium": 1, "high": 2}


def is_budget_compatible(user_budget: str, price: float) -> bool:
    product_bucket = get_budget_bucket(price)
    if user_budget == "low":
        return product_bucket == "low"
    if user_budget == "medium":
        return product_bucket in {"low", "medium"}
    if user_budget == "high":
        return product_bucket in {"low", "medium", "high"}
    return False


def evaluate_product_match(product: dict, user_profile: UserProfile) -> tuple[float, Dict[str, Dict[str, Union[str, bool, float]]], List[str]]:
    score = 0.0
    match_reasons: List[str] = []
    breakdown: Dict[str, Dict[str, Union[str, bool, float]]] = {}

    interest_match = product["category"] in user_profile.interests
    if interest_match:
        score += 40
        match_reasons.append(f"Categoria {product['category']} se află în interesele tale.")
    breakdown["interest"] = {
        "match": interest_match,
        "label": f"Interes: {product['category']}",
        "detail": "Se potrivește cu interesele tale" if interest_match else "Nu este în interesele declarate",
    }

    brand_match = product["brand"] in user_profile.preferred_brands
    if brand_match:
        score += 30
        match_reasons.append(f"Brandul {product['brand']} este în lista ta de preferințe.")
    breakdown["brand"] = {
        "match": brand_match,
        "label": f"Brand: {product['brand']}",
        "detail": "Este un brand preferat" if brand_match else "Nu este în lista de branduri preferate",
    }

    price = product["price"]
    budget_bucket = get_budget_bucket(price)
    budget_score = 0.0
    budget_match = False

    if user_profile.budget_range == "low" and budget_bucket == "low":
        budget_score = 30
        budget_match = True
    elif user_profile.budget_range == "medium":
        if budget_bucket == "medium":
            budget_score = 30
            budget_match = True
        elif budget_bucket == "low":
            budget_score = 20
    elif user_profile.budget_range == "high" and budget_bucket == "high":
        budget_score = 30
        budget_match = True

    if budget_score > 0:
        score += budget_score
        if budget_match:
            match_reasons.append(f"Prețul de {price:.2f} RON se potrivește cu bugetul tău ({user_profile.budget_range}).")
        else:
            match_reasons.append(f"Prețul de {price:.2f} RON este sub bugetul tău și oferă economie.")

    breakdown["budget"] = {
        "match": is_budget_compatible(user_profile.budget_range, price),
        "label": f"Buget: {user_profile.budget_range}",
        "detail": f"Produsul este în zona {budget_bucket} ({price:.2f} RON)",
        "awarded_points": budget_score,
    }

    return score, breakdown, match_reasons


async def verify_admin(user_id: str = Header(..., alias="X-User-Id"), user_role: str = Header(..., alias="X-User-Role")):
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"user_id": user_id, "role": user_role}

# API Routes
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user_data = next((u for u in HARDCODED_USERS if u["username"] == request.username and u["password"] == request.password), None)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return LoginResponse(
        user_id=user_data["id"],
        username=user_data["username"],
        role=user_data.get("role", "user"),
        profile=UserProfile(**user_data["profile"])
    )

def normalize_list(values: List[str]) -> List[str]:
    normalized: List[str] = []
    for value in values:
        cleaned = value.strip().lower()
        if cleaned:
            normalized.append(cleaned)
    return normalized

@api_router.post("/auth/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username invalid")
    if any(u["username"].lower() == username.lower() for u in HARDCODED_USERS):
        raise HTTPException(status_code=400, detail="Username already taken")
    interests = normalize_list(request.interests)
    if not interests:
        raise HTTPException(status_code=400, detail="Selectează cel puțin un interes")
    preferred_brands = [value.strip() for value in request.preferred_brands if value.strip()]
    new_user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": request.password,
        "role": request.role if request.role in {"admin", "user"} else "user",
        "profile": {
            "age_group": request.age_group,
            "budget_range": request.budget_range,
            "interests": interests,
            "preferred_brands": preferred_brands,
        },
    }
    HARDCODED_USERS.append(new_user)
    return LoginResponse(
        user_id=new_user["id"],
        username=new_user["username"],
        role=new_user["role"],
        profile=UserProfile(**new_user["profile"]),
    )


@api_router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    active_only: bool = True,
):
    products = get_products_list()
    if category:
        products = [p for p in products if p.get("category") == category]
    if active_only:
        products = [p for p in products if p.get("is_active", True) and p.get("stock", 0) > 0]
    normalized = []
    for product in products:
        ensure_product_tags(product)
        normalized.append(Product(**product))
    return normalized


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    products = get_products_list()
    product_data = next((p for p in products if p["id"] == product_id), None)
    
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    ensure_product_tags(product_data)
    return Product(**product_data)


@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate, admin: dict = Depends(verify_admin)):
    products = get_products_list()
    new_product = {
        "id": str(uuid.uuid4()),
        "name": product.name,
        "category": product.category,
        "brand": product.brand,
        "price": product.price,
        "description": product.description,
        "image_url": product.image_url,
        "specs": product.specs,
        "stock": product.stock,
        "supplier": product.supplier,
        "delivery_method": product.delivery_method,
        "tags": product.tags or [product.category]
    }
    new_product["is_active"] = product.is_active if product.stock > 0 else False
    refresh_product_status(new_product)
    ensure_product_tags(new_product)
    products.append(new_product)
    return Product(**new_product)


@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate, admin: dict = Depends(verify_admin)):
    existing_product = await get_product_by_id_from_db(product_id)
    
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.model_dump(exclude_unset=True)
    if "price" in update_data:
        update_data["price"] = float(update_data["price"])
    existing_product.update(update_data)
    refresh_product_status(existing_product)
    ensure_product_tags(existing_product)
    
    updated_product = await update_product_in_db(product_id, existing_product)
    return Product(**updated_product)


@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, admin: dict = Depends(verify_admin)):
    await delete_product_from_db(product_id)
    return {"message": "Product deleted successfully"}


@api_router.get("/categories", response_model=List[str])
async def get_categories(active_only: bool = True):
    products = await get_products_from_db(active_only=active_only)
    categories = list(set(p.get("category", "") for p in products if p.get("category")))
    return sorted(categories)


@api_router.put("/profile/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, profile_update: ProfileUpdate):
    user = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    desired_username = profile_update.username
    if desired_username is not None:
        normalized_username = desired_username.strip()
        if not normalized_username:
            raise HTTPException(status_code=400, detail="Username invalid")
        if normalized_username.lower() != user["username"].lower():
            if any(u["username"].lower() == normalized_username.lower() for u in HARDCODED_USERS):
                raise HTTPException(status_code=400, detail="Username already taken")
            user["username"] = normalized_username

    user_profile = user.get("profile", {})
    user_profile.update({
        "age_group": profile_update.age_group,
        "budget_range": profile_update.budget_range,
        "interests": profile_update.interests,
        "preferred_brands": profile_update.preferred_brands,
    })
    user["profile"] = user_profile

    return UserProfile(**user_profile)


@api_router.post("/transactions")
async def process_transaction(request: TransactionRequest, user_id: str = Header(..., alias="X-User-Id")):
    products = get_products_list()
    updated_products: List[Product] = []
    order_items: List[OrderItem] = []
    total_amount = 0.0

    for item in request.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if item.quantity <= 0:
            continue
        if product.get("stock", 0) < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficient pentru {product['name']}"
            )
        product["stock"] -= item.quantity
        refresh_product_status(product)
        ensure_product_tags(product)
        updated_products.append(Product(**product))
        
        item_price = product["price"] * item.quantity
        total_amount += item_price
        order_items.append(OrderItem(
            product_id=item.product_id,
            product_name=product["name"],
            quantity=item.quantity,
            price=product["price"]
        ))

    # Create order
    now = datetime.now().isoformat()
    shipping_info = None
    if request.shipping_address or request.phone or request.email:
        shipping_info = {
            "full_name": request.full_name or "",
            "address": request.shipping_address or "",
            "city": request.city or "",
            "postal_code": request.postal_code or "",
            "country": "Romania",
            "phone": request.phone or "",
            "email": request.email or ""
        }
    
    order_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "items": [item.model_dump() for item in order_items],
        "total_amount": total_amount,
        "shipping_info": shipping_info,
        "status": "confirmed",
        "created_at": now,
        "updated_at": now
    }
    ORDERS.append(order_data)

    return {
        "message": "Transaction processed",
        "order_id": order_data["id"],
        "updated_products": updated_products,
    }


@api_router.get("/favorites/{user_id}", response_model=List[Product])
async def get_favorites(user_id: str):
    favorites = USER_FAVORITES.get(user_id, [])
    products = get_products_list()
    favorite_products = [p for p in products if p["id"] in favorites]
    return [Product(**p) for p in favorite_products]


@api_router.post("/favorites/{user_id}/{product_id}")
async def add_to_favorites(user_id: str, product_id: str):
    products = get_products_list()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if user_id not in USER_FAVORITES:
        USER_FAVORITES[user_id] = []
    
    if product_id not in USER_FAVORITES[user_id]:
        USER_FAVORITES[user_id].append(product_id)
    
    return {"message": "Product added to favorites", "product_id": product_id}


@api_router.delete("/favorites/{user_id}/{product_id}")
async def remove_from_favorites(user_id: str, product_id: str):
    if user_id not in USER_FAVORITES:
        raise HTTPException(status_code=404, detail="User favorites not found")
    
    if product_id not in USER_FAVORITES[user_id]:
        raise HTTPException(status_code=404, detail="Product not in favorites")
    
    USER_FAVORITES[user_id].remove(product_id)
    return {"message": "Product removed from favorites", "product_id": product_id}


@api_router.get("/orders/{user_id}", response_model=List[Order])
async def get_user_orders(user_id: str):
    user_orders = await get_orders_from_db(user_id)
    # Convert to Order model format
    formatted_orders = []
    for order in user_orders:
        shipping_info = None
        if order.get("shipping_full_name") or order.get("shipping_address"):
            shipping_info = {
                "full_name": order.get("shipping_full_name", ""),
                "address": order.get("shipping_address", ""),
                "city": order.get("shipping_city", ""),
                "postal_code": order.get("shipping_postal_code", ""),
                "country": order.get("shipping_country", "Romania"),
                "phone": order.get("shipping_phone", ""),
                "email": order.get("shipping_email", "")
            }
        formatted_orders.append({
            "id": order["id"],
            "user_id": order["user_id"],
            "items": order.get("items", []),
            "total_amount": float(order["total_amount"]),
            "shipping_info": shipping_info,
            "status": order["status"],
            "created_at": order["created_at"],
            "updated_at": order.get("updated_at", order["created_at"])
        })
    return formatted_orders


@api_router.get("/orders/{user_id}/{order_id}", response_model=Order)
async def get_order(user_id: str, order_id: str):
    order = await get_order_by_id_from_db(user_id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    shipping_info = None
    if order.get("shipping_full_name") or order.get("shipping_address"):
        shipping_info = {
            "full_name": order.get("shipping_full_name", ""),
            "address": order.get("shipping_address", ""),
            "city": order.get("shipping_city", ""),
            "postal_code": order.get("shipping_postal_code", ""),
            "country": order.get("shipping_country", "Romania"),
            "phone": order.get("shipping_phone", ""),
            "email": order.get("shipping_email", "")
        }
    
    return {
        "id": order["id"],
        "user_id": order["user_id"],
        "items": order.get("items", []),
        "total_amount": float(order["total_amount"]),
        "shipping_info": shipping_info,
        "status": order["status"],
        "created_at": order["created_at"],
        "updated_at": order.get("updated_at", order["created_at"])
    }


@api_router.get("/recommendations/{user_id}", response_model=Recommendation)
async def get_recommendations(user_id: str):
    user_data = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = UserProfile(**user_data["profile"])
    
    products = await get_products_from_db(active_only=True)
    product_matches: List[ProductMatch] = []
    for product in products:
        if not product.get("is_active", True) or product.get("stock", 0) <= 0:
            continue
        ensure_product_tags(product)
        if product.get("category") not in user_profile.interests:
            continue
        if not is_budget_compatible(user_profile.budget_range, product.get("price", 0)):
            continue
        score, breakdown, match_reasons = evaluate_product_match(product, user_profile)
        if score <= 0:
            continue
        product_matches.append(
            ProductMatch(
                product=Product(**product),
                score=score,
                breakdown=breakdown,
                match_reasons=match_reasons
            )
        )
    
    product_matches.sort(key=lambda pm: pm.score, reverse=True)
    top_products = [match.product for match in product_matches]
    
    interests_str = ", ".join(user_profile.interests)
    brands_str = ", ".join(user_profile.preferred_brands)
    reason = f"Recomandate pe baza intereselor tale ({interests_str}), preferințelor pentru branduri ({brands_str}) și bugetului ({user_profile.budget_range})"
    
    return Recommendation(
        products=top_products,
        reason=reason,
        product_matches=product_matches,
        user_profile=user_profile
    )


@api_router.get("/debug/db")
async def debug_db():
    safe_users = []
    for u in HARDCODED_USERS:
        safe_user = {**u}
        if "password" in safe_user:
            safe_user["password"] = "******"
        safe_users.append(safe_user)
    
    supabase_status = "connected" if supabase else "not connected"
    if supabase_url and supabase_key:
        env_status = "configured"
    else:
        env_status = "not configured"
    
    return {
        "supabase_status": supabase_status,
        "supabase_env": env_status,
        "supabase_url_set": bool(supabase_url),
        "supabase_key_set": bool(supabase_key),
        "users": safe_users,
        "products_count": len(HARDCODED_PRODUCTS),
    }

@api_router.get("/")
async def root():
    return {"message": "Electronics Store API"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()