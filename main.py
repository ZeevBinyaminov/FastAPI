from fastapi import FastAPI, Depends, Request, Header, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, List
from datetime import datetime
import json

from db import get_db, init_db
from models import RequestHistory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("Application will continue, but database features may not work")
    yield

app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return 400 with 'bad request' message"""
    return Response(
        content="bad request",
        status_code=status.HTTP_400_BAD_REQUEST,
        media_type="text/plain"
    )


@app.get("/", tags=["root", "testing"])
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "Hello World"}


@app.get("/health", tags=["testing"])
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/items/{item_id}", tags=["items"])
async def get_item(item_id: int) -> dict[str, int]:
    """Read item endpoint"""
    print(f"Getting item {item_id}")
    return {"item_id": item_id}


class ForwardRequest(BaseModel):
    """Request model for /forward endpoint"""
    model_config = ConfigDict()  # Allow additional fields

    smart_contract_address: str = Field(...,
                                        description="The address of the smart contract")
    created_at: datetime = Field(default_factory=datetime.now, frozen=True)


@app.post("/forward", tags=["forward"])
async def forward(
    data: ForwardRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(
        None, description="Authorization header"),
    x_api_key: Optional[str] = Header(
        None, alias="X-API-Key", description="API Key header"),
    x_user_id: Optional[str] = Header(
        None, alias="X-User-Id", description="User ID header"),
) -> Dict[str, Any]:
    """
    Forward endpoint that accepts JSON data.

    Accepts JSON data in the request body and additional parameters in headers.
    Returns JSON response if model processes data successfully.
    """
    # Extract all headers for additional parameters
    headers = dict(request.headers)

    # Simulate model processing
    # In real implementation, this would be actual model inference
    model_success = process_with_model(data, headers)

    response_status = "success"
    response_data = None

    if not model_success:
        # Model failed to process data - save to history and return 403
        response_status = "error"
        response_data = {"error": "модель не смогла обработать данные"}

        # Save request to history before raising exception - even failed requests must be saved
        try:
            history_record = RequestHistory(
                smart_contract_address=data.smart_contract_address,
                created_at=data.created_at,
                request_headers=headers,
                response_status=response_status,
                response_data=response_data
            )
            db.add(history_record)
            await db.commit()
            print(
                f"✓ Failed request saved to history: {data.smart_contract_address}")
        except Exception as e:
            # Log error but don't fail the request
            print(
                f"✗ Error saving failed request to history: {type(e).__name__}: {e}")
            try:
                await db.rollback()
            except:
                pass

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="модель не смогла обработать данные"
        )

    # Model processed successfully - return JSON response
    response_data = {
        "status": "success",
        "data": data.model_dump(),
        "headers": {
            "authorization": authorization,
            "x_api_key": x_api_key,
            "x_user_id": x_user_id,
            "all_headers": headers
        },
        "result": {
            "processed": True,
            "smart_contract_address": data.smart_contract_address,
            "created_at": data.created_at.isoformat()
        }
    }

    # Save request to history - this is critical, so we try hard to save it
    try:
        history_record = RequestHistory(
            smart_contract_address=data.smart_contract_address,
            created_at=data.created_at,
            request_headers=headers,
            response_status=response_status,
            response_data=response_data
        )
        db.add(history_record)
        await db.commit()
        print(f"✓ Request saved to history: {data.smart_contract_address}")
    except Exception as e:
        # Log error but don't fail the request
        print(f"✗ Error saving to history: {type(e).__name__}: {e}")
        try:
            await db.rollback()
        except:
            pass

    return response_data


def process_with_model(data: ForwardRequest, headers: Dict[str, str]) -> bool:
    """
    Simulate model processing.
    In real implementation, this would call the actual model.

    Returns True if model processed successfully, False otherwise.
    """
    # Example: Model fails if smart_contract_address is empty or invalid
    if not data.smart_contract_address or len(data.smart_contract_address) < 10:
        return False

    # Simulate random model failures (for testing)
    # In production, remove this and use actual model logic
    # return random.random() > 0.2  # 80% success rate

    # For now, always return True (model always succeeds)
    # Replace with actual model logic
    return True


class HistoryResponse(BaseModel):
    """Response model for history endpoint"""
    id: int
    smart_contract_address: str
    created_at: datetime
    request_headers: Optional[Dict[str, Any]] = None
    response_status: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


@app.get("/history", tags=["history"], response_model=List[HistoryResponse])
async def get_history(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
) -> List[HistoryResponse]:
    """
    Get history of all requests.

    Returns a list of all requests stored in the database.
    """
    try:
        result = await db.execute(
            select(RequestHistory)
            .order_by(RequestHistory.timestamp.desc())
            .limit(limit)
        )
        history_records = result.scalars().all()
        return [HistoryResponse.model_validate(record) for record in history_records]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )
