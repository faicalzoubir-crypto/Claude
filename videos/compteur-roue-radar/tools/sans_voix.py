#!/usr/bin/env python3
"""Take the narration out of the assembled index.html (version without voice).

The voice clips stay listed in audio_meta.json: their word timings still drive
the subtitles and the pacing of every frame. Only the <audio> elements that play
them are removed from the root composition. Run after assemble-index.mjs and
transitions.mjs (both rewrite index.html), with the music built by
`python3 tools/music.py --sans-voix`.

  python3 tools/sans_voix.py
"""
import re
from pathlib import Path

index = Path(__file__).resolve().parent.parent / "index.html"
html = index.read_text()
html, n = re.subn(r'\n\s*<audio\b[^>]*\bid="el-[0-9]{2}-[a-z-]+-voice"[^>]*>\s*</audio>', "", html)
index.write_text(html)
print(f"removed {n} voice track(s) from index.html")
