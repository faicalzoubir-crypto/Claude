"""Remove neighbouring scooters from a BiRefNet cutout with hand-placed polygons.

usage: python3 tools/clean_cutout.py <cutout.png> <spec.json> <out.png>
spec = {"remove": [[[x,y],...], ...], "keep": [[[x,y],...], ...], "feather": 1.5}
Pixels inside a "remove" polygon become transparent unless they fall in a "keep" polygon.
"""
import json, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

src, spec_path, out = sys.argv[1:4]
spec = json.load(open(spec_path))
im = Image.open(src).convert("RGBA")
rm = Image.new("L", im.size, 0)
d = ImageDraw.Draw(rm)
for poly in spec.get("remove", []):
    d.polygon([tuple(p) for p in poly], fill=255)
for poly in spec.get("keep", []):
    d.polygon([tuple(p) for p in poly], fill=0)
for box in spec.get("clear_below", []):
    pass
f = spec.get("feather", 1.5)
if f:
    rm = rm.filter(ImageFilter.GaussianBlur(f))
a = im.getchannel("A")
a = ImageChops.multiply(a, ImageChops.invert(rm))
im.putalpha(a)
bbox = a.point(lambda v: 255 if v > 8 else 0).getbbox()
im.save(out)
print("saved", out, "bbox", bbox)
