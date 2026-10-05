from __future__ import annotations

import calendar
import json
import re
import zipfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
LINE = OUT / 'line'
TODAY = date(2026, 10, 4)
MONTHS = [(2026, 10), (2026, 11), (2026, 12), (2027, 1)]
HOLIDAYS = {
    date(2026, 10, 12): 'スポーツの日',
    date(2026, 11, 3): '文化の日',
    date(2026, 11, 23): '勤労感謝の日',
    date(2027, 1, 1): '元日',
    date(2027, 1, 11): '成人の日',
}
UNAVAILABLE = {date(2026, 10, d) for d in [7, 9, 12, 28]}
for a, b in [(date(2026, 11, 6), date(2026, 11, 9)),
             (date(2026, 11, 19), date(2026, 11, 24)),
             (date(2026, 12, 24), date(2027, 1, 5))]:
    while a <= b:
        UNAVAILABLE.add(a)
        a += timedelta(days=1)

# Exact dates read visually from the city's current fiscal-2026 collection calendar.
A = {date(2026, 10, d) for d in [14, 28]} | {date(2026, 11, d) for d in [11, 25]} | {date(2026, 12, d) for d in [9, 23]} | {date(2027, 1, d) for d in [13, 27]}
B = {date(2026, 10, d) for d in [7, 21]} | {date(2026, 11, d) for d in [4, 18]} | {date(2026, 12, d) for d in [2, 16]} | {date(2027, 1, d) for d in [6, 20]}

WORK = {
    '2026-10-05': (15, '4区画作り', '「新居へ／旧居保管／手放す／保留」の4区画を作る。衣類の引き出し1つだけ判定し、袋・箱の記録を始める。'),
    '2026-10-14': (60, '衣類①', '普段着・夏物・サイズ違いを選別。回収可能な古着、可燃、残す服を分ける。冬服は使用分を残す。'),
    '2026-10-19': (45, '台所小物', '不要な食器・鍋・金属小物を選別。50cm以上と電池入りは別置き。持込予定の家電は廃棄しない。'),
    '2026-10-21': (60, '衣類②収納', '衣類の2回目と収納1か所。A類は10/28が使えないので、次の11/11向けに室内保管する。'),
    '2026-10-26': (45, '小型家電', '使っていない小型家電・ケーブル・電池を判定。充電池を含む製品は市の専用ルールで別扱いにする。'),
    '2026-11-02': (45, 'B類準備', '11/4向けにビン・乾電池・蛍光灯等を整理。電池入り製品の処分方法も確認する。'),
    '2026-11-04': (60, '本・紙①', '本・書類・雑誌の1回目。必要な本と不要な古紙を分け、搬出用に小束を作る。'),
    '2026-11-11': (60, '趣味機材', '魚突き・昆虫採集・標本機材の棚卸し。新居持込と旧居保管を決め、不要と判断した物だけ処分に回す。'),
    '2026-11-16': (45, '衣類③', '衣類の最終選別と押入れ1区画。保留服のうち、引っ越し後も使う物を決める。'),
    '2026-11-18': (60, '家具採寸', '本人が使う家具を採寸・撮影。不要家具の品名・数量・最大寸法を確定し、粗大ごみ①の一覧を作る。'),
    '2026-11-25': (60, '本・紙②', '11月の残りを片付け、古紙をまとめる。処分予定量と使える収集回数を比較する。'),
    '2026-11-30': (45, '粗大①準備', '粗大ごみ①の搬出動線・料金・回収場所を整理。予約が取れたら回収日当日に出せる形に準備する。'),
    '2026-12-02': (60, '機材最終', '趣味機材・ケーブル等の残りを整理。持ち込む長物・標本箱・PC関係を箱数で記録する。'),
    '2026-12-07': (45, '残置品整理', '旧居に残す消耗品を種類別にまとめ、「取りに来る箱」を作る。新居に運ぶ分を増やしすぎない。'),
    '2026-12-09': (60, '台所再点検', '台所・不燃小物の2回目。粗大ごみ②が必要なら品目を確定し、次の予約相談につなげる。'),
    '2026-12-14': (45, '収納最終', '押入れ・棚・机まわりの残りを判定。まだ処分するか迷う物は保留1箱に収め、12/21までに判断する。'),
    '2026-12-16': (60, 'B類最終', '年内最後のB類排出後、電池・蛍光灯・ビン等の見落としを確認。追加分は1/6用に分別保管する。'),
    '2026-12-21': (45, 'A類袋準備', '12/23のA類用に最後の不燃小物をまとめる。保留箱を再判定し、12/22の可燃も準備する。'),
    '2026-12-23': (60, '年内区切り', '主要な断捨離・処分の完了確認。持込品の箱数、旧居保管リスト、1月に残す作業を記録して終了する。'),
    '2027-01-06': (60, '荷造り再開', 'B類の追加分を出し、衣類・機材の荷造りを再開。入居日・搬入経路・大型家電運搬方法を確認する。'),
    '2027-01-13': (60, 'A類追加分', 'A類の追加分を処分。PC・標本・長物の梱包を進め、搬入口と家具寸法を照合する。'),
    '2027-01-18': (45, '持込箱確定', '新居へ運ぶ箱数と大物を確定。原付の小口便と車・業者の大物便を分け、消耗品は旧居に残す。'),
    '2027-01-20': (60, 'B類・梱包', 'B類の追加分を出し、使用中の物以外を梱包。家電の水抜き・設置作業は引越日が決まってから別途設定する。'),
}

