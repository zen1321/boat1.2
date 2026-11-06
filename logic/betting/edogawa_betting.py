from typing import Dict, List, Tuple, Any

def generate_edogawa_formation(
    boat_scores: Dict[int, float], 
    weather_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    各艇の総合スコアと江戸川の気象・水面コンディション（潮、波速等）を基に、
    専用の3連単フォーメーションおよび信頼度を算出して返す。
    
    :param boat_scores: {1: 85.5, 2: 82.0, ...} (各艇の総合スコア)
    :param weather_info: {"tide_direction": "下げ潮", "wave_speed": "強", ...}
    :return: 買い目判定結果辞書
    """
    if len(boat_scores) < 6:
        raise ValueError("6艇分のスコアデータが必要です。")

    # スコアが高い順にソート (艇番号, スコア)
    sorted_boats = sorted(boat_scores.items(), key=lambda x: x[1], reverse=True)
    
    rank1_boat, rank1_score = sorted_boats[0]
    rank2_boat, rank2_score = sorted_boats[1]
    
    tide = weather_info.get("tide_direction", "")
    wave_speed = weather_info.get("wave_speed", "無")

    # 【1着の選定】原則は最高スコア艇
    # 江戸川の特殊条件：下げ潮かつ波速が「強」または「弱」で、1位と2位が僅差（<= 1.5pt）の場合の逆転考慮
    chassis_1st = rank1_boat
    if "下げ潮" in tide and wave_speed in ["弱", "強"]:
        if (rank1_score - rank2_score) <= 1.5:
            chassis_1st = rank2_boat

    # 【2着の選定】2位のスコアから「2.0pt以内」の選手（1着に選ばれた艇を除く）
    candidates_2nd = []
    for boat, score in sorted_boats:
        if boat == chassis_1st:
            continue
        if (rank2_score - score) <= 2.0 or score >= (rank2_score - 2.0):
            candidates_2nd.append(boat)
            
    # 【3着の選定】2位のスコアから「4.0pt以内」の選手（1着に選ばれた艇を除く）
    candidates_3rd = []
    for boat, score in sorted_boats:
        if boat == chassis_1st:
            continue
        if (rank2_score - score) <= 4.0 or score >= (rank2_score - 4.0):
            candidates_3rd.append(boat)

    candidates_2nd = list(dict.fromkeys(candidates_2nd))
    candidates_3rd = list(dict.fromkeys(candidates_3rd))

    # 【買い目（3連単フォーメーション文字列）の生成】
    tickets = []
    for b2 in candidates_2nd:
        for b3 in candidates_3rd:
            if b2 != b3:
                tickets.append(f"{chassis_1st}-{b2}-{b3}")

    # 信頼度の判定（荒れ水面や点差による判定）
    score_gap = rank1_score - rank2_score
    if wave_speed == "強" or score_gap < 1.0:
        confidence = "LOW"
        policy = "難水面・大混戦のため、フォーメーションを広めに回収率重視で狙います。"
    elif wave_speed == "弱" or (1.0 <= score_gap < 2.5):
        confidence = "MEDIUM"
        policy = "上位拮抗の展開。軸を信頼しつつ相手を少し手広く押さえます。"
    else:
        confidence = "HIGH"
        pattern_name = "上位の力上位"
        policy = "スコア差がついており本命サイド中心の組み立て。"

    formatted_bets = []
    total_combos = len(tickets)
    if total_combos > 0:
        weight_per_bet = round(100 / total_combos, 1)
        for t in tickets:
            formatted_bets.append({
                "bet": t,
                "weight": weight_per_bet
            })

    return {
        "confidence": confidence,
        "primary_development": f"江戸川水面 (波:{wave_speed}, 潮:{tide})",
        "development_rank": "A" if confidence == "HIGH" else ("B" if confidence == "MEDIUM" else "C"),
        "betting_policy": policy,
        "recommended_bets": formatted_bets,
        "chassis_1st": chassis_1st,
        "candidates_2nd": candidates_2nd,
        "candidates_3rd": candidates_3rd,
    }