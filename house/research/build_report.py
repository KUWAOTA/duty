from __future__ import annotations
import json
import math
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RESEARCH=Path(__file__).resolve().parent

def norm(t):
    return re.sub(r'[\s・.（）()\-－]+','',unicodedata.normalize('NFKC',t)).lower()

def roomkey(r):
    code=r['detail']['tables'].get('取り扱い店舗 物件コード','')
    m=re.fullmatch(r'[KW](\d{5})-(.+)',code)
    return (m[1],norm(m[2])) if m else None

def roomtag(r):
    key=roomkey(r)
    if key:
        code=r['detail']['tables'].get('取り扱い店舗 物件コード','')
        m=re.fullmatch(r'[KW]\d{5}-\d-(\d+)',code)
        return m[1].lstrip('0') if m else key[1].lstrip('0')
    code=r['detail']['tables'].get('取り扱い店舗 物件コード','')
    if code.startswith('HC2-'):
        p=code.split('-')
        if len(p)>=4:return norm(p[-2]).lstrip('0')
    p=code.split('-')
    if len(p)>=3 and re.fullmatch(r'[0-9A-Za-z]+',p[-2]):return norm(p[-2]).lstrip('0')
    return None

def generic(r):return r['name'].startswith(('阪急','ＪＲ','地下鉄'))

def near(a,b):
    pa=a.get('map_point');pb=b.get('map_point')
    if not pa or not pb:return a['address']==b['address']
    return math.hypot((pa['lat']-pb['lat'])*111000,(pa['lon']-pb['lon'])*91000)<65

def same(a,b):
    ka=roomkey(a);kb=roomkey(b)
    if ka and kb and ka==kb:return True
    if ka and kb and ka[0]==kb[0] and ka[1]!=kb[1]:return False
    if '鶏冠井町' in a['address'] and '鶏冠井町' in b['address'] and abs(a['area']-b['area'])<.02 and a['rent']==b['rent'] and a['area'] in [39,56.7]:return True
    if '円明寺' in a['name'] and '円明寺' in b['name'] and ('B棟' in unicodedata.normalize('NFKC',a['name'])) and ('B棟' in unicodedata.normalize('NFKC',b['name'])):return True
    if 'ビレッジハウス長岡' in a['name'] and 'ビレッジハウス長岡' in b['name'] and a['floor']==b['floor'] and abs(a['area']-b['area'])<.1:return True
    aliases=['ヴィラコンフォート','サンライフウィンディア','Uluru','Ｕｌｕｒｕ','柳本荘']
    ta=roomtag(a);tb=roomtag(b)
    if any(norm(x) in norm(a['name']) and norm(x) in norm(b['name']) for x in aliases) and a['floor']==b['floor'] and a['rent']==b['rent']:
        if ta and tb and ta==tb:return True
    if not near(a,b):return False
    if any(norm(x) in norm(a['name']) and norm(x) in norm(b['name']) for x in aliases) and a['floor']==b['floor'] and a['rent']==b['rent']:
        if 'ヴィラコンフォート' in a['name'] and 'ヴィラコンフォート' in b['name'] and a['area']==b['area']:return True
    if a['rent']==b['rent'] and a['floor']==b['floor'] and abs(a['area']-b['area'])<.02 and (generic(a) or generic(b)):
        return True
    if norm(a['name'])==norm(b['name']) and a['floor']==b['floor'] and abs(a['area']-b['area'])<.05 and abs(a['rent']-b['rent'])<=1000:
        if ka and kb and ka[1]!=kb[1]:return False
        # Keep distinct rooms in the same building when the agency's room identifiers differ.
        ca=a['detail']['tables'].get('取り扱い店舗 物件コード','')
        cb=b['detail']['tables'].get('取り扱い店舗 物件コード','')
        if ca and cb and ca!=cb and ca.split('-')[0]==cb.split('-')[0]:return False
        return True
    if '鶏冠井町' in a['address'] and '鶏冠井町' in b['address'] and abs(a['area']-b['area'])<.02 and a['rent']==b['rent'] and a['area'] in [39,56.7]:return True
    return False