LUNCH = {
    '2026-10-06': ('搬出確認', '11:30–11:40。朝の排出担当、分別ステーションの場所、古着の搬出経路を確認。', 'admin'),
    '2026-10-16': ('古着①仮', '11:30–11:55以内で小口の古着を市役所へ。勤務地との往復が25分以内の場合のみ。', 'drop'),
    '2026-10-23': ('量を点検', '11:30–11:40。袋数・粗大点数を記録し、通常収集だけで減らせそうかを見直す。', 'admin'),
    '2026-11-13': ('古着②仮', '11:30–11:55以内で小口の古着・古紙を市役所へ。往復条件を満たす場合のみ。', 'drop'),
    '2026-11-30': ('粗大①申込', '11:30–11:40。12/10前後の平日回収を相談する。品目・数量・当日搬出方法を確認。予約未取得。', 'admin'),
    '2026-12-04': ('古紙③仮', '11:30–11:55以内で小口の古紙を市役所へ。往復条件を満たす場合のみ。', 'drop'),
    '2026-12-10': ('粗大②相談', '11:30–11:40。残量がある場合だけ12/21までの粗大回収を相談。希望日に取れなければ市へ代替を相談。', 'admin'),
    '2026-12-18': ('古着④仮', '11:30–11:55以内で年内最後の古着・古紙搬出。往復条件を満たす場合のみ。', 'drop'),
    '2027-01-08': ('搬出予備仮', '11:30–11:55以内の古着・古紙の搬出予備。残りがない場合は通常の昼休みに戻す。', 'drop'),
}

MILESTONES = {
    '2026-12-10': ('粗大①仮', '粗大ごみ①の回収希望日の例。予約結果で移動。出すのは当日の指定時間まで。'),
    '2026-12-21': ('粗大②仮', '残量がある場合の粗大ごみ②の回収希望日の例。予約結果で移動。'),
    '2027-01-22': ('準備目標', '断捨離の残り・荷造り・運搬方法の準備完了目標。引越日が未定のため暫定。'),
    '2027-01-25': ('補充便仮', '入居済みの場合だけ、定時後20分以内を目安に旧居の消耗品を取りに寄る。未入居なら不要。'),
}

THEMES = {
    (2026, 10): ('衣類・台所の小物から', ['10/5は15分だけ。判定用の4区画を作る。', '10/14 A類はある分だけ。次の10/28は使えない。', '10/16 古着①は昼25分以内で往復できる場合のみ。']),
    (2026, 11): ('本・機材・家具の量を確定', ['11/18に家具を採寸し、粗大①の一覧を作る。', '11/25に残量を確認。11/30昼に粗大①を申し込む。', '用事の多い月。休み明けの詰め込み・休日の振替なし。']),
    (2026, 12): ('12/23までに主要処分を終える', ['粗大①12/10・②12/21は回収希望日の例。予約未取得。', '年内最後のB類12/16、A類12/23を使う。', '12/24から作業停止。新しい大片付けは始めない。']),
    (2027, 1): ('残りの処分・荷造り・搬入準備', ['1/6から再開。追加のA類1/13、B類1/20。', '1/22は準備完了の暫定目標。引越日ではない。', '1/25補充便は入居済みの場合のみ。1/27 A類は予備。']),
}

SOURCES = {
    'dates': 'https://www.city.nagaokakyo.lg.jp/cmsfiles/contents/0000014/14052/R8nittei.pdf',
    'shiori': 'https://www.city.nagaokakyo.lg.jp/cmsfiles/contents/0000011/11246/R8shiori.pdf',
    'rules': 'https://www.city.nagaokakyo.lg.jp/0000011246.html',
    'clothes': 'https://www.city.nagaokakyo.lg.jp/0000003961.html',
    'bulky': 'https://www.city.nagaokakyo.lg.jp/0000001497.html',
    'carry': 'https://cleanplaza-otokuni.jp/gomi/gomi/gomi.htm',
    'acceptance': 'https://cleanplaza-otokuni.jp/gomi/gomi/ukeire/ukeire.pdf',
    'fees': 'https://cleanplaza-otokuni.jp/gomi/gomi/ryoukin/ryoukin.pdf',
    'holidays': 'https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html',
}

COLORS = {'ink': '#1B3041', 'muted': '#61717D', 'bg': '#F4F6F8', 'line': '#DAE1E6',
          'work': '#176A62', 'creative': '#7751A0', 'pickup': '#AD3E3B', 'lunch': '#1965A1',
          'off': '#EEF0F3', 'busy': '#E9ECEF', 'week': '#F8FAFC', 'goal': '#FFF0C4'}
