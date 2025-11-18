from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB (opțional)
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = None
db = None
if mongo_url and db_name:
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
    except Exception:
        # Continuă fără DB dacă conexiunea nu poate fi stabilită
        client = None
        db = None

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World!"}

api_router = APIRouter(prefix="/api")

class UserProfile(BaseModel):
    age_group: str  # "18-25", "26-35", "36-50", "50+"
    interests: Dict[str, int]  # {"photo": 4, "gaming": 5, "laptops": 3, etc.}
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
    labels: Dict[str, int] = Field(default_factory=dict)  # {"photos": 2, "gaming": 3, etc.}
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class Recommendation(BaseModel):
    products: List[Product]
    reason: str


# Hardcoded users
HARDCODED_USERS = [
    {
        "id": "user-1",
        "username": "Elvis_Marcu",
        "password": "pass123",
        "profile": {
            "age_group": "26-35",
            "interests": {"laptops": 5, "gaming": 4, "photo": 4, "photography": 3},
            "budget_range": "high",
            "preferred_brands": ["Apple", "Dell", "Asus"]
        }
    },
    {
        "id": "user-2",
        "username": "robert_escrocul",
        "password": "pass123",
        "profile": {
            "age_group": "18-25",
            "interests": {"smartphones": 5, "fitness": 4, "photo": 4, "photography": 3},
            "budget_range": "medium",
            "preferred_brands": ["Samsung", "Google", "Apple"]
        }
    },
    {
        "id": "user-3",
        "username": "carastefania31",
        "password": "pass123",
        "profile": {
            "age_group": "18-25",
            "interests": {"gaming": 2, "laptops": 4, "audio": 4},
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
        },
        "labels": {"laptops": 5, "photo": 3, "photography": 2}
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
        "labels": {"smartphones": 5, "photo": 4, "photography": 3}
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
        "labels": {"smartphones": 5, "photo": 5, "photography": 4}
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
        "labels": {"laptops": 5, "photo": 4, "photography": 3}
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
        "labels": {"gaming": 5, "laptops": 4}
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
        "labels": {"audio": 5}
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
        "labels": {"fitness": 5}
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
        "labels": {"smartphones": 5, "photo": 5, "photography": 4}
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
        "labels": {"photo": 3, "photography": 2}
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
        "labels": {"fitness": 5},
        "created_at": datetime(2024, 1, 15, tzinfo=timezone.utc)
    },
    {
        "id": "prod-11",
        "name": "Razer Blade 18 Gaming Laptop",
        "category": "gaming",
        "brand": "Razer",
        "price": 2999.99,
        "description": "Laptop gaming premium cu RTX 4090 și display 18 inch",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500",
        "specs": {
            "processor": "Intel Core i9-13950HX",
            "gpu": "NVIDIA RTX 4090",
            "ram": "64GB DDR5",
            "storage": "2TB SSD",
            "display": "18 inch QHD 240Hz"
        },
        "labels": {"gaming": 5, "laptops": 4, "audio": 3},
        "created_at": datetime.now(timezone.utc) - timedelta(days=5)
    },
    {
        "id": "prod-12",
        "name": "Sony Alpha A7R V Camera",
        "category": "photography",
        "brand": "Sony",
        "price": 3999.99,
        "description": "Cameră mirrorless full-frame pentru fotografie profesională",
        "image_url": "https://i.ytimg.com/vi/TqZk1zW2i1U/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLBp-iEIxyXWoDPkvVzcQDjWFbr-ZA",
        "specs": {
            "sensor": "61MP Full-Frame",
            "iso": "100-32000",
            "video": "8K 24p, 4K 60p",
            "stabilization": "5-axis IBIS"
        },
        "labels": {"photo": 5, "photography": 5},
        "created_at": datetime.now(timezone.utc) - timedelta(days=10)
    },
    {
        "id": "prod-13",
        "name": "Asus ROG Phone 8 Pro",
        "category": "gaming",
        "brand": "Asus",
        "price": 1299.99,
        "description": "Smartphone gaming cu procesor overclocked și cooling activ",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
        "specs": {
            "processor": "Snapdragon 8 Gen 3",
            "ram": "24GB",
            "storage": "1TB",
            "display": "6.78 inch AMOLED 165Hz",
            "cooling": "Active cooling system"
        },
        "labels": {"gaming": 5, "smartphones": 4, "audio": 2},
        "created_at": datetime.now(timezone.utc) - timedelta(days=3)
    }
]

