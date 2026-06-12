from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import pandas as pd
from pyevmasm import disassemble_all

from app.features.evm_extractor import EVMBytecodeFeatureExtractor

_ARTIFACTS = Path(__file__).resolve().parents[1] / "models_artifacts"

_XGB_MODEL = None       # бинарный классификатор (70 фичей → is_vulnerable)
_VECTORIZER = None      # CountVectorizer(2000, ngram=(1,3)) для опкодов
_RFC_MODEL = None       # RFC на опкодах → oof_vuln_proba
_LGBM_MODEL = None      # MultiOutputClassifier(LGBM) (69 фичей → 8 классов)

# Экстрактор (70 фичей) — тот же, что использовался для обучения XGB
_EXTRACTOR = EVMBytecodeFeatureExtractor(n_workers=1)

# Фичи, которых нет в LGBM (были в XGB, но исключены из LGBM)
_LGBM_DROP_COLS = {"reads_from_memory", "writes_to_memory", "memory_access_ratio"}

# 8 классов уязвимостей (алфавитный порядок из MultiLabelBinarizer)
VULN_CLASSES = [
    "access-control",
    "arithmetic",
    "bad-randomness",
    "double-spending",
    "locked-ether",
    "other",
    "reentrancy",
    "unchecked-calls",
]


def _load_models() -> None:
    global _XGB_MODEL, _VECTORIZER, _RFC_MODEL, _LGBM_MODEL
    if _XGB_MODEL is None:
        _XGB_MODEL = joblib.load(_ARTIFACTS / "num_xgb_model_2025-12-28_14-34.pkl")
    if _VECTORIZER is None:
        _VECTORIZER = joblib.load(_ARTIFACTS / "count_vectorizer_2000_1_3.pkl")
    if _RFC_MODEL is None:
        _RFC_MODEL = joblib.load(_ARTIFACTS / "rfc_proba_predictor_default.pkl")
    if _LGBM_MODEL is None:
        _LGBM_MODEL = joblib.load(_ARTIFACTS / "best_lgbm_model_macro.pkl")


def _extract_opcode_text(bytecode: str) -> str:
    """Преобразует hex-байткод в строку мнемоник через пробел."""
    bytecode = bytecode.strip()
    if bytecode.startswith("0x"):
        bytecode = bytecode[2:]
    if not bytecode:
        return ""
    try:
        bytecode_bytes = bytes.fromhex(bytecode)
        instructions = list(disassemble_all(bytecode_bytes))
        return " ".join(instr.mnemonic for instr in instructions)
    except Exception:
        return ""


def _to_native(value: Any) -> Any:
    return value.item() if hasattr(value, "item") else value


def predict_with_features(bytecode: str) -> Tuple[List[str], Dict[str, Any]]:
    """
    Пайплайн классификации байткода:

    1. EVMBytecodeFeatureExtractor → 70 числовых фичей
    2. XGBClassifier(70) → is_vulnerable (бинарный флаг)
    3. CountVectorizer(2000) + RFC → oof_vuln_proba (вероятность)
    4. 67 base-фичей + is_vulnerable + oof_vuln_proba = 69 → LGBM MultiOutputClassifier
    5. Маппинг 8 бинарных флагов на названия классов уязвимостей

    Возвращает: (список_классов, словарь_числовых_признаков_для_БД)
    """
    _load_models()

    # 1. Числовые фичи (70)
    df = pd.DataFrame([{"bytecode": bytecode}])
    features_70: pd.DataFrame = _EXTRACTOR.transform(df)

    # 2. XGB → is_vulnerable
    is_vulnerable = int(_XGB_MODEL.predict(features_70)[0])

    # 3. Опкоды → CountVectorizer → RFC → oof_vuln_proba
    opcode_text = _extract_opcode_text(bytecode)
    opcode_vec = _VECTORIZER.transform([opcode_text])
    oof_vuln_proba = float(_RFC_MODEL.predict_proba(opcode_vec)[0, 1])

    # 4. Строим 69-фичевый вектор для LGBM
    lgbm_input = features_70.drop(
        columns=[c for c in _LGBM_DROP_COLS if c in features_70.columns]
    ).copy()
    lgbm_input["is_vulnerable"] = is_vulnerable
    lgbm_input["oof_vuln_proba"] = oof_vuln_proba

    # 5. Предсказание классов
    prediction_array = _LGBM_MODEL.predict(lgbm_input)[0]
    predicted_classes: List[str] = [
        cls for cls, flag in zip(VULN_CLASSES, prediction_array) if int(flag) == 1
    ]

    # Числовые фичи для ContractMetadata (только те, что есть в схеме)
    base_row = features_70.iloc[0].to_dict()
    features_dict = {key: _to_native(val) for key, val in base_row.items()}

    return predicted_classes, features_dict