FONTS = Path('C:/Windows/Fonts')
MEASURED = []


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ('meiryob.ttc' if bold else 'meiryo.ttc')), size)


def text(draw, xy, value, size=26, fill=None, bold=False, max_width=None):
    f = font(size, bold)
    w = draw.textlength(value, font=f)
    if max_width is not None:
        assert w <= max_width + 1, (value, w, max_width)
    draw.text(xy, value, font=f, fill=fill or COLORS['ink'])
    MEASURED.append((value, size, w))


def active(d):
    return d >= TODAY and d not in UNAVAILABLE and d.weekday() < 5 and d not in HOLIDAYS


def daily_labels(d):
    """Visible municipal opportunities are kept distinct from personal work commitments."""
    labels = []
    ds = d.isoformat()
    if d in A:
        labels.append(('朝 A収集', 'pickup'))
    elif d in B:
        labels.append(('朝 B収集', 'pickup'))
    elif d.weekday() in [1, 4] and not date(2026, 12, 24) <= d <= date(2027, 1, 5):
        labels.append(('朝 可燃', 'pickup'))
    if not active(d):
        if d in UNAVAILABLE:
            labels.append(('予定あり ×', 'muted'))
        elif d in HOLIDAYS:
            labels.append(('祝日・作業休', 'muted'))
        elif d.weekday() >= 5:
            labels.append(('作業休み', 'muted'))
        return labels
    if ds in WORK:
        mins, title, _ = WORK[ds]
        labels.append((f'夜{mins} {title}', 'work'))
    elif d.weekday() in [1, 3]:
        labels.append(('夜 小説', 'creative'))
    elif d.weekday() == 4:
        labels.append(('夜 記録10分', 'muted'))
    elif d.weekday() == 0:
        labels.append(('通常の予定', 'muted'))
    if ds in LUNCH:
        labels.append(('昼 ' + LUNCH[ds][0], 'lunch'))
    if ds in MILESTONES:
        labels.append((MILESTONES[ds][0], 'lunch'))
    assert len(labels) <= 4
    return labels


def draw_month(y, m):
    W, H = 1400, 1740
    im = Image.new('RGB', (W, H), COLORS['bg'])
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, W, 206), fill=COLORS['ink'])
    text(dr, (50, 25), '引っ越し前の断捨離', 30, '#CADAE3', True)
    text(dr, (48, 67), f'{y}年 {m}月', 66, '#FFFFFF', True)
    text(dr, (595, 95), THEMES[(y, m)][0], 29, '#FFFFFF', True, 755)
    text(dr, (50, 163), '高台2丁目の収集 ｜ 月45分・水60分 ｜ 火木は小説 ｜ 土日祝は作業休', 27, '#DCE8EF', max_width=1300)
    left, top, gap, cw, ch = 44, 259, 6, 182, 178
    # 7 * 182 + 6 * 6 = 1310 pixels.
    for col, name in enumerate(['月', '火', '水', '木', '金', '土', '日']):
        text(dr, (left + col * (cw + gap) + 76, 217), name, 28, COLORS['muted'], True)
    weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(y, m)
    while len(weeks) < 6:
        last = weeks[-1][-1]
        weeks.append([last + timedelta(days=i) for i in range(1, 8)])
    for row, week in enumerate(weeks):
        for col, d in enumerate(week):
            x, t = left + col * (cw + gap), top + row * (ch + gap)
            inside = d.month == m and d.year == y
            fill = '#FFFFFF'
            if not inside or d < TODAY:
                fill = COLORS['off']
            elif d in UNAVAILABLE:
                fill = COLORS['busy']
            elif d.weekday() >= 5 or d in HOLIDAYS:
                fill = COLORS['week']
            elif d.isoformat() == '2027-01-22':
                fill = COLORS['goal']
            dr.rounded_rectangle((x, t, x + cw, t + ch), radius=12, fill=fill, outline=COLORS['line'], width=1)
            if not inside:
                continue
            text(dr, (x + 12, t + 8), str(d.day), 34, COLORS['muted'] if d < TODAY else COLORS['ink'], True)
            if d < TODAY:
                continue
            for i, (label, color) in enumerate(daily_labels(d)):
                text(dr, (x + 10, t + 57 + i * 27), label, 21, COLORS[color], False, cw - 20)
    fy = 1384
    text(dr, (48, fy), '色の見方', 27, bold=True)
    x = 245
    for label, c in [('夜の整理', 'work'), ('小説', 'creative'), ('収集', 'pickup'), ('昼・仮予定', 'lunch')]:
        dr.ellipse((x, fy + 8, x + 17, fy + 25), fill=COLORS[c])
        text(dr, (x + 25, fy), label, 25, COLORS[c])
        x += 235
    for i, line in enumerate(THEMES[(y, m)][1]):
        text(dr, (48, fy + 49 + i * 38), line, 26, max_width=1300)
    text(dr, (48, 1557), '朝の排出は担当未確認。不可なら家族等への依頼・回収方法の調整が必要。', 24, COLORS['muted'], max_width=1300)
    text(dr, (48, 1593), '可燃：朝8時まで・45L×2袋/世帯　A/B：当日7〜9時　前夜の排出なし', 24, COLORS['muted'], max_width=1300)
    text(dr, (48, 1629), '仮＝未予約・移動条件未確認。収集日は市の令和8年度日程表で確認。', 24, COLORS['muted'], max_width=1300)
    text(dr, (48, 1678), '計画作成 2026/10/4 ｜ 引越日未定・1/22は準備目標 ｜ 自動通知なし', 23, COLORS['muted'], max_width=1300)
    p = LINE / f'{y}-{m:02d}_calendar.png'
    im.save(p, optimize=True)
    return p


