"""Logo generator — outlines the ü of Newsreader (wght 620, opsz 72) into the
petrol tile, dots split out for the brass accent, plus the wordmark.
Needs the FULL variable Newsreader (opsz axis), not the subset in fonts/:
  curl -o /tmp/newsreader.woff2 https://fonts.gstatic.com/s/newsreader/v26/cY9AfjOCX1hbuyalUrK4397yjIJFJpc.woff2
  python3 tools/logo.py /tmp/newsreader.woff2 && python3 build.py
"""
import sys
SRC_FONT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/newsreader.woff2'
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import re, json

def load(path, loc):
    f=TTFont(path); i=instantiateVariableFont(f,loc)
    return i.getGlyphSet(), i.getBestCmap(), i['head'].unitsPerEm
fmt=lambda v: ('%.2f'%v).rstrip('0').rstrip('.')

def contours(gs,cmap,ch,s,x,base):
    """list of (path d, bounds) per contour"""
    rp=DecomposingRecordingPen(gs); gs[cmap[ord(ch)]].draw(rp); rp2=DecomposingRecordingPen(gs); rp.replay(TransformPen(rp2,(s,0,0,-s,x,base))); rp=rp2
    out=[]; cur=[]
    for op,args in rp.value:
        cur.append((op,args))
        if op in('closePath','endPath'):
            sp=SVGPathPen(None,ntos=fmt); bp=BoundsPen(None)
            for o,a in cur: getattr(sp,o)(*a); getattr(bp,o)(*a)
            out.append((sp.getCommands(),bp.bounds)); cur=[]
    return out

def text(gs,cmap,upm,t,size,x,base,track=0):
    s=size/upm; d=''
    for ch in t:
        if ch==' ': x+=gs[cmap[32]].width*s+track; continue
        for c,_ in contours(gs,cmap,ch,s,x,base): d+=c
        x+=gs[cmap[ord(ch)]].width*s+track
    return d,x

nr=load(SRC_FONT,{'wght':620,'opsz':72})
js=load('fonts/jost-latin.woff2',{'wght':500})

# --- mark: ü in a 100-unit tile; dots split out so they can take the brass accent
gs,cmap,upm=nr
bp=BoundsPen(gs); gs[cmap[ord('ü')]].draw(bp); x0,y0,x1,y1=bp.bounds
H=60; s=H/(y1-y0); w=(x1-x0)*s
tx=(100-w)/2 - x0*s; base=50 + ((y1+y0)/2)*s + 1.5   # optical: nudge down, the dots are lighter than the stem
body='';dots=''
for d,b in contours(gs,cmap,'ü',s,tx,base):
    if b[3] < base - 0.55*(y1*s):  # contour lies high up → a dot
        dots+=d
    else: body+=d
json.dump({'body':body,'dots':dots},open('assets/mark.json','w'))
print('dots found:', dots.count('M'), 'body contours:', body.count('M'))

PET='#1F4A46'; CREAM='#F4EFE4'; BRASS='#C9A55C'
mark_inner=f'<rect width="100" height="100" rx="22" fill="{PET}"/><path fill="{CREAM}" d="{body}"/><path fill="{BRASS}" d="{dots}"/>'
open('assets/logo-mark.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{mark_inner}</svg>\n')


# --- full logo: mark + wordmark, brass dots on the ü, all outlined
gs,cmap,upm=nr; s=64/upm; x=122; base=64; ink='';brass=''
for ch in 'Schülein':
    for d,b in contours(gs,cmap,ch,s,x,base):
        if ch=='ü' and b[3] < base-30: brass+=d
        else: ink+=d
    x+=gs[cmap[ord(ch)]].width*s
sd,sx=text(*js,'ZAHNARZTPRAXIS NEUBRANDENBURG',13.5,124,88,track=2.1)
W=int(max(x,sx))+4
open('assets/logo.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 100">{mark_inner}<path fill="#17211F" d="{ink}"/><path fill="{BRASS}" d="{brass}"/><path fill="#5C6360" d="{sd}"/></svg>\n')
