"""Order routes."""
import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from app.models import Order, OrderItem, TransactionRequest, TransactionItem, Product
from app.data import refresh_product_status, ensure_product_tags
from app.utils import get_products_list
from app.database import create_order_in_db, get_orders_from_db, get_order_by_id_from_db
from app.database import get_user_by_id_from_db

router = APIRouter()


@router.post("/transactions")
async def process_transaction(request: TransactionRequest, user_id: str = Header(..., alias="X-User-Id")):
    """Process a transaction and create an order - actualizează stocul în Supabase."""
    from app.database import get_product_by_id_from_db, update_product_in_db

    user = await get_user_by_id_from_db(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    updated_products: List[Product] = []
    order_items: List[OrderItem] = []
    total_amount = 0.0

    for item in request.items:
        # Încearcă să găsească produsul în Supabase
        product = await get_product_by_id_from_db(item.product_id)
        
        # Fallback la HARDCODED_PRODUCTS
        if not product:
            products = get_products_list()
            product = next((p for p in products if p["id"] == item.product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if item.quantity <= 0:
            continue
        
        current_stock = product.get("stock", 0)
        if current_stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficient pentru {product['name']}. Disponibil: {current_stock}, Cerut: {item.quantity}"
            )
        
        # Actualizează stocul
        product["stock"] = current_stock - item.quantity
        refresh_product_status(product)
        ensure_product_tags(product)
        
        # Salvează actualizarea în Supabase
        try:
            updated_product = await update_product_in_db(item.product_id, product)
            updated_products.append(Product(**updated_product))
        except Exception as e:
            # Dacă eșuează, folosește produsul actualizat local
            updated_products.append(Product(**product))
        
        item_price = product["price"] * item.quantity
        total_amount += item_price
        order_items.append(OrderItem(
            product_id=item.product_id,
            product_name=product["name"],
            quantity=item.quantity,
            price=product["price"]
        ))

    # Create order
    now = datetime.now().isoformat()
    shipping_info = None
    if request.shipping_address or request.phone or request.email:
        shipping_info = {
            "full_name": request.full_name or "",
            "address": request.shipping_address or "",
            "city": request.city or "",
            "postal_code": request.postal_code or "",
            "country": "Romania",
            "phone": request.phone or "",
            "email": request.email or ""
        }
    
    # Prepare data for Supabase 'comenzi' table
    order_id = str(uuid.uuid4())
    flat_shipping = {}
    if shipping_info:
        flat_shipping = {
            "shipping_full_name": shipping_info.get("full_name", ""),
            "shipping_address": shipping_info.get("address", ""),
            "shipping_city": shipping_info.get("city", ""),
            "shipping_postal_code": shipping_info.get("postal_code", ""),
            "shipping_country": shipping_info.get("country", "Romania"),
            "shipping_phone": shipping_info.get("phone", ""),
            "shipping_email": shipping_info.get("email", ""),
        }

    order_data = {
        "id": order_id,
        "user_id": user_id,
        "total_amount": total_amount,
        "status": "confirmed",
        "created_at": now,
        "updated_at": now,
        **flat_shipping,
    }

    # Save order to DB (or fallback in-memory)
    full_order = await create_order_in_db(
        {
            **order_data,
            "items": [item.model_dump() for item in order_items],
        }
    )

    return {
        "message": "Transaction processed",
        "order_id": full_order["id"],
        "updated_products": updated_products,
    }


@router.get("/orders/{user_id}", response_model=List[Order])
async def get_user_orders(user_id: str):
    """Get all orders for a user."""
    user_orders = await get_orders_from_db(user_id)
    # Convert to Order model format
    formatted_orders = []
    for order in user_orders:
        shipping_info = None
        if order.get("shipping_full_name") or order.get("shipping_address"):
            shipping_info = {
                "full_name": order.get("shipping_full_name", ""),
                "address": order.get("shipping_address", ""),
                "city": order.get("shipping_city", ""),
                "postal_code": order.get("shipping_postal_code", ""),
                "country": order.get("shipping_country", "Romania"),
                "phone": order.get("shipping_phone", ""),
                "email": order.get("shipping_email", "")
            }
        formatted_orders.append({
            "id": order["id"],
            "user_id": str(order["user_id"]),
            "items": order.get("items", []),
            "total_amount": float(order["total_amount"]),
            "shipping_info": shipping_info,
            "status": order["status"],
            "created_at": order["created_at"],
            "updated_at": order.get("updated_at", order["created_at"])
        })
    return formatted_orders


@router.get("/orders/{user_id}/{order_id}", response_model=Order)
async def get_order(user_id: str, order_id: str):
    """Get a single order by ID."""
    order = await get_order_by_id_from_db(user_id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    shipping_info = None
    if order.get("shipping_full_name") or order.get("shipping_address"):
        shipping_info = {
            "full_name": order.get("shipping_full_name", ""),
            "address": order.get("shipping_address", ""),
            "city": order.get("shipping_city", ""),
            "postal_code": order.get("shipping_postal_code", ""),
            "country": order.get("shipping_country", "Romania"),
            "phone": order.get("shipping_phone", ""),
            "email": order.get("shipping_email", "")
        }
    
    return {
        "id": order["id"],
        "user_id": str(order["user_id"]),
        "items": order.get("items", []),
        "total_amount": float(order["total_amount"]),
        "shipping_info": shipping_info,
        "status": order["status"],
        "created_at": order["created_at"],
        "updated_at": order.get("updated_at", order["created_at"])
    }

