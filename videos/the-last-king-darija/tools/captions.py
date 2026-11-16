#!/usr/bin/env python3
"""Write compositions/captions.html: the six Arabic lines, one after another.

Edit LINES (text, start, end in seconds, the amber words by index), then run
  python3 tools/captions.py
Each line enters on its start (card colour in 0.25 s, words right to left 0.06 s apart) and leaves
0.25 s before its end, so the next line lands on its beat. Brand: text #E8EEEC on a #141D21 card,
one amber (#F4A62A) phrase per line.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
END = 85.739

# (text, start, end, amber words, place); lines 1-5 change on strong beats over their pictures.
# place "high" keeps the card off the king (on the balcony, and walking to the light); "low" elsewhere.
LINES = [
    ("واش كنتي عارف بلي هاد الأغنية", 0.15, 6.74, ["هاد الأغنية"], "high"),
    ("لي ديما كاتطلق فالمناسبات و الاحتفالات", 6.74, 15.74, ["فالمناسبات", "و الاحتفالات"], "low"),
    ("هي فالأصل كاتهضر على سقوط الملكية ففرنسا", 15.74, 23.77, ["سقوط الملكية"], "low"),
    ("فرقة coldplay عمرهم أكدو هادشي", 23.77, 32.26, ["coldplay"], "low"),
    ("وكيقولو الأغنية كاتكلم على سقوط القوة", 32.26, 40.0, ["سقوط القوة"], "low"),
    # the person asked: lines 1-5 within the first 40 s, the last line over the last 20 s
    ("و أن كل من يعيش المجد اليوم قد يجرب الذل غدا", END - 20.0, END, ["الذل"], "high"),
]


def tokens(text):
    """split on spaces, keeping a lone «و» with the word after it so it never ends a line."""
    out, words = [], text.split(" ")
    i = 0
    while i < len(words):
        if words[i] == "و" and i + 1 < len(words):
            out.append("و" + "\u00a0" + words[i + 1])
            i += 2
        else:
            out.append(words[i])
            i += 1
    return out

AR_RANGE = ("U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0897-08E1,U+08E3-08FF,U+200C-200E,"
            "U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC")
LAT_RANGE = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,"
             "U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")


def f(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def main():
    groups, js = [], []
    for i, (text, s, e, hl, place) in enumerate(LINES, 1):
        for h in hl:  # an amber phrase stays on one line
            if " " in h and not h.startswith("و "):
                text = text.replace(h, h.replace(" ", "\u00a0"))
        words = tokens(text)
        hl_norm = {h.replace(" ", "\u00a0") for h in hl}
        spans = " ".join(
            f'<span id="c{i}-w{k}" class="w{" hl" if w in hl_norm else ""}">{w}</span>' for k, w in enumerate(words))
        groups.append(
            f'    <div id="cap-{i}" class="cap {place} clip" data-start="{f(s)}" data-duration="{f(e - s)}" data-track-index="0">\n'
            f'      <div id="c{i}-card" class="card" dir="rtl" lang="ar">{spans}</div>\n'
            f'    </div>')
        ws = ", ".join(f'"#c{i}-w{k}"' for k in range(len(words)))
        out = e - 0.25 if i < len(LINES) else e - 0.4
        js.append(
            f'      tl.fromTo("#c{i}-card", {{ backgroundColor: "rgba(20,29,33,0)", borderColor: "rgba(38,52,59,0)", y: 18 }},\n'
            f'        {{ backgroundColor: "rgba(20,29,33,0.82)", borderColor: "rgba(38,52,59,1)", y: 0, duration: 0.25, ease: "power2.out" }}, {f(s)});\n'
            f'      tl.fromTo([{ws}], {{ opacity: 0, y: 12, filter: "blur(6px)" }},\n'
            f'        {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power2.out", stagger: 0.06 }}, {f(s + 0.05)});\n'
            f'      tl.to("#c{i}-card", {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, {f(out)});\n'
            f'      tl.set("#c{i}-card", {{ opacity: 0, visibility: "hidden" }}, {f(e - 0.02)});')
    html = f"""<template>
  <script src="vendor/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: "Readex Pro"; font-weight: 700; font-display: block;
      src: url("assets/fonts/readex-pro-arabic-700-normal.woff2") format("woff2"); unicode-range: {AR_RANGE}; }}
    @font-face {{ font-family: "Readex Pro"; font-weight: 700; font-display: block;
      src: url("assets/fonts/readex-pro-latin-700-normal.woff2") format("woff2"); unicode-range: {LAT_RANGE}; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    /* the box TikTok, Reels and Shorts all leave clear at this height: x 120-780, y up to 1248
       (TikTok's button rail takes the right side); the card sits centred in it, bottom at 1240 px */
    .cap {{ position: absolute; display: flex; justify-content: center; overflow: visible; }}
    .cap.low {{ left: 130px; width: 640px; bottom: 680px; }}
    /* higher up, all three apps leave x 120-888 clear (y 288-840): centred, 696 px wide */
    .cap.high {{ left: 192px; width: 696px; top: 330px; }}
    .card {{ display: inline-block; max-width: 640px; padding: 18px 30px 22px; border-radius: 14px;
      border: 2px solid rgba(38, 52, 59, 0); background-color: rgba(20, 29, 33, 0);
      font-family: "Readex Pro", sans-serif; font-weight: 700; font-size: 54px; line-height: 1.55;
      color: #E8EEEC; text-align: center; text-wrap: balance; }}
    .w {{ display: inline-block; }}
    .hl {{ color: #F4A62A; }}
  </style>
  <!-- Written by tools/captions.py: edit the lines or their times there, then run it again. -->
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920" data-duration="{f(END)}">
{chr(10).join(groups)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    open(os.path.join(ROOT, "compositions", "captions.html"), "w", encoding="utf-8").write(html)
    print("wrote compositions/captions.html")


if __name__ == "__main__":
    main()
