"""API routes package."""
from fastapi import APIRouter
from app.config import get_settings
from app.routes import auth, favorites, orders, products, recommendations, debug

api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(products.router, tags=["products"])
api_router.include_router(favorites.router, tags=["favorites"])
api_router.include_router(orders.router, tags=["orders"])
api_router.include_router(recommendations.router, tags=["recommendations"])
if get_settings().debug:
    api_router.include_router(debug.router, tags=["debug"])

