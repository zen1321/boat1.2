from typing import Dict


def calculate_tide_score(course: int, tide_state: str) -> float:
    """進入コースと潮の状態（満潮/干潮）に応じたスコアを算出

    :param course: 進入コース (1~6)
    :param tide_state: 潮の状態 ('満潮', '干潮' など)
    :return: 潮影響スコア (float)
    """
    # 満潮時
    if tide_state in ["満潮", "満潮時"]:
        scores = {1: 1.0, 2: -1.0, 3: -1.0, 4: -1.0, 5: -1.0, 6: -1.0}
        return scores.get(course, 0.0)

    # 干潮時
    elif tide_state in ["干潮", "干潮時"]:
        scores = {1: 0.0, 2: 0.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 0.0}
        return scores.get(course, 0.0)

    return 0.0


def calculate_race_tide_scores(tide_state: str) -> Dict[int, float]:
    """1レース分（1〜6コース）の潮スコアを一括算出"""
    return {c: calculate_tide_score(c, tide_state) for c in range(1, 7)}