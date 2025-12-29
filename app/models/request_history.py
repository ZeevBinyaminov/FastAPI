from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RequestHistory(Base):
    """Model for storing request history."""

    __tablename__ = "request_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    request_headers: Mapped[Optional[dict[str, Any]]]
    response_status: Mapped[Optional[str]]
    response_data: Mapped[Optional[dict[str, Any]]]
    processing_time_ms: Mapped[Optional[int]]
    bytecode_length: Mapped[Optional[int]]
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
