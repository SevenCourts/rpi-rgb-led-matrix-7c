"""Golden PNGs of the headless renderer: check them, or write them anew.

    python -m tests.render_goldens             # compare, all panel types
    python -m tests.render_goldens --update    # rewrite tests/golden/
    python -m tests.render_goldens --type L1   # one type, in this process

One process draws one panel type (PANEL_TYPE is frozen at import), so without
--type this starts itself once per type. tests/test_render.py runs the check.

The payloads come from the catalogue of tools/emulators/fixture_server.py, so
a golden shows what tools/emulators/emulators.sh shows for the same fixture.
This repository is public: SevenCourts style only, no club logos or names.

After a deliberate change to a view, run with --update and look at the diff of
the PNGs before committing them.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"
# Where a failed check leaves what it drew, to look at (and for CI to upload).
ACTUAL_DIR = REPO_ROOT / ".runtime" / "render-actual"

PANEL_TYPES = ("M1", "L1", "XL1")

# The moment every golden is drawn for; the booking fixtures are built around it.
NOW = "2026-05-25T14:30:00+02:00"
# In the middle of the fixtures' 13:00-14:30 booking.
NOW_MID_BOOKING = "2026-05-25T14:10:00+02:00"
# 14:57:10: the last 5 minutes of a booking, and the next booking's turn.
NOW_INTERCHANGE = "2026-05-25T14:57:10+02:00"

WEATHER = {"city": "Stuttgart,DE", "temperature": 21}


def _synthetic_image(w: int, h: int) -> bytes:
    """A colour ramp with a border and a crosshair: scaling, placement and
    cropping errors show at once. No text, so no font of the machine is used."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (255 * x // (w - 1), 255 * y // (h - 1), 128)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w - 1, h - 1], outline=(255, 255, 255))
    draw.line([(0, h // 2), (w - 1, h // 2)], fill=(255, 255, 255))
    draw.line([(w // 2, 0), (w // 2, h - 1)], fill=(255, 255, 255))
    out = BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


# Stands in for the tableau server the views download images from.
_IMAGES = {
    "/panel-image/wide.png": (320, 96),
    "/panel-image/square.png": (96, 96),
}


class _ImageHandler(BaseHTTPRequestHandler):
    def _send(self, with_body: bool):
        size = _IMAGES.get(self.path)
        if size is None:
            self.send_error(404)
            return
        data = _synthetic_image(*size)
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("ETag", "golden-%dx%d" % size)
        self.end_headers()
        if with_body:
            self.wfile.write(data)

    def do_HEAD(self):
        self._send(False)

    def do_GET(self):
        self._send(True)

    def log_message(self, *args):
        pass


def _start_image_server() -> str:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ImageHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return "http://127.0.0.1:%d" % server.server_address[1]


def scenarios(image_base_url: str) -> list:
    """(file name, panel_info, now, keyword arguments of render)."""
    sys.path.insert(0, str(REPO_ROOT / "tools" / "emulators"))
    import fixture_server as fixtures

    by_name = {f["name"]: f["info"] for f in fixtures.FIXTURES}

    def idle(**kw):
        return {"idle-info": {"timezone": "Europe/Berlin", **kw}}

    def live(name):
        """A booking fixture without its own clock: the time comes from `now`,
        as for a live panel."""
        booking = by_name[name]["booking"]
        return {"booking": {k: v for k, v in booking.items() if k != "_dev_timestamp"}}

    return [
        ("not-configured", {}, NOW, {}),
        ("standby", by_name["standby"], NOW, {}),
        ("clock-default", by_name["clock — default (clock:true)"], NOW, {}),
        ("clock-7segment-medium", by_name["clock — font-1 medium center/center"], NOW, {}),
        ("clock-spleen-large", by_name["clock — font-2 (Spleen) large center/center"], NOW, {}),
        ("clock-server-unreachable", by_name["clock — default (clock:true)"], NOW,
         {"comm_error": True}),
        ("message-two-lines", by_name["message — two lines"], NOW, {}),
        ("message-with-clock", by_name["message — with clock strip"], NOW, {}),
        ("image-preset", by_name["image — preset (sevencourts logo)"], NOW, {}),
        ("image-uploaded", idle(**{"image-url": "panel-image/wide.png"}), NOW, {}),
        ("image-uploaded-with-clock",
         idle(clock=True, **{"image-url": "panel-image/square.png"}), NOW, {}),
        ("ads-image", {"ebusy-ads": {"url": image_base_url + "/panel-image/wide.png"}},
         NOW, {}),
        ("scoreboard-singles", by_name["scoreboard — singles, 3 sets in progress"], NOW, {}),
        ("scoreboard-singles-finished", by_name["scoreboard — singles, T2 won"], NOW, {}),
        ("scoreboard-doubles", by_name["scoreboard — doubles, 3 sets"], NOW, {}),
        ("booking-single", live("booking — SevenCourts, 1-court"), NOW_MID_BOOKING,
         {"weather": WEATHER}),
        ("booking-single-blocked", by_name["booking — BLOCKING (maintenance)"], NOW,
         {"weather": WEATHER}),
        ("booking-multiple", by_name["booking — SevenCourts, 3-court"], NOW,
         {"weather": WEATHER}),
        ("booking-multiple-no-weather", by_name["booking — mixed (singles + doubles + free)"],
         NOW, {}),
        ("booking-multiple-next-turn",
         live("booking — Playtomic, 4-court (free/doubles/next/title)"), NOW_INTERCHANGE,
         {"weather": WEATHER}),
        ("signage-2-courts", by_name["signage — 2 courts (court 2 = doubles)"], NOW, {}),
        ("signage-4-courts", by_name["signage — 4 courts (full grid)"], NOW, {}),
        ("draw-error", {"signage-info": None}, NOW, {}),
    ]


def run_type(panel_type: str, update: bool) -> int:
    """Draw every scenario for one panel type; 0 when all goldens match."""
    from datetime import datetime

    image_base_url = _start_image_server()
    os.chdir(REPO_ROOT)
    os.environ["PANEL_TYPE"] = panel_type
    os.environ["TABLEAU_SERVER_BASE_URL"] = image_base_url
    os.environ["IMAGES_CACHE_DIR"] = tempfile.mkdtemp(prefix="7c-golden-cache-")
    sys.path.insert(0, str(REPO_ROOT))

    from PIL import Image, ImageChops

    from sevencourts.render import PANEL_SIZE, render

    golden_dir = GOLDEN_DIR / panel_type.lower()
    actual_dir = ACTUAL_DIR / panel_type.lower()
    failures = []
    names = set()
    for name, panel_info, now, kwargs in scenarios(image_base_url):
        names.add(name + ".png")
        png, _ = render(panel_info, datetime.fromisoformat(now), **kwargs)
        golden = golden_dir / (name + ".png")
        if update:
            golden_dir.mkdir(parents=True, exist_ok=True)
            golden.write_bytes(png)
            continue
        actual = Image.open(BytesIO(png)).convert("RGB")
        if not golden.is_file():
            problem = "no golden"
        else:
            expected = Image.open(golden).convert("RGB")
            if expected.size != actual.size:
                problem = "size %s, golden is %s" % (actual.size, expected.size)
            else:
                box = ImageChops.difference(expected, actual).getbbox()
                problem = None if box is None else "pixels differ within %s" % (box,)
        if problem:
            actual_dir.mkdir(parents=True, exist_ok=True)
            (actual_dir / (name + ".png")).write_bytes(png)
            failures.append("%s/%s: %s" % (panel_type, name, problem))

    stale = sorted(p.name for p in golden_dir.glob("*.png") if p.name not in names)
    if update:
        for name in stale:
            (golden_dir / name).unlink()
        print("%s %dx%d: %d goldens written" % ((panel_type,) + PANEL_SIZE + (len(names),)))
        return 0
    failures += ["%s/%s: golden without a scenario" % (panel_type, n) for n in stale]
    for failure in failures:
        print(failure)
    if failures:
        print("what was drawn instead: %s" % actual_dir)
    else:
        print("%s %dx%d: %d goldens match" % ((panel_type,) + PANEL_SIZE + (len(names),)))
    return 1 if failures else 0


def run_type_in_subprocess(panel_type: str, update: bool = False):
    args = [sys.executable, "-m", "tests.render_goldens", "--type", panel_type]
    return subprocess.run(
        args + (["--update"] if update else []),
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--type", choices=PANEL_TYPES, help="one type, in this process")
    parser.add_argument("--update", action="store_true", help="rewrite the goldens")
    args = parser.parse_args()
    if args.type:
        return run_type(args.type, args.update)
    status = 0
    for panel_type in PANEL_TYPES:
        result = run_type_in_subprocess(panel_type, args.update)
        sys.stdout.write(result.stdout)
        if result.returncode:
            sys.stderr.write(result.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
