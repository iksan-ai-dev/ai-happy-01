# ai-happy-01 entry (Python 3.13, standard library only).
#
# The image is drawn at build time by generate.py (Pillow) and shipped in
# this repository as entry.png. The grading runtime has no Pillow and no
# network, so this program only copies the finished image to the output
# directory: /output/entry.png (or $MAKEFUN_OUTPUT_DIR when set).

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"),
                os.path.join(OUT_DIR, "entry.png"))
