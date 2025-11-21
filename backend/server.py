from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Union
import uuid


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = None
db = None
if mongo_url and db_name:
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
    except Exception:
        client = None
        db = None

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


def get_products_list():
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
    products = get_products_list()
    product_index = next((i for i, p in enumerate(products) if p["id"] == product_id), None)
    
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_product = products[product_index]
    update_data = product_update.model_dump(exclude_unset=True)
    existing_product.update(update_data)
    refresh_product_status(existing_product)
    ensure_product_tags(existing_product)
    
    return Product(**existing_product)


@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, admin: dict = Depends(verify_admin)):
    products = get_products_list()
    product_index = next((i for i, p in enumerate(products) if p["id"] == product_id), None)
    
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    products.pop(product_index)
    return {"message": "Product deleted successfully"}


@api_router.get("/categories", response_model=List[str])
async def get_categories(active_only: bool = True):
    products = get_products_list()
    if active_only:
        products = [p for p in products if p.get("is_active", True) and p.get("stock", 0) > 0]
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
async def process_transaction(request: TransactionRequest):
    products = get_products_list()
    updated_products: List[Product] = []

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

    return {
        "message": "Transaction processed",
        "updated_products": updated_products,
    }


@api_router.get("/recommendations/{user_id}", response_model=Recommendation)
async def get_recommendations(user_id: str):
    user_data = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = UserProfile(**user_data["profile"])
    
    products = get_products_list()
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
    return {
        "mongo_connected": db is not None,
        "users": safe_users,
        "products": HARDCODED_PRODUCTS,
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