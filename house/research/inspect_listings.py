from __future__ import annotations
import concurrent.futures as cf
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import requests
from bs4 import BeautifulSoup
from collect_listings import get

ROOT=Path(__file__).resolve().parent

def inspect(row):
    row=row.copy()
    try:
        s=get(row['url'])
        tables={}
        for tr in s.select('tr'):
            children=tr.find_all(['th','td'],recursive=False)
            for i in range(0,len(children)-1,2):
                if children[i].name=='th':
                    tables[children[i].get_text(' ',strip=True)]=children[i+1].get_text(' ',strip=True)
        heading=s.find(string=re.compile('部屋の特徴・設備'))
        features=''
        if heading:
            h=heading.find_parent(['h2','h3'])
            if h:
                sib=h.find_next('ul')
                if sib:features=sib.get_text(' ',strip=True)
        row['detail']={'tables':tables,'features':features,'retrieved_at':datetime.now().isoformat()}
        row['detail']['source_links']=[urljoin(row['url'],a['href']) for a in s.select('a[href]') if '情報掲載元' in a.get_text() or '物件詳細' in a.get_text() and 'kyoto-life' in a['href']]
        # SUUMO's public map marker is approximate and may not identify the lot.
        mapurl=row['url'].split('?')[0]+'kankyo/?bc='+row['bc']
        m=get(mapurl)
        match=re.search(r'ido=([\d.]+)&(?:amp;)?keido=([\d.]+)',str(m))
        if match:
            row['map_point']={'lat':float(match[1]),'lon':float(match[2]),'source':mapurl,'accuracy':'掲載地図の参考地点。敷地一致は未確認'}
        row['alive']=True
        print(row['bc'],row['name'],tables.get('構造','?'),row.get('map_point',{}).get('lat','?'),flush=True)
    except Exception as e:
        row['alive']=False
        row['error']=str(e)
        print('ERROR',row['bc'],str(e),flush=True)
    return row

def main():
    data=json.loads((ROOT/'listings_2026-10-03.json').read_text(encoding='utf-8'))
    existing={}
    prior=ROOT/'details_2026-10-03.json'
    if prior.exists():existing={r['bc']:r for r in json.loads(prior.read_text(encoding='utf-8'))['rows'] if r.get('alive')}
    rows=[]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        rows=[existing[r['bc']] for r in data['rows'] if r['bc'] in existing]
        jobs=[pool.submit(inspect,r) for r in data['rows'] if r['bc'] not in existing]
        for f in cf.as_completed(jobs):rows.append(f.result())
    (ROOT/'details_2026-10-03.json').write_text(json.dumps({'retrieved_at':datetime.now().isoformat(),'rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
    print('TOTAL',len(rows),'alive',sum(r['alive'] for r in rows),flush=True)

if __name__=='__main__':main()
