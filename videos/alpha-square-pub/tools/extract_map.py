"""Extrait la terre et le trait de côte autour d'Alpha Square pour la scène carte.

Source : @geo-maps/earth-lands-100m (npm), données © OpenStreetMap contributors (ODbL),
résolution 100 m. Écrit assets/map/casablanca-map.js (window.CASA_MAP), en mètres
locaux centrés sur le point (x vers l'est, y vers le nord).

Usage : python tools/extract_map.py <chemin/vers/map.geo.json>
"""
import json
import math
import sys
from pathlib import Path

import warnings

from shapely.geometry import Point, Polygon, box, shape
from shapely.ops import transform, unary_union
from shapely.prepared import prep

ROOT = Path(__file__).resolve().parent.parent
LAT0, LON0 = 33.5620843, -7.6241886  # emplacement approximatif fourni par le client
HALF_KM = 36  # rayon de la zone extraite
DOT_STEP = 250  # pas de la trame de points sur la terre (m)
DOT_RADIUS_KM = 14

KX = 111320 * math.cos(math.radians(LAT0))
KY = 110574


def to_local(x, y, z=None):
    return ((x - LON0) * KX, (y - LAT0) * KY)


def main(src):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    dlon = HALF_KM * 1000 / KX
    dlat = HALF_KM * 1000 / KY
    bbox = box(LON0 - dlon, LAT0 - dlat, LON0 + dlon, LAT0 + dlat)
    data = json.loads(Path(src).read_text())
    parts = []
    for g in data["geometries"]:
        geom = shape(g)
        if not geom.intersects(bbox):
            continue
        clipped = geom.intersection(bbox)
        if not clipped.is_empty:
            parts.append(clipped)
    land = parts[0]
    for p in parts[1:]:
        land = land.union(p)
    land = transform(to_local, land).simplify(12, preserve_topology=True)
    polys = [land] if land.geom_type == "Polygon" else list(land.geoms)
    half = HALF_KM * 1000
    rings = []
    kept = []
    for poly in polys:
        if poly.area < 40000:  # ignore les îlots minuscules
            continue
        # contour extérieur seulement : les petits trous intérieurs (plans d'eau, artefacts) sont ignorés
        rings.append([[round(x), round(y)] for x, y in poly.exterior.coords])
        kept.append(Polygon(poly.exterior))
    land = unary_union(kept)
    # trame de points sur la terre, dans un rayon autour du point
    pl = prep(land)
    dots = []
    r = DOT_RADIUS_KM * 1000
    n = int(r // DOT_STEP)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * DOT_STEP, j * DOT_STEP
            if x * x + y * y <= r * r and pl.contains(Point(x, y)):
                dots.append([x, y])
    on_land = land.contains(Point(0, 0))
    # point de la mer le plus proche, pour placer « Océan Atlantique »
    coast = land.boundary
    nearest = coast.interpolate(coast.project(Point(0, 0)))
    out = {
        "source": "© OpenStreetMap contributors (ODbL) via @geo-maps/earth-lands-100m",
        "center": [LAT0, LON0],
        "half": half,
        "rings": rings,
        "dots": dots,
        "coastNearest": [round(nearest.x), round(nearest.y)],
    }
    dst = ROOT / "assets" / "map" / "casablanca-map.js"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("window.CASA_MAP = " + json.dumps(out, separators=(",", ":")) + ";\n")
    pts = sum(len(r) for r in rings)
    dist = math.hypot(*out["coastNearest"])
    print(f"{dst.relative_to(ROOT)}: {len(rings)} anneaux, {pts} points, {len(dots)} points de trame, "
          f"point sur la terre={on_land}, côte la plus proche à {dist:.0f} m ({out['coastNearest']}), "
          f"{dst.stat().st_size / 1024:.0f} Ko")


main(sys.argv[1])
