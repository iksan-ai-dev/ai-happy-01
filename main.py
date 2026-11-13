#!/usr/bin/env python3
"""ai-happy-01 entrypoint (Python 3.13, standard library only).

The entry image is pre-rendered at build time and shipped in this repo as
entry.png; this program only copies it to the output directory.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "entry.png", OUT / "entry.png")
print("wrote", OUT / "entry.png")
