"""
毎日のタスクチェッカー
「今日やること」を問い合わせると中古車アラートも一緒に確認する
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


DAILY_TASKS = [
    "メールチェック",
    "スケジュール確認",
    "AQUA中古車チェック",
]


def run_daily_check(check_cars: bool = True) -> str:
    """
    毎日のタスクチェックを実行
    中古車情報を取り込んで今日やることをまとめて返す
    """
    today = datetime.now().strftime("%Y年%m月%d日 (%a)")
    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📋 今日のタスク確認 ({today})",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    # 基本タスク
    lines.append("【通常タスク】")
    for task in DAILY_TASKS:
        if task != "AQUA中古車チェック":
            lines.append(f"  ☐ {task}")
    lines.append("")

    # 中古車チェック
    lines.append("【AQUA中古車チェック】")
    if check_cars:
        car_summary = _run_car_check_summary()
        lines.append(car_summary)
    else:
        lines.append("  (スキップ)")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


def _run_car_check_summary() -> str:
    """中古車チェックを実行してサマリー文字列を返す"""
    try:
        from car_alert.runner import run_car_check
        from car_alert.analyzer import format_car_summary

        result = run_car_check(silent=True)

        new_deals = result.get("new_good_deals", [])
        active_deals = result.get("active_good_deals", [])
        total = result.get("total", 0)
        filtered = result.get("filtered", 0)

        lines = [f"  取得: {total}件  条件合致: {filtered}件"]

        if new_deals:
            lines.append(f"")
            lines.append(f"  🎉 新規お得車両 {len(new_deals)}件 発見！")
            lines.append("")
            for i, deal in enumerate(new_deals[:3], 1):  # 最大3件表示
                summary = format_car_summary(deal, rank=i)
                for ln in summary.split("\n"):
                    lines.append("  " + ln)
                lines.append("")
            if len(new_deals) > 3:
                lines.append(f"  ... 他 {len(new_deals) - 3}件")
            lines.append("")
            lines.append("  ★ 見学予約の検討をおすすめします！")
            lines.append("    → python main.py cars --show  で詳細確認")
            lines.append("    → 気に入ったらカーセンサーのページから問い合わせ！")

        elif active_deals:
            lines.append(f"")
            lines.append(f"  📌 直近7日以内のお得車両: {len(active_deals)}件")
            for deal in active_deals[:2]:
                price = deal.get("price", "?")
                year = deal.get("year", "?")
                area = deal.get("area", "?")
                score = deal.get("deal_score", 0)
                lines.append(f"     {year}年式 {price}万円 ({area}) スコア:{score:.2f}")
            lines.append("  → まだ市場にある可能性があります。早めの見学予約を！")

        else:
            lines.append("  今日は新しいお得車両はありませんでした。")
            lines.append("  引き続き毎日チェックします。")

        return "\n".join(lines)

    except ImportError:
        return "  ⚠ car_alertモジュールが見つかりません。requirements.txtを確認してください。"
    except Exception as e:
        logger.error(f"中古車チェックエラー: {e}", exc_info=True)
        return f"  ⚠ チェック中にエラーが発生しました: {e}"