def _covers_all_interests(product: dict, user_profile: UserProfile) -> bool:
    """
    Verifică dacă un produs acoperă TOATE interesele utilizatorului.
    Un produs acoperă un interes dacă are un label care se potrivește (exact sau similar).
    """
    if not user_profile.interests:
        return False
    
    product_labels = product.get("labels", {})
    if not product_labels:
        return False
    
    # Normalizează label-urile produsului pentru matching
    normalized_labels = {}
    for label_key in product_labels.keys():
        normalized_key = label_key.lower().rstrip('s')
        normalized_labels[normalized_key] = label_key
    
    # Verifică dacă toate interesele utilizatorului sunt acoperite
    for interest_key in user_profile.interests.keys():
        interest_normalized = interest_key.lower().rstrip('s')
        
        # Verifică potrivire exactă
        if interest_key in product_labels:
            continue
        
        # Verifică potrivire normalizată
        if interest_normalized in normalized_labels:
            continue
        return False
    
    return True


def calculate_recommendation_score(product: dict, user_profile: UserProfile) -> float:
    """
    Calculează scorul de recomandare pentru un produs bazat pe profilul utilizatorului.
    Returnează un scor mai mare pentru produse care match-uiesc toate interesele, 
    apoi pentru cele care match-uiesc mai multe interese, și mai mic pentru cele cu match-uri parțiale.
    """
    score = 0.0
    
    # Potrivire Labels-Interese: pentru fiecare label care se potrivește, înmulțește valoarea interesului cu valoarea label-ului
    product_labels = product.get("labels", {})
    labels_score = 0.0
    max_labels_score = 0.0
    matched_interests_count = 0
    
    for interest_key, interest_value in user_profile.interests.items():
        # Verifică potrivire exactă
        if interest_key in product_labels:
            match_score = interest_value * product_labels[interest_key]
            labels_score += match_score
            max_labels_score += interest_value * 5  # Maxim posibil (presupunând că valoarea maximă a label-ului este 5)
            matched_interests_count += 1
        
        # Verifică și potriviri similare (ex: "photo" se potrivește cu "photos", "photography")
        # Normalizează cheile pentru o potrivire mai bună
        interest_normalized = interest_key.lower().rstrip('s')
        for label_key, label_value in product_labels.items():
            label_normalized = label_key.lower().rstrip('s')
            if interest_normalized == label_normalized and interest_key != label_key:
                # Potrivire parțială cu greutate redusă
                match_score = interest_value * label_value * 0.8
                labels_score += match_score
                matched_interests_count += 1
                break
    
    # Normalizează scorul label-urilor la intervalul 0-50 (50% din greutate)
    if max_labels_score > 0:
        normalized_labels_score = (labels_score / max_labels_score) * 50
    else:
        normalized_labels_score = 0
    score += normalized_labels_score
    
    # BONUS: Dacă produsul acoperă TOATE interesele utilizatorului, adaugă bonus semnificativ
    if _covers_all_interests(product, user_profile):
        score += 25
    elif matched_interests_count > 0:
        # Bonus progresiv pentru produse care match-uiesc mai multe interese
        total_interests = len(user_profile.interests)
        if total_interests > 0:
            match_ratio = matched_interests_count / total_interests
            score += match_ratio * 15
    
    # Preferință brand (30% din greutate)
    if product["brand"] in user_profile.preferred_brands:
        score += 30
    
    # Potrivire buget (20% din greutate)
    price = product["price"]
    if user_profile.budget_range == "low" and price < 500:
        score += 20
    elif user_profile.budget_range == "medium" and 500 <= price <= 1200:
        score += 20
    elif user_profile.budget_range == "high" and price > 1200:
        score += 20
    elif user_profile.budget_range == "medium" and price < 500:
        score += 15  
    return score


