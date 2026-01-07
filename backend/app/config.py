"""Configuration settings for the application."""
import os
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent


class Settings:
    """Application settings."""
    def __init__(self):
        self.app_name: str = os.getenv("APP_NAME", "TechStore API")
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
        self.supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")
        self.cors_origins: str = os.getenv("CORS_ORIGINS", "*")


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

