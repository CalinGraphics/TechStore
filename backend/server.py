"""Main FastAPI application."""
import logging
import os
from pathlib import Path
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes import api_router
from app.config import get_settings

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TechStore API",
    description="Electronics Store API with recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
def home():
    """Root endpoint."""
    return {"message": "Hello World!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "debug": settings.debug
    }


@app.get("/config")
async def get_config():
    """Configuration endpoint."""
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "debug": settings.debug
    }
