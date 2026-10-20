#!/usr/bin/env python3
"""Show or hide the burned-in subtitles in index.html, without deleting them.

Uses HyperFrames' `data-hidden` on the caption track (#el-captions): hidden in
both preview and render, reversible, the track and compositions/captions.html
stay as they are.

  python3 tools/sous_titres.py off   # version without subtitles
  python3 tools/sous_titres.py on    # back to subtitles (the project's default)
"""
import re
import sys
from pathlib import Path

index = Path(__file__).resolve().parent.parent / "index.html"
html = index.read_text()
mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode not in ("on", "off"):
    sys.exit("usage: python3 tools/sous_titres.py on|off")
html = re.sub(r'(id="el-captions")( data-hidden)?', r'\1 data-hidden' if mode == "off" else r'\1', html, count=1)
index.write_text(html)
print("subtitles", "hidden" if mode == "off" else "shown")
