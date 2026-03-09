"""Utility functions for legacy compatibility."""
from typing import List, Dict
from app.data import HARDCODED_PRODUCTS


def get_products_list() -> List[Dict]:
    """Returnează produsele demo (fallback).

    Funcția există doar pentru compatibilitate cu vechile fallback‑uri bazate pe
    produse hardcodate. Dacă Supabase nu este configurat, rutele folosesc aceste
    produse pentru a rula aplicația în mod demo.
    """
    return HARDCODED_PRODUCTS

