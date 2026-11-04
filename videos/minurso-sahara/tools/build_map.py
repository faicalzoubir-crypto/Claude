"""Build the projected map geometry (SVG path strings + points) for the MINURSO video.

Usage: python3 -I tools/build_map.py <ne_10m_admin_0_countries.geojson> <out geo.js>

Natural Earth 10m draws "Morocco" as Morocco + the territory west of the berm, and
"Western Sahara" as the area east of the berm. So:
  - full national territory = union(Morocco, Western Sahara)
  - buffer zone (east of the berm) = Western Sahara feature
  - berm = shared edge of the two features (approximate, Natural Earth precision)
"""
import json
import math
import sys

import numpy as np
import shapely
from shapely.geometry import LineString, MultiLineString, Point, box, shape
from shapely.ops import linemerge, substring, unary_union

src, out = sys.argv[1], sys.argv[2]
feats = {f["properties"]["ADMIN"]: shape(f["geometry"]) for f in json.load(open(src))["features"]}

# view window (lon/lat) and plane size in px
LON0, LON1, LAT0, LAT1 = -18.9, -0.6, 20.3, 37.3
W = 1000.0


def merc(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


K = W / math.radians(LON1 - LON0)
YTOP = merc(LAT1)
H = K * (YTOP - merc(LAT0))


def proj_xy(lon, lat):
    return (math.radians(lon - LON0) * K, (YTOP - merc(lat)) * K)


def proj(geom):
    def f(c):
        lon, lat = c[:, 0], c[:, 1]
        x = np.radians(lon - LON0) * K
        y = (YTOP - np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))) * K
        return np.column_stack([x, y])

    return shapely.transform(geom, f)


def fmt(coords):
    return " L".join(f"{x:.1f},{y:.1f}" for x, y in coords)


def path(geom, closed=True):
    if geom.is_empty:
        return ""
    parts = []
    if geom.geom_type == "Polygon":
        for ring in [geom.exterior, *geom.interiors]:
            parts.append("M" + fmt(ring.coords) + "Z")
    elif geom.geom_type == "LineString":
        parts.append("M" + fmt(geom.coords))
    elif geom.geom_type == "LinearRing":
        parts.append("M" + fmt(geom.coords) + "Z")
    elif hasattr(geom, "geoms"):
        for g in geom.geoms:
            parts.append(path(g))
    return " ".join(p for p in parts if p)


clip = box(LON0 - 12, LAT0 - 12, LON1 + 12, LAT1 + 4)
view_px = box(-40, -40, W + 40, H + 40)

morocco = feats["Morocco"]
zone = feats["Western Sahara"]
territory = unary_union([morocco, zone])

neighbours = {}
for name in ["Spain", "Portugal", "Algeria", "Mauritania", "Mali", "Gibraltar", "Tunisia", "Senegal"]:
    g = feats[name].intersection(clip)
    if not g.is_empty:
        neighbours[name] = proj(g).simplify(0.5)

def merge(g):
    return g if g.geom_type == "LineString" else linemerge(g)


# berm = edge of the zone that touches the Moroccan-held side
berm = merge(zone.boundary.intersection(morocco.buffer(0.02)))
# international border of the zone (Algeria + Mauritania), stopping at the coast north of
# the Cap Blanc peninsula
border = merge(
    zone.boundary.intersection(unary_union([feats["Algeria"], feats["Mauritania"]]).buffer(0.03))
    .intersection(box(-16.965, 21.329, -8.0, 28.0))
)

P_terr = proj(territory).simplify(0.4)
P_zone = proj(zone).simplify(0.4)
P_berm = proj(berm).simplify(0.4)
P_border = proj(border).simplify(0.4)

# coastline ripples around all land in view
land_px = unary_union([P_terr, *neighbours.values()]).buffer(0)
ripples = []
for r in (8, 18, 32):
    ring = land_px.buffer(r, quad_segs=6).boundary.intersection(box(-600, -300, W + 600, H + 600)).simplify(1.2)
    ripples.append(path(ring))


# berm ticks: short marks on the zone (east) side every 14 px
def longest(g):
    if g.geom_type == "LineString":
        return g
    return max(g.geoms, key=lambda s: s.length)


