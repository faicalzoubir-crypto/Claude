"""Versions du film dans une autre langue (en, ar ; fr = version d'origine).

  python3 tools/render_lang.py prepare ar    écrit index.html pour la langue (sauvegarde de l'original)
  python3 tools/render_lang.py restore       remet l'index.html d'origine
  python3 tools/render_lang.py render en     clip 3D de la langue + film complet → livrables/glissade-vespa-asr-<lang>-HD.mp4

La section 3D est pré-rendue par langue (assets/footage/s4-3d-rendu-<lang>.mp4) : le WebGL logiciel de ce
conteneur ne tient pas le film entier dans une seule page.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDX = ROOT / "index.html"
BACKUP = ROOT / ".hyperframes" / "index.lang-original.html"


def prepare(lang):
    BACKUP.parent.mkdir(exist_ok=True)
    if not BACKUP.exists():
        shutil.copy(IDX, BACKUP)
    s = BACKUP.read_text()
    attrs = f'lang="{lang}"' + (' dir="rtl"' if lang == "ar" else "")
    s = s.replace('<html lang="fr">', f"<html {attrs}>", 1)
    s = s.replace('<script>window.LANG = "fr";</script>', f'<script>window.LANG = "{lang}";</script>', 1)
    if lang != "fr":
        s = s.replace('src="assets/footage/s4-3d-rendu.mp4"', f'src="assets/footage/s4-3d-rendu-{lang}.mp4"', 1)
    IDX.write_text(s)


def restore():
    if BACKUP.exists():
        shutil.copy(BACKUP, IDX)
        BACKUP.unlink()


def run(cmd):
    print("→", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def render(lang):
    prepare(lang)
    try:
        clip = f"assets/footage/s4-3d-rendu-{lang}.mp4"
        if "--reuse-clip" not in sys.argv or not (ROOT / clip).exists():
            run(["python3", "-B", "tools/check_section.py", "s4", "--render", clip, "--quality", "delivery"])
        out = ROOT / "renders" / f"glissade-vespa-asr-{lang}.mp4"
        run(["npx", "hyperframes", "render", str(ROOT), "-o", str(out), "--quality", "delivery"])
        (ROOT / "livrables").mkdir(exist_ok=True)
        shutil.copy(out, ROOT / "livrables" / f"glissade-vespa-asr-{lang}-HD.mp4")
    finally:
        restore()


if __name__ == "__main__":
    cmd, lang = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
    {"prepare": lambda: prepare(lang), "restore": restore, "render": lambda: render(lang)}[cmd]()
