"""Recommendations routes."""
from typing import List

from fastapi import APIRouter, HTTPException

from app.database import get_products_from_db, get_user_by_id_from_db
from app.data import ensure_product_tags
from app.models import Product, ProductMatch, Recommendation, UserProfile
from app.services import evaluate_product_match, is_budget_compatible

router = APIRouter()


@router.get("/recommendations/{user_id}", response_model=Recommendation)
async def get_recommendations(user_id: str):
    """Returnează recomandări personalizate doar pe baza datelor din Supabase."""
    user_data = await get_user_by_id_from_db(user_id)

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = UserProfile(**user_data["profile"])

    products = await get_products_from_db(active_only=True)
    if not products:
        return Recommendation(
            products=[],
            reason="Nu există produse active în catalog.",
            product_matches=[],
            user_profile=user_profile,
        )

    # Normalizează interesele utilizatorului (lowercase pentru matching)
    normalized_interests = [interest.lower().strip() for interest in user_profile.interests]

    product_matches: List[ProductMatch] = []
    for product in products:
        if not product.get("is_active", True) or product.get("stock", 0) <= 0:
            continue
        ensure_product_tags(product)

        # Matching flexibil pe categorie
        product_category = product.get("category", "").lower().strip()
        category_match = False

        if product_category in normalized_interests:
            category_match = True
        else:
            for interest in normalized_interests:
                if product_category in interest or interest in product_category:
                    category_match = True
                    break

        if not category_match:
            continue

        if not is_budget_compatible(user_profile.budget_range, product.get("price", 0)):
            continue

        score, breakdown, match_reasons = evaluate_product_match(product, user_profile)
        if score <= 0:
            continue
        product_matches.append(
            ProductMatch(
                product=Product(**product),
                score=score,
                breakdown=breakdown,
                match_reasons=match_reasons,
            )
        )

    product_matches.sort(key=lambda pm: pm.score, reverse=True)
    top_products = [match.product for match in product_matches]

    interests_str = ", ".join(user_profile.interests)
    brands_str = ", ".join(user_profile.preferred_brands)
    reason = (
        f"Recomandate pe baza intereselor tale ({interests_str}), "
        f"preferințelor pentru branduri ({brands_str}) și bugetului ({user_profile.budget_range})."
    )

    return Recommendation(
        products=top_products,
        reason=reason,
        product_matches=product_matches,
        user_profile=user_profile,
    )