def draw_overview():
    W, H = 1200, 1650
    im = Image.new('RGB', (W, H), '#F6F8FA')
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, W, 212), fill=COLORS['ink'])
    text(dr, (52, 27), '2026年10月 → 2027年1月', 32, '#CDDBE3', True)
    text(dr, (48, 82), '平日で進める断捨離', 58, '#FFFFFF', True)
    text(dr, (52, 167), '主要処分は12/23まで。1月は荷造りと追加処分。', 30, '#DCE8EF', max_width=1090)
    y = 243
    text(dr, (52, y), '毎週のリズム', 38, bold=True)
    y += 68
    rhythms = [('月', '45分だけ選別', '残りはキャリア・英語など既存の予定', 'work'),
               ('火', '小説の時間', '朝に可燃ごみ。夜の大片付けは入れない', 'creative'),
               ('水', '60分だけ整理', 'A/B収集日に合わせる。60分で止める', 'work'),
               ('木', '小説の時間', '夜の大片付けは入れない', 'creative'),
               ('金', '記録10分・予備', '朝に可燃。昼の古着搬出は条件付き', 'lunch'),
               ('土日祝', '断捨離は休み', '使えない日も振替・詰め込みをしない', 'muted')]
    for dow, title, detail, color in rhythms:
        dr.rounded_rectangle((45, y, 1155, y + 98), radius=14, fill='#FFFFFF', outline=COLORS['line'])
        text(dr, (64, y + 16), dow, 34 if len(dow) == 1 else 27, COLORS[color], True)
        text(dr, (204, y + 9), title, 32, COLORS[color], True)
        text(dr, (204, y + 54), detail, 25, max_width=930)
        y += 110
    y += 14
    text(dr, (52, y), '高台2丁目の収集・搬出', 36, bold=True)
    y += 61
    lines = [
        '可燃：火・金、当日朝8時まで。1世帯45L×2袋まで。',
        'A類：10/14・11/11,25・12/9,23・1/13,27',
        'B類：10/21・11/4,18・12/2,16・1/6,20',
        'A＝その他不燃物・缶・PET等 ／ B＝ビン・電池・蛍光灯等',
        'A/Bは当日7〜9時。10/7 B・10/28 Aは本人予定で見送り。',
        '衣類・古紙：市役所へ平日9〜17時。昼の小口便を検討。',
        '施設の自己搬入：平日13〜16時。通常の昼休みでは不可。',
    ]
    for line in lines:
        text(dr, (52, y), line, 26, max_width=1090)
        y += 43
    dr.rounded_rectangle((45, 1416, 1155, 1609), radius=15, fill='#EAF0F4')
    text(dr, (67, 1434), '朝のごみ出し担当・引越日は未確認', 31, bold=True)
    text(dr, (67, 1483), '朝に出せない場合は、担当を頼むか回収方法を調整する。', 26, max_width=1070)
    text(dr, (67, 1527), '粗大回収①12/10・②12/21は希望日の例。予約未取得。', 26, max_width=1070)
    text(dr, (67, 1571), '1/22は準備完了の暫定目標。入居先・引越日は未確定。', 26, max_width=1070)
    p = LINE / '00_plan_overview.png'
    im.save(p, optimize=True)
    return p


def month_table(y, m):
    lines = ['| 月 | 火 | 水 | 木 | 金 | 土 | 日 |', '|---|---|---|---|---|---|---|']
    for week in calendar.Calendar().monthdatescalendar(y, m):
        cells = []
        for d in week:
            if d.month != m:
                cells.append('—')
            elif d < TODAY:
                cells.append(str(d.day) + ' 過去')
            else:
                labels = daily_labels(d)
                cells.append('**' + str(d.day) + '**<br>' + '<br>'.join(x[0] for x in labels))
        lines.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines)


