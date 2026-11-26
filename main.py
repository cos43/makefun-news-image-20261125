#!/usr/bin/env python3
"""News-image entry program (Python 3.13, standard library only).

The entry's image is the entry.png beside this file. The program copies it
byte for byte to /output/entry.png. The grader runs it twice and both runs
must write the same bytes, so this is a plain copy with a size check.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    src = HERE / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)
    if sha256(dst) != sha256(src):
        print("entry.png copy hash mismatch", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({dst.stat().st_size} bytes, sha256 {sha256(dst)[:16]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
