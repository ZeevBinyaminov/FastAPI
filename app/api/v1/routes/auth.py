from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token, create_confirm_token, require_admin
from app.schemas.auth import TokenRequest, TokenResponse

router = APIRouter()


@router.post("/auth/token", tags=["auth"], response_model=TokenResponse)
async def issue_token(payload: TokenRequest) -> TokenResponse:
    if (
        payload.username != settings.admin_username
        or payload.password != settings.admin_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        subject=payload.username,
        is_admin=True,
        expires_minutes=settings.jwt_expires_minutes,
    )
    return TokenResponse(access_token=token)


@router.post("/auth/confirm-token", tags=["auth"], response_model=TokenResponse)
async def issue_confirm_token(user: dict = Depends(require_admin)) -> TokenResponse:
    token = create_confirm_token(subject=user.get("sub", "admin"), expires_minutes=30)
    return TokenResponse(access_token=token)
