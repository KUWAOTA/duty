#!/usr/bin/env python3
"""
duty / 毎日の雑務管理ツール
━━━━━━━━━━━━━━━━━━━━━━
使い方:
  python main.py check          今日のタスクを確認 (中古車チェックも実行)
  python main.py cars           中古車チェックのみ実行
  python main.py cars --show    保存済みお得車両を表示
  python main.py cars --all     全条件合致車両を表示
  python main.py schedule       定期実行モード (毎朝8時に自動チェック)
"""
import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

# requests等のnoisy loggerを抑制
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


def cmd_check(args):
    """今日のタスクを確認"""
    from daily.checker import run_daily_check
    output = run_daily_check(check_cars=not args.no_cars)
    print(output)


def cmd_cars(args):
    """中古車チェック"""
    if args.show:
        _show_saved_deals()
        return

    if args.all:
        _show_all_filtered()
        return

    from car_alert.runner import run_car_check
    from car_alert.analyzer import format_car_summary
    from car_alert.notifier import send_alerts

    print("中古車チェック開始...")
    result = run_car_check(silent=True)

    print(f"\n取得件数: {result['total']}件")
    print(f"条件合致: {result['filtered']}件")

    new_deals = result.get("new_good_deals", [])
    if new_deals:
        print(f"\n🎉 新規お得車両 {len(new_deals)}件！")
        send_alerts(new_deals)
    else:
        print("\n今回の新規お得車両はありませんでした。")

    active = result.get("active_good_deals", [])
    if active and not new_deals:
        print(f"\n📌 直近7日のお得車両: {len(active)}件 (--show で確認)")


def _show_saved_deals():
    """保存済みお得車両を表示"""
    from car_alert.storage import load_current_good_deals
    from car_alert.analyzer import format_car_summary

    deals = load_current_good_deals()
    if not deals:
        print("直近7日のお得車両データはありません。")
        print("まず 'python main.py cars' でチェックを実行してください。")
        return

    print(f"\n━━━ 直近7日のお得AQUA {len(deals)}件 ━━━\n")
    for i, deal in enumerate(deals, 1):
        print(format_car_summary(deal, rank=i))
        found = deal.get("found_at", "")[:10]
        print(f"  発見日: {found}")
        print()
    print("気になる車は各URLから問い合わせ or カーセンサーで詳細確認を！")
    print("見学予約を入れると安心です。")


def _show_all_filtered():
    """全条件合致車両を表示"""
    from car_alert.scraper import fetch_all_pages
    from car_alert.analyzer import filter_cars, enrich_cars, format_car_summary

    print("全件取得中...")
    all_cars = fetch_all_pages(max_pages=5)
    filtered = filter_cars(all_cars)
    enriched = enrich_cars(filtered)
    enriched.sort(key=lambda c: c.get("deal_score", 0), reverse=True)

    print(f"\n━━━ 条件合致AQUA {len(enriched)}件 (お得度順) ━━━\n")
    for i, car in enumerate(enriched, 1):
        print(format_car_summary(car, rank=i))
        print()


def cmd_schedule(args):
    """毎朝8時に自動チェック"""
    try:
        import schedule
        import time
    except ImportError:
        print("scheduleパッケージが必要です: pip install schedule")
        sys.exit(1)

    from car_alert.runner import run_car_check
    from car_alert.notifier import send_alerts

    def job():
        print("\n[定期チェック] 中古車チェック実行...")
        result = run_car_check(silent=True)
        new_deals = result.get("new_good_deals", [])
        if new_deals:
            send_alerts(new_deals)
        else:
            print(f"[定期チェック] 新規お得車両なし (条件合致: {result['filtered']}件)")

    schedule.every().day.at("08:00").do(job)
    print("定期チェックモード起動 (毎朝8:00に実行)")
    print("停止: Ctrl+C")

    # 起動直後に1回実行
    job()

    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    parser = argparse.ArgumentParser(
        description="duty - 毎日の雑務管理ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command")

    # check コマンド
    p_check = subparsers.add_parser("check", help="今日のタスク確認")
    p_check.add_argument("--no-cars", action="store_true", help="中古車チェックをスキップ")
    p_check.set_defaults(func=cmd_check)

    # cars コマンド
    p_cars = subparsers.add_parser("cars", help="中古車チェック")
    p_cars.add_argument("--show", action="store_true", help="保存済みお得車両を表示")
    p_cars.add_argument("--all", action="store_true", help="全条件合致車両を表示")
    p_cars.set_defaults(func=cmd_cars)

    # schedule コマンド
    p_sched = subparsers.add_parser("schedule", help="毎朝8時に自動チェック")
    p_sched.set_defaults(func=cmd_schedule)

    args = parser.parse_args()

    if not args.command:
        # 引数なしは check と同じ
        args.no_cars = False
        cmd_check(args)
        return

    args.func(args)


if __name__ == "__main__":
    main()
