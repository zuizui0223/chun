#!/usr/bin/env python3
"""Recheck transcribed terminal states at frozen original-PDF image coordinates; no OCR."""
from __future__ import annotations
import argparse,hashlib,io,json
from collections import Counter
from pathlib import Path
import fitz
import numpy as np
from PIL import Image
from analyze_linoideae_mk_v0_2 import load_snapshot

def image_parts(pdf,page,width):
 d=fitz.open(pdf);parts=[]
 for item in d[page].get_images(full=True):
  if item[2]==width:
   parts.append(Image.open(io.BytesIO(d.extract_image(item[0])['image'])).convert('RGB'))
 if len(parts)!=2:raise ValueError('unexpected embedded figure image layout')
 canvas=Image.new('RGB',(width,sum(p.height for p in parts)));y=0
 for p in parts:canvas.paste(p,(0,y));y+=p.height
 return np.asarray(canvas)

def s5_colour(pixel):
 r,g,b=map(int,pixel)
 if min(r,g,b)>242:return 'WHITE'
 if max(r,g,b)-min(r,g,b)<=35:return None
 if r>170 and g>170 and b<160:return 'YELLOW'
 if g>r+35 and b>r+35:return 'BLUE'
 if r>g+30 and b>g+25:return 'PURPLE'
 if r>g+30 and r>b+20:return 'RED' if g<65 else 'PINK'
 return None

def run(manifest,source,out):
 data=load_snapshot(manifest);source=Path(source)
 pdf=source/'article.pdf';sup=source/'files/plants-11-01579-s001/Supplementary material.pdf'
 for name,path in [('article.pdf',pdf),('files/plants-11-01579-s001/Supplementary material.pdf',sup)]:
  if hashlib.sha256(path.read_bytes()).hexdigest()!=data['source_sha256'][name]:raise ValueError('PDF checksum failed')
 f2=image_parts(pdf,4,2182);s5=image_parts(sup,10,1778)
 palette={'YELLOW':(255,249,14),'BLUE':(0,157,220),'WHITE':(255,255,255),'PURPLE':(167,83,146),'RED':(240,0,70),'PINK':(244,20,156)}
 names=list(palette);ref=np.array(list(palette.values()));audit=[]
 for r in data['rows']:
  box=r['figureS5_marker_box'];box=list(map(int,box.split('|'))) if isinstance(box,str) else box
  x0,y0,x1,y1=box;votes=Counter(filter(None,(s5_colour(p) for p in s5[y0:y1,x0:x1].reshape(-1,3))))
  got5=sorted(c for c,n in votes.items() if n>=4)
  cy=round(float(r['figure2_marker_centre_y']));votes2=Counter()
  for p in f2[cy-1:cy+2,1765:1769].reshape(-1,3):
   distances=np.linalg.norm(ref-p.astype(float),axis=1);i=int(distances.argmin())
   if distances[i]<95:votes2[names[i]]+=1
  got2=sorted(c for c,n in votes2.items() if n>=2)
  audit.append({'tip_id':r['tip_id'],'figure2_pixels':got2,'figure2_declared':sorted(r['figure2_states']),'figureS5_pixels':got5,'figureS5_declared':sorted(r['figureS5_states'])})
 mismatches=[r for r in audit if r['figure2_pixels']!=r['figure2_declared'] or r['figureS5_pixels']!=r['figureS5_declared']]
 result={'terminal_records':len(audit),'figure_marker_checks':2*len(audit),'mismatches':mismatches,'records':audit,'scope':'Pixel recheck verifies depicted marker sets, not botanical truth or natural population polymorphism. Terminal labels were independently visually transcribed; ancestral node colours were not admitted.'}
 Path(out).parent.mkdir(parents=True,exist_ok=True);Path(out).write_text(json.dumps(result,indent=2)+'\n')
 if mismatches:raise ValueError(f'{len(mismatches)} marker mismatches; inspect saved audit')
 print(json.dumps({k:v for k,v in result.items() if k!='records'}));return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();run(a.manifest,a.source_dir,a.out)
