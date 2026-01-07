"""Authentication routes."""
import uuid
from fastapi import APIRouter, HTTPException
from app.models import LoginRequest, LoginResponse, RegisterRequest, UserProfile, ProfileUpdate
from app.data import HARDCODED_USERS
from app.database import (
    get_user_from_db,
    create_user_in_db,
    update_user_in_db,
    check_username_exists,
    get_user_by_id_from_db
)

router = APIRouter()


def normalize_list(values: list[str]) -> list[str]:
    """Normalize list of strings."""
    normalized: list[str] = []
    for value in values:
        cleaned = value.strip().lower()
        if cleaned:
            normalized.append(cleaned)
    return normalized


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint - verifică în Supabase, apoi fallback la HARDCODED_USERS."""
    # Încearcă să găsească utilizatorul în Supabase
    user_data = await get_user_from_db(request.username, request.password)
    
    # Fallback la HARDCODED_USERS dacă nu este în Supabase
    if not user_data:
        user_data = next(
            (u for u in HARDCODED_USERS if u["username"] == request.username and u["password"] == request.password),
            None
        )
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return LoginResponse(
        user_id=user_data["id"],
        username=user_data["username"],
        role=user_data.get("role", "user"),
        profile=UserProfile(**user_data["profile"])
    )


@router.post("/auth/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """Registration endpoint - salvează în Supabase."""
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username invalid")
    
    # Verifică dacă username-ul există (în Supabase sau fallback)
    if await check_username_exists(username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    interests = normalize_list(request.interests)
    if not interests:
        raise HTTPException(status_code=400, detail="Selectează cel puțin un interes")
    
    preferred_brands = [value.strip() for value in request.preferred_brands if value.strip()]
    
    # Validează rolul - doar "admin" sau "user" sunt permise
    role = request.role if request.role in {"admin", "user"} else "user"
    
    new_user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": request.password,
        "role": role,
        "profile": {
            "age_group": request.age_group,
            "budget_range": request.budget_range,
            "interests": interests,
            "preferred_brands": preferred_brands,
        },
    }
    
    # Salvează în Supabase (sau fallback la HARDCODED_USERS)
    try:
        created_user = await create_user_in_db(new_user)
    except Exception as e:
        # Dacă eșuează, folosește fallback
        from app.data import HARDCODED_USERS
        HARDCODED_USERS.append(new_user)
        created_user = new_user
    
    return LoginResponse(
        user_id=created_user["id"],
        username=created_user["username"],
        role=created_user["role"],
        profile=UserProfile(**created_user["profile"]),
    )


@router.put("/profile/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, profile_update: ProfileUpdate):
    """Update user profile - actualizează în Supabase."""
    # Încearcă să găsească utilizatorul în Supabase
    user = await get_user_by_id_from_db(user_id)
    
    # Fallback la HARDCODED_USERS
    if not user:
        user = next((u for u in HARDCODED_USERS if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    desired_username = profile_update.username
    if desired_username is not None:
        normalized_username = desired_username.strip()
        if not normalized_username:
            raise HTTPException(status_code=400, detail="Username invalid")
        if normalized_username.lower() != user["username"].lower():
            if await check_username_exists(normalized_username):
                raise HTTPException(status_code=400, detail="Username already taken")
            user["username"] = normalized_username

    user_profile = user.get("profile", {})
    user_profile.update({
        "age_group": profile_update.age_group,
        "budget_range": profile_update.budget_range,
        "interests": profile_update.interests,
        "preferred_brands": profile_update.preferred_brands,
    })
    user["profile"] = user_profile
    
    # Actualizează în Supabase
    try:
        updated_user = await update_user_in_db(user_id, user)
        return UserProfile(**updated_user["profile"])
    except Exception as e:
        # Dacă eșuează, returnează din memorie
        return UserProfile(**user_profile)

