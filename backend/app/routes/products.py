"""Product routes."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from app.models import Product, ProductCreate, ProductUpdate
from app.data import HARDCODED_PRODUCTS, refresh_product_status, ensure_product_tags
from app.utils import get_products_list
from app.database import (
    get_products_from_db,
    get_product_by_id_from_db,
    create_product_in_db,
    update_product_in_db,
    delete_product_from_db
)

router = APIRouter()


def verify_admin(user_id: str = Header(..., alias="X-User-Id"), user_role: str = Header(..., alias="X-User-Role")):
    """Verify admin access."""
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"user_id": user_id, "role": user_role}


@router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    active_only: bool = True,
):
    """Get all products - citește din Supabase."""
    # Citește din Supabase (sau fallback)
    products = await get_products_from_db(active_only=active_only, category=category)
    
    # Dacă nu sunt produse în Supabase și nu e specificată categorie, folosește fallback
    if not products and not category:
        products = get_products_list()
        if active_only:
            products = [p for p in products if p.get("is_active", True) and p.get("stock", 0) > 0]
    
    normalized = []
    for product in products:
        ensure_product_tags(product)
        normalized.append(Product(**product))
    return normalized


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a single product by ID - citește din Supabase."""
    # Încearcă din Supabase
    product_data = await get_product_by_id_from_db(product_id)
    
    # Fallback la HARDCODED_PRODUCTS
    if not product_data:
        products = get_products_list()
        product_data = next((p for p in products if p["id"] == product_id), None)
    
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    ensure_product_tags(product_data)
    return Product(**product_data)


@router.post("/products", response_model=Product)
async def create_product(product: ProductCreate, admin: dict = Depends(verify_admin)):
    """Create a new product (admin only) - salvează în Supabase."""
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
    
    # Salvează în Supabase (sau fallback)
    created_product = await create_product_in_db(new_product)
    return Product(**created_product)


@router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate, admin: dict = Depends(verify_admin)):
    """Update a product (admin only)."""
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


@router.delete("/products/{product_id}")
async def delete_product(product_id: str, admin: dict = Depends(verify_admin)):
    """Delete a product (admin only)."""
    await delete_product_from_db(product_id)
    return {"message": "Product deleted successfully"}


@router.get("/categories", response_model=List[str])
async def get_categories(active_only: bool = True):
    """Get all product categories."""
    products = await get_products_from_db(active_only=active_only)
    categories = list(set(p.get("category", "") for p in products if p.get("category")))
    return sorted(categories)

