"""Download HiDPI source images for the country flags missing from
`images/flags/big/`. Output goes into `images/flags/big/<name>.webp`, where
`<name>` matches the existing 18×12 PNG filename so the main generator
(`render_flags_27x18.py`) picks them up on next run.

Source: flagpedia.net (CC0-licensed flag image bank, 1000×667 webp).

Usage:
    python3 tools/fetch_missing_hidpi_flags.py
"""

from __future__ import annotations

import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "images" / "flags" / "big"

# Project filename → ISO-3166 alpha-2 code on flagpedia.
TARGETS: dict[str, str] = {
    "france":               "fr",
    "germany":              "de",
    "italy":                "it",
    "spain":                "es",
    "switzerland":          "ch",
    "portugal":             "pt",
    "ukraine":              "ua",
    "ivory coast":          "ci",
    "new caledonia":        "nc",
    "usa":                  "us",
    # Netherlands Antilles is defunct (2010); flagpedia retired the entry.
    # Their successors are Curaçao (cw), Sint Maarten (sx). For the existing
    # firmware asset name we approximate with the Curaçao flag.
    "netherlands antilles": "cw",
}

URL_TEMPLATE = "https://flagpedia.net/data/flags/w1160/{iso}.webp"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok, skipped, failed = 0, 0, 0
    for name, iso in TARGETS.items():
        out = OUT_DIR / f"{name}.webp"
        if out.exists():
            print(f"  {name}: already present, skipping")
            skipped += 1
            continue
        url = URL_TEMPLATE.format(iso=iso)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            out.write_bytes(data)
            print(f"  {name}: {len(data)} bytes -> {out.name}")
            ok += 1
        except Exception as ex:
            print(f"  {name}: FAILED — {ex}")
            failed += 1
    print(f"done: {ok} downloaded, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
