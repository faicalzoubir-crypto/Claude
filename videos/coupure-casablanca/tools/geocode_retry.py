import json, time, urllib.parse, urllib.request, sys
Q = {
 "bourgogne": ["Bourgogne, Casablanca", "Quartier Bourgogne Casablanca"],
 "hopitaux": ["Hôpital Ibn Rochd, Casablanca", "Quartier des Hôpitaux"],
 "sbata": ["Sbata, Casablanca", "Arrondissement de Sbata"],
 "bouskoura": ["Bouskoura"],
 "haymohammadi": ["Hay Mohammadi, Casablanca", "Arrondissement de Hay Mohammadi"],
 "anfa_q": ["Anfa Supérieur, Casablanca", "Quartier Anfa, Casablanca"],
 "maarif_q": ["Maârif, Casablanca, quartier", "Twin Center, Casablanca"],
 "hassani_q": ["Hay Hassani, quartier, Casablanca", "Hay Hassani"],
}
out = {}
for k, qs in Q.items():
    out[k] = []
    for q in qs:
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({"q": q, "format": "jsonv2", "limit": 4, "accept-language": "fr", "countrycodes": "ma"})
        req = urllib.request.Request(url, headers={"User-Agent": "hyperframes-map-bake/1.0"})
        for attempt in range(3):
            try:
                res = json.load(urllib.request.urlopen(req, timeout=30)); break
            except Exception as e:
                print("retry", k, e, file=sys.stderr); time.sleep(6); res = []
        for h in res:
            out[k].append({"q": q, "lat": float(h["lat"]), "lon": float(h["lon"]), "type": h.get("addresstype") or h.get("type"), "name": h.get("display_name","")[:80]})
            print(k, "|", q, "|", round(float(h["lat"]),4), round(float(h["lon"]),4), h.get("addresstype"), "|", h.get("display_name","")[:70])
        time.sleep(2.5)
json.dump(out, open("data/places-retry.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
