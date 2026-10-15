"""Lance `hyperframes check` sur une seule section (le contrôle complet dépasse la limite fixe de 2 min
du CLI sur ce conteneur sans GPU). Écrit un index.html réduit à la section, contrôle, puis restaure.

Usage : python3 tools/check_section.py s3                       (contrôle)
        python3 tools/check_section.py s3 --render out.mp4 [--quality delivery]   (rendu de la section seule,
        sans fondu de film ni musique : sert aux aperçus et au clip pré-rendu de la section 3D)
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sec = sys.argv[1]
idx = ROOT / "index.html"
backup = ROOT / ".hyperframes" / "index.full.html"
backup.parent.mkdir(exist_ok=True)
shutil.copy(idx, backup)
try:
    s = idx.read_text()
    # la section 4 est importée comme clip pré-rendu : on la remplace par son hôte d'origine si on la vise, sinon on la retire
    clip = re.search(r'      <!-- Section 4 pré-rendue.*?\n      </div>\n', s, flags=re.S)
    if clip:
        host = "" if sec != "s4" else (
            '      <div\n        id="el-s4"\n        data-composition-id="s4-3d"\n        data-composition-src="compositions/s4-3d.html"\n'
            '        data-start="36.2"\n        data-duration="26.4"\n        data-track-index="4"\n        data-width="1080"\n        data-height="1920"\n      ></div>\n\n'
        )
        s = s.replace(clip.group(0), host)
    hosts = re.findall(r'      <div\n        id="el-(s\d)".*?></div>\n\n', s, flags=re.S)
    m = re.search(rf'      <div\n        id="el-{sec}".*?></div>\n\n', s, flags=re.S)
    block = m.group(0)
    dur = re.search(r'data-duration="([\d.]+)"', block).group(1)
    for h in hosts:
        if h != sec:
            s = re.sub(rf'      <div\n        id="el-{h}".*?></div>\n\n', "", s, flags=re.S)
    s = re.sub(r'(id="el-' + sec + r'".*?data-start=")[\d.]+', r"\g<1>0", s, flags=re.S)
    s = re.sub(r'(data-composition-id="main"\n      data-start="0"\n      data-duration=")[\d.]+', r"\g<1>" + dur, s)
    s = re.sub(r'\n      tl\.fromTo\("#el-s\d".*', "", s)
    if "--render" in sys.argv:
        # rendu d'une section seule pour l'importer comme clip : pas de fondu de film ni de musique
        s = re.sub(r'\n      tl\.(fromTo|to)\("#film-fade".*', "", s)
        s = s.replace('      <div id="film-fade"></div>\n', "")
        s = re.sub(r'\n      <!-- fond musical.*?</audio>\n', "\n", s, flags=re.S)
    idx.write_text(s)
    cmd = ["npx", "hyperframes", "check"]
    if "--render" in sys.argv:
        quality = sys.argv[sys.argv.index("--quality") + 1] if "--quality" in sys.argv else "looks"
        cmd = ["npx", "hyperframes", "render", "-o", sys.argv[sys.argv.index("--render") + 1], "--quality", quality]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("[INFO]"))
    print(out[-3000:])
finally:
    shutil.copy(backup, idx)
