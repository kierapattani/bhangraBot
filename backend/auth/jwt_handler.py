from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from backend.config import settings


def create_jwt_token(email: str) -> str:
    """Create a JWT token for the given email."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_jwt_token(token: str) -> str | None:
    """
    Verify a JWT token and return the email if valid.
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
