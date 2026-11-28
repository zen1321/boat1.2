# logic/snapshot_exporter.py
from datetime import datetime
import json
from typing import Any, Dict, List, Optional


def build_prediction_snapshot(
    venue_name: str,
    race_no: int,
    logic_type: str,
    weather_info: Dict[str, Any],
    predictions: List[Dict[str, Any]],
    betting_info: Dict[str, Any],
    race_date: Optional[str] = None,
) -> Dict[str, Any]:
    """予測結果一式から結果比較用のJSONスナップショット辞書を生成する。

    Args:
        venue_name: 競艇場名（例: "大村", "江戸川"）
        race_no: レース番号（1〜12）
        logic_type: 使用ロジック種別（"standard" / "edogawa" など）
        weather_info: 風向・風速・潮位・安定板フラグなどの環境条件辞書
        predictions: 各艇の予測順位・艇番・進入コース・総合スコア・内訳などのリスト
        betting_info: 展開予想や推奨買い目フォーメーションなどの辞書
        race_date: 開催日（"YYYY-MM-DD"）。未指定時は当日日付を使用

    Returns:
        スナップショット用の辞書データ
    """
    now = datetime.now()
    target_date = race_date or now.strftime("%Y-%m-%d")
    date_compact = target_date.replace("-", "")
    snapshot_id = f"{date_compact}_{venue_name}_{int(race_no)}R_{int(now.timestamp())}"

    return {
        "schema_version": "1.0",
        "snapshot_id": snapshot_id,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "logic_type": logic_type,
        "race_info": {
            "date": target_date,
            "venue_name": venue_name,
            "race_no": int(race_no),
        },
        "conditions": weather_info,
        "predictions": predictions,
        "betting": betting_info,
    }


def snapshot_to_json_bytes(snapshot: Dict[str, Any]) -> bytes:
    """スナップショット辞書をUTF-8のJSONバイト列に変換する。"""
    return json.dumps(snapshot, ensure_ascii=False, indent=2).encode("utf-8")


def build_snapshot_filename(snapshot: Dict[str, Any]) -> str:
    """ダウンロード時のファイル名（例: pred_2026-11-25_大村_12R_standard.json）を生成する。"""
    info = snapshot.get("race_info", {})
    r_date = info.get("date", datetime.now().strftime("%Y-%m-%d"))
    venue = info.get("venue_name", "unknown")
    race_no = info.get("race_no", 0)
    logic_type = snapshot.get("logic_type", "standard")
    return f"pred_{r_date}_{venue}_{race_no}R_{logic_type}.json"