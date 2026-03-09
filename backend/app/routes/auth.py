"""Authentication routes."""
from fastapi import APIRouter, HTTPException

from app.database import (
    check_username_exists,
    create_user_in_db,
    get_user_by_id_from_db,
    get_user_from_db,
    update_user_in_db,
)
from app.models import (
    LoginRequest,
    LoginResponse,
    ProfileUpdate,
    RegisterRequest,
    UserProfile,
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
    """Login endpoint - verifică doar în Supabase."""
    user_data = await get_user_from_db(request.username, request.password)

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return LoginResponse(
        user_id=user_data["id"],
        username=user_data["username"],
        role=user_data.get("role", "user"),
        profile=UserProfile(**user_data["profile"]),
    )


@router.post("/auth/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """Registration endpoint - salvează utilizatorul în Supabase."""
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username invalid")

    if await check_username_exists(username):
        raise HTTPException(status_code=400, detail="Username already taken")

    interests = normalize_list(request.interests)
    if not interests:
        raise HTTPException(status_code=400, detail="Selectează cel puțin un interes")

    preferred_brands = [
        value.strip() for value in request.preferred_brands if value.strip()
    ]

    role = request.role if request.role in {"admin", "user"} else "user"

    new_user = {
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

    try:
        created_user = await create_user_in_db(new_user)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Could not create user in database"
        ) from exc

    return LoginResponse(
        user_id=created_user["id"],
        username=created_user["username"],
        role=created_user["role"],
        profile=UserProfile(**created_user["profile"]),
    )


@router.put("/profile/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, profile_update: ProfileUpdate):
    """Update user profile - actualizează doar în Supabase."""
    user = await get_user_by_id_from_db(user_id)

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
    user_profile.update(
        {
            "age_group": profile_update.age_group,
            "budget_range": profile_update.budget_range,
            "interests": profile_update.interests,
            "preferred_brands": profile_update.preferred_brands,
        }
    )
    user["profile"] = user_profile

    try:
        updated_user = await update_user_in_db(user_id, user)
        return UserProfile(**updated_user["profile"])
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Could not update user in database"
        ) from exc