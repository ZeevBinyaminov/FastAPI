from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import pandas as pd

from app.features.evm_extractor import EVMBytecodeFeatureExtractor

_MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models_artifacts"
    / "num_xgb_model_2025-12-28_14-34.pkl"
)
_MODEL = None
_EXTRACTOR = EVMBytecodeFeatureExtractor(n_workers=1)


def _load_model() -> Any:
    global _MODEL
    if _MODEL is None:
        _MODEL = joblib.load(_MODEL_PATH)
    return _MODEL


def _to_native(value: Any) -> Any:
    return value.item() if hasattr(value, "item") else value


def extract_features(bytecode: str) -> Dict[str, Any]:
    features = _EXTRACTOR.transform(pd.DataFrame([{"bytecode": bytecode}]))
    row = features.iloc[0].to_dict()
    return {key: _to_native(val) for key, val in row.items()}


def predict_bytecode_class(bytecode: str) -> Any:
    model = _load_model()
    features = _EXTRACTOR.transform(pd.DataFrame([{"bytecode": bytecode}]))
    prediction = model.predict(features)[0]
    return _to_native(prediction)


def predict_with_features(bytecode: str) -> Tuple[Any, Dict[str, Any]]:
    model = _load_model()
    features = _EXTRACTOR.transform(pd.DataFrame([{"bytecode": bytecode}]))
    prediction = model.predict(features)[0]
    row = features.iloc[0].to_dict()
    return _to_native(prediction), {key: _to_native(val) for key, val in row.items()}
