import json
from pathlib import Path
from typing import Any, Dict, List

# water_conditions.json のパス設定
WATER_JSON_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data_json" / "water_conditions.json"
)

def _load_water_master() -> List[Dict[str, Any]]:
    """water_conditions.json から水面条件データを読み込む"""
    if not WATER_JSON_PATH.exists():
        return []
    try:
        with open(WATER_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def calc_water_score(wind_dir: str, wind_speed: int, tide_dir: str, wave_speed: str, boat_num: int) -> float:
    """水面条件データ（JSON）から該当する艇の加点値を取得する"""
    conditions = _load_water_master()
    
    matched = None
    for cond in conditions:
        if (cond.get("wind_dir") == wind_dir and 
            cond.get("wind_speed") == wind_speed and 
            cond.get("tide_dir") == tide_dir and 
            cond.get("wave_speed") == wave_speed):
            matched = cond
            break
            
    if not matched:
        return 0.0
        
    score_key = f"boat_{boat_num}_score"
    return float(matched.get(score_key, 0.0))

def calculate_race_edogawa_water_scores(weather_info: Dict[str, Any]) -> Dict[int, float]:
    """1レース分（1~6号艇）の水面・気象補正スコアを一括算出する"""
    wind_dir = weather_info.get("wind_direction", "無風")
    wind_speed = int(weather_info.get("wind_speed", 0))
    tide_dir = weather_info.get("tide_direction", "潮止まり")
    wave_speed = weather_info.get("wave_speed", "無")

    scores = {}
    for pit in range(1, 7):
        scores[pit] = calc_water_score(
            wind_dir=wind_dir,
            wind_speed=wind_speed,
            tide_dir=tide_dir,
            wave_speed=wave_speed,
            boat_num=pit
        )
    return scores


# ==========================================
# 江戸川専用 展示タイム評価ロジック
# ==========================================
def calculate_edogawa_exhibition_scores(
    ex_times: List[float], wave_speed: str, wind_speed: int
) -> List[float]:
    """江戸川専用の展示タイム評価スコアを算出する（難水面時はスコアを軽減）"""
    scores = [0.0] * 6
    
    # 波速が「強」または風速が5m以上の場合は難水面（信頼度低下）と判定してスコアを50%割引
    is_unreliable_water = (wave_speed == "強") or (wind_speed >= 5)

    valid_times = []
    for t in ex_times:
        try:
            valid_times.append(float(t))
        except (ValueError, TypeError):
            valid_times.append(6.80)  # 欠損時のデフォルトタイム
            
    # ソートしてユニークなタイム一覧を作成（タイムが小さいほど上位）
    sorted_unique_times = sorted(list(set(valid_times)))
    
    for i in range(6):
        t = valid_times[i]
        rank = sorted_unique_times.index(t) + 1
        
        # 配点ルール
        if rank == 1:
            base_score = 1.5
        elif rank == 2:
            base_score = 0.5
        elif 3 <= rank <= 5:
            base_score = 0.0
        else:  # 6位以降
            base_score = -1.0
            
        # 難水面時は影響度50%割引
        if is_unreliable_water:
            base_score *= 0.5
            
        scores[i] = round(base_score, 2)
        
    return scores