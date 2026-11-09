"""Build the map geometry (SVG paths + label points) for the weather video.

Usage:
  python3 -I tools/build_map.py <ne_10m_admin_0_countries.geojson> <geoBoundaries-MAR-ADM2.geojson> <out geo.js>

Sources:
  - Natural Earth 10m admin-0: the national outline. Natural Earth splits the country into
    "Morocco" and "Western Sahara"; the complete official map of Morocco is their union, drawn as
    ONE shape with no line inside it.
  - geoBoundaries MAR ADM2 (75 provinces and prefectures, southern provinces included): the four
    provinces under the orange bulletin and the north + centre regions, clipped to that outline.
"""
import json
import math
import sys

import numpy as np
import shapely
from shapely.geometry import box, shape
from shapely.ops import unary_union

ne_src, gb_src, out = sys.argv[1], sys.argv[2], sys.argv[3]
ne = {f["properties"]["ADMIN"]: shape(f["geometry"]) for f in json.load(open(ne_src))["features"]}
gb = [(f["properties"]["shapeName"], shape(f["geometry"]).buffer(0)) for f in json.load(open(gb_src))["features"]]

# map window (lon/lat): the whole territory with a small margin, Mercator
LON0, LON1, LAT0, LAT1 = -17.6, -0.6, 20.45, 36.25
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
        x = np.radians(c[:, 0] - LON0) * K
        y = (YTOP - np.log(np.tan(np.pi / 4 + np.radians(c[:, 1]) / 2))) * K
        return np.column_stack([x, y])

    return shapely.transform(geom, f)


def fmt(coords):
    return " L".join(f"{x:.1f},{y:.1f}" for x, y in coords)


def path(geom):
    if geom.is_empty:
        return ""
    if geom.geom_type == "Polygon":
        return " ".join("M" + fmt(r.coords) + "Z" for r in [geom.exterior, *geom.interiors])
    if hasattr(geom, "geoms"):
        return " ".join(p for p in (path(g) for g in geom.geoms) if p)
    return "M" + fmt(geom.coords)


def drop_specks(g, min_area):
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and p.area >= min_area]
    return unary_union(parts)


# ---- the national territory: one shape, no inner line ----------------------------------------
territory = unary_union([ne["Morocco"], ne["Western Sahara"]]).buffer(0.002).buffer(-0.002)
territory = drop_specks(territory, 0.002)
assert territory.geom_type in ("Polygon", "MultiPolygon")
bx = territory.bounds
print(f"territory bounds {[round(v, 2) for v in bx]}", file=sys.stderr)
assert bx[1] < 20.9 and bx[0] < -17.0, "the southern provinces must be inside the outline"

clip = box(LON0 - 8, LAT0 - 8, LON1 + 8, LAT1 + 4)
neighbours = []
for name in ["Spain", "Portugal", "Algeria", "Mauritania", "Mali", "Gibraltar"]:
    g = ne[name].intersection(clip)
    if not g.is_empty:
        neighbours.append(proj(g).simplify(0.6))

# ---- provinces ------------------------------------------------------------------------------
def prov(*keys):
    hits = [g for n, g in gb if any(k.lower() in n.lower() for k in keys)]
    assert hits, keys
    return unary_union(hits).intersection(territory)


ORANGE = {
    "chichaoua": ("شيشاوة", prov("Chichaoua")),
    "haouz": ("الحوز", prov("Al Haouz")),
    "taroudant": ("تارودانت", prov("Taroudant")),
    "essaouira": ("الصويرة", prov("Essaouira")),
}

REGIONS = {
    # the seven regions of the north and the centre (2015 regional division)
    "tanger": ["Tangier", "M'diq", "Tetouan", "Fahs-Anjra", "Larache", "Al Hoceima", "Chefchaouen", "Ouezzane"],
    "oriental": ["Oujda", "Nador", "Driouch", "Jerada", "Berkane", "Taourirt", "Guercif", "Figuig"],
    "fes": ["Préfecture de Fès", "Meknès", "El Hajeb", "Ifrane", "Moulay Yacoub", "Sefrou", "Boulemane", "Taounate", "Taza"],
    "rabat": ["Prefecture of Rabat", "Salé", "Skhirate", "Kenitra", "Khémisset", "Sidi Kacem", "Sidi Slimane"],
    "benimellal": ["Beni Mellal", "Azilal", "Fquih Ben Saleh", "Khénifra", "Khouribga"],
    "casa": ["Casablanca", "Mohammédia", "El Jadida", "Nouaceur", "Médiouna", "Benslimane", "Berrechid", "Settat", "Sidi Bennour"],
    "marrakech": ["Marrakech", "Chichaoua", "Al Haouz", "Sraghna", "Essaouira", "Rhamna", "Safi", "Youssoufia"],
}
used = set()
north_parts = []
for reg, keys in REGIONS.items():
    for k in keys:
        hits = [(n, g) for n, g in gb if k.lower() in n.lower()]
        assert len(hits) == 1, (k, [n for n, _ in hits])
        used.add(hits[0][0])
        north_parts.append(hits[0][1])
print(f"north+centre provinces: {len(used)}", file=sys.stderr)
assert len(used) == 54
north = unary_union(north_parts).buffer(0.01).buffer(-0.01).intersection(territory)
north = drop_specks(north, 0.002)

P_terr = proj(territory).simplify(0.35)
P_north = proj(north).simplify(0.35)

# coastline ripples around all land in view (decoration on the sea)
land_px = unary_union([P_terr, *neighbours]).buffer(0)
ripples = []
for r in (9, 20, 34):
    ring = land_px.buffer(r, quad_segs=6).boundary.intersection(box(-400, -300, W + 400, H + 300)).simplify(1.2)
    ripples.append(path(ring))

orange = {}
for key, (label, g) in ORANGE.items():
    pg = proj(g).simplify(0.3)
    c = pg.representative_point()
    orange[key] = {"name": label, "d": path(pg), "c": [round(c.x, 1), round(c.y, 1)]}

pts = lambda dct: {k: [round(v, 1) for v in proj_xy(*ll)] for k, ll in dct.items()}

geo = {
    "view": [LON0, LON1, LAT0, LAT1],
    "W": round(W, 1),
    "H": round(H, 1),
    "territory": path(P_terr),
    "north": path(P_north),
    "neighbours": " ".join(path(n) for n in neighbours),
    "ripples": ripples,
    "orange": orange,
    "cities": pts({"الرباط": (-6.84, 34.02), "العيون": (-13.20, 27.15), "الداخلة": (-15.94, 23.71)}),
}
with open(out, "w") as fh:
    fh.write("// generated by tools/build_map.py: do not edit by hand\n")
    fh.write("window.GEO = " + json.dumps(geo, ensure_ascii=False) + ";\n")
print(f"W={W} H={H:.1f} → {out}", file=sys.stderr)
