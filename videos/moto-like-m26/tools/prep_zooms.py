"""Square close-up crops of the real M26 photos for the equipment beats (frame 5).

usage: python3 tools/prep_zooms.py  ->  assets/m26/zoom-*.webp (900x900)
Each entry: source photo, crop centre (x, y) and half-size in source pixels.
"""
from PIL import Image

ZOOMS = {
    "guidon":       ("source/m26-trois-quarts-arriere-droit.jpg", (1000, 640), 400),
    "phare":        ("source/m26-face-phare.jpg", (930, 770), 330),
    "ecran":        ("source/m26-trois-quarts-arriere-droit.jpg", (1350, 550), 300),
    "confort":      ("source/m26-trois-quarts-arriere-droit.jpg", (640, 1130), 560),
    "frein-avant":  ("source/m26-trois-quarts-avant-gauche.jpg", (660, 1830), 270),
    "frein-arriere":("source/m26-trois-quarts-arriere-gauche-blanc.jpg", (1932, 1597), 230),
    "fourche":      ("source/m26-face-phare.jpg", (830, 1470), 300),
    "amortisseur":  ("source/m26-profil-gauche.jpg", (500, 1230), 250),
}
for name, (src, (cx, cy), h) in ZOOMS.items():
    im = Image.open(src).convert("RGB")
    im.crop((cx - h, cy - h, cx + h, cy + h)).resize((900, 900), Image.LANCZOS).save(
        f"assets/m26/zoom-{name}.webp", "WEBP", quality=88, method=6)
    print("zoom", name)

# shop facade for the closing shot
Image.open("source/magasin-moto-like.png").convert("RGB").save("assets/m26/magasin.webp", "WEBP", quality=90, method=6)
print("magasin")
