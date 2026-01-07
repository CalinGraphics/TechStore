"""Debug routes."""
from fastapi import APIRouter
from app.data import HARDCODED_USERS, HARDCODED_PRODUCTS
from app.database import get_supabase_client
import os

router = APIRouter()


@router.get("/debug/db")
async def debug_db():
    """Debug endpoint to check database status."""
    safe_users = []
    for u in HARDCODED_USERS:
        safe_user = {**u}
        if "password" in safe_user:
            safe_user["password"] = "******"
        safe_users.append(safe_user)
    
    supabase = get_supabase_client()
    supabase_status = "connected" if supabase else "not connected"
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
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


@router.get("/")
async def root():
    """Root API endpoint."""
    return {"message": "Electronics Store API"}

