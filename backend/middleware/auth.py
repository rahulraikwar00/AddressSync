from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
from core.config import settings
from core.logging import logger


class AuthMiddleware(BaseHTTPMiddleware):
    """Optional auth middleware for protected routes"""

    EXCLUDED_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/",
        "/health",
        "/agencies/register",
        "/agencies/login",
        "/users/register",
        "/users/login",
        "/static"
    ]

    async def dispatch(self, request: Request, call_next):
        # Skip auth for excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return await call_next(request)

        # Check for protected routes that require authentication
        if request.url.path.startswith("/requests") or \
           request.url.path.startswith("/agencies/me") or \
           request.url.path.startswith("/users/me"):

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header"
                )

            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM]
                )
                request.state.user_id = payload.get("sub")
                request.state.user_type = payload.get("type")
            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

        return await call_next(request)
