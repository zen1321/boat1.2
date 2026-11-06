import sys
from pathlib import Path
import streamlit as st

# プロジェクトルートを Python パスに追加
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

st.set_page_config(
    page_title="ボートレース総合予測",
    page_icon="🚤",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

# 初期表示を sub_page01 に設定
if "current_page" not in st.session_state:
    st.session_state.current_page = "sub_page01"

# 各ページオブジェクトの生成（sub_page01 を先に配置）
program_data_page = st.Page(
    BASE_DIR / "pages" / "programDataManagementPage.py",
    title="番組データ管理・読込",
    icon="⚙️"
)

score_prediction_page = st.Page(
    BASE_DIR / "pages" / "scorePredictionPage.py",
    title="総合スコア予測",
    icon="🚤"
)

# app.py の抜粋・修正例
edogawa_page = st.Page(
    BASE_DIR / "pages" / "edogawaPredictionPage.py",
    title="江戸川専用予測",
    icon="🌊"
)

# ナビゲーションの初期化
pg = st.navigation([program_data_page, score_prediction_page, edogawa_page])
pg.run()