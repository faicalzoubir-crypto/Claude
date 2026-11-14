# Geocode tools/places.tsv with OpenStreetMap Nominatim (1 request/s, generic UA) -> data/places-raw.json
import csv, json, time, urllib.parse, urllib.request, sys
rows = list(csv.DictReader(open("tools/places.tsv", encoding="utf-8"), delimiter="\t"))
out = []
for r in rows:
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": r["query"], "format": "jsonv2", "limit": 3, "accept-language": "fr"})
    req = urllib.request.Request(url, headers={"User-Agent": "hyperframes-map-bake/1.0"})
    try:
        res = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        res = []; print("ERR", r["id"], e, file=sys.stderr)
    hits = [{"lat": float(h["lat"]), "lon": float(h["lon"]), "name": h.get("display_name", "")[:90],
             "type": h.get("addresstype") or h.get("type"), "bbox": h.get("boundingbox")} for h in res]
    out.append({**r, "hits": hits})
    print(r["id"], hits[0]["lat"] if hits else None, hits[0]["lon"] if hits else None, hits[0]["type"] if hits else "", hits[0]["name"][:60] if hits else "NO HIT")
    time.sleep(1.2)
json.dump(out, open("data/places-raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