def excluded(r):
    a=unicodedata.normalize('NFKC',r['address'])
    if re.search(r'長岡京市長岡2(?:\D|$)',a) or any(x in a for x in ['野添','京都市伏見区','山科','宇治']):return '家族が指定した除外地域'
    if '小池マンション' in r['name']:return '長岡1丁目・2丁目の住所表記が混在。除外地域との照合待ち'
    if r['hazard_flag']=='区域表示あり':return '掲載地図の参考地点に災害区域の表示'
    return ''

def feature(r):
    f=r['detail']['features'];parts=[]
    parts.append('ACあり' if 'エアコン' in f else 'AC設置要確認')
    if 'ネット使用料不要' in f:parts.append('ネット無料')
    elif any(x in f for x in ['光ファイバー','ネット専用回線','高速ネット','インターネット']):parts.append('回線記載あり')
    else:parts.append('回線要確認')
    if 'バストイレ別' in f:parts.append('BT別')
    else:parts.append('浴室・トイレ要確認')
    if 'バイク置場' in f:parts.append('バイク置場')
    if '室内洗濯置' in f:parts.append('室内洗濯')
    elif '洗濯' not in f:parts.append('洗濯位置要確認')
    if '3口以上コンロ' in f:parts.append('3口以上')
    elif '2口コンロ' in f:parts.append('2口コンロ')
    elif '1口コンロ' in f:parts.append('1口コンロ・シンク注意')
    return '／'.join(parts)

def routes(r):
    t=r['detail']['tables'].get('駅徒歩','')
    texts=[t]+r['access']
    found=[]
    for t in texts:
        for station,w in re.findall(r'/([^/\s]+)駅\s*歩(\d+)分',t):
            x=(station,int(w))
            if x not in found:found.append(x)
    return found

def access(r):
    short=[(s,w) for s,w in routes(r) if w<=5]
    if short:return '・'.join(f'{s}{w}分' for s,w in short)
    buses=[x for x in r['access'] if 'バス' in x]
    return '・'.join(x.replace('阪急バス/','').replace('阪急京都線/','').replace('ＪＲ東海道本線/','') for x in buses) or '要確認'

def commute(r):
    rr=dict(routes(r))
    if rr.get('長岡京',99)<=21:
        w=rr['長岡京'];return f'徒歩約{w+2}〜{w+5}分'
    for s,train in [('向日町',3),('桂川',5),('西大路',7),('京都',11),('山崎',4),('島本',7),('高槻',13)]:
        if rr.get(s,99)+train+7<=25:
            w=rr[s];return f'JR経由約{w+train+7}〜{w+train+12}分（推定）'
    p=r.get('map_point')
    if p:
        dist=math.hypot((p['lat']-34.922)*111,(p['lon']-135.702)*91)
        lo=max(5,round(dist*1.3/25*60+2));hi=max(lo+3,round(dist*1.5/18*60+3))
        return f'原付約{lo}〜{hi}分（距離推定・要実走）'
    return '通勤経路・所要時間要確認'

def group_rows(rows):
    groups=[]
    for r in sorted(rows,key=lambda r:(generic(r),-r['area'],r['total'],r['name'])):
        g=next((g for g in groups if any(same(r,x) for x in g)),None)
        if g is None:groups.append([r])
        else:g.append(r)
    # Merge groups again when a third listing bridges different agency labels.
    changed=True
    while changed:
        changed=False
        for i in range(len(groups)):
            j=next((j for j in range(i+1,len(groups)) if any(same(a,b) for a in groups[i] for b in groups[j])),None)
            if j is not None:
                groups[i].extend(groups.pop(j));changed=True;break
    return groups

OVERRIDE={'100511822482':'フレンドコスモス 101（SUUMOでは名称非公開）'}
PRIORITY=['100525212701','100501045272','100510528610','100503937123','100527847957','100507422280','100371616988','100490316423','100461289576','100511822482','100424903722']

