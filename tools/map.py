"""Bakes the 'Mitten im Ring' map from OpenStreetMap data (© OpenStreetMap
contributors, ODbL) fetched once into tools/data/. No runtime requests.
Writes tools/data/map.html — an inline SVG fragment pasted into index.html."""
import json, math
d = json.load(open('tools/data/overpass.json'))['elements']
addr = json.load(open('tools/data/address.json'))[0]
A = (float(addr['lat']), float(addr['lon']))
walls = [e['geometry'] for e in d if e.get('tags', {}).get('barrier') == 'city_wall' or e.get('tags', {}).get('historic') == 'citywalls']
pts = [(p['lat'], p['lon']) for w in walls for p in w]
lat0 = sum(p[0] for p in pts) / len(pts); lon0 = sum(p[1] for p in pts) / len(pts)
k = math.cos(math.radians(lat0))
S, W, H = 0.92, 1240, 900                      # metres → svg units
_raw = lambda lat, lon: ((lon - lon0) * k * 111320 * S, (lat0 - lat) * 110540 * S)
_r = [_raw(*p) for p in pts]
OX = W / 2 - (min(a for a, b in _r) + max(a for a, b in _r)) / 2
OY = H / 2 - (min(b for a, b in _r) + max(b for a, b in _r)) / 2
def xy(lat, lon): a, b = _raw(lat, lon); return (a + OX, b + OY)
f = lambda v: f'{v:.1f}'

# the ring park (Wallanlagen): wall points sorted by angle, smoothed
cx, cy = xy(lat0, lon0)
ring = sorted((xy(*p) for p in pts), key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
n = len(ring); sm = []
for i in range(n):
    w = [ring[(i + j) % n] for j in range(-4, 5)]
    sm.append((sum(a for a, b in w) / 9, sum(b for a, b in w) / 9))
ringd = 'M' + ' L'.join(f(a) + ' ' + f(b) for a, b in sm[::2]) + 'Z'
walld = ''.join('M' + ' L'.join(f(a) + ' ' + f(b) for a, b in (xy(p['lat'], p['lon']) for p in w)) for w in walls)

def centroid(name):
    cs = []
    for e in d:
        t = e.get('tags', {})
        if t.get('name') == name and e.get('geometry') and (t.get('historic') == 'city_gate' or 'kirche' in name.lower()):
            g = e['geometry']; cs.append((sum(p['lat'] for p in g) / len(g), sum(p['lon'] for p in g) / len(g)))
    return xy(sum(a for a, b in cs) / len(cs), sum(b for a, b in cs) / len(cs))

P = xy(*A)
gates = [('Friedländer Tor', 'ne'), ('Neues Tor', 'e'), ('Stargarder Tor', 's'), ('Treptower Tor', 'w')]
out = []
out.append(f'<path class="map__park" d="{ringd}"/>')
out.append(f'<path class="map__wall" d="{walld}"/>')
kk = centroid('Konzertkirche Neubrandenburg')
out.append(f'<g class="map__place"><rect x="{f(kk[0]-9)}" y="{f(kk[1]-16)}" width="18" height="32" rx="3"/><text x="{f(kk[0])}" y="{f(kk[1]-32)}" text-anchor="middle">Konzertkirche</text></g>')
for name, side in gates:
    g = centroid(name)
    metres = math.hypot(g[0] - P[0], g[1] - P[1]) / S
    mins = max(1, round(metres * 1.3 / 80))
    out.append(f'<path class="map__walk" d="M{f(g[0])} {f(g[1])} L{f(P[0])} {f(P[1])}"/>')
    lx, ly, anchor = {'ne': (W - 6, g[1] - 40, 'end'), 'n': (g[0], g[1] - 30, 'middle'), 's': (g[0], g[1] + 50, 'middle'),
                      'e': (W - 6, g[1] - 36, 'end'), 'w': (g[0] - 26, g[1] + 2, 'end')}[side]
    out.append(f'<g class="map__gate"><circle cx="{f(g[0])}" cy="{f(g[1])}" r="10"/>'
               f'<text x="{f(lx)}" y="{f(ly)}" text-anchor="{anchor}">{name}<tspan x="{f(lx)}" dy="1.25em">ca. {mins} Min. zu Fuß</tspan></text></g>')
out.append(f'<g class="map__pin" transform="translate({f(P[0])} {f(P[1])})"><circle r="34" class="map__pulse"/><circle r="15"/></g>')
open('tools/data/map.html', 'w').write(
    f'<svg class="map__svg" viewBox="0 0 {W} {H}" role="img" aria-label="Lageplan: die Praxis in der Pfaffenstraße liegt innerhalb der Neubrandenburger Stadtmauer, nahe dem Neuen Tor">\n' +
    '\n'.join(out) + '\n</svg>\n')
print('pin', f(P[0]), f(P[1]), 'viewBox', W, H)
