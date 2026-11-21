from typing import Dict


def calculate_wind_score(
    course: int, wind_direction: str, wind_speed: float
) -> float:
    """進入コース・風向・風速に応じたスコアを算出

    :param course: 進入コース (1~6)
    :param wind_direction: 風向 ('追い風', '向かい風' など)
    :param wind_speed: 風速 (m)
    :return: 風影響スコア (float)
    """
    if wind_speed < 4.0:
        return 0.0  # 4m未満は影響なし

    # 追い風 4m以上（1コース減点、2・3コース加点、4〜6コース加点）
    if wind_direction in ["追い風", "追風"]:
        scores = {1: -0.5, 2: 1.5, 3: 1.5, 4: 1.0, 5: 1.0, 6: 1.0}
        return scores.get(course, 0.0)

    # 向かい風 4m以上
    elif wind_direction in ["向かい風", "向風"]:
        scores = {1: 0.0, 2: 0.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0}
        return scores.get(course, 0.0)

    return 0.0


def calculate_race_wind_scores(
    wind_direction: str, wind_speed: float
) -> Dict[int, float]:
    """1レース分（1〜6コース）の風スコアを一括算出"""
    return {
        c: calculate_wind_score(c, wind_direction, wind_speed)
        for c in range(1, 7)
    }