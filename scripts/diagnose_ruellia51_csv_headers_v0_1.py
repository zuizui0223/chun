#!/usr/bin/env python3
# Outcome-blind diagnostic: reads exact public CSV bytes but parses header row only.
import csv, hashlib, io, json, urllib.request
from pathlib import Path

FILES={
 'anthocyanins_spectra.csv':('https://ndownloader.figshare.com/files/58502632',468339,'bb76b658952017e1c30bc5b488068f63'),
 'raw_data.csv':('https://ndownloader.figshare.com/files/58502635',130680,'0e3b9830abb1378f9546cd7d07ae1f97')
}
out=[]
for name,(url,size,md5) in FILES.items():
    req=urllib.request.Request(url,headers={'User-Agent':'CHUN-ruellia51-preflight/0.1'})
    with urllib.request.urlopen(req,timeout=90) as r: b=r.read()
    got=hashlib.md5(b).hexdigest()
    assert len(b)==size,(name,len(b),size)
    assert got==md5,(name,got,md5)
    text=io.StringIO(b.decode('utf-8-sig'))
    header=next(csv.reader(text))
    out.append({'name':name,'size':len(b),'md5':got,'header':[x.strip() for x in header]})
result={
 'status':'CSV_HEADERS_ONLY_OUTCOMES_UNOPENED',
 'files':out,
 'data_rows_read':0,
 'row_level_HPLC_values_read':False,
 'AUC_computed':False,
 'winner_computed':False
}
p=Path('build/ruellia51_csv_headers_v0_1.json'); p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
