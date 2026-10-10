"""Write the M26 side-profile outlines into the compositions.

<path data-outline="profil">    ← assets/m26/layout.json    (French version, real photo)
<path data-outline="profil-ar"> ← assets/m26-ar/layout.json (Arabic version, grey/green render)
usage: python3 tools/inject_outline.py
"""
import glob, json, re

OUTLINES = {
    "profil": json.load(open("assets/m26/layout.json"))["profil"]["outline"][0],
    "profil-ar": json.load(open("assets/m26-ar/layout.json"))["profil-vert"]["outline"][0],
}
for f in glob.glob("compositions/**/*.html", recursive=True):
    s = open(f).read()
    total = 0
    for key, d in OUTLINES.items():
        s, n = re.subn(rf'(data-outline="{key}"[^>]*?\sd=")[^"]*(")', lambda m: m.group(1) + d + m.group(2), s)
        total += n
    if total:
        open(f, "w").write(s)
        print(f, total)
