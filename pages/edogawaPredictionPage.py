import sys
from pathlib import Path

# プロジェクトルートを Python パスに追加
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import streamlit as st
from data.racer_course_repository import get_racer_basic_info
from data.venue_repository import get_all_venues
from logic.racer.win_rate_score import calculate_win_rate_score

# 江戸川専用ロジックのインポート
from logic.venue.edogawa import (
    calculate_race_edogawa_water_scores,
    calculate_edogawa_exhibition_scores
)
from logic.betting.edogawa_betting import generate_edogawa_formation

# --- タイトル ＆ 画面遷移 ---
st.title("🌊 ボートレース江戸川 総合スコア予測（難水面・水流特化）")

col_head1, col_head2 = st.columns([7, 3])
with col_head1:
    st.caption("江戸川専用の風・水流条件と展示データを入力し、専用ロジックで予測と買い目を算出します。")
with col_head2:
    if st.button("⬅️ 管理画面へ戻る", type="secondary", use_container_width=True):
        st.switch_page("pages/programDataManagementPage.py")

st.markdown("---")

# ------------------------------------------------------------------------------
# 1. 江戸川専用の気象・水面（水流）条件設定エリア
# ------------------------------------------------------------------------------
st.subheader("⚙️ 江戸川 水面・気象コンディション設定")

selected_venue = "江戸川"

col_env1, col_env2, col_env3, col_env4 = st.columns(4)

with col_env1:
    wind_dir = st.selectbox(
        "風向",
        ["追い風", "向かい風", "横風", "無風"],
        key="edo_wind_dir"
    )

with col_env2:
    wind_speed_label = st.selectbox(
        "風速",
        ["0m", "5m未満", "5m以上"],
        key="edo_wind_spd_label"
    )
    if wind_speed_label == "0m":
        wind_speed = 0
    elif wind_speed_label == "5m未満":
        wind_speed = 1
    else:
        wind_speed = 5

with col_env3:
    tide_dir = st.selectbox(
        "潮流向",
        ["上げ潮", "下げ潮", "潮止まり"],
        key="edo_tide_dir"
    )

with col_env4:
    wave_speed_label = st.selectbox(
        "波速",
        ["0cm", "30cm未満", "30cm以上"],
        key="edo_wave_spd_label"
    )
    if wave_speed_label == "0cm":
        wave_speed = "無"
    elif wave_speed_label == "30cm未満":
        wave_speed = "弱"
    else:
        wave_speed = "強"

# 安定板装着オプションの追加
is_stabilizer = st.checkbox("⚙️ 安定板装着（当地勝率に1.2倍の補正を適用）", key="edo_is_stabilizer")

edogawa_weather_info = {
    "venue": selected_venue,
    "wind_direction": wind_dir,
    "wind_speed": wind_speed,
    "tide_direction": tide_dir,
    "wave_speed": wave_speed,
}

st.markdown("---")

# ------------------------------------------------------------------------------
# 2. データ入力グリッド（江戸川仕様: 展示タイム・直線・ST）
# ------------------------------------------------------------------------------
index_items = [
    "登録番号",
    "名前",
    "ランク",
    "2連対率",
    "今期",
    "全国",
    "当地",
    "展示",      # 展示タイム
    "ST",        # 展示ST
]
columns = [f"{i+1}号艇" for i in range(6)]

if "edo_grid_df" not in st.session_state:
    st.session_state.edo_grid_df = pd.DataFrame(
        "", index=index_items, columns=columns, dtype=object
    )

st.subheader("📋 江戸川用データ貼り付け・入力")
raw_text = st.text_area(
    label="コピペ用エリア",
    key="edo_input_text",
    height=100,
    placeholder="データを貼り付け...",
    label_visibility="collapsed",
)

col_b1, col_b2, _ = st.columns([2, 2, 6])
with col_b1:
    if st.button("📥 表に反映する", type="primary", use_container_width=True):
        if raw_text.strip():
            import re
            lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]
            for r, line in enumerate(lines):
                row_values = [v.strip() for v in re.split(r"\s+", line) if v.strip()]
                if not row_values:
                    continue
                first_val = row_values[0]
                if first_val in index_items:
                    target_row_idx = index_items.index(first_val)
                    clean_values = row_values[1:]
                else:
                    target_row_idx = min(r, len(index_items) - 1)
                    clean_values = row_values

                if target_row_idx < len(index_items):
                    cols_to_copy = min(len(clean_values), 6)
                    for c in range(cols_to_copy):
                        val_str = str(clean_values[c]).strip().replace("%", "").replace("％", "")
                        st.session_state.edo_grid_df.iloc[target_row_idx, c] = val_str

            # 選手基本情報の補完
            toban_idx = index_items.index("登録番号")
            name_idx = index_items.index("名前")
            rank_idx = index_items.index("ランク")
            st_idx = index_items.index("今期")

            for c in range(6):
                toban_val = str(st.session_state.edo_grid_df.iloc[toban_idx, c]).strip()
                if toban_val:
                    info = get_racer_basic_info(toban_val)
                    if info["name"]:
                        st.session_state.edo_grid_df.iloc[name_idx, c] = info["name"]
                    if info["rank"]:
                        st.session_state.edo_grid_df.iloc[rank_idx, c] = info["rank"]
                    if info["st_avg"]:
                        st.session_state.edo_grid_df.iloc[st_idx, c] = info["st_avg"]

            st.success("データを反映し、選手情報を補完しました！")
            st.rerun()
        else:
            st.warning("テキストが入力されていません。")

