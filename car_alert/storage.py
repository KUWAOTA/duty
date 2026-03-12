"""
車両データ永続化モジュール
- 既出車両の管理 (重複アラート防止)
- お得車両履歴の保存
"""
import json
import logging
import os
from datetime import datetime

from .config import SEEN_CARS_FILE, GOOD_DEALS_FILE, ALERT_LOG_FILE, DATA_DIR

logger = logging.getLogger(__name__)


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"JSON読み込みエラー ({path}): {e}")
        return default


def _save_json(path: str, data):
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_seen_ids() -> set:
    """過去に見た車両IDセットを取得"""
    data = _load_json(SEEN_CARS_FILE, {})
    return set(data.keys())


def mark_seen(cars: list[dict]):
    """車両を既出としてマーク"""
    data = _load_json(SEEN_CARS_FILE, {})
    now = datetime.now().isoformat()
    for car in cars:
        car_id = car.get("id")
        if car_id and car_id not in data:
            data[car_id] = {
                "first_seen": now,
                "price": car.get("price"),
                "year": car.get("year"),
            }
    _save_json(SEEN_CARS_FILE, data)


def get_new_cars(cars: list[dict]) -> list[dict]:
    """今回初めて見つかった車両のみ返す"""
    seen = get_seen_ids()
    new = [c for c in cars if c.get("id") not in seen]
    return new


def save_good_deals(deals: list[dict]):
    """お得車両を保存 (最新100件を保持)"""
    history = _load_json(GOOD_DEALS_FILE, [])
    now = datetime.now().isoformat()

    existing_ids = {d.get("id") for d in history}
    for deal in deals:
        if deal.get("id") not in existing_ids:
            record = deal.copy()
            record["found_at"] = now
            history.append(record)

    # 最新100件
    history = history[-100:]
    _save_json(GOOD_DEALS_FILE, history)


def load_good_deals() -> list[dict]:
    """保存されたお得車両を読み込む"""
    return _load_json(GOOD_DEALS_FILE, [])


def load_current_good_deals() -> list[dict]:
    """現在アクティブなお得車両 (直近7日以内に発見)"""
    from datetime import timedelta
    deals = load_good_deals()
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    return [d for d in deals if d.get("found_at", "") >= cutoff]


def log_alert(deals: list[dict]):
    """アラート送信ログを記録"""
    logs = _load_json(ALERT_LOG_FILE, [])
    now = datetime.now().isoformat()
    for deal in deals:
        logs.append({
            "alerted_at": now,
            "car_id": deal.get("id"),
            "price": deal.get("price"),
            "year": deal.get("year"),
            "deal_score": deal.get("deal_score"),
        })
    logs = logs[-200:]
    _save_json(ALERT_LOG_FILE, logs)
