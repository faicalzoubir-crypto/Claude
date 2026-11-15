"""INTRO (0–22.845 s): the reference clip's edit, rebuilt with the story's paintings.
  0.000–5.667  hook shot (the Galerie des Glaces), words WAIT · WHAT'S · SONG · THAT · GOES · LIKE
  5.667–6.100  black
  6.100–9.467  one long pan across the whole Galerie (Cochin, 1745), accelerating into the first lyric
  9.467–22.845 one painting detail per cut (the reference's cut times), one lyric word per beat
At 22.845 the film cuts to the King (verse 1) on the downbeat; the last word, OWN, rides over that cut.
Writes assets/img/intro/*.jpg and compositions/intro.html."""
import os
import numpy as np
from PIL import Image

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = f"{P}/assets/src", f"{P}/assets/img/intro"
os.makedirs(OUT, exist_ok=True)


def gmap(img, stops):
    lum = img @ np.array([0.299, 0.587, 0.114], np.float32)
    xs = np.array([s[0] for s in stops], np.float32)
    return np.stack([np.interp(lum, xs, np.array([s[1][c] for s in stops], np.float32) / 255) for c in range(3)], -1)


CANDLE = [(0.00, (12, 7, 3)), (0.30, (58, 30, 12)), (0.62, (150, 92, 40)), (0.85, (222, 172, 104)), (1.00, (250, 222, 166))]
DAWN = [(0.00, (18, 22, 28)), (0.40, (70, 80, 92)), (0.78, (150, 158, 166)), (1.00, (206, 208, 204))]
TONES = {"candle": CANDLE, "dawn": DAWN}
cache = {}


def src(name):
    if name not in cache:
        path = f"{P}/assets/img/{name}" if name == "king-royal.png" else f"{SRC}/{name}"
        cache[name] = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255
    return cache[name]


def dial_on_black(out):
    d = Image.open(f"{P}/assets/img/cadran.png")
    canvas = Image.new("RGB", (900, 1600), (8, 6, 4))
    dw = 820
    dd = d.resize((dw, dw), Image.LANCZOS)
    canvas.paste(dd, ((900 - dw) // 2, 640 - dw // 2), dd)
    canvas.save(f"{OUT}/{out}.jpg", quality=92)
    return out


def crop(name, cx, cy, w, tone=None, out=None):
    im = src(name)
    h = round(w * 16 / 9)
    H, W = im.shape[:2]
    x0 = int(np.clip(cx - w / 2, 0, W - w)); y0 = int(np.clip(cy - h / 2, 0, H - h))
    c = im[y0:y0 + h, x0:x0 + w]
    if tone:
        c = gmap(c, TONES[tone])
    Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)).save(f"{OUT}/{out}.jpg", quality=92)
    return out