def main():
    LINE.mkdir(parents=True, exist_ok=True)
    for ds in WORK:
        assert active(date.fromisoformat(ds)), ds
    for ds in LUNCH:
        assert active(date.fromisoformat(ds)), ds
    for ds in MILESTONES:
        assert active(date.fromisoformat(ds)), ds
    pre_work = sum(v[0] for k, v in WORK.items() if k <= '2026-12-23')
    burn = []
    d = date(2026, 10, 5)
    while d <= date(2026, 12, 23):
        if active(d) and d.weekday() in [1, 4]:
            burn.append(d)
        d += timedelta(days=1)
    assert len(burn) == 18, burn
    assert len(A - UNAVAILABLE) == 7
    assert pre_work == 975
    images = [draw_overview()] + [draw_month(y, m) for y, m in MONTHS]
    stamp = datetime.now(timezone(timedelta(hours=9)))
    previous = OUT / 'plan_2026-10-04.json'
    report = ROOT / 'daily' / stamp.strftime('%Y-%m-%d') / f"claude_{stamp.strftime('%H-%M-%S')}_declutter_calendar.md"
    if previous.exists():
        report = ROOT / json.loads(previous.read_text(encoding='utf-8'))['report']
    report.parent.mkdir(parents=True, exist_ok=True)
    line_text = '\n'.join([
        '【引っ越し前の断捨離｜2026/10→2027/1】',
        '月45分・水60分だけ。火木は小説、金は記録10分。土日祝と用事の日は休み。',
        '主要な処分は12/23まで。12/24〜1/5は作業しない。1/22は準備完了の仮目標（引越日は未定）。',
        '',
        '高台2丁目：可燃は火金の朝8時まで、45L×2袋/世帯まで。生活ごみも含む。A/Bは当日7〜9時。前夜には出さない。朝のごみ出し担当は未確認。',
        'A＝不燃小物・缶・PET等、B＝ビン・電池・蛍光灯等。電池は市の専用ルールに従う。',
        '',
        '10月：A 14（28は用事で見送り）／B 21（7は用事で見送り）。衣類と台所小物。古着小口便は16昼に仮置き。',
        '11月：A 11・25／B 4・18。本・趣味機材・家具。18に家具採寸、30昼に粗大①の申込。古着小口便は13昼に仮置き。',
        '12月：A 9・23／B 2・16。粗大①10・②21は回収希望日の例（未予約）。古紙4昼・古着18昼は仮置き。23で主要処分の区切り。',
        '1月：6から再開。A 13・27（27は予備）／B 6・20。18に持込箱数を決め、22までに準備。25の消耗品補充便は入居済みの場合だけ。',
        '',
        '昼の古着・古紙便は11:30〜11:55の25分以内で往復できる場合だけ。無理なら代替搬出方法を相談。',
        '施設への自己搬入は平日13〜16時。11:30〜12:15の昼休みや通常の定時後には入れられない。',
        '何往復するかは袋数・粗大点数・車の容量を見て決める。レンタカー・回収はまだ予約していません。',
        '使えない日：10/7,9,12,28、11/6〜9,19〜24、12/24〜1/5。',
        '出典：長岡京市の令和8年度ごみ日程表（2026/10/4確認）', SOURCES['dates'],
        '住所の番地は共有画像・この文章に載せていません。',
    ])
    (LINE / 'LINE_copy_text.txt').write_text(line_text + '\n', encoding='utf-8')

    md = [
        '# 引っ越し前の断捨離・ごみ出しカレンダー', '',
        f"作成：{stamp.strftime('%Y-%m-%d %H:%M:%S')}（日本時間）。対象：2026年10月5日〜2027年1月31日。", '',
        '**月曜45分・水曜60分を基本にして、火曜・木曜の小説時間と土日祝を残します。主要な断捨離・処分は12月23日までに終え、1月6日からは残りの処分と荷造りに移ります。** 12/24〜1/5は作業を入れません。', '',
        '**確認待ちの前提：朝のごみ出しだけ3〜5分を確保できるかは未回答です。** 分別は定時後に行いますが、通常収集への排出は朝に必要です。下記は自分または家族等が当日朝に出せる場合の基本案で、担当未確定です。朝の排出ができない場合の分岐も後半に載せました。引越日は未定なので、**1/22は準備完了の暫定目標で、引越日の決定ではありません。**', '',
        '## LINEで共有する', '',
        '最初に概要画像1枚、その後に月別画像4枚をLINEに添付すると伝わりやすくなります。画像を開いて保存してから、LINEの写真添付で送れます。共有用には住所の番地を載せていません。', '',
        '- [概要画像](../../house/moving_plan/line/00_plan_overview.png)',
        '- [10月](../../house/moving_plan/line/2026-10_calendar.png)／[11月](../../house/moving_plan/line/2026-11_calendar.png)／[12月](../../house/moving_plan/line/2026-12_calendar.png)／[1月](../../house/moving_plan/line/2027-01_calendar.png)',
        '- [LINE用のコピー文章](../../house/moving_plan/line/LINE_copy_text.txt)',
        '- [画像5枚＋文章をまとめたZIP](../../house/moving_plan/line/declutter_calendar_LINE.zip)', '',
        '![計画の概要](../../house/moving_plan/line/00_plan_overview.png)', '',
        '## 週間の配分', '',
        '既存の[曜日希望](../../taskManagement/master/schedule.md)にある火・木の小説、月・水・金のキャリア・英語を踏まえています。定時の時刻は不明なので、夜の開始時刻は固定せず、夕食・帰宅後の取りやすい時間に始めてください。', '',
        '| 曜日 | 定時後 | ごみ・昼休み |', '|---|---|---|',
        '| 月 | 断捨離45分で終了。残りを既存のキャリア・英語へ。初回10/5だけ15分。 | 必要な予約・確認は昼11:30〜11:40。 |',
        '| 火 | 小説の時間を確保。90分を目安に本人の生活に合わせる。大片付けは入れない。 | 可燃を朝に出す。前日の整理で袋を室内に準備。 |',
        '| 水 | 断捨離60分。A/B回収後の次の仕分けを進める。 | 指定のA/B収集機会を使う。 |',
        '| 木 | 小説の時間を確保。90分を目安に本人の生活に合わせる。 | 粗大の予約電話等が必要な日だけ昼10分。 |',
        '| 金 | 袋数・箱数の記録10分まで。残りはキャリア・英語や休息。 | 朝は可燃。月に1〜2回、小口の古着・古紙搬出を昼に仮置き。 |',
        '| 土日祝・用事の日 | 断捨離・搬出は予定しない。できなかった分は次の作業日に送る。 | カレンダーの「収集」は市の機会。休みや用事の日の本人排出は見送る。 |', '',
        '年内の夜の選別枠は合計**16時間15分**。金曜記録と予約・小口搬出を含めると、概ね**18〜21時間**の計画です。一軒家を丸ごと空にする量を見積もった数字ではありません。10/23と11/25に実際の残量で見直します。', '',
        '## 高台2丁目の収集日と出し方', '',
        f"高台1〜4丁目・高台西の行を、市の**令和8年度分別収集日程表**で確認しました。以下のA/Bの具体的な日付は公式表から転記しています。[日程表PDF]({SOURCES['dates']})", '',
        '| 種別 | 使い方・時間 | 本人が使える年内の機会 |', '|---|---|---|',
        '| 可燃 | 火・金の当日朝8時まで。市指定袋、1世帯45L×2袋まで。普段の生活ごみを含む。 | 10/6,13,16,20,23,27,30、11/10,13,17,27、12/1,4,8,11,15,18,22の18回。 |',
        '| A類 | その他不燃物、缶、PET、スプレー缶等。第2・4水曜、当日7〜9時。 | **10/14・11/11・11/25・12/9・12/23**。10/28は用事で見送り。 |',
        '| B類 | ビン、乾電池・条件を満たす充電池、蛍光灯等。第1・3水曜、当日7〜9時。 | **10/21・11/4・11/18・12/2・12/16**。10/7は用事で見送り。 |',
        '| プラ容器包装 | A/Bどちらの日も可。プラ製品全般が対象ではない。 | A/Bと同時。 |',
        '| 古着・古紙 | 市役所分庁舎1の回収。平日9〜17時。古着は中身の見える袋、古紙は種類別にひもで束ねる。 | 昼の小口便を10/16・11/13・12/4・12/18、1/8予備に仮置き。 |',
        '| 粗大ごみ | 1辺50cm以上は予約収集。品目別の有料。回収当日の指定時間までに指定場所へ。 | 第1便を11/30申込→12/10前後、第2便は必要時12/10相談→12/21までを希望。予約未取得。 |', '',
        f"可燃は生活ごみで1袋使うなら、断捨離の割当は**1袋/回＝年内18袋程度**が目安です。生活ごみで2袋埋まる日は断捨離分を次回へ送り、一時多量ごみは市へ相談します。前夜に外のステーションへ出す予定にはしていません。[可燃のルール]({SOURCES['rules']})", '',
        f"資源物の場所は可燃のステーションと異なる場合があるので、10/6に現在利用できる分別ステーションを確認します。年末年始の可燃の特別日程は12月の公式告知で確認するため、12/24〜1/5は本人の排出予定も置いていません。新居の地区へ移った後は新居の収集日を別に確認してください。この表は**高台2丁目の現住所用**です。[令和8年度しおりPDF]({SOURCES['shiori']})", '',
        '## 月別カレンダー', '',
        '「夜45／夜60」＝定時後の作業分数。「朝A／朝B」＝市の収集機会。「仮」＝未予約または移動条件未確認。朝の排出担当が確保できることが前提です。色付き画像はLINE用、下の表は検索・修正用です。', '',
    ]
    for y, m in MONTHS:
        md += [f'### {y}年{m}月：{THEMES[(y,m)][0]}', '',
               f'![{y}年{m}月カレンダー](../../house/moving_plan/line/{y}-{m:02d}_calendar.png)', '',
               month_table(y, m), '']
    md += ['## 作業日の具体的な内容', '', '| 日付 | 夜の上限 | やること |', '|---|---:|---|']
    for ds, (mins, title, detail) in WORK.items():
        d = date.fromisoformat(ds)
        md.append(f'| {d.month}/{d.day}（{"月火水木金土日"[d.weekday()]}） | {mins}分 | **{title}**：{detail} |')
    md += ['', '1回で触るのは引き出し1つ、棚1段など小区画に限ります。終了10分前から袋・箱を閉じ、床と通路を戻して終了。途中でも時間上限で止め、休みの日へ振り替えません。', '',
           '## 古着・古紙を昼休みに出せるか', '',
           f"市役所分庁舎1は平日9〜17時なので、受付時間としては昼休みに合います。ただし現在の勤務地が不明で、45分の昼休みに往復できるかは未確認です。**搬出・移動を11:30〜11:55の25分以内に収め、食事に20分残せる場合だけ**実行します。自宅へ戻って積む往復まで詰め込まず、前日までに持ち運べる小口を用意し、安全に運べる量だけを原付で運びます。[古紙・古着の公式案内]({SOURCES['clothes']})", '',
           '4回に分けるのは予定を確保するためで、荷物を測る前に往復数を決めたわけではありません。袋が多く原付に載らない、勤務地から遠い、雨で古紙・古着が濡れる場合は搬出を中止して次便へ。12/4までに減らせていなければ、市へ近隣の集団回収や別の搬出方法を相談し、昼休みの過密な往復で解決しない計画です。', '',
           '古着回収には下着・靴下、汚れた物、ダウン、布団、毛布、カッパ等を混ぜません。回収できない衣類は市の品目ルールに従って可燃・粗大等へ分けます。', '',
           '## まとめて捨てる場合と、レンタカーの判断', '',
           '**基本案は通常収集＋市の粗大ごみ予約回収です。ごみ処分のためのレンタカーは、まだ借りません。** 10/23に袋数、11/18に粗大の品目・数量、11/25に残量を見てから決めます。粗大①②は希望日の例で、回収日・時刻は予約結果に合わせて変更します。', '',
           f"市の粗大ごみは通常、申込後1週間〜10日前後、繁忙期はそれ以上かかります。電話は平日9〜12時・13〜17時なので11:30〜11:40を使えます。市公式LINEからの申込も可能です。搬出は家の中までは行われないため、大物を自分で運べない場合は搬出の手伝い・サービスを別途手配します。[粗大ごみの公式案内]({SOURCES['bulky']})", '',
           f"**クリーンプラザおとくにへの自己搬入は平日13〜16時です。11:30〜12:15の昼休みには入れられず、定時後も16時を過ぎるなら使えません。** 市環境業務課（075-955-9689）への事前連絡が必要です。複数往復する場合は予定回数・種別・車両番号も事前に相談します。市町外のごみを持ち込む案ではありません。[持込窓口]({SOURCES['carry']})／[2026年7月改訂の受入基準PDF・4ページ]({SOURCES['acceptance']}#page=7)", '',
           '| 実際に判明した量・制約 | 選ぶ方法 |', '|---|---|',
           '| 可燃は通常枠で減り、A/Bも次の回収まで保管できる | 現行の18回＋A/B各5回で少しずつ排出。車は不要。 |',
           '| 粗大が数点で当日搬出できる | 市の予約回収。回収場所まで動かす手伝いの必要性を確認。 |',
           '| 通常枠に収まらない袋・粗大が残るが、平日午後に時間を取れる | 市へ事前相談し、13〜16時に自己搬入。レンタカーは品目寸法・重量・荷室を確定してから。 |',
           '| 平日午後も朝の搬出も確保できない | 市に、本人の利用できる時間で対応可能な一般廃棄物の許可業者等を相談。料金・時間は見積もり前なので未確定。 |', '',
           f"自己搬入の処理手数料は**1回100kg以下1,500円**。100kg超〜300kgは超過10kgごとに200円が加算されます。レンタカー・燃料・搬出作業の費用は別です。[公式料金表PDF]({SOURCES['fees']})", '',
           '| 自己搬入の比較例 | 処理手数料だけ |', '|---|---:|',
           '| 1回100kg | 1,500円 |',
           '| 1回200kg | 3,500円 |',
           '| 2回、各100kg | 合計3,000円 |',
           '| 3回、各70kg | 合計4,500円 |', '',
           'このため「一気に1往復が常に最安」とは限りません。**総額＝処理手数料＋車両代＋燃料＋確保する作業時間**で比べます。往復数は、車の有効な積載容量・重量制限・実際の荷物で決めます。車を使う追加案は利用可能時間の変更が必要なため、基本カレンダーへ確定作業として入れていません。', '',
           '## 朝のごみ出しができない場合', '',
           '昼や定時後に通常ステーションへ出す置き換えはできません。袋は室内または自宅敷地内の保管場所にまとめ、当日朝に出す担当を家族等へ頼めるか確認します。A/Bも前夜にステーションへ置きません。粗大は予約時間に合う当日搬出が必要です。', '',
           '担当を頼めない場合は、分別作業の月・水枠はそのまま使い、**10/6昼に市へ相談する作業を優先**します。平日午後の自己搬入時間を別途確保するか、本人の利用可能時間に対応する回収方法を確認します。朝の排出が成立しないまま「毎週捨てられる」とは見積もりません。', '',
           '## 新居へ運ぶ物と、旧居に残す物', '',
           '長岡中央第一ビル（前回掲載53.7㎡・2DK）とカサブランカ（前回掲載36.45㎡・2DK）をモデルにして、**小さい方へ置ける持込量**を先に作ると、どちらを選んでも荷物を調整しやすくなります。畳数や部屋形状、シンク・食洗機給水、大型家電の置場・搬入経路は未確認なので、面積だけで配置を保証しません。[前回の物件リンク集](../2026-10-03/claude_19-05-38_murata_housing_links.md)', '',
           '| 区画 | 今回の扱い |', '|---|---|',
           '| 新居へ | 日常の衣類・寝具・PC、持込予定家電、必要な機材を優先。箱数と大物寸法を11/18〜1/18に確定。 |',
           '| 旧居保管 | 消耗品の在庫、すぐ使わない残す機材等。種類と置場を書き、消耗品を取りに来る箱を作る。旧居を全面退去する前提ではない。 |',
           '| 手放す | 本人が不要と判断した物のみ。衣類・可燃・A・B・古紙・粗大・特別処理に分ける。 |',
           '| 保留 | 1箱まで。12/21に再判定。共有物や処分可否を決められない物は勝手に廃棄対象にしない。 |', '',
           '持込予定の食洗機・乾燥機・洗濯機・冷蔵庫・ワインセラー・PCを不要家電扱いにはしていません。冷蔵庫・洗濯機・衣類乾燥機等を手放すことになった場合は、通常の粗大ごみとは別のリサイクル手続を確認します。', '',
           '入居後の消耗品の補充は、**第2・第4月曜の帰宅時に20分以内で寄る**ことを暫定の習慣にします。1/25は入居済みの場合だけの最初の例です。空の物を買い足す前に旧居の在庫表を確認し、原付に安全に積める小口で持ち帰ります。', '',
           '## 残量を見て計画を変える基準', '',
           '| 確認日 | 数えるもの | 判断 |', '|---|---|---|',
           '| 10/23昼 | 捨てる可燃袋、A類の箱、衣類袋、未着手の収納区画 | 1区画の実測時間×残区画が残りの月水枠を超えるなら、小区画に絞るか追加の搬出支援を検討。休日へ自動振替しない。 |',
           '| 11/18夜 | 粗大品名・数量・最大寸法、搬出の人手 | 11/30の予約申込に必要な情報を確定。売却・譲渡は期限内に決まらなければ処分方法を選び直す。 |',
           '| 11/25夜 | 年内残る可燃袋、A/B、古着・古紙、粗大 | 可燃の残り8回（11/27〜12/22）で処理できるか確認。生活ごみ分を引いた上で不足なら市へ多量ごみ相談。 |',
           '| 12/9夜 | 粗大②と最後のA/Bの残量 | 回収②は必要な時だけ。12/23を越えそうなら1/13のA類等へ送り、入居日と照合。 |',
           '| 1/6夜 | 実際の入居日と残り荷物 | 1/22の暫定目標を入居日に合わせて変更。入居が早ければ1/6〜8に小口荷造りを先行し、旧居保管を活用。 |', '',
           '袋・箱の記録は「日付／品目／新居箱数／旧居保管箱数／処分袋数／次の搬出先」の1行だけで十分です。手放す物の量がまだ分からないため、処分完了・車の往復数・実際の引越日を確定した記録にはしていません。', '',
           '## 今すぐ始める最初の1手', '',
           '**10/5（月）の定時後に15分だけ、4区画を作って衣類の引き出し1つを判定する。** 朝のごみ出し担当は別途確認し、判定した量を1行記録します。', '',
           f"指定の用事日と土日祝には作業を入れていません。祝日は[内閣府の2026・2027年表]({SOURCES['holidays']})で確認しました。LINE送信、粗大予約、車の予約、自動通知設定は実行していません。", '',
           '[タスク正本](../../taskManagement/tasks/moving-declutter.md)／[計画の保存データ](../../house/moving_plan/plan_2026-10-04.json)', '',
    ]
    report.write_text('\n'.join(md), encoding='utf-8')
    data = {'created_at': stamp.isoformat(), 'report': report.relative_to(ROOT).as_posix(),
            'morning_disposal': 'unconfirmed', 'moving_day': 'unconfirmed',
            'preparation_target': '2027-01-22', 'main_disposal_target': '2026-12-23',
            'sources': SOURCES, 'unavailable_dates': sorted(x.isoformat() for x in UNAVAILABLE),
            'holidays': {d.isoformat(): n for d, n in HOLIDAYS.items()},
            'A_dates': sorted(x.isoformat() for x in A), 'B_dates': sorted(x.isoformat() for x in B),
            'usable_pre_year_end_burn_dates': [d.isoformat() for d in burn],
            'work': WORK, 'lunch': LUNCH, 'milestones': MILESTONES,
            'pre_year_end_work_minutes': pre_work,
            'images': [p.relative_to(ROOT).as_posix() for p in images]}
    previous.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    with zipfile.ZipFile(LINE / 'declutter_calendar_LINE.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in images + [LINE / 'LINE_copy_text.txt']:
            z.write(p, p.name)
    print(report.relative_to(ROOT).as_posix())
    print('PNG', len(images), 'night work slots', len(WORK), 'pre-year-end minutes', pre_work, 'burn opportunities', len(burn))


if __name__ == '__main__':
    main()
