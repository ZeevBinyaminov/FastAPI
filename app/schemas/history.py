from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class HistoryResponse(BaseModel):
    """Response model for history endpoint."""

    id: int
    created_at: datetime
    request_headers: Optional[Dict[str, Any]] = None
    response_status: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    bytecode_length: Optional[int] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
