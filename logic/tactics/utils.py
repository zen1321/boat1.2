from typing import Any, Dict, List, Optional


def _safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    """欠損値('-', None, 0.0等)を安全にfloatまたはNoneへ変換する"""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        v = float(val)
        return v if v > 0.0 else default
    try:
        s = str(val).strip()
        if not s or s in ("-", "None", "null", "0", "0.0"):
            return default
        v = float(s)
        return v if v > 0.0 else default
    except (ValueError, TypeError):
        return default


def _get_st_val(d: Dict[str, Any]) -> float:
    """直前STを優先取得し、欠損時は平均STで代替する"""
    ex_st = _safe_float(d.get("exhibition_st"))
    if ex_st is not None:
        return ex_st
    avg_st = _safe_float(d.get("avg_st"))
    return avg_st if avg_st is not None else 0.15


def _get_rank_ascending(values: List[Optional[float]], target_val: Optional[float]) -> int:
    """タイム等の値が小さい（早い）順の順位を算出する（欠損時は最下位6位）"""
    if target_val is None:
        return 6
    valid_vals = [v for v in values if v is not None]
    if not valid_vals:
        return 6
    sorted_unique = sorted(list(set(valid_vals)))
    return sorted_unique.index(target_val) + 1 if target_val in sorted_unique else 6