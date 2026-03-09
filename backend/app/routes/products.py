"""Product routes."""
import uuid
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.data import HARDCODED_PRODUCTS, ensure_product_tags, refresh_product_status
from app.database import (
    create_product_in_db,
    delete_product_from_db,
    get_product_by_id_from_db,
    get_products_from_db,
    get_user_by_id_from_db,
    update_product_in_db,
)
from app.models import Product, ProductCreate, ProductUpdate
from app.search_engine import SearchResult, build_product_index, build_spec_index
from app.utils import get_products_list

router = APIRouter()


async def verify_admin(user_id: str = Header(..., alias="X-User-Id")):
    """Verify admin access using DB role (nu doar header spoofable)."""
    user = await get_user_by_id_from_db(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"user_id": user_id, "role": user.get("role", "user")}


async def _get_all_products_for_ir(active_only: bool = True) -> List[dict]:
    """Helper to fetch products (DB + fallback) and normalize tags."""
    products = await get_products_from_db(active_only=active_only)
    if not products:
        products = get_products_list()
        if active_only:
            products = [
                p
                for p in products
                if p.get("is_active", True) and p.get("stock", 0) > 0
            ]
    for product in products:
        ensure_product_tags(product)
    return products


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
            products = [
                p
                for p in products
                if p.get("is_active", True) and p.get("stock", 0) > 0
            ]

    normalized: List[Product] = []
    for product in products:
        ensure_product_tags(product)
        normalized.append(Product(**product))
    return normalized


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product_data = await get_product_by_id_from_db(product_id)

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
        "tags": product.tags or [product.category],
    }
    new_product["is_active"] = product.is_active if product.stock > 0 else False
    refresh_product_status(new_product)
    ensure_product_tags(new_product)

    # Salvează în Supabase
    created_product = await create_product_in_db(new_product)
    return Product(**created_product)


@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str, product_update: ProductUpdate, admin: dict = Depends(verify_admin)
):
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
    categories = list(
        set(p.get("category", "") for p in products if p.get("category"))
    )
    return sorted(categories)


@router.get("/products/search", response_model=List[Product])
async def search_products(
    q: str = Query(..., min_length=1, description="Cuvinte cheie pentru căutare"),
    method: str = Query(
        "bm25",
        pattern="^(tfidf|bm25)$",
        description="Algoritm de scor: tfidf sau bm25",
    ),
    active_only: bool = True,
    order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Ordinea rezultatelor după scor (asc sau desc)",
    ),
):
    """Full-text search în colecția de produse folosind TF-IDF sau BM25.

    Produsele sunt ordonate descrescător după scorul Lucene-style.
    """
    products = await _get_all_products_for_ir(active_only=active_only)
    if not products:
        return []

    index = build_product_index(products)
    if method == "tfidf":
        results: List[SearchResult] = index.search_tfidf(q, top_k=len(products))
    else:
        results = index.search_bm25(q, top_k=len(products))

    score_by_id = {r.product_id: r.score for r in results}

    reverse = order == "desc"

    ordered_products = [
        Product(**p)
        for p in sorted(
            products,
            key=lambda prod: score_by_id.get(prod["id"], 0.0),
            reverse=reverse,
        )
        if score_by_id.get(p["id"], 0.0) > 0.0
    ]
    return ordered_products


