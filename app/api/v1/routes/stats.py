from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.session import get_db
from app.models.request_history import RequestHistory
from app.services.stats_service import build_stats

router = APIRouter()


@router.get("/stats", tags=["stats"])
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_admin),
) -> dict:
    """Return request statistics (admin only)."""
    try:
        result = await db.execute(
            select(
                RequestHistory.processing_time_ms,
                RequestHistory.input_text_length,
                RequestHistory.input_token_count,
            )
        )
        rows = result.all()

        processing_times = [row[0] for row in rows if row[0] is not None]
        text_lengths = [row[1] for row in rows if row[1] is not None]
        token_counts = [row[2] for row in rows if row[2] is not None]

        stats = build_stats(
            processing_times,
            text_lengths,
            token_counts,
        )

        return {
            "total_requests": len(rows),
            "stats": stats,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {exc}",
        )
