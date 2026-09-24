"""Logo generator — the signature logo.
The name "Schülein" is outlined from Herr Von Muellerhoff (a pen-signature
script, SIL OFL), with a tapered brass pen stroke beneath it, the way a
doctor signs a prescription. Everything is outlined, so the logo needs no
font at runtime.

  curl -o /tmp/hvm.woff2 <Google Fonts woff2 of "Herr Von Muellerhoff", latin>
  python3 tools/logo.py /tmp/hvm.woff2 /path/to/jost.woff2
Writes assets/logo.svg, assets/logo-mark.svg and assets/signature.json.
"""
import sys, json, math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

SIG = sys.argv[1] if len(sys.argv) > 1 else '/tmp/hvm.woff2'
SANS = sys.argv[2] if len(sys.argv) > 2 else 'fonts/jost-latin.woff2'
INK, BRASS, MUTED, PETROL, CREAM = '#17211F', '#B8913F', '#5C6360', '#1F4A46', '#F4EFE4'
fmt = lambda v: ('%.2f' % v).rstrip('0').rstrip('.')

def setup(path, loc=None):
    f = TTFont(path)
    if loc and 'fvar' in f:
        from fontTools.varLib.instancer import instantiateVariableFont
        f = instantiateVariableFont(f, loc)
    return f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm, f

def run(font, text, size, x, base, track=0):
    gs, cmap, upm, f = font
    s = size / upm; d = ''; bp = BoundsPen(gs)
    kern = {}
    for ch in text:
        if ch == ' ':
            x += gs[cmap[32]].width * s + track; continue
        g = cmap[ord(ch)]
        rp = DecomposingRecordingPen(gs); gs[g].draw(rp)
        sp = SVGPathPen(None, ntos=fmt)
        rp.replay(TransformPen(sp, (s, 0, 0, -s, x, base)))
        rp.replay(TransformPen(bp, (s, 0, 0, -s, x, base)))
        d += sp.getCommands()
        x += gs[g].width * s + track
    return d, bp.bounds, x

def stroke(x0, x1, y, sag, rise, th):
    """a tapered pen stroke: thick in the first third, thin at both ends"""
    n = 60; top = []; bot = []
    for i in range(n + 1):
        u = i / n
        cx = x0 + (x1 - x0) * u
        cy = y + sag * math.sin(math.pi * u) - rise * u * u
        w = th * (math.sin(math.pi * min(1, u * 1.35)) ** .8) * (1 - .55 * u) + .15
        top.append((cx, cy - w / 2)); bot.append((cx, cy + w / 2))
    pts = top + bot[::-1]
    return 'M' + ' L'.join(fmt(a) + ' ' + fmt(b) for a, b in pts) + 'Z'

sig = setup(SIG)
sans = setup(SANS, {'wght': 500})

# --- full logo: signature, pen stroke, caption
d, (bx0, by0, bx1, by1), _ = run(sig, 'Schülein', 120, 0, 100)
dx = -bx0 + 4
d, (bx0, by0, bx1, by1), _ = run(sig, 'Schülein', 120, dx, 100)
line = stroke(bx0 + 10, bx1 + 6, by1 + 6, 2.2, 7, 4.2)
cap, (cx0, cy0, cx1, cy1), _ = run(sans, 'ZAHNARZTPRAXIS · NEUBRANDENBURG', 13, bx0 + 18, by1 + 34, track=2.4)
W = math.ceil(max(bx1 + 10, cx1) + 4); H = math.ceil(cy1 + 4); top = math.floor(by0 - 4)
open('assets/logo.svg', 'w').write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {top} {W} {H - top}">'
    f'<path fill="{INK}" stroke="{INK}" stroke-width="1.9" stroke-linejoin="round" d="{d}"/><path fill="{BRASS}" d="{line}"/><path fill="{MUTED}" d="{cap}"/></svg>\n')

# --- inline signature for the page (signature + stroke only, currentColor)
json.dump({'viewBox': f'0 {top} {W} {math.ceil(by1 + 14) - top}', 'name': d, 'stroke': line},
          open('assets/signature.json', 'w'))

# --- favicon / touch mark: "Sch" from the signature on petrol, pen stroke beneath
gs, cmap, upm, _ = sig
probe, (x0, y0, x1, y1), _ = run(sig, 'Sch', 100, 0, 0)
w, h = x1 - x0, y1 - y0
k = min(84 / w, 70 / h)
sd, (a0, b0, a1, b1), _ = run(sig, 'Sch', 100 * k, 50 - (x0 + w / 2) * k, 46 - (y0 + h / 2) * k)
st = stroke(a0 + 6, a1 + 2, b1 + 5, 1, 3.5, 3.6)
open('assets/logo-mark.svg', 'w').write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="{PETROL}"/>'
    f'<path fill="{CREAM}" stroke="{CREAM}" stroke-width="2.6" stroke-linejoin="round" d="{sd}"/><path fill="{BRASS}" d="{st}"/></svg>\n')
print('logo', W, H - top)