def calculate_similarity_score(product: dict, reference_product: dict) -> float:
    """
    Calculează scorul de similaritate între două produse.
    Produsele sunt similare dacă au:
    - Aceeași categorie
    - Brand-uri similare sau aceleași
    - Labels similare (interese comune)
    - Preț similar (în același range)
    """
    score = 0.0
    
    # Potrivire categorie (40% din greutate)
    if product.get("category") == reference_product.get("category"):
        score += 40
    
    # Potrivire brand (25% din greutate)
    if product.get("brand") == reference_product.get("brand"):
        score += 25
    
    # Similaritate labels (30% din greutate)
    product_labels = set(product.get("labels", {}).keys())
    ref_labels = set(reference_product.get("labels", {}).keys())
    
    if ref_labels:
        # Normalizează label-urile pentru o potrivire mai bună
        product_labels_norm = {label.lower().rstrip('s') for label in product_labels}
        ref_labels_norm = {label.lower().rstrip('s') for label in ref_labels}
        
        common_labels = product_labels_norm.intersection(ref_labels_norm)
        if common_labels:
            similarity_ratio = len(common_labels) / len(ref_labels_norm)
            score += similarity_ratio * 30
    
    # Similaritate preț (5% din greutate) - produse în același range de preț
    price_diff = abs(product.get("price", 0) - reference_product.get("price", 0))
    ref_price = reference_product.get("price", 1)
    if ref_price > 0:
        price_ratio = 1 - min(price_diff / ref_price, 1.0)
        score += price_ratio * 5
    
    return score


def get_similar_products(reference_product: dict, all_products: List[dict], limit: int = 5) -> List[dict]:
    """
    Găsește produse similare cu un produs de referință.
    Exclude produsul de referință din rezultate.
    """
    similar_products = []
    
    for product in all_products:
        # Sare peste produsul de referință
        if product.get("id") == reference_product.get("id"):
            continue
        
        similarity = calculate_similarity_score(product, reference_product)
        if similarity > 0:
            similar_products.append((similarity, product))
    
    # Sortează după scorul de similaritate descrescător
    similar_products.sort(key=lambda x: x[0], reverse=True)
    
    return [p[1] for p in similar_products[:limit]]


def _matches_user_interests(product: dict, user_profile: UserProfile) -> bool:
    """
    Verifică dacă un produs se potrivește cu cel puțin unul dintre interesele utilizatorului.
    """
    product_labels = product.get("labels", {})
    if not product_labels:
        return False
    
    for interest_key in user_profile.interests.keys():
        # Check exact match
        if interest_key in product_labels:
            return True
        
        # Check normalized match
        interest_normalized = interest_key.lower().rstrip('s')
        for label_key in product_labels.keys():
            label_normalized = label_key.lower().rstrip('s')
            if interest_normalized == label_normalized:
                return True
    
    return False


def get_discovery_recommendations(user_profile: UserProfile, all_products: List[dict], limit: int = 5) -> List[tuple]:
    """
    Găsește produse care NU se potrivesc cu interesele utilizatorului direct,
    dar sunt similare cu produse care SE potrivesc cu interesele sale.
    Acestea sunt recomandări "discovery" sau "surprising" care pot deschide 
    noi interese pentru utilizator.
    
    Returns: List of tuples (similarity_score, product, reference_product_id)
    """
    # Găsește produse care se potrivesc cu interesele utilizatorului
    matching_products = []
    for product in all_products:
        if _matches_user_interests(product, user_profile):
            matching_products.append(product)
    
    if not matching_products:
        return []
    
    # Pentru fiecare produs relevant, găsește produse similare
    discovery_candidates = {}
    
    for matching_product in matching_products:
        similar_products = get_similar_products(matching_product, all_products, limit=20)
        
        for similar_product in similar_products:
            # Verifică că produsul similar NU se potrivește cu interesele utilizatorului
            if not _matches_user_interests(similar_product, user_profile):
                product_id = similar_product.get("id")
                similarity = calculate_similarity_score(similar_product, matching_product)
                
                # Păstrează cel mai bun scor de similaritate pentru fiecare produs
                if product_id not in discovery_candidates or similarity > discovery_candidates[product_id][0]:
                    discovery_candidates[product_id] = (similarity, similar_product, matching_product.get("id"))
    
    # Sortează după scorul de similaritate
    discovery_list = list(discovery_candidates.values())
    discovery_list.sort(key=lambda x: x[0], reverse=True)
    
    return discovery_list[:limit]


