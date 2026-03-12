"""
AQUA中古車 検索条件設定
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ===== 検索条件 =====
SEARCH_CRITERIA = {
    "maker_code": "TO",        # メーカーコード (TO = Toyota)
    "model": "AQUA",           # 車種
    "max_price": 110,          # 最大価格 (万円)
    "max_mileage": 60000,      # 最大走行距離 (km)
    "min_year": 2014,          # 最小年式
    "no_repair": True,         # 修復歴なし
    "kansai_prefs": {          # 関西エリア (都道府県コード)
        "25": "滋賀",
        "26": "京都",
        "27": "大阪",
        "28": "兵庫",
        "29": "奈良",
        "30": "和歌山",
    },
    "required_options": [
        "バックモニター",
        "衝突軽減ブレーキ",
        "Bluetooth",
    ],
}

# ===== ドラレコ関連 =====
DASHCAM_COST = int(os.getenv("DASHCAM_COST", "15000"))  # 円
DASHCAM_KEYWORDS = ["ドラレコ", "ドライブレコーダー", "ドライブレコーダ"]

# ===== お得度スコアリング =====
# 基準価格テーブル (年式別) ※市場相場感
REFERENCE_PRICES = {
    2014: 75,
    2015: 80,
    2016: 85,
    2017: 90,
    2018: 95,
    2019: 100,
    2020: 105,
    2021: 110,
    2022: 120,
    2023: 130,
}

# お得と判定するしきい値 (基準価格の何%以下ならお得)
GOOD_DEAL_THRESHOLD = 0.88

# ===== 通知設定 =====
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")

# ===== データ保存先 =====
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SEEN_CARS_FILE = os.path.join(DATA_DIR, "seen_cars.json")
GOOD_DEALS_FILE = os.path.join(DATA_DIR, "good_deals.json")
ALERT_LOG_FILE = os.path.join(DATA_DIR, "alert_log.json")
