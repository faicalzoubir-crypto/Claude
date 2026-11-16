#!/usr/bin/env python3
"""Regional night map of the 225 kV artery around Casablanca (scenes 3 and 5).

Positions and routes come from OpenStreetMap (Overpass, fetched 14 Nov 2026, kept in data/osm-*.json):
substations (power=substation) and the 225/400 kV lines (power=line) between them. The chain found in
the line graph: Mediouna -> Oulad Haddou (33 km), Oulad Haddou -> Dar Bouazza (18.9 km),
Dar Bouazza -> J -> Ouled Saleh (19 km; J -> Ouled Saleh is the 5 km double-circuit in-out),
J -> Laawamer. Satellite: Esri World Imagery z13, stitched once, graded to night in the composition.

  python3 tools/region_map.py
"""
import json, math, os, io, urllib.request, concurrent.futures as cf
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LINES = json.loads((ROOT / "data/osm-lines.json").read_text())["elements"]
WAYS = {e["id"]: [(p["lat"], p["lon"]) for p in e["geometry"]] for e in LINES}

Z = 13; T = 256; W = T * 2 ** Z
wx = lambda lon: (lon + 180) / 360 * W
def wy(lat):
    s = math.radians(lat); return (1 - math.log(math.tan(s) + 1 / math.cos(s)) / math.pi) / 2 * W

# frame: lon -7.84..-7.34 across x 40..1040, lat 33.64 at y 330
S = 1000 / (wx(-7.34) - wx(-7.84))           # screen px per z13 px
CX = wx(-7.59) ; CY = wy(33.64) + (960 - 330) / S
HALF = 2                                       # the image is saved at half resolution
x0 = int((CX - 1080 / S / 2 - 200) // T); x1 = int((CX + 1080 / S / 2 + 200) // T) + 1
y0 = int((CY - 1920 / S / 2 - 200) // T); y1 = int((CY + 1920 / S / 2 + 200) // T) + 1
os.makedirs(ROOT / "data/tiles13", exist_ok=True)


def get(xy):
    x, y = xy
    p = ROOT / f"data/tiles13/{y}_{x}.jpg"
    if not p.exists():
        u = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{y}/{x}"
        p.write_bytes(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "hyperframes-map-bake/1.0"}), timeout=60).read())
    return xy, p


img = Image.new("RGB", ((x1 - x0) * T, (y1 - y0) * T))
with cf.ThreadPoolExecutor(6) as ex:
    for (x, y), p in ex.map(get, [(x, y) for y in range(y0, y1) for x in range(x0, x1)]):
        img.paste(Image.open(p).convert("RGB"), ((x - x0) * T, (y - y0) * T))
half = img.resize((img.width // HALF, img.height // HALF), Image.LANCZOS)
(ROOT / "assets/map").mkdir(parents=True, exist_ok=True)
half.save(ROOT / "assets/map/casa-region.jpg", quality=88)
OX, OY = x0 * T, y0 * T


def ip(lat, lon):                               # image px (half res)
    return round((wx(lon) - OX) / HALF, 1), round((wy(lat) - OY) / HALF, 1)


SUBS = {  # OpenStreetMap power=substation (way id), name as tagged
    "med": (33.4533, -7.4002, "way/131946012 Poste 400/225kV Mediouna"),
    "oh": (33.5412, -7.6171, "way/143628748 poste 225/22 kV de Oulad Haddou"),
    "db": (33.5500, -7.6958, "way/131591106 poste 225/22 kV de Dar Bouazza"),
    "os": (33.4347, -7.6462, "way/690063702 225 kV, unnamed, in Oulad Salah commune"),
    "aw": (33.3527, -7.7590, "way/131588990 Poste 225kV Laawamer"),
    "ne": (33.6344, -7.4290, "way/207991977 225 kV, unnamed (north-east)"),
}
SEGS = {  # chain segments: OSM way ids in order (X = the junction east of Oulad Haddou)
    "oh-x": [144011574], "x-med": [131945819], "x-ne": [207993336], "oh-db": [131677069], "db-j": [893093775],
    "j-os": [893093786], "j-aw": [216023481],
    "jorf-med": [215414082], "aw-jorf": [216023463],
}


def chain(ids, start=None):
    pts = []
    for wid in ids:
        g = WAYS[wid]
        if pts:
            if math.dist(pts[-1], g[-1]) < math.dist(pts[-1], g[0]):
                g = g[::-1]
        pts += g
    if start is not None and math.dist(pts[-1], start) < math.dist(pts[0], start):
        pts = pts[::-1]
    return pts


def km(a, b):
    return math.hypot((a[0] - b[0]) * 111.0, (a[1] - b[1]) * 111.0 * math.cos(math.radians(33.5)))


segs = {}
for k, ids in SEGS.items():
    start = {"oh-x": SUBS["oh"][:2], "x-med": SUBS["med"][:2], "x-ne": SUBS["ne"][:2], "oh-db": SUBS["db"][:2], "db-j": SUBS["aw"][:2], "j-os": SUBS["aw"][:2],
             "j-aw": SUBS["aw"][:2], "jorf-med": (33.10, -8.63), "aw-jorf": SUBS["aw"][:2]}[k]
    pts = chain(ids, start)
    length = sum(km(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    segs[k] = {"km": round(length, 1), "pts": [ip(*p) for p in pts[:: max(1, len(pts) // 160)]] + [ip(*pts[-1])]}

city = json.loads((ROOT / "data/map.json").read_text())["places"]
DARK = ["centre", "belyout", "anfa", "bourgogne", "maarif", "ghallef", "merssultan", "hopitaux", "fida",
        "californie", "ainchock", "oulfa", "cfc", "hassani", "sbata", "benmsick", "sidiothmane", "sidimaarouf", "bouskoura"]
meta = {
    "image": "assets/map/casa-region.jpg", "w": half.width, "h": half.height,
    "center": {"x": round((CX - OX) / HALF, 1), "y": round((CY - OY) / HALF, 1)}, "scale": round(S * HALF, 5),
    "subs": {k: {"lat": a, "lon": b, "osm": n, "px": ip(a, b)} for k, (a, b, n) in SUBS.items()},
    "segs": segs,
    "dark": {k: ip(city[k]["lat"], city[k]["lon"]) for k in DARK},
    "source": "OpenStreetMap contributors (ODbL), Overpass 2026-11-14; Esri World Imagery",
}
(ROOT / "data/region.json").write_text(json.dumps(meta, indent=1))
print(half.size, "scale", meta["scale"], {k: v["km"] for k, v in segs.items()})
