from data.racer_repository import get_water_type_from_db

# ==========================================
# 勝率スコア算出の重み付け係数・閾値設定
# ==========================================
# 当地勝率が未設定(0)の場合に全国勝率から換算する係数
LOCAL_ZERO_FALLBACK_RATIO = 0.8

# 静水時の重み付け
CALM_NATIONAL_WEIGHT = 1.0
CALM_LOCAL_WEIGHT = 0.5

# 難水時の重み付け
ROUGH_NATIONAL_WEIGHT = 0.5
ROUGH_LOCAL_WEIGHT = 1.0


def calculate_win_rate_score(
    national_win_rate: float, local_win_rate: float, venue: str = "多摩川"
) -> float:
    """全国勝率・当地勝率・水面タイプ（静水/難水）から勝率スコアを算出する

    :param national_win_rate: 全国勝率 (例: 6.50)
    :param local_win_rate: 当地勝率 (例: 7.20)
    :param venue: 競艇場名 (例: '江戸川') または 水面タイプ ('静水', '難水')
    :return: 勝率スコア (float)
    """
    # 当地勝率が0の場合の代用値設定
    is_local_zero = float(local_win_rate or 0.0) == 0.0
    if is_local_zero:
        calc_local_win_rate = float(national_win_rate or 0.0) * LOCAL_ZERO_FALLBACK_RATIO
    else:
        calc_local_win_rate = float(local_win_rate)

    # venueに水面タイプが直接指定されているか、競艇場名が渡されたかを判断
    if venue in ["静水", "難水"]:
        water_type = venue
    else:
        water_type = get_water_type_from_db(venue)

    # 静水の場合
    if water_type == "静水":
        score = (national_win_rate * CALM_NATIONAL_WEIGHT) + (calc_local_win_rate * CALM_LOCAL_WEIGHT)
        return round(score, 2)

    # 難水の場合（当地技巧補正を排除し、重み付け計算のみを実施）
    elif water_type == "難水":
        score = (
            (national_win_rate * ROUGH_NATIONAL_WEIGHT)
            + (calc_local_win_rate * ROUGH_LOCAL_WEIGHT)
        )
        return round(score, 2)

    # バックアップ（デフォルトは静水計算）
    return round((national_win_rate * CALM_NATIONAL_WEIGHT) + (calc_local_win_rate * CALM_LOCAL_WEIGHT), 2)