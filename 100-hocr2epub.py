#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Das Komplott",
    # "--doc-subtitle", "",
    # "--doc-subject", "",
    "--doc-date", "2024-09-28",
    "--doc-edition", "1",
    "--doc-extent", "138 pages",
    "--color-image-pages", "139,140",
    "--doc-author", "Wolfgang Eggert",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "BoD – Books on Demand",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9783759796462",
    "--doc-cover-image", "075-level/139.tiff",
    "--canonical-url-base", "https://milahu.github.io/wolfgang-eggert-das-komplott-2024/",
    "--doc-description", """
Sicherheitsexperten stimmen darin überein,
daß die Schüsse auf Donald Trump in Butler/Pennsylvania
erst durch Polizeiversagen möglich wurden.

Gleichzeitig lassen Größe und Gemengelage der Pannen den Gedanken,
die Beamten der unterschiedlichen Polizeieinheiten hätten -
jeder für sich und alle zusammen - einfach nur einen "schlechten Tag" gehabt,
als abwegig erscheinen.

Somit steht der beunruhigende Gedanke im Raum,
daß am 13.7.2024 staatliche Manöver im Spiel waren.

Welche das gewesen sein könnten, und von wem sie ausgegangen sein mögen -
das sind die Fragen, denen sich das Buch in kriminalistischer Manier zuwendet.

Dabei werden ungewöhnliche Spuren und Verbindungen freigelegt.
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
