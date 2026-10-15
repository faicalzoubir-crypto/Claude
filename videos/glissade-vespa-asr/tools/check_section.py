"""Lance `hyperframes check` sur une seule section (le contrôle complet dépasse la limite fixe de 2 min
du CLI sur ce conteneur sans GPU). Écrit un index.html réduit à la section, contrôle, puis restaure.

Usage : python3 tools/check_section.py s3                       (contrôle)
        python3 tools/check_section.py s3 --render out.mp4      (aperçu rendu de la section seule)
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
    idx.write_text(s)
    cmd = ["npx", "hyperframes", "check"]
    if "--render" in sys.argv:
        cmd = ["npx", "hyperframes", "render", "-o", sys.argv[sys.argv.index("--render") + 1], "--quality", "looks"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("[INFO]"))
    print(out[-3000:])
finally:
    shutil.copy(backup, idx)
