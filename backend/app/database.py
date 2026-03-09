"""Database connection and helper functions."""
import logging
from typing import List, Optional, Dict
from fastapi import HTTPException
from passlib.context import CryptContext
from supabase import create_client, Client
from app.config import get_settings
from app.data import HARDCODED_PRODUCTS, HARDCODED_USERS, USER_FAVORITES, ORDERS

logger = logging.getLogger(__name__)

# Password hashing (bcrypt via passlib)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def _verify_password(plain_password: str, stored_password: str) -> bool:
    try:
        return _pwd_context.verify(plain_password, stored_password)
    except Exception:
        return False

# Global Supabase client
_supabase: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Get or create Supabase client."""
    global _supabase
    if _supabase is None:
        import os
        settings = get_settings()
        supabase_url = settings.supabase_url or os.environ.get('SUPABASE_URL')
        supabase_key = settings.supabase_key or os.environ.get('SUPABASE_KEY')
        
        if supabase_url and supabase_key:
            try:
                _supabase = create_client(supabase_url, supabase_key)
                logger.info("Connected to Supabase")
            except Exception as e:
                logger.warning(f"Failed to connect to Supabase: {e}")
                _supabase = None
        else:
            logger.warning("Supabase credentials not found, using in-memory storage")
            _supabase = None
    return _supabase


# Initialize connection
get_supabase_client()


# Database helper functions
async def get_products_from_db(active_only: bool = True, category: Optional[str] = None) -> List[dict]:
    """Get products from Supabase (tabela 'produse') sau fallback la lista hardcodată."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("produse").select("*")
            if active_only:
                query = query.eq("is_active", True).gt("stock", 0)
            if category:
                query = query.eq("category", category)
            response = query.execute()
            return [dict(row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching products from DB: {e}")
            return HARDCODED_PRODUCTS
    return HARDCODED_PRODUCTS


async def get_product_by_id_from_db(product_id: str) -> Optional[dict]:
    """Get a single product by ID from Supabase (tabela 'produse') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            response = supabase.table("produse").select("*").eq("id", product_id).execute()
            if response.data:
                return dict(response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error fetching product from DB: {e}")
            return next((p for p in HARDCODED_PRODUCTS if p["id"] == product_id), None)
    return next((p for p in HARDCODED_PRODUCTS if p["id"] == product_id), None)


async def create_product_in_db(product_data: dict) -> dict:
    """Create a product in Supabase (tabela 'produse') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            response = supabase.table("produse").insert(product_data).execute()
            return dict(response.data[0])
        except Exception as e:
            logger.error(f"Error creating product in DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")
    # Fallback: add to hardcoded list
    HARDCODED_PRODUCTS.append(product_data)
    return product_data


async def update_product_in_db(product_id: str, product_data: dict) -> dict:
    """Update a product in Supabase (tabela 'produse') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            response = supabase.table("produse").update(product_data).eq("id", product_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Product not found")
            return dict(response.data[0])
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating product in DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")
    # Fallback: update in hardcoded list
    product_index = next((i for i, p in enumerate(HARDCODED_PRODUCTS) if p["id"] == product_id), None)
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    HARDCODED_PRODUCTS[product_index].update(product_data)
    return HARDCODED_PRODUCTS[product_index]


async def delete_product_from_db(product_id: str) -> None:
    """Delete a product from Supabase (tabela 'produse') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            response = supabase.table("produse").delete().eq("id", product_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Product not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting product from DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")
    # Fallback: remove from hardcoded list
    product_index = next((i for i, p in enumerate(HARDCODED_PRODUCTS) if p["id"] == product_id), None)
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    HARDCODED_PRODUCTS.pop(product_index)


async def get_favorites_from_db(user_id: str) -> List[str]:
    """Get favorite product IDs for a user from Supabase (tabela 'produse_favorite') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            uid = int(user_id)
            response = supabase.table("produse_favorite").select("product_id").eq("user_id", uid).execute()
            return [item["product_id"] for item in response.data]
        except (ValueError, TypeError):
            return []
        except Exception as e:
            logger.error(f"Error fetching favorites from DB: {e}")
            return USER_FAVORITES.get(user_id, [])
    return USER_FAVORITES.get(user_id, [])


async def add_favorite_to_db(user_id: str, product_id: str) -> None:
    """Add a favorite to Supabase (tabela 'produse_favorite') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            uid = int(user_id)
            logger.info(f"Adding favorite: user={user_id}, product={product_id}")
            response = supabase.table("produse_favorite").insert({"user_id": uid, "product_id": product_id}).execute()
            logger.info(f"Successfully added favorite: {response.data}")
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid user id")
        except Exception as e:
            logger.error(f"Error adding favorite to DB: {e}", exc_info=True)
            # Check if it's a duplicate error - ignore duplicates
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                logger.info("Favorite already exists, ignoring")
                return
            raise HTTPException(status_code=500, detail=f"Error adding favorite: {str(e)}")
    else:
        # Fallback
        logger.warning("Supabase not available, using fallback storage for favorites")
        if user_id not in USER_FAVORITES:
            USER_FAVORITES[user_id] = []
        if product_id not in USER_FAVORITES[user_id]:
            USER_FAVORITES[user_id].append(product_id)


async def remove_favorite_from_db(user_id: str, product_id: str) -> None:
    """Remove a favorite from Supabase (tabela 'produse_favorite') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            uid = int(user_id)
            response = supabase.table("produse_favorite").delete().eq("user_id", uid).eq("product_id", product_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Favorite not found")
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid user id")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing favorite from DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error removing favorite: {str(e)}")
    else:
        # Fallback
        if user_id in USER_FAVORITES and product_id in USER_FAVORITES[user_id]:
            USER_FAVORITES[user_id].remove(product_id)


async def create_order_in_db(order_data: dict) -> dict:
    """Create an order in Supabase folosind tabelele 'comenzi', 'comenzi_produse' și 'istoric_comenzi' sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            # Extragem produsele din comandă (vor merge în 'comenzi_produse')
            order_items = order_data.pop("items", [])

            # user_id trebuie integer în DB (API trimite string)
            if "user_id" in order_data and isinstance(order_data["user_id"], str):
                order_data["user_id"] = int(order_data["user_id"])

            # Inserăm comanda în tabela 'comenzi'
            response = supabase.table("comenzi").insert(order_data).execute()
            created_order = dict(response.data[0])
            order_id = created_order["id"]

            # Inserăm liniile de comandă în tabela 'comenzi_produse'
            if order_items:
                items_to_insert = [
                    {
                        "order_id": order_id,
                        "product_id": item["product_id"],
                        "product_name": item["product_name"],
                        "quantity": item["quantity"],
                        "price": item["price"],
                    }
                    for item in order_items
                ]
                supabase.table("comenzi_produse").insert(items_to_insert).execute()
                created_order["items"] = order_items

            # Salvăm intrarea și în istoricul de comenzi
            uid = created_order.get("user_id")
            if isinstance(uid, str):
                uid = int(uid)
            try:
                supabase.table("istoric_comenzi").insert(
                    {
                        "order_id": order_id,
                        "user_id": uid,
                        "status": created_order.get("status", "confirmed"),
                        "total_amount": created_order.get("total_amount", 0),
                        "created_at": created_order.get("created_at"),
                    }
                ).execute()
            except Exception as history_error:
                # Nu blocăm comanda dacă istoricul eșuează, doar logăm
                logger.warning(f"Failed to write to istoric_comenzi: {history_error}")

            return created_order
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid user id")
        except Exception as e:
            logger.error(f"Error creating order in DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")
    # Fallback
    ORDERS.append(order_data)
    return order_data


async def get_orders_from_db(user_id: str) -> List[dict]:
    """Get orders for a user from Supabase (tabela 'comenzi') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            uid = int(user_id)
            response = (
                supabase.table("comenzi")
                .select("*")
                .eq("user_id", uid)
                .order("created_at", desc=True)
                .execute()
            )
            orders = [dict(order) for order in response.data]
            
            # Fetch order items for each order din tabela 'comenzi_produse'
            for order in orders:
                items_response = (
                    supabase.table("comenzi_produse")
                    .select("*")
                    .eq("order_id", order["id"])
                    .execute()
                )
                order["items"] = [dict(item) for item in items_response.data]
            
            return orders
        except (ValueError, TypeError):
            return []
        except Exception as e:
            logger.error(f"Error fetching orders from DB: {e}")
            return [o for o in ORDERS if o.get("user_id") == user_id]
    return [o for o in ORDERS if o.get("user_id") == user_id]


async def get_order_by_id_from_db(user_id: str, order_id: str) -> Optional[dict]:
    """Get a single order by ID from Supabase (tabela 'comenzi') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            uid = int(user_id)
            response = (
                supabase.table("comenzi")
                .select("*")
                .eq("id", order_id)
                .eq("user_id", uid)
                .execute()
            )
            if not response.data:
                return None
            order = dict(response.data[0])
            
            # Fetch order items din tabela 'comenzi_produse'
            items_response = (
                supabase.table("comenzi_produse")
                .select("*")
                .eq("order_id", order_id)
                .execute()
            )
            order["items"] = [dict(item) for item in items_response.data]
            
            return order
        except (ValueError, TypeError):
            return None
        except Exception as e:
            logger.error(f"Error fetching order from DB: {e}")
            return next((o for o in ORDERS if o.get("id") == order_id and o.get("user_id") == user_id), None)
    return next((o for o in ORDERS if o.get("id") == order_id and o.get("user_id") == user_id), None)


# User database functions
def _build_profile_from_row(row: dict) -> dict:
    """Construiește obiectul profile din coloanele tabelei utilizatori."""
    return {
        "age_group": row.get("age_group") or "",
        "budget_range": row.get("budget_range") or "",
        "interests": list(row.get("interests") or []),
        "preferred_brands": list(row.get("preferred_brands") or []),
    }


def _user_row_to_api(row: dict) -> dict:
    """Convertește un rând din DB (coloane) în format API (id str, profile dict)."""
    return {
        "id": str(row["id"]),
        "username": row["username"],
        "role": row.get("role", "user"),
        "profile": _build_profile_from_row(row),
    }


def _hardcoded_user_to_api(user: dict) -> dict:
    return {
        "id": str(user.get("id", "")),
        "username": user.get("username", ""),
        "role": user.get("role", "user"),
        "profile": user.get("profile") or {},
    }


async def get_user_from_db(username: str, password: str) -> Optional[dict]:
    """Get user from Supabase (tabela 'utilizatori') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            response = (
                supabase.table("utilizatori")
                .select("*")
                .eq("username", username)
                .execute()
            )
            if response.data:
                row = dict(response.data[0])
                stored_password = str(row.get("password") or "")

                # Normal case: hashed password
                if _verify_password(password, stored_password):
                    return _user_row_to_api(row)

                # Compatibility: old plaintext password stored in DB
                if stored_password == password:
                    try:
                        supabase.table("utilizatori").update(
                            {"password": _hash_password(password)}
                        ).eq("id", row["id"]).execute()
                    except Exception as upgrade_error:
                        logger.warning(f"Failed to upgrade plaintext password: {upgrade_error}")
                    return _user_row_to_api(row)

                return None
            return None
        except Exception as e:
            logger.error(f"Error fetching user from DB: {e}")
            return None
    # Fallback: in-memory demo users
    for user in HARDCODED_USERS:
        if str(user.get("username", "")).lower() != username.lower():
            continue
        stored_password = str(user.get("password") or "")
        if _verify_password(password, stored_password):
            return _hardcoded_user_to_api(user)
        if stored_password == password:
            user["password"] = _hash_password(password)
            return _hardcoded_user_to_api(user)
        return None
    return None


async def get_user_by_id_from_db(user_id: str) -> Optional[dict]:
    """Get user by ID from Supabase (tabela 'utilizatori') sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            uid = int(user_id)
            response = (
                supabase.table("utilizatori")
                .select("*")
                .eq("id", uid)
                .execute()
            )
            if response.data:
                row = dict(response.data[0])
                return _user_row_to_api(row)
            return None
        except (ValueError, TypeError):
            return None
        except Exception as e:
            logger.error(f"Error fetching user by ID from DB: {e}")
            return None
    # Fallback: in-memory demo users
    for user in HARDCODED_USERS:
        if str(user.get("id")) == str(user_id):
            return _hardcoded_user_to_api(user)
    return None


async def create_user_in_db(user_data: dict) -> dict:
    """Create a user in Supabase (tabela 'utilizatori'). Nu trimite id; DB generează id numeric."""
    supabase = get_supabase_client()
    if supabase:
        try:
            profile = user_data.get("profile") or {}
            db_user = {
                "username": user_data["username"],
                "password": _hash_password(user_data["password"]),
                "role": user_data.get("role", "user"),
                "age_group": profile.get("age_group") or "",
                "budget_range": profile.get("budget_range") or "",
                "interests": list(profile.get("interests") or []),
                "preferred_brands": list(profile.get("preferred_brands") or []),
            }
            response = supabase.table("utilizatori").insert(db_user).execute()
            if response.data:
                row = dict(response.data[0])
                return _user_row_to_api(row)
            raise HTTPException(status_code=500, detail="Failed to create user")
        except Exception as e:
            logger.error(f"Error creating user in DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
    # Fallback: add to hardcoded list
    profile = user_data.get("profile") or {}
    existing_ids: List[int] = []
    for u in HARDCODED_USERS:
        try:
            existing_ids.append(int(str(u.get("id"))))
        except Exception:
            continue
    new_id = str((max(existing_ids) + 1) if existing_ids else 1)
    new_user = {
        "id": new_id,
        "username": user_data["username"],
        "password": _hash_password(user_data["password"]),
        "role": user_data.get("role", "user"),
        "profile": {
            "age_group": profile.get("age_group") or "",
            "budget_range": profile.get("budget_range") or "",
            "interests": list(profile.get("interests") or []),
            "preferred_brands": list(profile.get("preferred_brands") or []),
        },
    }
    HARDCODED_USERS.append(new_user)
    return _hardcoded_user_to_api(new_user)


async def update_user_in_db(user_id: str, user_data: dict) -> dict:
    """Update a user in Supabase (tabela 'utilizatori'). Actualizează coloanele profilului."""
    supabase = get_supabase_client()
    if supabase:
        try:
            uid = int(user_id)
            profile = user_data.get("profile") or {}
            update_data = {
                "username": user_data.get("username"),
                "age_group": profile.get("age_group"),
                "budget_range": profile.get("budget_range"),
                "interests": list(profile.get("interests") or []),
                "preferred_brands": list(profile.get("preferred_brands") or []),
            }
            if "password" in user_data:
                pwd = str(user_data["password"] or "")
                update_data["password"] = pwd if pwd.startswith("$2") else _hash_password(pwd)
            if "role" in user_data:
                update_data["role"] = user_data["role"]
            update_data = {k: v for k, v in update_data.items() if v is not None}

            response = supabase.table("utilizatori").update(update_data).eq("id", uid).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="User not found")
            row = dict(response.data[0])
            return _user_row_to_api(row)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid user id")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user in DB: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")
    # Fallback: update in hardcoded list
    user_index = next(
        (i for i, u in enumerate(HARDCODED_USERS) if str(u.get("id")) == str(user_id)),
        None,
    )
    if user_index is None:
        raise HTTPException(status_code=404, detail="User not found")

    profile = user_data.get("profile") or {}
    if user_data.get("username") is not None:
        HARDCODED_USERS[user_index]["username"] = user_data["username"]
    if "role" in user_data:
        HARDCODED_USERS[user_index]["role"] = user_data["role"]
    if "password" in user_data:
        pwd = str(user_data["password"] or "")
        HARDCODED_USERS[user_index]["password"] = pwd if pwd.startswith("$2") else _hash_password(pwd)

    current_profile = HARDCODED_USERS[user_index].get("profile") or {}
    current_profile.update(
        {
            "age_group": profile.get("age_group", current_profile.get("age_group", "")),
            "budget_range": profile.get("budget_range", current_profile.get("budget_range", "")),
            "interests": list(profile.get("interests") or current_profile.get("interests") or []),
            "preferred_brands": list(profile.get("preferred_brands") or current_profile.get("preferred_brands") or []),
        }
    )
    HARDCODED_USERS[user_index]["profile"] = current_profile
    return _hardcoded_user_to_api(HARDCODED_USERS[user_index])


async def check_username_exists(username: str) -> bool:
    """Check if username already exists in Supabase sau fallback."""
    supabase = get_supabase_client()
    if supabase:
        try:
            response = (
                supabase.table("utilizatori")
                .select("id")
                .eq("username", username)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking username in DB: {e}")
            # Fallback to hardcoded
            from app.data import HARDCODED_USERS
            return any(u["username"].lower() == username.lower() for u in HARDCODED_USERS)
    # Fallback
    return any(str(u.get("username", "")).lower() == username.lower() for u in HARDCODED_USERS)