@router.get("/products/autocomplete", response_model=List[str])
async def autocomplete_products(
    q: str = Query(..., min_length=1, description="Prefix sau fragment din titlu"),
    limit: int = Query(8, ge=1, le=20),
):
    """Autocomplete / căutare predictivă în titlurile produselor.

    Folosește potrivire de prefix, trigram similarity și distanță Levenshtein
    pentru a ordona sugestiile.
    """
    query = q.strip().lower()
    if not query:
        return []

    products = await _get_all_products_for_ir(active_only=True)

    def trigrams(text: str) -> List[str]:
        t = f"  {text} "
        return [t[i : i + 3] for i in range(len(t) - 2)]

    def trigram_similarity(a: str, b: str) -> float:
        ta = trigrams(a)
        tb = trigrams(b)
        if not ta or not tb:
            return 0.0
        inter = len(set(ta).intersection(tb))
        union = len(set(ta).union(tb))
        return inter / union if union else 0.0

    def levenshtein(a: str, b: str) -> int:
        if a == b:
            return 0
        if not a:
            return len(b)
        if not b:
            return len(a)
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            curr = [i]
            for j, cb in enumerate(b, 1):
                cost = 0 if ca == cb else 1
                curr.append(
                    min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
                )
            prev = curr
        return prev[-1]

    scored: List[Tuple[str, float]] = []
    for p in products:
        title = str(p.get("name", ""))
        title_norm = title.lower()
        if not title_norm:
            continue

        prefix_match = title_norm.startswith(query)
        contains_match = query in title_norm
        trigram_score = trigram_similarity(query, title_norm)
        lev = levenshtein(query, title_norm[: len(query) + 8])

        score = 0.0
        if prefix_match:
            score += 3.0
        if contains_match:
            score += 1.5
        score += 2.0 * trigram_score
        score += max(0.0, 2.0 - 0.3 * lev)

        if score > 0:
            scored.append((title, score))

    # Remove duplicates and sort
    unique_scores: Dict[str, float] = {}
    for title, score in scored:
        if title not in unique_scores or score > unique_scores[title]:
            unique_scores[title] = score

    suggestions = [
        title
        for title, _ in sorted(
            unique_scores.items(), key=lambda x: x[1], reverse=True
        )[:limit]
    ]
    return suggestions


@router.get("/products/similar/{product_id}", response_model=List[Product])
async def get_similar_products(
    product_id: str,
    limit: int = Query(5, ge=1, le=20),
):
    """Returnează produse similare bazate pe similaritate cosinus a conținutului."""
    products = await _get_all_products_for_ir(active_only=True)
    if not products:
        return []

    index = build_product_index(products)
    # Map product_id -> IndexedDocument
    by_pid = {doc.product_id: doc for doc in index.documents.values()}
    target_doc = by_pid.get(product_id)
    if not target_doc:
        raise HTTPException(status_code=404, detail="Product not found")

    target_vec = index.build_tfidf_vector(target_doc)
    if not target_vec:
        return []

    similarities: List[Tuple[str, float]] = []
    for doc in index.documents.values():
        if doc.product_id == product_id:
            continue
        vec = index.build_tfidf_vector(doc)
        sim = index.cosine_similarity(target_vec, vec)
        if sim > 0:
            similarities.append((doc.product_id, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_ids = {pid for pid, _ in similarities[:limit]}

    id_to_product = {p["id"]: p for p in products}
    similar_products = [
        Product(**id_to_product[pid]) for pid, _ in similarities if pid in id_to_product
    ][:limit]
    return similar_products


@router.get("/spec-search", response_model=List[Product])
async def search_specifications(
    q: str = Query(..., min_length=1, description="Căutare full-text în fișele tehnice"),
    method: str = Query(
        "bm25",
        pattern="^(tfidf|bm25)$",
        description="Algoritm de scor: tfidf sau bm25",
    ),
    order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Ordinea rezultatelor după scor (asc sau desc)",
    ),
):
    """Căutare avansată în documentele de specificații folosind TF-IDF / BM25.

    Indexul este construit peste câmpul `specs` + descrierea produsului.
    Rezultatele sunt ordonate descrescător după scorul Lucene-style.
    """
    products = await _get_all_products_for_ir(active_only=True)
    if not products:
        return []

    index = build_spec_index(products)
    if method == "tfidf":
        results: List[SearchResult] = index.search_tfidf(q, top_k=len(products))
    else:
        results = index.search_bm25(q, top_k=len(products))

    score_by_id = {r.product_id: r.score for r in results}

    reverse = order == "desc"

    ordered_products = [
        Product(**p)
        for p in sorted(
            products,
            key=lambda prod: score_by_id.get(prod["id"], 0.0),
            reverse=reverse,
        )
        if score_by_id.get(p["id"], 0.0) > 0.0
    ]
    return ordered_products
