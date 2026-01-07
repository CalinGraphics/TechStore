"""Business logic services."""
from typing import Dict, List, Union
from app.models import UserProfile


def get_budget_bucket(price: float) -> str:
    """Get budget bucket for a price."""
    if price < 500:
        return "low"
    if price <= 1200:
        return "medium"
    return "high"


def is_budget_compatible(user_budget: str, price: float) -> bool:
    """Check if price is compatible with user budget."""
    product_bucket = get_budget_bucket(price)
    if user_budget == "low":
        return product_bucket == "low"
    if user_budget == "medium":
        return product_bucket in {"low", "medium"}
    if user_budget == "high":
        return product_bucket in {"low", "medium", "high"}
    return False


def evaluate_product_match(product: dict, user_profile: UserProfile) -> tuple[float, Dict[str, Dict[str, Union[str, bool, float]]], List[str]]:
    """Evaluate how well a product matches a user profile."""
    score = 0.0
    match_reasons: List[str] = []
    breakdown: Dict[str, Dict[str, Union[str, bool, float]]] = {}

    interest_match = product["category"] in user_profile.interests
    if interest_match:
        score += 40
        match_reasons.append(f"Categoria {product['category']} se află în interesele tale.")
    breakdown["interest"] = {
        "match": interest_match,
        "label": f"Interes: {product['category']}",
        "detail": "Se potrivește cu interesele tale" if interest_match else "Nu este în interesele declarate",
    }

    brand_match = product["brand"] in user_profile.preferred_brands
    if brand_match:
        score += 30
        match_reasons.append(f"Brandul {product['brand']} este în lista ta de preferințe.")
    breakdown["brand"] = {
        "match": brand_match,
        "label": f"Brand: {product['brand']}",
        "detail": "Este un brand preferat" if brand_match else "Nu este în lista de branduri preferate",
    }

    price = product["price"]
    budget_bucket = get_budget_bucket(price)
    budget_score = 0.0
    budget_match = False

    if user_profile.budget_range == "low" and budget_bucket == "low":
        budget_score = 30
        budget_match = True
    elif user_profile.budget_range == "medium":
        if budget_bucket == "medium":
            budget_score = 30
            budget_match = True
        elif budget_bucket == "low":
            budget_score = 20
    elif user_profile.budget_range == "high" and budget_bucket == "high":
        budget_score = 30
        budget_match = True

    if budget_score > 0:
        score += budget_score
        if budget_match:
            match_reasons.append(f"Prețul de {price:.2f} RON se potrivește cu bugetul tău ({user_profile.budget_range}).")
        else:
            match_reasons.append(f"Prețul de {price:.2f} RON este sub bugetul tău și oferă economie.")

    breakdown["budget"] = {
        "match": is_budget_compatible(user_profile.budget_range, price),
        "label": f"Buget: {user_profile.budget_range}",
        "detail": f"Produsul este în zona {budget_bucket} ({price:.2f} RON)",
        "awarded_points": budget_score,
    }

    return score, breakdown, match_reasons

