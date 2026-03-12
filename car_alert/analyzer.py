"""
中古車お得度判定モジュール
- 検索条件フィルタリング
- ドラレコなし車のコスト補正
- お得度スコア計算
"""
import logging
from datetime import datetime

from .config import (
    SEARCH_CRITERIA,
    DASHCAM_COST,
    REFERENCE_PRICES,
    GOOD_DEAL_THRESHOLD,
)

logger = logging.getLogger(__name__)


def filter_cars(cars: list[dict]) -> list[dict]:
    """検索条件に合う車だけ抽出"""
    filtered = []
    criteria = SEARCH_CRITERIA

    for car in cars:
        reason = _check_filter(car, criteria)
        if reason:
            logger.debug(f"除外 [{car.get('id')}]: {reason}")
            continue
        filtered.append(car)

    logger.info(f"フィルタ結果: {len(cars)}件 → {len(filtered)}件")
    return filtered


def _check_filter(car: dict, criteria: dict) -> str | None:
    """条件に合わない場合は理由を返す、合う場合はNone"""
    # 価格チェック
    price = car.get("price")
    if price is None or price > criteria["max_price"]:
        return f"価格超過: {price}万円"

    # 走行距離チェック
    mileage = car.get("mileage")
    if mileage is not None and mileage > criteria["max_mileage"]:
        return f"走行距離超過: {mileage:,}km"

    # 年式チェック
    year = car.get("year")
    if year is not None and year < criteria["min_year"]:
        return f"年式古: {year}年"

    # 修復歴チェック
    if criteria["no_repair"] and not car.get("no_repair"):
        return "修復歴あり(不明含む)"

    # 必須装備チェック
    options = car.get("options", {})
    if not options.get("backup_monitor"):
        return "バックモニターなし"
    if not options.get("collision_prevention"):
        return "衝突軽減ブレーキなし"
    if not options.get("bluetooth"):
        return "Bluetoothなし"

    return None


def enrich_cars(cars: list[dict]) -> list[dict]:
    """
    車両情報を補完・スコアリング
    - ドラレコなし → 実質価格 = 価格 + ドラレコ費用
    - お得度スコア算出
    """
    enriched = []
    for car in cars:
        car = car.copy()

        # 実質価格計算 (ドラレコなし → 上乗せ)
        has_dashcam = car.get("options", {}).get("dashcam", False)
        dashcam_adjustment = 0 if has_dashcam else DASHCAM_COST
        dashcam_adjustment_man = round(dashcam_adjustment / 10000, 1)

        car["has_dashcam"] = has_dashcam
        car["dashcam_adjustment"] = dashcam_adjustment  # 円
        car["effective_price"] = (car["price"] or 0) + dashcam_adjustment_man  # 万円

        # お得度スコア計算
        car["deal_score"] = _calculate_deal_score(car)
        car["is_good_deal"] = car["deal_score"] >= 1.0

        enriched.append(car)

    return enriched


def _calculate_deal_score(car: dict) -> float:
    """
    お得度スコア計算 (1.0以上 = お得)

    スコア = 基準価格 / 実質価格 × 走行距離係数 × 年式係数

    基準価格より安い → スコア > 1.0 → お得
    """
    year = car.get("year")
    effective_price = car.get("effective_price", 0)
    mileage = car.get("mileage")

    if not year or effective_price <= 0:
        return 0.0

    # 基準価格 (年式に応じた相場)
    current_year = datetime.now().year
    if year in REFERENCE_PRICES:
        base_price = REFERENCE_PRICES[year]
    else:
        # テーブルにない年式は補間
        base_price = max(70, 70 + (year - 2014) * 5)

    # 走行距離係数 (少ないほど高評価)
    km_factor = 1.0
    if mileage is not None:
        if mileage <= 20000:
            km_factor = 1.1
        elif mileage <= 40000:
            km_factor = 1.05
        elif mileage <= 60000:
            km_factor = 1.0
        else:
            km_factor = 0.9

    # 年式係数 (新しいほど高評価)
    age = current_year - year
    age_factor = max(0.8, 1.0 - age * 0.02)

    # スコア計算: 基準価格との比率
    score = (base_price * GOOD_DEAL_THRESHOLD) / effective_price * km_factor * age_factor

    return round(score, 3)


def get_good_deals(cars: list[dict]) -> list[dict]:
    """お得な車だけ抽出・スコア順にソート"""
    good = [c for c in cars if c.get("is_good_deal")]
    good.sort(key=lambda c: c.get("deal_score", 0), reverse=True)
    return good


def format_car_summary(car: dict, rank: int = None) -> str:
    """車両情報を日本語テキストにフォーマット"""
    lines = []
    prefix = f"#{rank} " if rank else ""

    price = car.get("price", "?")
    eff = car.get("effective_price", price)
    year = car.get("year", "?")
    mileage = car.get("mileage")
    area = car.get("area", "?")
    score = car.get("deal_score", 0)
    url = car.get("url", "")
    has_dashcam = car.get("has_dashcam", True)
    adjustment = car.get("dashcam_adjustment", 0)

    mileage_str = f"{mileage:,}km" if mileage else "不明"
    dashcam_note = "" if has_dashcam else f" (+ドラレコ {adjustment//10000}万円)"

    lines.append(f"{prefix}【{year}年式 / {mileage_str} / {area}】")
    lines.append(f"  価格: {price}万円{dashcam_note} → 実質 {eff}万円")
    lines.append(f"  お得度スコア: {score:.2f}  {'★★★ 超お得！' if score >= 1.2 else '★★ お得' if score >= 1.0 else ''}")
    lines.append(f"  {url}")

    return "\n".join(lines)