def _format_interest_list(interests: Dict[str, int], max_items: int = 3) -> str:
    if not interests:
        return "fără preferințe specifice"
    
    sorted_interests = sorted(interests.items(), key=lambda item: item[1], reverse=True)
    labels = [key.replace("_", " ") for key, _ in sorted_interests[:max_items]]
    
    if not labels:
        return "fără preferințe specifice"
    
    if len(labels) == 1:
        base_text = labels[0]
    elif len(labels) == 2:
        base_text = " și ".join(labels)
    else:
        base_text = ", ".join(labels[:-1]) + f" și {labels[-1]}"
    
    if len(sorted_interests) > max_items:
        return f"{base_text}, alături de alte interese"
    
    return base_text


@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user_data = next((u for u in HARDCODED_USERS if u["username"] == request.username and u["password"] == request.password), None)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return LoginResponse(
        user_id=user_data["id"],
        username=user_data["username"],
        profile=UserProfile(**user_data["profile"])
    )


def _filter_products(
    products: List[dict],
    *,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
) -> List[dict]:
    filtered = products

    if category:
        filtered = [p for p in filtered if p.get("category") == category]

    if brand:
        filtered = [p for p in filtered if p.get("brand") == brand]

    if price_min is not None:
        filtered = [p for p in filtered if float(p.get("price", 0)) >= price_min]

    if price_max is not None:
        filtered = [p for p in filtered if float(p.get("price", 0)) <= price_max]

    return filtered


@api_router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
):
    filtered = _filter_products(
        HARDCODED_PRODUCTS,
        category=category,
        brand=brand,
        price_min=price_min,
        price_max=price_max,
    )
    return [Product(**p) for p in filtered]


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product_data = next((p for p in HARDCODED_PRODUCTS if p["id"] == product_id), None)
    
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(**product_data)


@api_router.get("/products/{product_id}/similar", response_model=List[Product])
async def get_similar_products_endpoint(product_id: str, limit: int = 5):
    """
    Returnează produse similare cu un produs dat.
    Produsele sunt considerate similare dacă au aceeași categorie, brand similar,
    labels comune sau preț similar.
    """
    reference_product = next((p for p in HARDCODED_PRODUCTS if p["id"] == product_id), None)
    
    if not reference_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    similar_products = get_similar_products(reference_product, HARDCODED_PRODUCTS, limit=limit)
    
    return [Product(**p) for p in similar_products]


@api_router.get("/recommendations/{user_id}/by-interest-type", response_model=Dict[str, Recommendation])
async def get_recommendations_by_interest_type(
    user_id: str,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
):
    """
    Returnează recomandări grupate pe tipul de match:
    - "all_interests": Produse care match-uiesc toate interesele
    - "multiple_interests": Produse care match-uiesc mai multe interese
    - "single_interest": Produse care match-uiesc cel puțin un interes
    """
    user_data = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = UserProfile(**user_data["profile"])
    candidate_products = _filter_products(
        HARDCODED_PRODUCTS,
        category=category,
        brand=brand,
        price_min=price_min,
        price_max=price_max,
    )
    
    products_covering_all = []
    products_covering_multiple = []
    products_covering_one = []
    
    for product in candidate_products:
        score = calculate_recommendation_score(product, user_profile)
        if score > 0:
            covers_all = _covers_all_interests(product, user_profile)
            
            product_labels = product.get("labels", {})
            matched_count = 0
            for interest_key in user_profile.interests.keys():
                interest_normalized = interest_key.lower().rstrip('s')
                if interest_key in product_labels:
                    matched_count += 1
                else:
                    for label_key in product_labels.keys():
                        label_normalized = label_key.lower().rstrip('s')
                        if interest_normalized == label_normalized:
                            matched_count += 1
                            break
            
            if covers_all:
                products_covering_all.append((score, product))
            elif matched_count >= 2:
                products_covering_multiple.append((score, product))
            else:
                products_covering_one.append((score, product))
    
    products_covering_all.sort(key=lambda x: x[0], reverse=True)
    products_covering_multiple.sort(key=lambda x: x[0], reverse=True)
    products_covering_one.sort(key=lambda x: x[0], reverse=True)
    
    interests_str = _format_interest_list(user_profile.interests)
    
    result = {}
    
    if products_covering_all:
        result["all_interests"] = Recommendation(
            products=[Product(**p[1]) for p in products_covering_all[:5]],
            reason=f"Produse care acoperă toate interesele tale în {interests_str}"
        )
    
    if products_covering_multiple:
        result["multiple_interests"] = Recommendation(
            products=[Product(**p[1]) for p in products_covering_multiple[:5]],
            reason=f"Produse care acoperă mai multe dintre interesele tale în {interests_str}"
        )
    
    if products_covering_one:
        result["single_interest"] = Recommendation(
            products=[Product(**p[1]) for p in products_covering_one[:5]],
            reason=f"Produse care se potrivesc cu cel puțin unul dintre interesele tale în {interests_str}"
        )
    
    return result


