"""
アラート通知モジュール
- コンソール出力 (常時)
- LINE Notify (設定時)
- メール通知 (設定時)
"""
import logging
import smtplib
from email.mime.text import MIMEText

import requests

from .config import LINE_NOTIFY_TOKEN, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, ALERT_EMAIL
from .analyzer import format_car_summary

logger = logging.getLogger(__name__)


def send_alerts(new_good_deals: list[dict]) -> bool:
    """新しいお得車両をすべての通知チャネルで送信"""
    if not new_good_deals:
        return False

    message = _build_message(new_good_deals)

    print("\n" + "=" * 60)
    print("🚗 AQUAお得情報アラート！")
    print("=" * 60)
    print(message)
    print("=" * 60)

    if LINE_NOTIFY_TOKEN:
        _send_line(message)

    if ALERT_EMAIL and SMTP_USER and SMTP_PASS:
        _send_email(message)

    return True


def _build_message(deals: list[dict]) -> str:
    lines = [
        f"お得なAQUA {len(deals)}件が見つかりました！",
        "",
    ]
    for i, deal in enumerate(deals, 1):
        lines.append(format_car_summary(deal, rank=i))
        lines.append("")

    lines.append("▼ 見学の予約を検討しましょう！")
    return "\n".join(lines)


def _send_line(message: str):
    """LINE Notify で通知"""
    try:
        resp = requests.post(
            "https://notify-api.line.me/api/notify",
            headers={"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"},
            data={"message": "\n" + message},
            timeout=10,
        )
        if resp.status_code == 200:
            logger.info("LINE Notify 送信成功")
        else:
            logger.warning(f"LINE Notify 送信失敗: {resp.status_code}")
    except Exception as e:
        logger.error(f"LINE Notify エラー: {e}")


def _send_email(message: str):
    """メールで通知"""
    try:
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = f"【AQUA中古車アラート】お得な車が{len(message.splitlines())}件！"
        msg["From"] = SMTP_USER
        msg["To"] = ALERT_EMAIL

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())
        logger.info("メール送信成功")
    except Exception as e:
        logger.error(f"メール送信エラー: {e}")
