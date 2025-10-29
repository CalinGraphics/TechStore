from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (optional)
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = None
db = None
if mongo_url and db_name:
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
    except Exception:
        # Proceed without DB if connection cannot be established
        client = None
        db = None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class UserProfile(BaseModel):
    age_group: str  # "18-25", "26-35", "36-50", "50+"
    interests: List[str]  # ["laptops", "smartphones", "gaming", "photography", "fitness"]
    budget_range: str  # "low", "medium", "high"
    preferred_brands: List[str]  # ["Apple", "Samsung", "Dell", "HP", etc.]

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    profile: UserProfile

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: str
    username: str
    profile: UserProfile

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

class Recommendation(BaseModel):
    products: List[Product]
    reason: str


# Hardcoded users
HARDCODED_USERS = [
    {
        "id": "user-1",
        "username": "john_tech",
        "password": "pass123",
        "profile": {
            "age_group": "26-35",
            "interests": ["laptops", "gaming", "photography"],
            "budget_range": "high",
            "preferred_brands": ["Apple", "Dell", "Asus"]
        }
    },
    {
        "id": "user-2",
        "username": "maria_smart",
        "password": "pass123",
        "profile": {
            "age_group": "18-25",
            "interests": ["smartphones", "fitness", "photography"],
            "budget_range": "medium",
            "preferred_brands": ["Samsung", "Google", "Apple"]
        }
    },
    {
        "id": "user-3",
        "username": "alex_gamer",
        "password": "pass123",
        "profile": {
            "age_group": "18-25",
            "interests": ["gaming", "laptops", "audio"],
            "budget_range": "high",
            "preferred_brands": ["Asus", "Razer", "Sony"]
        }
    }
]

# Hardcoded products
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
        }
    },
    {
        "id": "prod-2",
        "name": "iPhone 15 Pro Max",
        "category": "smartphones",
        "brand": "Apple",
        "price": 1299.99,
        "description": "Ultimul flagship iPhone cu cameră titanium și A17 Pro chip",
        "image_url": "https://images.unsplash.com/photo-1592286927505-b0d6e7f6e5b3?w=500",
        "specs": {
            "processor": "A17 Pro",
            "camera": "48MP Main + 12MP Ultra Wide",
            "storage": "256GB",
            "display": "6.7 inch Super Retina XDR"
        }
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
        }
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
        }
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
        }
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
        }
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
        }
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
        }
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
        }
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
        }
    }
]


# Recommendation algorithm
def calculate_recommendation_score(product: dict, user_profile: UserProfile) -> float:
    score = 0.0
    
    # Interest match (40% weight)
    if product["category"] in user_profile.interests:
        score += 40
    
    # Brand preference (30% weight)
    if product["brand"] in user_profile.preferred_brands:
        score += 30
    
    # Budget match (30% weight)
    price = product["price"]
    if user_profile.budget_range == "low" and price < 500:
        score += 30
    elif user_profile.budget_range == "medium" and 500 <= price <= 1200:
        score += 30
    elif user_profile.budget_range == "high" and price > 1200:
        score += 30
    elif user_profile.budget_range == "medium" and price < 500:
        score += 20  # Still affordable
    
    return score


# API Routes
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Find user
    user_data = next((u for u in HARDCODED_USERS if u["username"] == request.username and u["password"] == request.password), None)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return LoginResponse(
        user_id=user_data["id"],
        username=user_data["username"],
        profile=UserProfile(**user_data["profile"])
    )


@api_router.get("/products", response_model=List[Product])
async def get_products():
    return [Product(**p) for p in HARDCODED_PRODUCTS]


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product_data = next((p for p in HARDCODED_PRODUCTS if p["id"] == product_id), None)
    
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(**product_data)


@api_router.get("/recommendations/{user_id}", response_model=Recommendation)
async def get_recommendations(user_id: str):
    # Find user
    user_data = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = UserProfile(**user_data["profile"])
    
    # Calculate scores for all products
    scored_products = []
    for product in HARDCODED_PRODUCTS:
        score = calculate_recommendation_score(product, user_profile)
        if score > 0:  # Only include products with some relevance
            scored_products.append((score, product))
    
    # Sort by score and get top 3
    scored_products.sort(key=lambda x: x[0], reverse=True)
    top_products = [Product(**p[1]) for p in scored_products[:3]]
    
    # Generate reason
    interests_str = ", ".join(user_profile.interests)
    brands_str = ", ".join(user_profile.preferred_brands)
    reason = f"Recomandate pe baza intereselor tale ({interests_str}), preferințelor pentru branduri ({brands_str}) și bugetului ({user_profile.budget_range})"
    
    return Recommendation(products=top_products, reason=reason)


@api_router.get("/")
async def root():
    return {"message": "Electronics Store API"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()