def main():
    raw=json.loads((RESEARCH/'verified_2026-10-03.json').read_text(encoding='utf-8'))['rows']
    rejected=[dict(r,exclusion_reason=excluded(r)) for r in raw if excluded(r)]
    pool=[r for r in raw if not excluded(r)]
    groups=group_rows(pool)
    selected=[]
    for g in groups:
        r=g[0].copy();r['members']=g
        r['name']=OVERRIDE.get(r['bc'],r['name'])
        if generic(r):r['name']=r['address'].replace('京都府','')+'・'+r['layout']+'（建物名非公開）'
        issues=[]
        if any(x['hazard_flag']=='境界付近' for x in g):issues.append('災害区域の境界付近')
        if any(x['hazard_flag']=='位置未確認' for x in g):issues.append('地図位置未確認')
        if any('ビレッジハウス長岡' in x['name'] for x in g):issues.append('地図位置が別掲載と不一致')
        if len({x['layout'] for x in g})>1 or len({x['area'] for x in g})>1:issues.append('間取り・面積が掲載間で不一致')
        if len({x['floor'] for x in g})>1:issues.append('階数が掲載間で不一致')
        if len({x['rent'] for x in g})>1:issues.append('家賃が掲載間で不一致')
        points=[x['map_point'] for x in g if x.get('map_point')]
        if any(math.hypot((a['lat']-b['lat'])*111000,(a['lon']-b['lon'])*91000)>100 for a in points for b in points):issues.append('掲載地図の位置が不一致')
        if '定期借家' in r['detail']['tables'].get('契約期間',''):issues.append(r['detail']['tables']['契約期間'])
        r['issues']=issues
        r['section']='C' if issues and any(x in ' '.join(issues) for x in ['災害','地図','階数','間取り']) else ('A' if r['area']>=30 else 'B')
        if any(r['bc']==x for x in PRIORITY):r['rank']=PRIORITY.index(r['bc'])
        else:r['rank']=100+r['total']/10000-r['area']/20
        selected.append(r)
    # An agency-only listing not duplicated in the station-based search.
    selected.append({'bc':'KS-006','name':'奥海印寺南垣外・2K（物件006）','url':'https://ks-sp.com/?p=1033&post_type=fudo',
                     'address':'京都府長岡京市奥海印寺南垣外','rent':32000,'fee':3000,'total':35000,'area':26,'layout':'2K','floor':'1階／2階の記載不一致',
                     'access':['阪急京都線/長岡天神駅 歩25分','阪急バス/海印寺 歩2分'],'age':'1968年11月築','deposit':'記載なし','key_money':'記載なし',
                     'detail':{'features':'バストイレ別、バイク置場、洗濯機置き場、シャワー、専用トイレ','tables':{'駅徒歩':'阪急京都線/長岡天神駅 歩25分','構造':'木造','入居':'即時','契約期間':'要確認','情報更新日':'記事2026/09/19'}},
                     'hazard_flag':'位置未確認','hazards':{},'members':[],'issues':['地図位置未確認','説明は2階、概要表は1階。階数要確認','原付20分以内の実走確認が必要'],
                     'section':'C','rank':130})
    selected.sort(key=lambda r:(r['section'],r['rank'],r['total'],r['name']))
    selected=selected[:100]
    for i,r in enumerate(selected,1):r['number']=i
    stamp=datetime.now();date=stamp.strftime('%Y-%m-%d')
    path=ROOT/'daily'/date/f"claude_{stamp.strftime('%H-%M-%S')}_murata_housing_links.md"
    previous=RESEARCH/'selected_2026-10-03.json'
    if previous.exists():
        old=json.loads(previous.read_text(encoding='utf-8')).get('report','')
        if old.startswith('daily/'+date+'/'):path=ROOT/old
    path.parent.mkdir(parents=True,exist_ok=True)
    counts=Counter(r['section'] for r in selected)
    lines=[
        '# 村田製作所本社（JR長岡京）への通勤を前提にした賃貸候補リンク集',
        '',f"調査・作成: {stamp.strftime('%Y-%m-%d %H:%M:%S')}（日本時間）",'',
        f"**通常賃貸は、重複を整理して{len(selected)}候補を掲載しました。広さを優先する暫定候補{counts['A']}件、小さめの予備候補{counts['B']}件、位置・ハザード境界・掲載不一致の確認を先に行う保留候補{counts['C']}件です。別枠で京大周辺のシェアハウス4施設と、京大研究室に関係する参考施設1件を載せています。**",'',
        '**すべての必須条件を満たすと確認できた物件は、現時点では0件です。** 特に50〜60cmの魚を扱えるシンク、持込家電の配置、実際の通信品質、冬の室温、告知事項は広告だけでは確認しきれません。この一覧は、家賃・交通・地域で絞り込み、問い合わせと内見を行うための候補です。C欄は家族のハザード条件を満たすか未確定なので、確認が終わるまで内見優先候補にしません。', '',
        '最初に問い合わせるなら、**長岡中央第一ビル、ハイツ山田、カイデハイツ、ヴィーヴル向日、フレンドコスモス**です。費用を抑えるなら西向日ハイツ、カサブランカも比較対象になります。鎌田マンションは掲載間の間取り不一致を照合してから検討します。リンクは以下の表にあります。', '',
        '## 要件の扱い', '',
        '参照: [本人の要件](../../house/requirements_by_myself.md)、[家族の要件](../../house/requirement_by_family.md)。', '',
        '| 要件 | 今回の扱い |', '|---|---|',
        '| 家賃7万円台まで | 賃料本体79,999円以下。管理費と合計も表示。合計8万円以上は明示し、安い候補を優先。光熱費・保証料等は合計に含まない。 |',
        '| 原付20分以内、または徒歩・公共交通25分以内 | 徒歩・JR経由を優先。原付・バス利用は下記の概算と実走・時刻表確認が必要。原付候補は公共交通で25分を超えても本人のOR条件に沿う。 |',
        '| 公共交通＋徒歩5分以内で駅へアクセス | 鉄道駅へ徒歩5分以内、または駅へ行くバス停へ徒歩5分以内と解釈。バス候補は系統・行先・時刻表の確認が必要。 |',
        '| 機材・家具・家電の置き場所 | 30㎡以上と2DK・2LDK・3DKを優先。本人は最低面積を指定していないため25〜30㎡も別枠で調査。小さい部屋は外部倉庫の費用も含めて判断。 |',
        '| シンク、空調、冬の寒さ、シャワー、トイレ、水道 | シンク内寸と作業台寸法は全件未確認。空調の広告記載は表に表示。設備の現物・給水・排水・断熱は内見または管理会社確認が必要。 |',
        '| 音声通話ができるネット | 光回線・ネット無料等の記載を拾う。ただし回線方式、上り速度、混雑時の実測は未確認。 |',
        '| 長岡二丁目・野添・山科・宇治・京都市伏見区を避ける | 所在地の表記で除外。小池マンションは長岡一丁目・二丁目の記載が混在するため除外地域との照合が済むまで外す。 |',
        '| 浸水・土砂災害の危険区域を避ける | 国土地理院の参考地点確認で区域表示がある物件は外す。境界近接と位置不明はC欄。敷地単位の確定と自治体最新版との照合は未完了。 |',
        '| 原付置場、防音、外での機材水洗い等のWANT | 必須フィルターにしない。掲載されている設備だけ記載。 |',
        '| 瑕疵・告知事項 | 表の全候補は未確認。取得した設備・備考等に明示は見つからなかったが、記載なしは「瑕疵なし」を意味しない。 |',
        '', '## 通勤時間の読み方', '',
        '勤務先は東神足1丁目10番1号の本社を想定しています。公式案内ではJR長岡京駅東口から徒歩約1分、阪急長岡天神駅東口から徒歩約15分です。[村田製作所・本社アクセス](https://corporate.murata.com/ja-jp/company/muratalocations/branch/headoffice)', '',
        '表の徒歩時間は物件広告のJR長岡京駅への徒歩に駅周辺の移動を2〜5分足した目安です。JR経由は広告の駅徒歩に乗車と駅内移動・短い待ち時間を加えた推定で、朝の通勤便は未指定です。京都〜長岡京は約10〜11分、向日町〜長岡京は約3分を基準にしています。[長岡京市のアクセス案内](https://www.city.nagaokakyo.lg.jp/0000001981.html)、[区間時刻表](https://www.jorudan.co.jp/time/to/%E9%95%B7%E5%B2%A1%E4%BA%AC_%E5%90%91%E6%97%A5%E7%94%BA/?r=%E6%9D%B1%E6%B5%B7%E9%81%93%E3%83%BB%E5%B1%B1%E9%99%BD%E6%9C%AC%E7%B7%9A)', '',
        '原付時間は掲載参考地点と本社の距離から推定した調査用の目安です。走行経路、信号、渋滞、駐輪・入館時間を確認していないため20分以内を保証しません。範囲の上限が20分を超える場合やJR経由で25分を超える場合は、必要な便・経路で上限内に収まることを確認してください。特にフレンドコスモス、円明寺ヶ丘団地、バス利用物件は通勤の確認を先に行います。', '',
        '薬師堂からJR長岡京駅西口へ向かう系統と、長法寺・上長法寺を通る長岡京線は確認できました。カサブランカの「バス3分」は物件広告の表記で、別の経路検索には長岡天神〜上長法寺11分の便もあり、そのまま確定時間として使いません。[阪急バス・薬師堂の行先](https://transfer-cloud.navitime.biz/hankyubus/courses?busstop=00021044)、[阪急バス・路線別時刻表](https://www.hankyubus.co.jp/rosen/timetable/)、[長岡天神〜上長法寺の便の例](https://ekitan.com/transit/bus-section/sf-5701/st-1100482)', '',
        '## ハザードの確認範囲と記号', '',
        '出典: [国土地理院「重ねるハザードマップ」](https://disaportal.gsi.go.jp/maps/)。SUUMO掲載地図の参考座標で、洪水（想定最大規模）、内水、急傾斜、土石流、地すべり、ため池の公開データを照合しました。画像データを加工・読み取り、地点と近傍の区域色の有無を一次判定しています。敷地位置や境界の確定には使っていません。[国土地理院・利用上の説明](https://disaportal.gsi.go.jp/hazardmapportal/hazardmap/faq/faq.html)', '',
        '- **H0**: 取得できたデータでは参考地点と近傍に区域色を見つけていない。安全・要件充足の証明ではない。',
        '- **H△**: 参考地点は無着色だが近傍に区域色がある。境界の外か、地図の位置ずれかを正確な住所で確認する。',
        '- **H?**: 参考位置不明、掲載位置不一致などで未判定。',
        '- **データ不足**: 一部の災害データを取得できない。区域外と判断せず、自治体マップで確認する。',
        '',
        '細かいズームでデータが得られない場合は広い地図を参照したため、小さな区域や境界の確認には限界があります。各物件の正確な番地・敷地を不動産会社から取得し、次の最新版も確認してください。', '',
        '- [長岡京市・2025年版防災ハザードマップ](https://www.city.nagaokakyo.lg.jp/0000000329.html)',
        '- [向日市・防災情報](https://www.city.muko.kyoto.jp/life/1/5/23/)',
        '- [大山崎町・防災ハザードマップ](https://www.town.oyamazaki.kyoto.jp/annai/somuka/kikikanri/hinanjo/index.html)',
        '- [京都市・防災情報マップ](https://www.bousaimap.city.kyoto.lg.jp/)／[ハザードマップの説明](https://www.bousai.city.kyoto.lg.jp/0000000146.html)',
        '', '## 一覧の凡例', '',
        'AC＝エアコン。BT別＝バス・トイレ別。回線の記載と実際の通信性能は別です。バイク置場と書かれていても原付のサイズ・料金・空きは確認してください。「AC設置要確認」はエアコンなしという断定ではなく、広告で設置可否まで確認できていない意味です。', '',
        '**全件共通: シンク内寸・家電配置・冬の寒さ・水道/シャワーの現物・通信実測・告知事項は要確認。** 表の告知欄はこの未確認状態を明示しています。月額合計は家賃＋掲載管理費だけです。', ''
    ]
    headings={'A':'A. 広さを優先して問い合わせる暫定候補（30㎡以上）','B':'B. 小さめの予備候補（25〜30㎡未満）','C':'C. ハザード・位置・掲載不一致を先に確認する保留候補'}
    for section in ['A','B','C']:
        sectionrows=[r for r in selected if r['section']==section]
        lines += ['## '+headings[section], '',f'{len(sectionrows)}件。', '',
                  '| No. | 物件・詳細リンク／所在地 | 間取り・面積・階 | 家賃／管理費 → 月額合計 | 駅・バス停への徒歩／本社への目安 | 設備の広告記載 | ハザード・告知 |',
                  '|---:|---|---|---|---|---|---|']
        for r in sectionrows:
            links=f"[{r['name']}]({r['url']})"
            alternatives=[x for x in r.get('members',[]) if x['url']!=r['url']]
            for j,a in enumerate(alternatives,1):links+=f" / [別掲載{j}]({a['url']})"
            addr=r['address'].replace('京都府','').replace('大阪府','')
            price=f"{r['rent']:,}円／{r['fee']:,}円 → **{r['total']:,}円**"+('（合計8万円以上）' if r['total']>=80000 else '')
            hazard='H△' if any('災害区域' in x for x in r['issues']) else ('H?' if any('地図' in x for x in r['issues']) else 'H0')
            if any(v['result']=='データ取得なし・未確認' for v in r['hazards'].values()):hazard+='・一部データ不足'
            p=r.get('map_point')
            if p:hazard+=f" [参考地図](https://disaportal.gsi.go.jp/maps/?ll={p['lat']:.7f},{p['lon']:.7f}&z=17)"
            issues='; '.join(r['issues'])
            lines.append(f"| {r['number']} | {links}<br>{addr} | {r['layout']}／{r['area']:g}㎡／{r['floor']} | {price} | {access(r)}<br>{commute(r)} | {feature(r)} | {hazard}<br>告知: **未確認**"+(f'<br>{issues}' if issues else '')+' |')
        lines.append('')
    lines += ['## 最初に確認したい物件の補足', '',
              '- **長岡中央第一ビル**: 53.7㎡・2DK、月額72,000円。エアコン2台、収納1間半、2口コンロ、ネット無料の記載。機材と家電の配置を検討しやすい広さ。無料ネットの回線方式・上り速度とシンク実寸が最初の確認点。',
              '- **ハイツ山田**: 2階45.05㎡と3階43.74㎡。ともに月額72,000円、長岡天神駅2分・JR長岡京駅14分の掲載。エアコン・光ファイバー記載。室外洗濯機の記載がある募集もあり、洗濯機と乾燥機の置き方・雨対策を確認。',
              '- **カイデハイツ**: 58.32㎡・3DK、101と203の募集をまとめて比較。機材用の部屋を分けやすい。西向日駅5分、原付通勤の確認が必要。空調・光回線・大型家電の設置可否は未確定。',
              '- **ヴィーヴル向日**: 51.15㎡・2LDK、月額71,000円。RC、収納2間、室内洗濯の記載。防音性能は未測定。空調の設置と通信の導入可否を確認。',
              '- **フレンドコスモス**: 55.12㎡・2LDK、月額78,000円。2口IH・システムキッチン、室内洗濯、バイク置場の掲載。長法寺バス停4分。原付通勤、空調の設置、シンク実寸を確認。[名称・別の掲載元](https://www.elitz.co.jp/detail/48261-0101/)',
              '- **ウエストヒルB棟**: 40.78㎡・1LDK、家賃60,000円、薬師堂バス停5分。**定期借家2030年12月まで**の掲載があるため再契約の可否を確認。管理費なしでも保険・サポート・保証料等の月額費用が別途掲載。',
              '- **円明寺ヶ丘団地B棟**: 54.52㎡で広さは候補になるが、B棟204の募集と4階表記の募集があり、階数・家賃の整合が取れていないためC欄。別住戸か同一住戸かを確認してから比較。',
              '- **ビレッジハウス長岡**: 同じ住所の地図マーカーが離れた地点を示す例があるためC欄。公式住所は粟生畑ヶ田24。上限確認には棟と部屋を指定する。[運営会社の物件ページ](https://www.villagehouse.jp/chintai/kinki/kyoto/nagaokakyo-shi-262099/nagaoka-5044/)',
              '', '## 京大周辺のシェアハウス（本人が許容した遠距離の例外枠）', '',
              '以下は通常の20分/25分通勤条件を満たすと確認した物件ではありません。「京大系など面白いシェアハウスなら多少遠くてもよい」という本人の記述に基づく別枠です。シンクの共同利用、魚をさばくこと、匂い・夜のVC、手銛や採集用具の保管、自前の冷蔵庫・洗濯機・乾燥機等を持ち込めるかは必ず確認してください。京大の近くという説明だけで京大関係者が運営していると推定していません。家族の地域・ハザード条件も未確認です。', '',
              '| 施設・リンク | 掲載費用・設備 | 募集状態と注意点 |', '|---|---|---|',
              '| [Satolet（さとれ）](https://satolet.site/details/) / [空室情報](https://satolet.site/) | 家賃49,000円、共益費13,480円の初期費用例。バルコニー付＋1,000円。10Gbps光回線・各室有線LAN、共用の広い調理台、洗濯機・ガス乾燥機、個室空調の記載。元田中駅1分。 | 空室は個室ごとに確認。日本人学生・社会人も対象という案内。シンクの内寸は未確認。共用設備があるので、持込家電の置場を確認。 |',
              '| [Aminif京都 吉田京大前](https://aminif.com/) | 京大徒歩2分。NURO光2ギガ・共用キッチン・洗濯乾燥機・コワーキング。通常入居の部屋別家賃は要確認。 | 社会人も対象という案内。学生の割引を社会人の予算に使わない。短期プランは5,000円/日で予算外。通常入居条件を問い合わせる候補。 |',
              '| [EVER KITASHIRAKAWA](https://ever-kitashirakawa.com/) | 公式案内の家賃は月55,000円〜。京大徒歩10分を案内。 | 空室、共益費、個室寸法、ネット、機材・家電持込を確認。全員の家賃が55,000円とは限らない。 |',
              '| [エイトネスト 京大鞠小路](https://www.sharehouse180.net/houses/8nest-kyodaimarikoji/) | 家賃43,000〜61,000円の掲載。京大吉田キャンパス徒歩4分。 | **確認した掲載は満室**（最終更新2026/08/06）。空室がある候補の件数には含めず、将来の候補として残す。 |',
              '',
              '京大関係者による企画という条件に直接関係する例は、[新建築社 北大路ハウス](https://hirataalab.wixsite.com/website-kitaojihouse)です。京都大学平田晃久研究室を中心に建築学生のために企画された6人用住宅という説明があります。ただし一般社会人の募集、家賃、現在の空室を確認できず、入居候補の件数には含めません。',
              '', '## 不動産会社にまとめて送れる確認文', '',
              '> 村田製作所本社（JR長岡京駅東口）へ通勤する住居を探しています。家賃は7万円台までを希望します。候補の現在の空室、正確な住所・棟・部屋番号、管理費等を含む毎月の必須費用を教えてください。', '>',
              '> 長岡二丁目・野添・山科・宇治・京都市伏見区と、浸水・土砂災害の危険区域を避けています。最新の洪水・内水・土砂災害ハザードマップで物件敷地がどこに当たるか確認できる資料をお願いします。', '>',
              '> 50〜60cm程度の魚を調理したいので、シンク槽の内寸（幅・奥行・深さ）と調理台の寸法を教えてください。魚が丸ごと収まる必要はありませんが、作業に使える大きさか確認したいです。写真だけでなく採寸を希望します。', '>',
              '> 冷蔵庫GR-U36SV(ZJ)、洗濯機NA-F6B1、乾燥機NH-D603、食洗器DWS-600D、ワインセラーFURNIEL SAB-50G、PC机・モニター2枚と機材を持ち込みます。搬入口・室内通路・各家電置場・コンセント・給排水を確認したいです。', '>',
              '> エアコンの有無または設置許可、窓・断熱・冬の室温、シャワー・トイレ・水道、インターネットの回線方式と個別光回線を引けるか、夜間に音声通話をする際の注意、心理的・物理的な瑕疵や告知事項の有無を教えてください。告知事項は書面で確認したいです。', '>',
              '> 原付置場と屋外で機材を水洗いできる場所は、可能なら希望します。原付20分以内または徒歩・公共交通25分以内の通勤経路と、徒歩5分以内で利用できる駅または駅へ向かうバス停も確認したいです。',
              '', '## 調査対象と除外記録', '',
              f'駅別・市内検索で見つけた**{len(raw)}件の個別掲載**について、詳細ページと掲載地図を取得しました。検索した駅は、長岡京・長岡天神・西山天王山・西向日・東向日・向日町・桂川・西大路・京都・山崎・大山崎・島本・水無瀬・高槻です。長岡京市・向日市の市内検索から、バス停徒歩5分以内の掲載も拾いました。大山崎町の追加市内検索はエラーで取得できず、駅別検索で補っています。網羅的な全サイト検索や全物件の空室保証ではありません。', '',
              f'除外した掲載は{len(rejected)}件（重複を含む）です。内訳: '+ '、'.join(f'{k}: {v}件' for k,v in Counter(r['exclusion_reason'] for r in rejected).items())+'。', '',
              'たとえばJR長岡京駅近くの登龍閣・アクエルド長岡京、桂川駅近くの第二晴風荘、西大路駅近くのラムダ西大路・ステラランド、大山崎駅近くのマンション晃苑、水無瀬・高槻の多くの掲載は、参考地点に浸水等の区域表示があり通常候補から外しました。これは地域全体の評価ではなく、掲載参考地点を使った今回の絞り込みです。正確な敷地が異なれば判定を見直す必要があります。', '',
              '同じ部屋と判断できる募集は部屋コード・参考位置・階・面積・費用等でまとめ、別掲載リンクを同じ行に残しました。間取り等が食い違う場合はC欄に置いています。別室と確認できる部屋番号や階の違いは別候補として扱っています。100件に合わせるために既知の不適合物件を混ぜていません。', '',
              '[候補・取得情報・ハザード照合・除外理由の保存データ](../../house/research/selected_2026-10-03.json)。広告は変わるため、家賃・募集状況はリンク先と不動産会社で再確認してください。', ''
              ]
    path.write_text('\n'.join(lines),encoding='utf-8')
    (RESEARCH/'selected_2026-10-03.json').write_text(json.dumps({'created_at':stamp.isoformat(),'report':str(path.relative_to(ROOT)).replace('\\','/'),'counts':dict(counts),'selected':selected,'rejected':rejected},ensure_ascii=False,indent=2),encoding='utf-8')
    print(path)
    print('Selected',len(selected),'sections',dict(counts),'rejected',len(rejected),'source IDs',len(raw))
    for r in selected:print(r['number'],r['section'],r['name'],r['area'],r['total'],r['issues'])

if __name__=='__main__':main()
