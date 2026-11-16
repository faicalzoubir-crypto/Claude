# Stitch Esri World Imagery z14 tiles around Casablanca, save at half size, and project the places.
# Output: assets/map/casa-sat.jpg (daytime imagery; the night look is a media-treatment grade in HF)
#         data/map.json (image size, frame scales, every place in image pixels)
import json, math, os, io, urllib.request, concurrent.futures as cf
from PIL import Image

Z = 14; T = 256; W = T * 2 ** Z
def wx(lon): return (lon + 180) / 360 * W
def wy(lat):
    s = math.radians(lat); return (1 - math.log(math.tan(s) + 1 / math.cos(s)) / math.pi) / 2 * W

# Curated, approximate neighbourhood points (OpenStreetMap Nominatim, see data/places-raw.json).
P = {
 # dark: reported outage
 "centre": (33.5916, -7.6198), "belyout": (33.6000, -7.6130), "anfa": (33.5890, -7.6639),
 "bourgogne": (33.5986, -7.6419), "maarif": (33.5810, -7.6375), "ghallef": (33.5736, -7.6296),
 "merssultan": (33.5790, -7.6070), "hopitaux": (33.5775, -7.6220), "fida": (33.5649, -7.5966),
 "californie": (33.5412, -7.6260), "ainchock": (33.5371, -7.5982), "oulfa": (33.5490, -7.6820),
 "cfc": (33.5632, -7.6604), "hassani": (33.5600, -7.6950), "sbata": (33.5377, -7.5640),
 "benmsick": (33.5543, -7.5814), "sidiothmane": (33.5570, -7.5604), "sidimaarouf": (33.5286, -7.6465),
 "bouskoura": (33.4564, -7.6507),
 # lit: not mentioned in reports
 "ainsebaa": (33.6060, -7.5388), "haymohammadi": (33.5856, -7.5667), "sidimoumen": (33.5844, -7.5072),
 "bernoussi": (33.6191, -7.5003), "aindiab": (33.5870, -7.6830),
 # off-frame
 "darbouazza": (33.5216, -7.8164), "ouledazzouz": (33.5186, -7.7575), "nouaceur": (33.3679, -7.5681),
 "mohammedia": (33.6958, -7.3893),
}

# Frame: final scale S1 screen px per z14 px; content centre lon -7.600; Bouskoura lands at screen y 1330.
S1 = 0.40; S0 = 0.34
cx = wx(-7.600)
cy = wy(33.4564) - (1330 - 960) / S1          # world y at the screen centre (960)
half_w = 1080 / S0 / 2 + 64; half_h = 1920 / S0 / 2 + 64
x0, x1 = int((cx - half_w) // T), int((cx + half_w) // T) + 1
y0, y1 = int((cy - half_h) // T), int((cy + half_h) // T) + 1
print("tiles", x1 - x0, "x", y1 - y0, "=", (x1 - x0) * (y1 - y0))

os.makedirs("data/tiles", exist_ok=True)
def get(xy):
    x, y = xy; p = f"data/tiles/{Z}_{y}_{x}.jpg"
    if not os.path.exists(p):
        u = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{y}/{x}"
        req = urllib.request.Request(u, headers={"User-Agent": "hyperframes-map-bake/1.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        open(p, "wb").write(data)
    return xy, p
img = Image.new("RGB", ((x1 - x0) * T, (y1 - y0) * T))
with cf.ThreadPoolExecutor(6) as ex:
    for (x, y), p in ex.map(get, [(x, y) for y in range(y0, y1) for x in range(x0, x1)]):
        img.paste(Image.open(p).convert("RGB"), ((x - x0) * T, (y - y0) * T))
half = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
os.makedirs("assets/map", exist_ok=True)
half.save("assets/map/casa-sat.jpg", quality=90)
ox, oy = x0 * T, y0 * T   # world px of image (0,0) at full res
pts = {k: {"lat": la, "lon": lo, "x": round((wx(lo) - ox) / 2, 1), "y": round((wy(la) - oy) / 2, 1)} for k, (la, lo) in P.items()}
meta = {"image": "assets/map/casa-sat.jpg", "w": half.width, "h": half.height,
        "center": {"x": round((cx - ox) / 2, 1), "y": round((cy - oy) / 2, 1)},
        "scaleEnd": S1 * 2, "scaleStart": S0 * 2, "pxPerKmEnd": round(S1 * W / 40075.016686 / math.cos(math.radians(33.56)), 2),
        "places": pts}
json.dump(meta, open("data/map.json", "w"), indent=1)
print(half.size, meta["center"], "px/km at end", meta["pxPerKmEnd"])
