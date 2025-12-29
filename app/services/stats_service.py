from statistics import mean
from typing import Dict, List, Optional


def _quantile(values: List[int], q: float) -> Optional[float]:
    if not values:
        return None
    values_sorted = sorted(values)
    idx = int(round(q * (len(values_sorted) - 1)))
    return float(values_sorted[idx])


def build_stats(
    processing_times: List[int],
    bytecode_lengths: List[int],
) -> Dict[str, Dict[str, Optional[float]]]:
    stats = {
        "processing_time_ms": {
            "mean": float(mean(processing_times)) if processing_times else None,
            "p50": _quantile(processing_times, 0.50),
            "p95": _quantile(processing_times, 0.95),
            "p99": _quantile(processing_times, 0.99),
            "count": len(processing_times),
        },
        "bytecode_length": {
            "mean": float(mean(bytecode_lengths)) if bytecode_lengths else None,
            "p50": _quantile(bytecode_lengths, 0.50),
            "p95": _quantile(bytecode_lengths, 0.95),
            "p99": _quantile(bytecode_lengths, 0.99),
            "count": len(bytecode_lengths),
        },
    }
    return stats
