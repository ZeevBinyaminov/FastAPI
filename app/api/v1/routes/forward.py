import json
from time import perf_counter
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.contract import Contract, ContractMetadata
from app.models.request_history import RequestHistory
from app.schemas.forward import ForwardRequest
from app.services.evm_inference import predict_with_features

router = APIRouter()


@router.post("/forward", tags=["forward"])
async def forward(
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(
        None, description="Authorization header"),
    x_bytecode: Optional[str] = Header(
        None,
        alias="X-Bytecode",
        description="EVM bytecode as hex string (0x...)",
    ),
) -> Dict[str, Any]:
    """Forward endpoint that accepts JSON or form data."""
    stored_headers = dict(request.headers)
    content_type = (request.headers.get("content-type") or "").lower()

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        text = form.get("text")
        if not x_bytecode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Bytecode header is required",
            )
        data = ForwardRequest(
            bytecode=x_bytecode,
            text=str(text) if text is not None else None,
        )
    else:
        raw_body = await request.body()
        if raw_body and raw_body.strip():
            try:
                payload = json.loads(raw_body)
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="invalid JSON body",
                ) from exc
        else:
            payload = {}
        if not payload and x_bytecode:
            payload = {"bytecode": x_bytecode}
        data = ForwardRequest.model_validate(payload)

    if not data.bytecode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="bytecode is required",
        )
    start_time = perf_counter()
    try:
        prediction, features = predict_with_features(data.bytecode)
        model_success = True
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="model file not found",
        ) from exc
    except Exception as exc:
        model_success = False
        prediction = None
        features = None
    processing_time_ms = int((perf_counter() - start_time) * 1000)

    response_status = "success"
    response_data = None
    text_length = len(data.text) if data.text else None
    token_count = len(data.text.split()) if data.text else None

    if not model_success:
        response_status = "error"
        response_data = {"error": "модель не смогла обработать данные"}

        try:
            history_record = RequestHistory(
                created_at=data.created_at,
                request_headers=None,
                response_status=response_status,
                response_data=response_data,
                processing_time_ms=processing_time_ms,
                input_text_length=text_length,
                input_token_count=token_count,
            )
            db.add(history_record)
            await db.commit()
            print("✓ Failed request saved to history")
        except Exception as exc:
            print(
                f"✗ Error saving failed request to history: {type(exc).__name__}: {exc}")
            try:
                await db.rollback()
            except Exception:
                pass

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="модель не смогла обработать данные",
        )

    response_data = {
        "status": "success",
        "data": data.model_dump(mode="json"),
        "result": {
            "processed": True,
            "created_at": data.created_at.isoformat(),
            "prediction": prediction,
        },
    }

    try:
        contract = Contract(
            bytecode=data.bytecode,
            prediction=int(prediction),
            processing_time_ms=processing_time_ms,
            created_at=data.created_at,
        )
        metadata = ContractMetadata(contract_rel=contract, **(features or {}))
        db.add(contract)
        db.add(metadata)
        await db.commit()
    except Exception as exc:
        print(f"✗ Error saving contract data: {type(exc).__name__}: {exc}")
        try:
            await db.rollback()
        except Exception:
            pass

    try:
        history_record = RequestHistory(
            created_at=data.created_at,
            request_headers=None,
            response_status=response_status,
            response_data=response_data,
            processing_time_ms=processing_time_ms,
            input_text_length=text_length,
            input_token_count=token_count,
        )
        db.add(history_record)
        await db.commit()
        print("✓ Request saved to history")
    except Exception as exc:
        print(f"✗ Error saving to history: {type(exc).__name__}: {exc}")
        try:
            await db.rollback()
        except Exception:
            pass

    return response_data
