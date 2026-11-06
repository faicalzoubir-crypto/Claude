#!/usr/bin/env python3
"""Insère les @font-face de Cairo (sous-ensembles arabe + latin, 600/700/800) à la place de /*FONTS*/ dans compositions/*.html."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AR = "U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0897-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC"
LA = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
rules = []
for w in (600, 700, 800):
    for sub, rng in (("arabic", AR), ("latin", LA)):
        rules.append(
            f'@font-face {{ font-family: "Cairo"; src: url("assets/fonts/cairo-{sub}-{w}-normal.woff2") format("woff2"); '
            f"font-weight: {w}; font-style: normal; font-display: block; unicode-range: {rng}; }}"
        )
css = "\n        ".join(rules)
for f in sorted((ROOT / "compositions").glob("*.html")):
    s = f.read_text()
    if "/*FONTS*/" in s:
        f.write_text(s.replace("/*FONTS*/", "/* Cairo (tools/polices.py) */\n        " + css))
        print("polices →", f.name)
