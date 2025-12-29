from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, require_admin
from app.db.session import get_db
from app.models.request_history import RequestHistory
from app.schemas.history import HistoryResponse

router = APIRouter()


@router.get("/history", tags=["history"], response_model=List[HistoryResponse])
async def get_history(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
) -> List[HistoryResponse]:
    """Get history of all requests."""
    try:
        result = await db.execute(
            select(RequestHistory)
            .order_by(RequestHistory.timestamp.desc())
            .limit(limit)
        )
        history_records = result.scalars().all()
        return [HistoryResponse.model_validate(record) for record in history_records]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {exc}",
        )


@router.delete("/history", tags=["history"])
async def delete_history(
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_admin),
    confirm_token: Optional[str] = Header(None, alias="X-Confirm-Token"),
) -> dict:
    """Delete all history entries (admin only)."""
    try:
        if confirm_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing confirmation token",
            )
        confirm_payload = decode_token(confirm_token)
        if (
            confirm_payload.get("sub") != _user.get("sub")
            or not confirm_payload.get("is_admin")
            or confirm_payload.get("purpose") != "confirm_history_delete"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid confirmation token",
            )
        result = await db.execute(delete(RequestHistory))
        await db.commit()
        return {"deleted": result.rowcount or 0}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {exc}",
        )
