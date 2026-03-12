"""
中古車チェック実行エントリポイント
- スクレイピング → フィルタ → スコアリング → アラート
"""
import logging

from .scraper import fetch_all_pages
from .analyzer import filter_cars, enrich_cars, get_good_deals
from .storage import get_new_cars, mark_seen, save_good_deals, log_alert, load_current_good_deals
from .notifier import send_alerts

logger = logging.getLogger(__name__)


def run_car_check(silent: bool = False) -> dict:
    """
    中古車チェックを実行して結果を返す

    Returns:
        {
            "total": 取得件数,
            "filtered": 条件合致件数,
            "new_good_deals": 新規お得車両リスト,
            "active_good_deals": 現在のお得車両リスト (直近7日),
        }
    """
    logger.info("中古車チェック開始...")

    # 1. データ取得
    all_cars = fetch_all_pages(max_pages=5)
    if not all_cars:
        logger.warning("車両データが取得できませんでした")
        return {
            "total": 0,
            "filtered": 0,
            "new_good_deals": [],
            "active_good_deals": load_current_good_deals(),
        }

    # 2. 条件フィルタ
    filtered = filter_cars(all_cars)

    # 3. スコアリング・実質価格計算
    enriched = enrich_cars(filtered)

    # 4. 既出でない新規車両を特定
    new_cars = get_new_cars(enriched)
    mark_seen(enriched)  # 今回見た車両を全部記録

    # 5. お得車両判定
    new_good_deals = get_good_deals(new_cars)

    # 6. 保存
    if new_good_deals:
        save_good_deals(new_good_deals)
        log_alert(new_good_deals)

    # 7. 通知 (サイレントモードでない場合)
    if not silent and new_good_deals:
        send_alerts(new_good_deals)

    active_deals = load_current_good_deals()

    result = {
        "total": len(all_cars),
        "filtered": len(filtered),
        "new_good_deals": new_good_deals,
        "active_good_deals": active_deals,
    }

    logger.info(
        f"チェック完了: 取得{len(all_cars)}件 / 条件合致{len(filtered)}件 / "
        f"新規お得{len(new_good_deals)}件"
    )
    return result
