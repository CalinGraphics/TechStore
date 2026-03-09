"""Favorites routes."""
from typing import List
from fastapi import APIRouter, HTTPException
from app.models import Product
from app.utils import get_products_list
from app.database import get_favorites_from_db, add_favorite_to_db, remove_favorite_from_db
from app.database import get_user_by_id_from_db

router = APIRouter()


@router.get("/favorites/{user_id}", response_model=List[Product])
async def get_favorites(user_id: str):
    """Get user's favorite products - citește din Supabase."""
    from app.database import get_products_from_db
    from app.data import ensure_product_tags

    user = await get_user_by_id_from_db(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    favorites_ids = await get_favorites_from_db(user_id)
    
    # Încearcă să găsească produsele din Supabase
    all_products = await get_products_from_db(active_only=False)
    
    # Dacă nu sunt produse în Supabase, folosește fallback
    if not all_products:
        products = get_products_list()
    else:
        products = all_products
    
    favorite_products = [p for p in products if p["id"] in favorites_ids]
    
    # Asigură că toate produsele au tags
    for product in favorite_products:
        ensure_product_tags(product)
    
    return [Product(**p) for p in favorite_products]


@router.post("/favorites/{user_id}/{product_id}")
async def add_to_favorites(user_id: str, product_id: str):
    """Add a product to favorites - salvează în Supabase."""
    from app.database import get_product_by_id_from_db

    user = await get_user_by_id_from_db(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verifică dacă produsul există în Supabase
    product = await get_product_by_id_from_db(product_id)
    
    # Fallback la HARDCODED_PRODUCTS
    if not product:
        products = get_products_list()
        product = next((p for p in products if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Adaugă la favorite în Supabase
    await add_favorite_to_db(user_id, product_id)
    return {"message": "Product added to favorites", "product_id": product_id}


@router.delete("/favorites/{user_id}/{product_id}")
async def remove_from_favorites(user_id: str, product_id: str):
    """Remove a product from favorites."""
    user = await get_user_by_id_from_db(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await remove_favorite_from_db(user_id, product_id)
    return {"message": "Product removed from favorites", "product_id": product_id}