@api_router.get("/recommendations/{user_id}/discovery", response_model=Recommendation)
async def get_discovery_recommendations_endpoint(
    user_id: str,
    limit: int = 5,
):
    """
    Returnează recomandări de produse care NU se potrivesc cu interesele directe ale utilizatorului,
    dar sunt similare cu produse care SE potrivesc cu interesele sale.
    Acestea sunt recomandări "discovery" care pot deschide noi interese pentru utilizator.
    
    Exemple:
    - Dacă utilizatorul este interesat de "gaming" și "laptops", ar putea primi recomandări 
      pentru produse de "audio" sau "tablets" care sunt similare cu produsele sale de interes.
    """
    user_data = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = UserProfile(**user_data["profile"])
    
    discovery_list = get_discovery_recommendations(user_profile, HARDCODED_PRODUCTS, limit=limit)
    
    if not discovery_list:
        return Recommendation(
            products=[],
            reason="Nu s-au găsit produse similare care să nu fie deja în lista ta de interese."
        )
    
    discovery_products = [Product(**item[1]) for item in discovery_list]
    
    interests_str = _format_interest_list(user_profile.interests)
    reason = (
        f"Aceste produse nu sunt în lista ta de interese ({interests_str}), "
        f"dar sunt similare cu produse care te interesează. "
        f"Ar putea deschide noi pasiuni pentru tine!"
    )
    
    return Recommendation(products=discovery_products, reason=reason)


