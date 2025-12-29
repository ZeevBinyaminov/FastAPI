from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ForwardRequest(BaseModel):
    """Request model for /forward endpoint."""

    model_config = ConfigDict()

    bytecode: Optional[str] = Field(
        default=None, description="EVM bytecode as hex string (0x...)"
    )
    text: Optional[str] = Field(
        default=None, description="Optional input text")
    created_at: datetime = Field(default_factory=datetime.now, frozen=True)


class ForwardResponse(BaseModel):
    """Response model for /forward endpoint."""

    status: str
    data: Dict[str, Any]
    result: Dict[str, Any]
