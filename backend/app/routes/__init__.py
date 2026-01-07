"""API routes package."""
from fastapi import APIRouter
from app.routes import auth, products, favorites, orders, recommendations, debug

api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(products.router, tags=["products"])
api_router.include_router(favorites.router, tags=["favorites"])
api_router.include_router(orders.router, tags=["orders"])
api_router.include_router(recommendations.router, tags=["recommendations"])
api_router.include_router(debug.router, tags=["debug"])

