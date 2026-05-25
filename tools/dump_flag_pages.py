"""Dump the test-server's synthesised 320x96 flag-page PNGs to disk.

The test server (`test/xl1_test_server.py`) computes these pages dynamically
from `images/flags_27x18/`. This tool freezes the current state to:
    spec/xl1-layouts/mockups/flags-page-N.png

Useful as static mockups and as a quick check that the hand-drawn flags
look right when tiled.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "test"))

from xl1_test_server import _synth_flags_page, _flag_page_count  # noqa: E402


OUT_DIR = REPO_ROOT / "spec" / "xl1-layouts" / "mockups"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n = _flag_page_count()
    for p in range(1, n + 1):
        data = _synth_flags_page(p)
        out = OUT_DIR / f"flags-page-{p}.png"
        out.write_bytes(data)
        print(f"wrote {out}  ({len(data):,} bytes)")
    print(f"--- {n} page(s)")


if __name__ == "__main__":
    main()
