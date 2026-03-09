"""Pydantic models for the application."""
import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Union


class UserProfile(BaseModel):
    """User profile model."""
    age_group: str
    interests: List[str]
    budget_range: str
    preferred_brands: List[str]


class User(BaseModel):
    """User model."""
    model_config = ConfigDict(extra="ignore")
    
    id: Optional[str] = None
    username: str
    password: str
    role: str = "user"
    profile: UserProfile


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    user_id: str
    username: str
    role: str
    profile: UserProfile


class RegisterRequest(BaseModel):
    """Registration request model."""
    username: str
    password: str
    age_group: str
    budget_range: str
    interests: List[str]
    preferred_brands: List[str] = []
    role: Optional[str] = None


class Product(BaseModel):
    """Product model."""
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
    """Product match model for recommendations."""
    product: Product
    score: float
    breakdown: Dict[str, Dict[str, Union[str, bool, float]]]
    match_reasons: List[str]


class Recommendation(BaseModel):
    """Recommendation model."""
    products: List[Product]
    reason: str
    product_matches: Optional[List[ProductMatch]] = None
    user_profile: UserProfile


class ProductCreate(BaseModel):
    """Product creation model."""
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
    """Product update model."""
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
    """Profile update model."""
    age_group: str
    budget_range: str
    interests: List[str]
    preferred_brands: List[str]
    username: Optional[str] = None


class TransactionItem(BaseModel):
    """Transaction item model."""
    product_id: str
    quantity: int


class TransactionRequest(BaseModel):
    """Transaction request model."""
    items: List[TransactionItem]
    shipping_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    payment_method: Optional[str] = None
    full_name: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None


class ShippingInfo(BaseModel):
    """Shipping information model."""
    full_name: str
    address: str
    city: str
    postal_code: str
    country: str
    phone: str
    email: str


class OrderItem(BaseModel):
    """Order item model."""
    product_id: str
    product_name: str
    quantity: int
    price: float


class Order(BaseModel):
    """Order model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[OrderItem]
    total_amount: float
    shipping_info: Optional[ShippingInfo] = None
    status: str = "pending"  # pending, confirmed, shipped, delivered, cancelled
    created_at: str
    updated_at: str

