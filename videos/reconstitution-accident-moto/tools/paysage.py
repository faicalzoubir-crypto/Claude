#!/usr/bin/env python3
"""Version 16:9 (1920×1080) du même film.

Les scènes sont communes : elles lisent window.FORMAT et html[data-format] (route horizontale dans compositions/world.html,
mise en page paysage des cartes). Ce script :
  prépare .paysage/ : copie du projet dont index.html est la racine 16:9 (format 16x9, cadre 1920×1080),
  pour check, snapshot, aperçu et rendu. Pas de seconde racine dans le projet (lint multiple_root_compositions).

  python3 tools/paysage.py                      # .paysage/
  npx --yes hyperframes@0.9.19 check .paysage
  npx --yes hyperframes@0.9.19 render .paysage -o livrables/reconstitution-accident-moto-16x9.mp4 --fps 30
  python3 tools/normaliser.py livrables/reconstitution-accident-moto-16x9.mp4
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "index.html").read_text()
pairs = [
    ('data-resolution="portrait" data-format="9x16"', 'data-resolution="landscape" data-format="16x9"'),
    ('<meta name="viewport" content="width=1080, height=1920" />', '<meta name="viewport" content="width=1920, height=1080" />'),
    ('<script>window.FORMAT = "9x16";</script>', '<script>window.FORMAT = "16x9";</script>'),
    ("width: 1080px;\n        height: 1920px;\n        overflow: hidden;\n        background: #0d1316;", "width: 1920px;\n        height: 1080px;\n        overflow: hidden;\n        background: #0d1316;"),
    ("width: 1080px;\n        height: 1920px;\n        overflow: hidden;\n      }", "width: 1920px;\n        height: 1080px;\n        overflow: hidden;\n      }"),
    ('data-width="1080" data-height="1920"', 'data-width="1920" data-height="1080"'),
    ("<!-- format : 9x16 ici ; la version 16x9 est générée dans .paysage/ par tools/paysage.py -->", "<!-- GÉNÉRÉ par tools/paysage.py depuis index.html : modifier index.html, puis relancer. -->"),
]
out = src
for a, b in pairs:
    n = out.count(a)
    assert n >= 1, a
    out = out.replace(a, b)

build = ROOT / ".paysage"
if build.exists():
    shutil.rmtree(build)
build.mkdir()
for name in ("compositions", "assets", "vendor"):
    shutil.copytree(ROOT / name, build / name)
for name in ("hyperframes.json", "meta.json", "package.json"):
    shutil.copy(ROOT / name, build / name)
(build / "index.html").write_text(out)
# les scènes déclarent le cadre de leur racine : 1920×1080 dans la copie paysage
for f in (build / "compositions").glob("*.html"):
    t, n = re.subn(r'data-width="1080"(\s+)data-height="1920"', r'data-width="1920"\1data-height="1080"', f.read_text())
    assert n == 1, f.name
    f.write_text(t)
print(".paysage/ prêt (racine 16:9)")