berm_main = longest(P_berm)
ticks = []
d = 7.0
while d < berm_main.length:
    p = berm_main.interpolate(d)
    q = berm_main.interpolate(min(d + 1.0, berm_main.length))
    dx, dy = q.x - p.x, q.y - p.y
    n = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / n, dx / n
    if not P_zone.contains(Point(p.x + nx * 3, p.y + ny * 3)):
        nx, ny = -nx, -ny
    ticks.append(f"M{p.x:.1f},{p.y:.1f} L{p.x + nx * 6:.1f},{p.y + ny * 6:.1f}")
    d += 14.0

# points
CITIES = {
    "الرباط": (-6.84, 34.02),
    "العيون": (-13.20, 27.15),
    "الداخلة": (-15.94, 23.71),
    "تندوف": (-8.15, 27.67),
}
# MINURSO team sites east of the berm (Wikipedia coords; Mehaires 26°8'50"N 11°4'9"W)
SITES = {
    "بئر لحلو": (-9.57, 26.35),
    "تيفاريتي": (-10.57, 26.15),
    "المهيريز": (-11.069, 26.147),
    "ميجك": (-12.87, 23.45),
    "أغوانيت": (-13.13, 22.19),
}
for name, (lon, lat) in SITES.items():
    inside = zone.contains(Point(lon, lat))
    print(f"site {lon},{lat} inside zone: {inside}", file=sys.stderr)

pts = lambda dct: {k: [round(v, 1) for v in proj_xy(*ll)] for k, ll in dct.items()}

# tanks for scenario 2: placed in the wide parts of the zone (lon, lat), each facing away
# from the nearest berm point (= direction of advance), with a track from that point
TANKS = [(-9.0, 26.7), (-9.2, 26.2), (-10.1, 26.2), (-11.0, 26.2), (-12.45, 24.4), (-13.45, 22.95), (-13.55, 21.95)]
border_main = longest(P_border)
tanks = []
for lon, lat in TANKS:
    assert zone.contains(Point(lon, lat)), (lon, lat)
    tx, ty = proj_xy(lon, lat)
    near = berm_main.interpolate(berm_main.project(Point(tx, ty)))
    vx, vy = tx - near.x, ty - near.y
    L = math.hypot(vx, vy) or 1.0
    ux, uy = vx / L, vy / L
    tanks.append(
        {
            "x": round(tx, 1),
            "y": round(ty, 1),
            "a": round(math.degrees(math.atan2(uy, ux)), 1),
            "track": [round(near.x, 1), round(near.y, 1), round(tx - ux * 16, 1), round(ty - uy * 16, 1)],
        }
    )

# threat blips for scenario 3 (east of the border)
THREATS = [(-7.6, 27.05), (-7.6, 26.4), (-9.9, 25.4), (-11.4, 24.6), (-12.2, 22.6)]

geo = {
    "view": [LON0, LON1, LAT0, LAT1],
    "W": round(W, 1),
    "H": round(H, 1),
    "territory": path(P_terr),
    "zone": path(P_zone),
    "berm": path(P_berm),
    "bermTicks": " ".join(ticks),
    "border": path(P_border),
    "neighbours": {k: path(v) for k, v in neighbours.items()},
    "ripples": ripples,
    "cities": pts(CITIES),
    "sites": pts(SITES),
    "labels": pts(
        {
            "المغرب": (-6.2, 31.9),
            "الجزائر": (-3.2, 27.6),
            "موريتانيا": (-9.6, 22.4),
            "إسبانيا": (-4.6, 37.05),
            "المحيط الأطلسي": (-15.6, 31.2),
        }
    ),
    "tanks": tanks,
    "threats": [[round(v, 1) for v in proj_xy(*ll)] for ll in THREATS],
}
open(out, "w").write("window.GEO = " + json.dumps(geo, ensure_ascii=False) + ";\n")
print(f"wrote {out}: plane {W:.0f}x{H:.0f}, berm {berm_main.length:.0f}px, border {border_main.length:.0f}px", file=sys.stderr)
