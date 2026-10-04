from __future__ import annotations
import concurrent.futures as cf
import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlencode
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
STATIONS = [
    ('長岡京', 'kyoto', '26920', '2420'),
    ('長岡天神', 'kyoto', '26950', '2095'),
    ('西山天王山', 'kyoto', '83780', '2095'),
    ('西向日', 'kyoto', '29420', '2095'),
    ('東向日', 'kyoto', '32470', '2095'),
    ('向日町', 'kyoto', '38640', '2420'),
    ('桂川', 'kyoto', '28425', '2420'),
    ('西大路', 'kyoto', '28420', '2420'),
    ('京都', 'kyoto', '12011', '2420'),
    ('山崎', 'kyoto', '40250', '2420'),
    ('大山崎', 'kyoto', '06430', '2095'),
    ('島本', 'osaka', '80807', '2420'),
    ('水無瀬', 'osaka', '37190', '2095'),
    ('高槻', 'osaka', '22420', '2420'),
    ('長岡京市・バス利用', 'kyoto', '26209', ''),
    ('向日市・バス利用', 'kyoto', '26208', ''),
    ('大山崎町・バス利用', 'kyoto', '26303', ''),
]

def get(url):
    r=requests.get(url, timeout=30, headers={'User-Agent':'Mozilla/5.0'})
    r.raise_for_status()
    s=BeautifulSoup(r.content, 'html.parser')
    if s.title and 'エラー' in s.title.text:
        raise ValueError(s.title.text)
    return s

def txt(s, q):
    e=s.select_one(q)
    return e.get_text(' ', strip=True) if e else ''

def money(v):
    m=re.search(r'([\d.]+)万円', v)
    if m: return round(float(m[1])*10000)
    m=re.search(r'(\d+)円', v)
    return int(m[1]) if m else 0

def collect(st):
    name, prefecture, code, rail=st
    params={'ar':'060','bs':'040','ct':'8.0','mb':'25','pc':'50'}
    if rail:params.update({'ek':rail+code,'rn':rail,'ra':'026' if prefecture=='kyoto' else '027','et':'5'})
    else:params.update({'ta':'26','sc':code})
    initial='https://suumo.jp/jj/chintai/ichiran/FR301FC001/?'+urlencode(params)
    pending=[initial]; seen=set(); rows=[]
    while pending and len(seen)<12:
        url=pending.pop(0)
        if url in seen: continue
        seen.add(url)
        s=get(url)
        for c in s.select('.cassetteitem'):
            base={'name':txt(c,'.cassetteitem_content-title'),'address':txt(c,'.cassetteitem_detail-col1'),
                  'access':[x.get_text(' ',strip=True) for x in c.select('.cassetteitem_detail-text')],
                  'age':txt(c,'.cassetteitem_detail-col3'),'type':txt(c,'.cassetteitem_content-label'),
                  'list_url':url,'search_station':name}
            if not rail and not any('バス' in a and re.search(r'歩[1-5]分',a) for a in base['access']):continue
            for tr in c.select('tr.js-cassette_link'):
                a=tr.select_one('a.js-cassette_link_href')
                bc=tr.select_one('input[name=bc]')
                tds=tr.select('td')
                if not a or not bc: continue
                row=base.copy()
                row.update({'bc':bc['value'],'url':urljoin(url,a['href']).split('?')[0]+'?bc='+bc['value'],
                            'rent':money(txt(tr,'.cassetteitem_price--rent')),
                            'fee':money(txt(tr,'.cassetteitem_price--administration')),
                            'deposit':txt(tr,'.cassetteitem_price--deposit'),
                            'key_money':txt(tr,'.cassetteitem_price--gratuity'),
                            'layout':txt(tr,'.cassetteitem_madori'),
                            'area':float(re.search(r'[\d.]+',txt(tr,'.cassetteitem_menseki'))[0]),
                            'floor':tds[2].get_text(' ',strip=True)})
                row['total']=row['rent']+row['fee']
                if row['rent']<80000 and row['area']>=25: rows.append(row)
        for a in s.select('a'):
            if a.get_text(strip=True)=='次へ':
                nxt=urljoin(url,a.get('href',''))
                if nxt not in seen: pending.append(nxt)
        time.sleep(.25)
    print(f'{name}: {len(rows)} rooms, {len(seen)} pages',flush=True)
    return rows

def main():
    allrows=[]; errors=[]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        jobs={pool.submit(collect,st):st[0] for st in STATIONS}
        for f in cf.as_completed(jobs):
            try: allrows.extend(f.result())
            except Exception as e: errors.append({'station':jobs[f],'error':str(e)})
    bybc={r['bc']:r for r in allrows}
    rows=list(bybc.values())
    (ROOT/'listings_2026-10-03.json').write_text(json.dumps({'retrieved_at':datetime.now().isoformat(),'rows':rows,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'TOTAL: {len(allrows)}, unique listing IDs: {len(rows)}, errors: {errors}',flush=True)

if __name__=='__main__':main()
