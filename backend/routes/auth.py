from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from backend.config import settings
from backend.models.schemas import UserResponse
from backend.auth.google_oauth import (
    generate_state,
    get_google_auth_url,
    exchange_code_for_tokens,
    get_user_email,
)
from backend.auth.jwt_handler import create_jwt_token, verify_jwt_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(response: Response):
    """Redirect to Google OAuth consent screen."""
    state = generate_state()
    auth_url = get_google_auth_url(state)

    # Create redirect response and set state cookie for CSRF protection
    redirect = RedirectResponse(url=auth_url, status_code=302)
    redirect.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=600,  # 10 minutes
    )
    return redirect


@router.get("/callback")
async def callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle Google OAuth callback."""
    # Check for OAuth errors
    if error:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={error}",
            status_code=302,
        )

    if not code or not state:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=missing_params",
            status_code=302,
        )

    # Verify state for CSRF protection
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=invalid_state",
            status_code=302,
        )

    # Exchange code for tokens
    tokens = await exchange_code_for_tokens(code)
    if not tokens:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=token_exchange_failed",
            status_code=302,
        )

    # Get user email
    access_token = tokens.get("access_token")
    email = await get_user_email(access_token)
    if not email:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=email_fetch_failed",
            status_code=302,
        )

    # Check whitelist
    if settings.ALLOWED_EMAILS and email not in settings.ALLOWED_EMAILS:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=not_authorized",
            status_code=302,
        )

    # Create JWT and set cookie
    jwt_token = create_jwt_token(email)
    redirect = RedirectResponse(
        url=f"{settings.FRONTEND_URL}/dashboard",
        status_code=302,
    )
    redirect.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.JWT_EXPIRATION_HOURS * 3600,
    )
    # Clear OAuth state cookie
    redirect.delete_cookie("oauth_state")
    return redirect


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request):
    """Get current user info from JWT cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    email = verify_jwt_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return UserResponse(email=email, authenticated=True)


@router.post("/logout")
async def logout():
    """Clear JWT cookie."""
    response = Response(status_code=200)
    response.delete_cookie("access_token")
    return response
