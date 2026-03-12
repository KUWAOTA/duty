"""
CarSensor / Goo-net スクレイパー
AQUA中古車情報を取得する
"""
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

from .config import SEARCH_CRITERIA

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_carsensor(page: int = 1) -> list[dict]:
    """
    CarSensorから検索結果を取得する
    URL例: https://www.carsensor.net/usedcar/search.php?STID=CS_C_CTG_SRCH&...
    """
    criteria = SEARCH_CRITERIA
    pref_str = "_".join(criteria["kansai_prefs"].keys())

    params = {
        "STID": "CS_C_CTG_SRCH",
        "CARC": "T",
        "MKER": criteria["maker_code"],
        "MDL": criteria["model"],
        "PRICET": str(criteria["max_price"]),
        "YEARF": str(criteria["min_year"]),
        "KILO": "06",       # 走行距離6万km以下 (CarSensorのコード)
        "FUNE": "0",        # 修復歴なし
        "PREF": pref_str,   # 都道府県 (関西)
        "pg": str(page),
    }

    url = "https://www.carsensor.net/usedcar/search.php?" + urlencode(params)
    logger.info(f"CarSensor検索URL: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return _parse_carsensor(resp.text, url)
    except requests.RequestException as e:
        logger.error(f"CarSensor取得エラー: {e}")
        return []


def _parse_carsensor(html: str, source_url: str) -> list[dict]:
    """CarSensorのHTML解析"""
    soup = BeautifulSoup(html, "lxml")
    cars = []

    # CarSensorの車両リストアイテム (複数のセレクタを試す)
    items = (
        soup.select(".cassetteP")
        or soup.select(".cs-cassette-wrap")
        or soup.select("[data-cassette]")
        or soup.select(".stockDetail")
    )

    if not items:
        logger.warning("CarSensor: 車両リストが見つかりませんでした。HTML構造が変わった可能性があります。")
        logger.debug(f"取得URL: {source_url}")
        return []

    for item in items:
        try:
            car = _extract_car_from_carsensor_item(item, source_url)
            if car:
                cars.append(car)
        except Exception as e:
            logger.debug(f"アイテム解析エラー: {e}")
            continue

    logger.info(f"CarSensor: {len(cars)}件取得")
    return cars


def _extract_car_from_carsensor_item(item, source_url: str) -> dict | None:
    """CarSensorの個別アイテムから車両情報を抽出"""
    # リンク / 車両ID
    link_el = item.select_one("a[href]")
    if not link_el:
        return None
    href = link_el.get("href", "")
    if not href.startswith("http"):
        href = "https://www.carsensor.net" + href

    # 車両ID (URLから抽出)
    car_id_match = re.search(r"CS(\w+)\.html", href)
    car_id = car_id_match.group(0) if car_id_match else href

    # 価格 (万円)
    price = None
    for selector in [".cassetteP_price", ".price", "[class*='price']"]:
        price_el = item.select_one(selector)
        if price_el:
            price_text = price_el.get_text()
            price_match = re.search(r"([\d,]+)\s*万", price_text)
            if price_match:
                price = int(price_match.group(1).replace(",", ""))
                break

    if price is None:
        return None

    # 年式
    year = None
    for selector in [".cassetteP_year", "[class*='year']", ".nenShiki"]:
        year_el = item.select_one(selector)
        if year_el:
            year_match = re.search(r"(\d{4})", year_el.get_text())
            if year_match:
                year = int(year_match.group(1))
                break

    # テキスト全体からも年式を探す
    if year is None:
        text = item.get_text()
        year_match = re.search(r"(201[4-9]|202\d)年", text)
        if year_match:
            year = int(year_match.group(1))

    # 走行距離 (km)
    mileage = None
    for selector in [".cassetteP_km", "[class*='km']", "[class*='mileage']"]:
        km_el = item.select_one(selector)
        if km_el:
            km_text = km_el.get_text()
            km_match = re.search(r"([\d.]+)\s*万", km_text)
            if km_match:
                mileage = int(float(km_match.group(1)) * 10000)
                break
            km_match2 = re.search(r"([\d,]+)\s*km", km_text)
            if km_match2:
                mileage = int(km_match2.group(1).replace(",", ""))
                break

    # 都道府県 (エリア)
    area = ""
    for selector in [".cassetteP_area", "[class*='area']", "[class*='pref']"]:
        area_el = item.select_one(selector)
        if area_el:
            area = area_el.get_text().strip()
            break

    # 装備 / オプション
    full_text = item.get_text()
    options = _extract_options(full_text)

    # 修復歴
    no_repair = "修復歴なし" in full_text or "修復歴無" in full_text

    # 車名
    name = "トヨタ AQUA"
    title_el = item.select_one("[class*='title'], [class*='name'], h2, h3")
    if title_el:
        name = title_el.get_text().strip()[:50]

    return {
        "id": car_id,
        "name": name,
        "price": price,  # 万円
        "year": year,
        "mileage": mileage,  # km
        "area": area,
        "options": options,
        "no_repair": no_repair,
        "url": href,
        "source": "carsensor",
    }


def _extract_options(text: str) -> dict:
    """テキストから装備・オプション情報を抽出"""
    return {
        "backup_monitor": any(kw in text for kw in ["バックカメラ", "バックモニター", "リアカメラ", "後退時カメラ"]),
        "collision_prevention": any(kw in text for kw in [
            "衝突軽減", "衝突被害軽減", "プリクラッシュ", "自動ブレーキ",
            "衝突防止", "Toyota Safety Sense", "セーフティセンス",
        ]),
        "bluetooth": any(kw in text for kw in ["Bluetooth", "bluetooth", "ブルートゥース"]),
        "dashcam": any(kw in text for kw in ["ドラレコ", "ドライブレコーダー", "ドライブレコーダ"]),
    }


def fetch_all_pages(max_pages: int = 5) -> list[dict]:
    """全ページ取得 (最大max_pages)"""
    all_cars = []
    for page in range(1, max_pages + 1):
        cars = fetch_carsensor(page)
        if not cars:
            break
        all_cars.extend(cars)
        if len(cars) < 10:
            break  # 最後のページと判断
        time.sleep(2)  # 負荷軽減
    return all_cars