with col_b2:
    if st.button("🧹 表をリセット", use_container_width=True):
        st.session_state.edo_grid_df = pd.DataFrame(
            "", index=index_items, columns=columns, dtype=object
        )
        st.rerun()

edited_edo_df = st.data_editor(
    st.session_state.edo_grid_df,
    num_rows="fixed",
    use_container_width=True,
    key="edo_boat_editor",
)
st.session_state.edo_grid_df = edited_edo_df

# ------------------------------------------------------------------------------
# 3. 進入コース設定
# ------------------------------------------------------------------------------
st.markdown("---")
st.markdown("#### 🧭 進入コース設定")
course_cols = st.columns(6)
updated_edo_courses = []

for i, col in enumerate(course_cols):
    pit_no = i + 1
    with col:
        c = st.selectbox(f"{pit_no}号艇", [1, 2, 3, 4, 5, 6], index=pit_no - 1, key=f"edo_course_{pit_no}")
        updated_edo_courses.append(c)

# ------------------------------------------------------------------------------
# 4. 江戸川専用予測の実行
# ------------------------------------------------------------------------------
st.markdown("---")
if st.button("🚀 江戸川専用の予測を実行", type="primary", use_container_width=True):
    try:
        def safe_float(val, default=0.0):
            try:
                return float(val) if str(val).strip() != "" else default
            except (ValueError, TypeError):
                return default

        # 1. 各種リポジトリおよびロジックのインポート
        from data.racer_repository import (
            get_rank_score_from_db,
            get_motor_score_from_db,
            get_venue_type_from_db
        )
        from data.venue_repository import get_course_score
        
        # 勝率スコア算出ロジックのインポート
        from logic.racer.win_rate_score import calculate_win_rate_score
        
        # 平均STスコア算出ロジックのインポート
        from logic.racer.avg_st_score import calculate_avg_st_score
        
        # 【追加】展示STスコア算出ロジックのインポート
        from logic.exhibition.exhibition_st_score import calculate_race_exhibition_st_scores

        venue_type = get_venue_type_from_db("江戸川")

        # 水面・気象スコアの取得（JSON連動）
        water_scores = calculate_race_edogawa_water_scores(edogawa_weather_info)

        # 各艇の展示タイムリスト作成
        ex_times = []
        for pit_no in range(1, 7):
            col_data = edited_edo_df[f"{pit_no}号艇"]
            ex_times.append(safe_float(col_data.get("展示"), 6.70))

        # 江戸川専用展示評価スコアの算出（タイム速さベース）
        ex_scores = calculate_edogawa_exhibition_scores(
            ex_times=ex_times,
            wave_speed=wave_speed,
            wind_speed=wind_speed
        )

        # 【追加】展示STスコア用のデータリスト作成
        race_st_data = []
        for pit_no in range(1, 7):
            col_data = edited_edo_df[f"{pit_no}号艇"]
            ex_st_val_raw = str(col_data.get("ST", "")).strip()
            
            # F（フライング）や欠損の判定
            is_f = "f" in ex_st_val_raw.lower() or safe_float(ex_st_val_raw, 0.15) < 0.0
            
            # 数値変換（Fや"-"の場合は 0.0 や負の値にするなど安全に処理）
            if is_f:
                ex_st_float = -0.01
            elif ex_st_val_raw == "" or ex_st_val_raw == "-":
                ex_st_float = 0.0
            else:
                ex_st_float = safe_float(ex_st_val_raw, 0.15)

            # 今期平均STの取得
            avg_st_val = safe_float(col_data.get("今期"), 0.15)

            race_st_data.append({
                "pit_no": pit_no,
                "exhibition_st": ex_st_float,
                "avg_st": avg_st_val,
                "is_flying": is_f
            })

        # exhibition_st_score.py を用いた全艇の展示STスコア算出
        ex_st_results = calculate_race_exhibition_st_scores(race_st_data)
        # 艇番(1~6)をキーにした辞書に変換
        ex_st_dict = {res["pit_no"]: res for res in ex_st_results}

        results_list = []
        for i in range(6):
            pit_no = i + 1
            chosen_course = updated_edo_courses[i]
            col_data = edited_edo_df[f"{pit_no}号艇"]

            # 各種生データの取得
            r_rank = str(col_data.get("ランク", "")).strip() or "B1"
            nat_win = safe_float(col_data.get("全国"), 5.0)
            loc_win = safe_float(col_data.get("当地"), 5.0)
            motor_rate = safe_float(col_data.get("2連対率"), 30.0)
            avg_st_val = safe_float(col_data.get("今期"), 0.15)

            # --- 各種スコアの算出 ---
            rank_score = get_rank_score_from_db(r_rank)
            motor_score = get_motor_score_from_db(motor_rate, venue_type)
            course_score = get_course_score("江戸川", chosen_course)
            
            # 勝率スコアの算出
            win_score = calculate_win_rate_score(
                nat_win, 
                loc_win, 
                venue="江戸川", 
                is_stabilizer=edogawa_weather_info.get("is_stabilizer", False)
            )
            
            # 平均STスコアの算出
            st_score = calculate_avg_st_score(avg_st_val)

            # 選手基本小計（階級 + 勝率 + モーター + 平均ST + コース）
            racer_base_subtotal = round(rank_score + win_score + motor_score + st_score + course_score, 2)

            # 【変更】展示STスコアを exhibition_st_score.py の結果から取得
            ex_st_score = ex_st_dict[pit_no]["exhibition_st_score"]

            # 展示評価スコア（江戸川専用展示タイム評価）
            ex_eval_score = ex_scores[i]

            # 風＋水面スコア（江戸川専用JSON連動）
            wind_tide_score = water_scores.get(pit_no, 0.0)

            # 総合スコア合算
            total_score = round(racer_base_subtotal + ex_eval_score + ex_st_score + wind_tide_score, 2)

            results_list.append({
                "pit_no": pit_no,
                "entry_course": chosen_course,
                "total_score": total_score,
                "racer_base_subtotal": racer_base_subtotal,
                "rank_score": rank_score,
                "win_score": win_score,
                "motor_score": motor_score,
                "st_score": st_score,
                "course_score": course_score,
                "ex_eval_score": ex_eval_score,
                "ex_st_score": ex_st_score,
                "wind_tide_score": wind_tide_score,
            })

        # 予測順位の付与
        results_list.sort(key=lambda x: x["total_score"], reverse=True)
        for idx, r in enumerate(results_list):
            r["predicted_rank"] = idx + 1

        boat_scores = {r["pit_no"]: r["total_score"] for r in results_list}

        # 江戸川専用買い目の生成
        edogawa_result = generate_edogawa_formation(boat_scores, edogawa_weather_info)

        st.success("【江戸川】予測集計が完了しました！")

        # 結果表示：買い目
        st.subheader("🎫 3連単推奨買い目 (江戸川専用フォーメーション)")
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="軸 (1着候補)", value=f"{edogawa_result['chassis_1st']}号艇")
        with col_res2:
            st.metric(label="信頼度", value=edogawa_result["confidence"])
        with col_res3:
            st.metric(label="展開ランク", value=edogawa_result["development_rank"])

        st.info(f"💡 **買い目方針:** {edogawa_result['betting_policy']}")

        bets_list = edogawa_result.get("recommended_bets", [])
        if bets_list:
            df_bets = pd.DataFrame(bets_list)
            df_bets.columns = ["買い目 (3連単)", "推奨配分 (%)"]
            st.dataframe(df_bets, use_container_width=True, hide_index=True)

        st.markdown("---")

        # 総合評価一覧テーブル
        st.subheader("📊 各艇の江戸川総合スコア詳細")
        table_rows = []
        for r in results_list:
            table_rows.append({
                "予測順位": f"{r['predicted_rank']}位",
                "艇番": f"{r['pit_no']}号艇",
                "進入": f"{r['entry_course']}コース",
                "総合スコア": r["total_score"],
                "選手基本": r["racer_base_subtotal"],
                "階級": r["rank_score"],
                "勝率": r["win_score"],
                "モーター": r["motor_score"],
                "平均ST": r["st_score"],
                "コース": r["course_score"],
                "展示": r["ex_eval_score"],
                "展示ST": r["ex_st_score"],
                "風＋水面": r["wind_tide_score"],
            })

        df_results = pd.DataFrame(table_rows)
        st.dataframe(df_results, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"計算中にエラーが発生しました: {e}")