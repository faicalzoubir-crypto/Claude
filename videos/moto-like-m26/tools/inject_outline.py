"""Write the M26 side-profile outline (assets/m26/layout.json) into every <path data-outline="profil">.

usage: python3 tools/inject_outline.py
"""
import glob, json, re

d = json.load(open("assets/m26/layout.json"))["profil"]["outline"][0]
for f in glob.glob("compositions/*.html"):
    s = open(f).read()
    n = re.subn(r'(data-outline="profil"[^>]*?\sd=")[^"]*(")', lambda m: m.group(1) + d + m.group(2), s)
    if n[1]:
        open(f, "w").write(n[0])
        print(f, n[1])