@api_router.get("/recommendations/{user_id}", response_model=Recommendation)
async def get_recommendations(
    user_id: str,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
):
    """
    Returnează recomandări de produse pentru un utilizator bazate pe interesele sale.
    Algoritmul recomandă:
    1. Produse care match-uiesc TOATE interesele utilizatorului (prioritate maximă)
    2. Produse care match-uiesc mai multe interese
    3. Produse care match-uiesc cel puțin un interes
    """
    user_data = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = UserProfile(**user_data["profile"])
    
    candidate_products = _filter_products(
        HARDCODED_PRODUCTS,
        category=category,
        brand=brand,
        price_min=price_min,
        price_max=price_max,
    )

    scored_products = []
    products_covering_all = []
    products_covering_multiple = []
    products_covering_one = []
    
    for product in candidate_products:
        score = calculate_recommendation_score(product, user_profile)
        if score > 0:
            covers_all = _covers_all_interests(product, user_profile)
            
            product_labels = product.get("labels", {})
            matched_count = 0
            for interest_key in user_profile.interests.keys():
                interest_normalized = interest_key.lower().rstrip('s')
                if interest_key in product_labels:
                    matched_count += 1
                else:
                    for label_key in product_labels.keys():
                        label_normalized = label_key.lower().rstrip('s')
                        if interest_normalized == label_normalized:
                            matched_count += 1
                            break
            
            scored_products.append((score, product, covers_all, matched_count))
    
    # Sortează: 1) acoperă toate interesele, 2) scor, 3) număr de interese match-uite
    scored_products.sort(key=lambda x: (not x[2], -x[0], -x[3]), reverse=False)
    
    # Separează produsele după tipul de potrivire
    for score, product, covers_all, matched_count in scored_products:
        if covers_all:
            products_covering_all.append((score, product))
        elif matched_count >= 2:
            products_covering_multiple.append((score, product))
        else:
            products_covering_one.append((score, product))
    
    # Selectează produsele top: prioritizează produsele care acoperă toate interesele, apoi cele multiple, apoi cele cu un singur interes
    top_products = []
    if products_covering_all:
        top_products.extend([Product(**p[1]) for p in products_covering_all[:3]])
    if len(top_products) < 3 and products_covering_multiple:
        remaining = 3 - len(top_products)
        top_products.extend([Product(**p[1]) for p in products_covering_multiple[:remaining]])
    if len(top_products) < 3 and products_covering_one:
        remaining = 3 - len(top_products)
        top_products.extend([Product(**p[1]) for p in products_covering_one[:remaining]])
    
    interests_str = _format_interest_list(user_profile.interests)
    if user_profile.preferred_brands:
        brands_str = ", ".join(user_profile.preferred_brands)
        brands_phrase = f", preferințelor tale pentru brandurile {brands_str}"
    else:
        brands_phrase = ""
    criteria_parts = []
    if category:
        criteria_parts.append(f"categorie: {category}")
    if brand:
        criteria_parts.append(f"brand: {brand}")
    if price_min is not None or price_max is not None:
        rng = f"de la {price_min if price_min is not None else '—'} până la {price_max if price_max is not None else '—'} RON"
        criteria_parts.append(f"preț: {rng}")
    criteria_str = ", ".join(criteria_parts) if criteria_parts else "fără criterii suplimentare"

    match_info = ""
    if products_covering_all and top_products[0] in [Product(**p[1]) for p in products_covering_all]:
        match_info = " Produsele acoperă toate interesele tale."
    elif products_covering_multiple and any(p in [Product(**p2[1]) for p2 in products_covering_multiple] for p in top_products):
        match_info = " Produsele acoperă mai multe dintre interesele tale."
    elif products_covering_one:
        match_info = " Produsele se potrivesc cu cel puțin unul dintre interesele tale."

    reason = (
        f"Recomandate pe baza intereselor tale în {interests_str}"
        f"{brands_phrase}, bugetului ({user_profile.budget_range}) și criteriilor selectate ({criteria_str}).{match_info}"
    )
    
    return Recommendation(products=top_products, reason=reason)


@api_router.get("/users/{user_id}/new-products", response_model=List[Product])
async def get_new_products_for_user(
    user_id: str,
    days: int = 30,  
):
    """
    Returnează produse noi care se potrivesc cu interesele utilizatorului.
    Un produs este considerat "nou" dacă a fost creat în ultimele N zile.
    """
    user_data = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = UserProfile(**user_data["profile"])
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    matching_products = []
    for product in HARDCODED_PRODUCTS:
        product_created = product.get("created_at")
        if product_created:
            if isinstance(product_created, str):
                try:
                    product_created = datetime.fromisoformat(product_created.replace('Z', '+00:00'))
                except:
                    continue
            if product_created < cutoff_date:
                continue
        
        product_labels = product.get("labels", {})
        matches_interest = False
        
        for interest_key in user_profile.interests.keys():
            if interest_key in product_labels:
                matches_interest = True
                break
            
            interest_normalized = interest_key.lower().rstrip('s')
            for label_key in product_labels.keys():
                label_normalized = label_key.lower().rstrip('s')
                if interest_normalized == label_normalized:
                    matches_interest = True
                    break
            
            if matches_interest:
                break
        
        if matches_interest:
            matching_products.append(product)
    
    def sort_key(p):
        covers_all = _covers_all_interests(p, user_profile)
        score = calculate_recommendation_score(p, user_profile)
        return (not covers_all, -score)
    
    matching_products.sort(key=sort_key)
    
    return [Product(**p) for p in matching_products]


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