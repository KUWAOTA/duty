"""Export the saved decluttering plan as an iCloud-compatible iCalendar file."""

from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event, Timezone, TimezoneStandard


ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / "plan_2026-10-04.json").read_text(encoding="utf-8"))
OUTPUT = ROOT / "declutter_2026-10_to_2027-01.ics"
JST = ZoneInfo("Asia/Tokyo")
START, END = date(2026, 10, 5), date(2027, 1, 31)
EXCLUDED = set(PLAN["unavailable_dates"]) | set(PLAN["holidays"])
STAMP = datetime.now(timezone.utc)
COUNTS = Counter()


def usable(day):
    return START <= day <= END and day.weekday() < 5 and day.isoformat() not in EXCLUDED


calendar = Calendar()
calendar.add("prodid", "-//Duty//Moving and Decluttering Plan//JA")
calendar.add("version", "2.0")
calendar.add("calscale", "GREGORIAN")
calendar.add("method", "PUBLISH")
calendar.add("x-wr-calname", "引越し準備・断捨離（2026年10月〜2027年1月）")
calendar.add("x-wr-timezone", "Asia/Tokyo")
calendar.add("x-wr-caldesc", "月水は断捨離、火木は創作、金は10分の記録。定時後の時刻は未指定のため終日表示。朝の排出担当・粗大回収日・引越日は未確定。指定の用事日と土日祝を除外。")

tz = Timezone()
tz.add("tzid", "Asia/Tokyo")
tz.add("x-lic-location", "Asia/Tokyo")
standard = TimezoneStandard()
standard.add("dtstart", datetime(1970, 1, 1))
standard.add("tzoffsetfrom", timedelta(hours=9))
standard.add("tzoffsetto", timedelta(hours=9))
standard.add("tzname", "JST")
tz.add_component(standard)
calendar.add_component(tz)


def add(day, kind, title, description, *, clock=None, minutes=None, tentative=False, url=None, location=None):
    if isinstance(day, str):
        day = date.fromisoformat(day)
    assert usable(day), f"Unavailable event date: {day}"
    event = Event()
    event.add("uid", f"{uuid5(NAMESPACE_URL, f'duty/declutter/{day}/{kind}')}@duty.local")
    event.add("dtstamp", STAMP)
    event.add("summary", title)
    event.add("description", description)
    event.add("categories", [kind])
    event.add("transp", "TRANSPARENT")
    if clock is None:
        event.add("dtstart", day)
        event.add("dtend", day + timedelta(days=1))
    else:
        start = datetime.combine(day, clock, tzinfo=JST)
        event.add("dtstart", start)
        event.add("dtend", start + timedelta(minutes=minutes))
    if tentative:
        event.add("status", "TENTATIVE")
    if url:
        event.add("url", url)
    if location:
        event.add("location", location)
    calendar.add_component(event)
    COUNTS[kind] += 1


for day, (minutes, title, description) in PLAN["work"].items():
    add(day, "断捨離", f"定時後｜{title}（{minutes}分）", f"定時後に{minutes}分。開始時刻は未指定のため終日表示。\n{description}")

for day, (title, description, kind) in PLAN["lunch"].items():
    add(day, "昼休み", f"昼｜{title}", description, clock=time(11, 30), minutes=25 if kind == "drop" else 10,
        tentative=kind == "drop", url=PLAN["sources"]["clothes"] if kind == "drop" else None)

for day, (title, description) in PLAN["milestones"].items():
    if "粗大" in title:
        title = title.replace("仮", "（回収希望日・未予約）")
        description += "\n未予約。予約で確定した日・排出期限へ変更する。"
    elif title == "準備目標":
        title = "引越し準備の完了目標（仮）"
        description += "\n引越し当日の予定ではない。"
    else:
        title = "定時後｜旧居へ補充便（20分・仮）"
    add(day, "仮予定", title, description, tentative=True,
        url=PLAN["sources"]["bulky"] if "粗大" in title else None)

burn_days = list(PLAN["usable_pre_year_end_burn_dates"])
day = date(2027, 1, 6)
while day <= END:
    if usable(day) and day.weekday() in (1, 4):
        burn_days.append(day.isoformat())
    day += timedelta(days=1)

for day in burn_days:
    add(day, "可燃ごみ", "可燃ごみ｜朝8時まで（担当未定）",
        "当日朝8時までに指定場所へ。朝の排出担当は未確認。本人または家族の対応が可能な場合に実施。\n市指定袋を使用。通常の家庭ごみと合わせて45L袋2つまで。前夜の排出はしない。",
        tentative=True, url=PLAN["sources"]["rules"])

for kind, label in (("A", "不燃小物・缶・PET"), ("B", "ビン・電池・蛍光灯等")):
    for day in PLAN[f"{kind}_dates"]:
        if not usable(date.fromisoformat(day)):
            continue
        add(day, f"資源{kind}", f"{kind}類｜{label}（7〜9時・担当未定）",
            "当日7:00〜9:00が排出可能時間。2時間の作業ではない。朝の排出担当は未確認。\n品目別に分別して高台2丁目の資源分別ステーションへ。充電池・電池入り製品は市の回収条件を確認する。",
            clock=time(7), minutes=120, tentative=True, url=PLAN["sources"]["dates"], location="高台2丁目の資源分別ステーション（場所要確認）")

day = START
while day <= END:
    if usable(day) and day.weekday() in (1, 3):
        add(day, "創作", "定時後｜創作（90分目安）", "火・木は小説などの創作時間。90分は目安。開始時刻は未指定のため終日表示。")
    elif usable(day) and day.weekday() == 4 and day <= date.fromisoformat(PLAN["preparation_target"]):
        add(day, "進捗記録", "定時後｜片付けの記録（10分）", "袋数・箱数・残りの区画を記録。余った定時後の時間は創作や普段の予定へ。開始時刻は未指定のため終日表示。")
    day += timedelta(days=1)

# Put events in date order for predictable previews; keep the timezone first.
calendar.subcomponents[1:] = sorted(calendar.subcomponents[1:], key=lambda event: (
    event.decoded("dtstart").isoformat(), str(event["summary"])))
content = calendar.to_ical()
OUTPUT.write_bytes(content)

# Read the actual output with an independent parser pass before delivery.
parsed = Calendar.from_ical(OUTPUT.read_bytes())
events = parsed.walk("VEVENT")
assert len(events) == sum(COUNTS.values())
assert len({str(event["uid"]) for event in events}) == len(events)
assert not parsed.walk("VALARM")
assert content.endswith(b"\r\n")
assert all(len(line) <= 75 for line in content.split(b"\r\n"))
for event in events:
    start, end = event.decoded("dtstart"), event.decoded("dtend")
    assert usable(start.date() if isinstance(start, datetime) else start)
    assert end > start
    if isinstance(start, datetime):
        assert start.utcoffset() == timedelta(hours=9)
        assert start.hour in (7, 11)
    else:
        assert end == start + timedelta(days=1)
assert COUNTS["断捨離"] == len(PLAN["work"])
assert COUNTS["昼休み"] == len(PLAN["lunch"])
assert COUNTS["資源A"] == 7 and COUNTS["資源B"] == 7
print(json.dumps({"file": str(OUTPUT), "events": len(events), "categories": dict(COUNTS), "bytes": len(content), "validation": "passed"}, ensure_ascii=False))