def throne_on_black(out):
    t = Image.open(f"{P}/assets/img/trone.png")
    canvas = Image.new("RGB", (1100, 1956), (6, 5, 4))
    tw = 1000; th = round(tw * t.height / t.width)
    canvas.paste(t.resize((tw, th), Image.LANCZOS), (50, 1956 // 2 - th // 2 - 60), t.resize((tw, th), Image.LANCZOS))
    canvas.save(f"{OUT}/{out}.jpg", quality=92)
    return out


# the long pan: the whole engraved gallery (inside its printed border, above its lettering), candle-toned
g = src("galerie-bal-masque-1746.jpg")[149:2021, 144:3696]
Image.fromarray((np.clip(gmap(g, CANDLE), 0, 1) * 255).astype(np.uint8)).save(f"{OUT}/pan.jpg", quality=92)

# (start, end, image id, move: "in" | "out" | "up" | "down")
B = "galerie-bal-masque-1746.jpg"; C = "cour-de-marbre-1789.jpg"; V = "a-versailles-1789.jpg"
DX = "demachy-execution-1793.jpg"; DU = "demachy-unite-1793.jpg"; H = "houel-bastille-1789.jpg"; K = "king-royal.png"   # the recoloured Callet (blue coat), same pixel grid as the source
shots = [
    (9.467, 10.567, crop(C, 1880, 1350, 1000, "dawn", "s01-cour"), "in"),          # USED
    (10.567, 11.000, crop("couronne-louis-xv.jpg", 1944, 1400, 1300, None, "s02-couronne"), "out"),  # RULE
    (11.000, 11.900, crop(K, 2300, 3600, 1000, None, "s03-etoile"), "in"),         # RULE — the Saint-Esprit star
    (11.900, 12.367, crop(B, 1460, 1250, 900, "candle", "s04-lustres"), "up"),     # THE
    (12.367, 12.767, crop(B, 2600, 1000, 1000, "candle", "s05-plafond"), "out"),   # WORLD
    (12.767, 13.233, crop(B, 2000, 1200, 900, "candle", "s06-bal"), "in"),         # WORLD
    (13.233, 13.667, crop(DU, 2050, 1557, 1000, None, "s07-foule"), "out"),        # SEAS
    (13.667, 14.100, crop(V, 1900, 1380, 900, None, "s08-piques"), "up"),          # RISE
    (14.100, 14.567, crop(V, 850, 1300, 900, None, "s09-femmes"), "in"),           # WHEN
    (14.567, 15.000, crop(K, 1080, 3150, 800, None, "s10-manteau"), "out"),         # I — the fleur-de-lis mantle
    (15.000, 15.433, crop(C, 1880, 1250, 800, "dawn", "s11-balcon"), "in"),        # GAVE
    (15.433, 15.900, crop(C, 1300, 1500, 900, "dawn", "s12-cour-foule"), "down"),  # THE WORD
    (15.900, 16.333, crop(DX, 2900, 1100, 1000, None, "s13-ciel"), "up"),          # NOW
    (16.333, 16.767, crop(C, 2400, 1260, 900, "dawn", "s14-toits"), "in"),         # IN THE
    (16.767, 17.200, crop(DU, 2900, 1100, 1100, None, "s15-matin"), "out"),        # MORNING
    (17.200, 17.667, throne_on_black("s16-trone"), "in"),                          # I
    (17.667, 18.567, crop(B, 1900, 1100, 1100, "candle", "s17-galerie-vide"), "in"),  # SLEEP
    (18.567, 18.967, dial_on_black("s18-cadran"), "out"),  # SLEEP
    (18.967, 19.433, crop(V, 3300, 1450, 700, None, "s19-seule"), "in"),           # ALONE
    (19.433, 19.867, crop(H, 950, 1300, 1000, None, "s20-tour"), "up"),            # ALONE
    (19.867, 20.333, crop(H, 2950, 1450, 1000, None, "s21-feu"), "in"),            # SWEEP
    (20.333, 20.767, crop(DU, 1350, 1640, 900, None, "s22-drapeaux"), "out"),      # THE
    (20.767, 21.200, crop(H, 3200, 1950, 1000, None, "s23-canon"), "in"),          # STREETS
    (21.200, 21.667, crop(DX, 700, 1730, 1000, None, "s24-chapeaux"), "down"),     # I
    (21.667, 22.100, crop(V, 1100, 1549, 800, None, "s25-roue"), "in"),            # USED
    (22.100, 22.533, crop(DX, 520, 1100, 800, None, "s26-liberte"), "out"),        # TO
    (22.533, 22.845, crop(C, 1880, 1300, 1046, "dawn", "s27-palais"), "in"),       # OWN
]

words = [
    (0.00, 0.47, "WAIT"), (0.48, 1.12, "WHAT'S"), (1.14, 1.50, "SONG"), (1.52, 1.88, "THAT"), (1.90, 2.36, "GOES"),
    (2.38, 3.30, "LIKE"),
    (9.50, 10.22, "USED"), (10.25, 11.45, "RULE"), (11.50, 11.95, "THE"), (12.00, 12.95, "WORLD"),
    (13.00, 13.70, "SEAS"), (13.75, 13.97, "RISE"), (14.00, 14.70, "WHEN"), (14.75, 14.97, "I"),
    (15.00, 15.22, "GAVE"), (15.25, 15.47, "THE"), (15.50, 15.97, "WORD"), (16.00, 16.22, "NOW"),
    (16.25, 16.47, "IN"), (16.50, 16.72, "THE"), (16.75, 17.22, "MORNING"), (17.25, 17.47, "I"),
    (17.50, 18.97, "SLEEP"), (19.00, 19.97, "ALONE"), (20.25, 20.72, "SWEEP"), (20.75, 20.97, "THE"),
    (21.00, 21.47, "STREETS"), (21.50, 21.97, "I"), (22.00, 22.22, "USED"), (22.25, 22.72, "TO"),
    (22.75, 23.25, "OWN"),
]

MOVES = {"in": ("scale: 1.0", "scale: 1.09"), "out": ("scale: 1.09", "scale: 1.0"),
         "up": ("scale: 1.06, y: 60", "scale: 1.06, y: -60"), "down": ("scale: 1.06, y: -60", "scale: 1.06, y: 60")}

html = ["<template>", """  <style>
    @font-face { font-family: "Montserrat HF"; src: url("assets/fonts/montserrat-latin-600-normal.woff2") format("woff2"); font-weight: 600; }
    #root { position: absolute; inset: 0; overflow: hidden; }
    .intro-shot { position: absolute; inset: 0; overflow: hidden; background: #000; }
    .intro-move { position: absolute; inset: 0; }
    .intro-img { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }
    #intro-pan-move { position: absolute; left: 0; top: 0; width: 3643px; height: 1920px; }
    #intro-pan-img { position: absolute; left: 0; top: 0; width: 3643px; height: 1920px; }
    /* the reference's lettering: geometric caps, salmon, difference-blended with the picture */
    .intro-word {
      position: absolute; left: 0; right: 0; top: 735px; height: 170px; z-index: 50;
      display: flex; align-items: center; justify-content: center;
      font-family: "Montserrat HF", sans-serif; font-weight: 600; font-size: 138px; line-height: 1;
      letter-spacing: 0.02em; color: #e3957f; mix-blend-mode: difference; white-space: nowrap;
    }
  </style>""",
        '  <div id="root" data-composition-id="intro" data-width="1080" data-height="1920">',
        '    <div id="intro-hook" class="intro-shot clip" data-start="0" data-duration="5.667" data-track-index="0">',
        '      <div id="intro-hook-move" class="intro-move">',
        '        <img id="intro-hook-img" class="intro-img" src="assets/img/galerie.jpg" alt="The Galerie des Glaces, 1745" />',
        '      </div>', '    </div>',
        '    <div id="intro-pan" class="intro-shot clip" data-start="6.1" data-duration="3.367" data-track-index="0">',
        '      <div id="intro-pan-move">',
        '        <img id="intro-pan-img" class="intro-img" src="assets/img/intro/pan.jpg" alt="The whole Galerie des Glaces" />',
        '      </div>', '    </div>']
for i, (a, b, img, mv) in enumerate(shots, 1):
    html += [f'    <div id="intro-s{i:02d}" class="intro-shot clip" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-track-index="0">',
             f'      <div id="intro-s{i:02d}-move" class="intro-move">',
             f'        <img id="intro-s{i:02d}-img" class="intro-img" src="assets/img/intro/{img}.jpg" alt="" />',
             '      </div>', '    </div>']
for j, (a, b, w) in enumerate(words, 1):
    html.append(f'    <div id="intro-w{j:02d}" class="intro-word clip" data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="1">{w}</div>')
html.append("  </div>")
js = ["  <script>", "    (function () {", "      const tl = gsap.timeline({ paused: true });",
      '      tl.fromTo("#intro-hook-move", { scale: 1.0 }, { scale: 1.08, duration: 5.667, ease: "none" }, 0);',
      '      tl.fromTo("#intro-pan-move", { x: 0 }, { x: -2563, duration: 3.367, ease: "power2.in" }, 6.1);']
for i, (a, b, img, mv) in enumerate(shots, 1):
    f, t = MOVES[mv]
    js.append(f'      tl.fromTo("#intro-s{i:02d}-move", {{ {f} }}, {{ {t}, duration: {b - a:.3f}, ease: "none" }}, {a:.3f});')
js += ['      window.__timelines["intro"] = tl;', "    })();", "  </script>", "</template>", ""]
open(f"{P}/compositions/intro.html", "w").write("\n".join(html + js))
print(len(shots), "shots,", len(words), "words")
