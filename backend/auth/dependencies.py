from fastapi import Request, HTTPException
from backend.auth.jwt_handler import verify_jwt_token
from backend.config import settings


async def get_current_user(request: Request) -> str:
    """
    Dependency to get current authenticated user from JWT cookie.
    Raises 401 if not authenticated or 403 if not whitelisted.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    email = verify_jwt_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Check whitelist
    if settings.ALLOWED_EMAILS and email not in settings.ALLOWED_EMAILS:
        raise HTTPException(status_code=403, detail="Email not authorized")

    return email
