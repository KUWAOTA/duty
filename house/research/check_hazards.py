from __future__ import annotations
import concurrent.futures as cf
import io
import json
import math
from pathlib import Path
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'hazard_tiles'
LAYERS={
    '洪水':'01_flood_l2_shinsuishin_data',
    '内水':'02_naisui_data',
    '急傾斜':'05_kyukeishakeikaikuiki',
    '土石流':'05_dosekiryukeikaikuiki',
    '地すべり':'05_jisuberikeikaikuiki',
    'ため池':'07_tameike',
}

def xy(lat,lon,z):
    return ((lon+180)/360*2**z,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*2**z)

def fetch(task):
    layer,z,x,y=task
    path=CACHE/f'{layer}_{z}_{x}_{y}.png'
    url=f'https://disaportaldata.gsi.go.jp/raster/{layer}/{z}/{x}/{y}.png'
    try:
        if path.exists(): raw=path.read_bytes();status=200
        else:
            r=requests.get(url,timeout=20);raw=r.content;status=r.status_code
        if status==200:
            im=Image.open(io.BytesIO(raw)).convert('RGBA')
            if not path.exists():path.write_bytes(raw)
            return task,{'status':status,'image':im,'url':url}
        return task,{'status':status,'url':url}
    except Exception as e:return task,{'status':'error','error':str(e),'url':url}

def main():
    CACHE.mkdir(exist_ok=True)
    data=json.loads((ROOT/'details_2026-10-03.json').read_text(encoding='utf-8'))
    tasks=set()
    for row in data['rows']:
        p=row.get('map_point')
        if not p:continue
        for z in [14,13,12,10]:
            fx,fy=xy(p['lat'],p['lon'],z)
            for layer in LAYERS.values():tasks.add((layer,z,int(fx),int(fy)))
    found={}
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for task,r in pool.map(fetch,sorted(tasks)):found[task]=r
    for row in data['rows']:
        p=row.get('map_point'); hazards={}
        if p:
            for name,layer in LAYERS.items():
                results=[]
                for z in [14,13,12,10]:
                    fx,fy=xy(p['lat'],p['lon'],z)
                    r=found[(layer,z,int(fx),int(fy))]
                    if r['status']==200:
                        im=r['image'];px=int(fx%1*256);py=int(fy%1*256)
                        pixel=im.getpixel((px,py))
                        # Nearby colours are recorded separately, never called a lot-level determination.
                        pad=3 if z>=13 else 1
                        adjacent={im.getpixel((ix,iy)) for ix in range(max(0,px-pad),min(256,px+pad+1)) for iy in range(max(0,py-pad),min(256,py+pad+1))}
                        coloured=sorted(x for x in adjacent if x[3]>0)
                        results.append({'z':z,'pixel':pixel,'nearby_colours':coloured,'source':r['url']})
                        # Prefer the most detailed successfully obtained tile.
                        break
                if results:
                    r=results[0]
                    r['result']='区域表示あり' if r['pixel'][3]>0 else ('境界付近' if r['nearby_colours'] else '参考地点で表示なし')
                    hazards[name]=r
                else:hazards[name]={'result':'データ取得なし・未確認'}
        row['hazards']=hazards
        row['hazard_flag']='区域表示あり' if any(v['result']=='区域表示あり' for v in hazards.values()) else ('境界付近' if any(v['result']=='境界付近' for v in hazards.values()) else ('参考地点で表示なし' if hazards else '位置未確認'))
    out=ROOT/'verified_2026-10-03.json'
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    counts={v:sum(r['hazard_flag']==v for r in data['rows']) for v in set(r['hazard_flag'] for r in data['rows'])}
    print('Tile requests',len(tasks),'success',sum(v['status']==200 for v in found.values()),'summary',counts,flush=True)

if __name__=='__main__':main()
