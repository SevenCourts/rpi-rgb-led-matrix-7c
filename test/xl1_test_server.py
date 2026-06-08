"""XL1 visual-test fixture server.

Mimics the SevenCourts backend endpoints the panel firmware polls. Cycles a
curated catalogue of XL1 v1 scenarios (scoreboard variants, idle clock/image/
message, signage, standby). Auto-advances on a timer; web UI at `/` exposes
Next / Prev / Pause / Resume / Jump.

Usage:
    python3 test/xl1_test_server.py [--port 8000] [--interval 15] [--no-auto]

Point the panel at the dev workstation:
    TABLEAU_SERVER_BASE_URL=http://192.168.178.175:8000 ./xl1.sh
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parent.parent


def _lan_ip() -> str:
    """Best-effort LAN IP of this host (the one the panels can reach)."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No packet is sent; the kernel just resolves which interface
        # would route to 8.8.8.8 and returns its address.
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


# Used to build absolute URLs for `ebusy-ads` (fetched via gateway.head() which
# does NOT prepend TABLEAU_SERVER_BASE_URL — it expects a full URL).
LAN_BASE_URL = f"http://{_lan_ip()}:8000"


def _synth_image(w: int, h: int, label: str) -> bytes:
    """Generate a vivid test image so size/aspect issues are immediately visible
    on the panel. PNG bytes returned. Cached on first call by (w, h, label)."""
    from io import BytesIO
    from PIL import Image, ImageDraw

    cache_key = (w, h, label)
    cached = _SYNTH_CACHE.get(cache_key)
    if cached is not None:
        return cached
    img = Image.new("RGB", (w, h), (0, 0, 0))
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (
                int(255 * x / max(w - 1, 1)),     # red ramps left→right
                int(255 * y / max(h - 1, 1)),     # green ramps top→bottom
                128,
            )
    # 1-px border so panel-edge alignment is verifiable
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w - 1, h - 1], outline=(255, 255, 255))
    # Crosshair through the center
    draw.line([(0, h // 2), (w - 1, h // 2)], fill=(255, 255, 255))
    draw.line([(w // 2, 0), (w // 2, h - 1)], fill=(255, 255, 255))
    # Size label, top-left
    draw.text((3, 2), label, fill=(255, 255, 255))
    buf = BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    _SYNTH_CACHE[cache_key] = data
    return data


_SYNTH_CACHE: Dict[tuple, bytes] = {}


# 320×96 tile of 27×18 flags with 1-px black gutters between cells.
# 11 cols × 5 rows = 55 flags per page → 3 pages cover all 156.
_FLAG_TILE_W, _FLAG_TILE_H = 27, 18
_FLAG_STRIDE_X = _FLAG_TILE_W + 1  # 28
_FLAG_STRIDE_Y = _FLAG_TILE_H + 1  # 19
_FLAG_COLS = 11   # 11 * 28 - 1 = 307 px wide, 13 px right margin
_FLAG_ROWS = 5    #  5 * 19 - 1 =  94 px tall,  2 px bottom margin
_FLAGS_PER_PAGE = _FLAG_COLS * _FLAG_ROWS


def _synth_flags_page(page: int) -> bytes:
    """Tile 55 27×18 flags into a 320×96 panel image. `page` is 1-indexed.

    Reads from `images/flags_27x18/`. Pages are taken in sorted order so the
    same page always shows the same flags."""
    from io import BytesIO
    from PIL import Image as PILImage

    cache_key = ("flags-page", page)
    cached = _SYNTH_CACHE.get(cache_key)
    if cached is not None:
        return cached

    flags_dir = REPO_ROOT / "images" / "flags_27x18"
    all_flags = sorted(p for p in flags_dir.glob("*.png"))
    start = (page - 1) * _FLAGS_PER_PAGE
    chunk = all_flags[start:start + _FLAGS_PER_PAGE]

    canvas = PILImage.new("RGB", (320, 96), (0, 0, 0))
    for i, path in enumerate(chunk):
        col, row = i % _FLAG_COLS, i // _FLAG_COLS
        x = col * _FLAG_STRIDE_X
        y = row * _FLAG_STRIDE_Y
        flag = PILImage.open(path).convert("RGB")
        canvas.paste(flag, (x, y))

    buf = BytesIO()
    canvas.save(buf, format="PNG")
    data = buf.getvalue()
    _SYNTH_CACHE[cache_key] = data
    return data


def _flag_page_count() -> int:
    flags_dir = REPO_ROOT / "images" / "flags_27x18"
    if not flags_dir.exists():
        return 0
    n = len(list(flags_dir.glob("*.png")))
    return (n + _FLAGS_PER_PAGE - 1) // _FLAGS_PER_PAGE


# --- Fixture catalogue --------------------------------------------------------

# Flag codes used in fixtures map to filenames under images/flags/<name>.png.
# Restricted set during the hand-drawn-flag rollout: the redrawn flags we want
# to eyeball + a few emblem-bearing ones to exercise the load path.
_FLAGS = {
    "US": "usa",
    "DE": "germany",
    "CH": "switzerland",
    "ES": "spain",
    "GB": "great britain",
    "SE": "sweden",
    "GR": "greece",
    "AU": "australia",
    # Emblem extras
    "BR": "brazil",
    "MX": "mexico",
    "AR": "argentina",
}

# When True, drop the dedicated flag-page demo fixtures ("flags — page N") while
# keeping everything else (scoreboards, signage, clocks, messages, images,
# bookings, standby, ebusy-ads). Toggle off to include the flag pages too.
EXCLUDE_FLAGS_DEMO = True


def _player(name: str, flag: str = "DE") -> Dict[str, Any]:
    # Scoreboard reads `lastname` / `firstname`; signage reads `name`. Provide all.
    return {
        "name": name,
        "lastname": name,
        "firstname": "",
        "flag": _FLAGS.get(flag, flag),
    }


def _team(p1: Dict[str, Any], p2: Optional[Dict[str, Any]] = None, *,
          serves: bool = False, set_scores=None, game_score: str = "",
          name: Optional[str] = None) -> Dict[str, Any]:
    return {
        "name": name,
        "p1": p1,
        "p2": p2,
        "serves": serves,
        "setScores": set_scores or [],
        "gameScore": game_score,
    }


def _scoreboard(team1, team2, *, match_result: Optional[str] = None,
                is_total_points: bool = False,
                hide_service: bool = False,
                is_team_event: bool = False) -> Dict[str, Any]:
    is_doubles = (team1.get("p2") is not None) or (team2.get("p2") is not None)
    return {
        "team1": team1,
        "team2": team2,
        "matchResult": match_result,
        "isTotalPointsMatch": is_total_points,
        "hideServiceIndicator": hide_service,
        "isDoubles": is_doubles,
        "isTeamEvent": is_team_event,
    }


def _signage_team(p1: Dict[str, Any], p2: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"p1": p1, "p2": p2}


def _signage_match_court(name, team1, team2, *,
                         score_sets=None, score_game=("", ""),
                         is_serving_t1: bool = False,
                         match_status: Optional[str] = None) -> Dict[str, Any]:
    """Signage uses a different schema than scoreboard:
    `score-sets` is a list of [t1, t2] pairs and `score-game` is a [t1, t2] pair."""
    return {
        "name": name,
        "team1": team1,
        "team2": team2,
        "score-sets": score_sets or [],
        "score-game": list(score_game),
        "is-serving-t1": is_serving_t1,
        "match-status": match_status,
    }


def _idle(**kw) -> Dict[str, Any]:
    base = {"timezone": "Europe/Berlin"}
    base.update(kw)
    return {"idle-info": base}


def _signage_court(name, team1, team2, *, status: Optional[str] = None):
    court = {"name": name, "team1": team1, "team2": team2}
    if status is not None:
        court["status"] = status
    return court


def _signage(*courts) -> Dict[str, Any]:
    return {"signage-info": {"courts": list(courts)}}


# --- eBusy (court booking) helpers --------------------------------------------

# All booking fixtures share a fixed "now" so the past/current/next slots
# resolve consistently regardless of when the test server is launched.
_EBUSY_NOW = "2026-05-25T14:30:00+02:00"


def _bp(first: str, last: str) -> Dict[str, str]:
    return {"firstname": first, "lastname": last}


def _bslot(start: str, end: str, *, text: str = "",
           p1=None, p2=None, p3=None, p4=None,
           blocking: bool = False) -> Optional[Dict[str, Any]]:
    slot: Dict[str, Any] = {
        "start-date": f"2026-05-25T{start}+02:00",
        "end-date":   f"2026-05-25T{end}+02:00",
        "display-text": text,
        "p1": p1, "p2": p2, "p3": p3, "p4": p4,
    }
    if blocking:
        slot["type"] = "BLOCKING"
    return slot


def _bcourt(cid: int, name: str, *, past=None, current=None, next=None,
            short_name: Optional[str] = None) -> Dict[str, Any]:
    return {
        "court": {
            "id": cid,
            "name": name,
            "shortName": short_name or f"P{cid}",
        },
        "past": past, "current": current, "next": next,
    }


def _booking(style: str, *courts) -> Dict[str, Any]:
    return {"booking": {
        "style": style,
        "_dev_timestamp": _EBUSY_NOW,
        "courts": list(courts),
    }}


def _ebusy_ads(url: str) -> Dict[str, Any]:
    return {"ebusy-ads": {"url": url}}


# Realistic court samples reused across style fixtures.
def _court_busy_singles(cid: int, name: str) -> Dict[str, Any]:
    return _bcourt(cid, name,
        current=_bslot("13:00:00", "14:30:00", p1=_bp("Roger", "Federer")),
        next=_bslot("14:30:00", "16:00:00", text="H1 Training",
                    p1=_bp("Rafael", "Nadal")),
    )


def _court_busy_doubles(cid: int, name: str) -> Dict[str, Any]:
    return _bcourt(cid, name,
        current=_bslot("14:00:00", "15:30:00",
                       p1=_bp("Ilya", "Shinkarenko"),
                       p2=_bp("Roman", "Churkov"),
                       p3=_bp("Mario", "Lopez"),
                       p4=_bp("Alex", "Drachnev")),
        next=_bslot("15:30:00", "17:00:00", text="Verbandspiel",
                    p1=_bp("Novak", "Djokovic")),
    )


def _court_blocking(cid: int, name: str) -> Dict[str, Any]:
    return _bcourt(cid, name,
        current=_bslot("13:00:00", "18:00:00", text="Maintenance",
                       blocking=True),
    )


def _court_empty(cid: int, name: str) -> Dict[str, Any]:
    return _bcourt(cid, name)


FIXTURES: List[Dict[str, Any]] = [
    # --- Standby / idle states -----------------------------------------------
    {"name": "standby", "info": {"standby": True}},

    # --- Clock variants (font-1 = 7-segment) ---------------------------------
    {"name": "clock — default (clock:true)", "info": _idle(clock=True)},
    {"name": "clock — font-1 large center/center",
     "info": _idle(clock={"font": "font-1", "size": "large",
                          "h-align": "center", "v-align": "center"})},
    {"name": "clock — font-1 medium center/center",
     "info": _idle(clock={"font": "font-1", "size": "medium",
                          "h-align": "center", "v-align": "center"})},
    {"name": "clock — font-1 small center/center",
     "info": _idle(clock={"font": "font-1", "size": "small",
                          "h-align": "center", "v-align": "center"})},
    {"name": "clock — font-2 (Spleen) large center/center",
     "info": _idle(clock={"font": "font-2", "size": "large",
                          "h-align": "center", "v-align": "center"})},
    {"name": "clock — font-1 large right/bottom",
     "info": _idle(clock={"font": "font-1", "size": "large",
                          "h-align": "right", "v-align": "bottom"})},

    # --- Message variants ----------------------------------------------------
    {"name": "message — short single line", "info": _idle(message="WELCOME")},
    {"name": "message — long single line",
     "info": _idle(message="COURT MAINTENANCE THIS AFTERNOON")},
    {"name": "message — two lines",
     "info": _idle(message="MATCH STARTS\nIN 10 MINUTES")},
    {"name": "message — with clock strip",
     "info": _idle(message="WELCOME", clock=True)},

    # --- Image variants ------------------------------------------------------
    {"name": "image — uploaded", "info": _idle(**{"image-url": "panel-image/test-xl1.png"})},
    {"name": "image — uploaded with clock",
     "info": _idle(clock=True, **{"image-url": "panel-image/test-xl1-portrait.png"})},
    {"name": "image — preset (sevencourts logo)",
     "info": _idle(**{"image-preset": "7C/sevencourts_7c_64x32.png"})},

    # --- Scoreboard singles --------------------------------------------------
    {"name": "scoreboard — singles, 0 sets",
     "info": _scoreboard(
         _team(_player("FEDERER", "CH"), serves=True, game_score="15"),
         _team(_player("NADAL", "ES"), game_score="0"),
     )},
    {"name": "scoreboard — singles, 1 set in progress",
     "info": _scoreboard(
         _team(_player("FEDERER", "CH"), serves=True, set_scores=[3], game_score="30"),
         _team(_player("NADAL", "ES"), set_scores=[2], game_score="15"),
     )},
    {"name": "scoreboard — singles, 3 sets in progress",
     "info": _scoreboard(
         _team(_player("FEDERER", "CH"), serves=False, set_scores=[6, 7, 3], game_score="40"),
         _team(_player("NADAL", "ES"), serves=True, set_scores=[4, 5, 6], game_score="A"),
     )},
    {"name": "scoreboard — singles, long names (font fallback)",
     "info": _scoreboard(
         _team(_player("STEFANSSON", "SE"), serves=True, set_scores=[6, 7], game_score="15"),
         _team(_player("PAPADOPOULOS", "GR"), set_scores=[4, 6], game_score="40"),
     )},
    {"name": "scoreboard — singles, T1 game point (Ad)",
     "info": _scoreboard(
         _team(_player("KYRGIOS", "AU"), serves=True, set_scores=[6, 7, 3], game_score="A"),
         _team(_player("ALCARAZ", "ES"), set_scores=[4, 5, 6], game_score="40"),
     )},
    {"name": "scoreboard — singles, T2 won",
     "info": _scoreboard(
         _team(_player("FEDERER", "CH"), set_scores=[6, 4, 3], game_score=""),
         _team(_player("NADAL", "ES"), set_scores=[4, 6, 6], game_score=""),
         match_result="T2_WON",
     )},
    {"name": "scoreboard — match tiebreak (10-pt)",
     "info": _scoreboard(
         _team(_player("ZVEREV", "DE"), serves=True, set_scores=[6, 3, 7], game_score="8"),
         _team(_player("FRITZ", "US"), set_scores=[4, 6, 5], game_score="6"),
     )},
    # Finished match-tie-break: deciding set score >= 10 moves into the big
    # game-score slot (winner white / loser grey) and the cup shrinks to tuck
    # left of the 2-digit score. Exercises the won/lost color-shift fix.
    {"name": "scoreboard — match tiebreak FINISHED, T1 won (10-8)",
     "info": _scoreboard(
         _team(_player("ZVEREV", "DE"), set_scores=[6, 3, 10], game_score=""),
         _team(_player("FRITZ", "US"), set_scores=[4, 6, 8], game_score=""),
         match_result="T1_WON",
     )},
    {"name": "scoreboard — match tiebreak FINISHED, T2 won (7-10)",
     "info": _scoreboard(
         _team(_player("FEDERER", "CH"), set_scores=[4, 6, 7], game_score=""),
         _team(_player("NADAL", "ES"), set_scores=[6, 4, 10], game_score=""),
         match_result="T2_WON",
     )},
    {"name": "scoreboard — Americano (total points)",
     "info": _scoreboard(
         _team(_player("BERG", "SE"), serves=True, game_score="21"),
         _team(_player("TSITSIPAS", "GR"), game_score="17"),
         is_total_points=True,
     )},
    {"name": "scoreboard — singles, emblem flags",
     "info": _scoreboard(
         _team(_player("ALCARAZ", "ES"), serves=True, set_scores=[6, 4], game_score="40"),
         _team(_player("SILVA", "BR"), set_scores=[4, 6], game_score="30"),
     )},
    {"name": "scoreboard — singles, emblem flags 2",
     "info": _scoreboard(
         _team(_player("MARTINEZ", "MX"), serves=True, set_scores=[7], game_score="0"),
         _team(_player("GONZALEZ", "AR"), set_scores=[5], game_score="15"),
     )},

    # --- Scoreboard doubles --------------------------------------------------
    {"name": "scoreboard — doubles, 3 sets",
     "info": _scoreboard(
         _team(_player("MUELLER", "DE"), _player("SCHMID", "CH"),
               serves=True, set_scores=[6, 4, 3], game_score="40"),
         _team(_player("PAPPAS", "GR"), _player("BERG", "SE"),
               set_scores=[4, 6, 6], game_score="30"),
     )},
    {"name": "scoreboard — doubles, long names",
     "info": _scoreboard(
         _team(_player("STEFANSSON", "SE"), _player("SKUPSKI", "GB"),
               serves=True, set_scores=[7, 6], game_score="15"),
         _team(_player("KUBLER", "AU"), _player("HIJIKATA", "AU"),
               set_scores=[5, 7], game_score="40"),
     )},
    # Exercises the `same_flags_in_teams` branch in view_scoreboard:
    # both players in each team share a flag → one large flag is rendered
    # per team via `_draw_singles_flags`, not 4 small flags.
    {"name": "scoreboard — doubles, team flags (same nationality)",
     "info": _scoreboard(
         _team(_player("MUELLER", "DE"), _player("SCHMID", "DE"),
               serves=True, set_scores=[6, 4, 3], game_score="40"),
         _team(_player("LOPEZ", "ES"), _player("GARCIA", "ES"),
               set_scores=[4, 6, 6], game_score="30"),
     )},

    # --- eBusy / booking -----------------------------------------------------
    # 5 styles × 4 court counts + edge cases (blocking, empty, ads).
    # Court samples are sharable across styles since the schema is the same.
] + [
    {"name": f"booking — {style}, {n}-court",
     "info": _booking(style, *[_court_busy_singles(i + 1, f"Platz {i + 1}")
                                for i in range(n)])}
    for style in ("SevenCourts", "SV1845", "TABB", "MatchCenter", "TC Heidelberg")
    for n in (1, 2, 3, 4)
] + [
    # Edge cases on the SevenCourts style.
    {"name": "booking — empty (no slots)",
     "info": _booking("SevenCourts",
                      _court_empty(1, "Platz 1"),
                      _court_empty(2, "Platz 2"))},
    {"name": "booking — BLOCKING (maintenance)",
     "info": _booking("SevenCourts",
                      _court_blocking(1, "Platz 1"))},
    {"name": "booking — doubles match in progress",
     "info": _booking("SevenCourts",
                      _court_busy_doubles(1, "Center Court"))},
    {"name": "booking — mixed (singles + doubles + free)",
     "info": _booking("SevenCourts",
                      _court_busy_singles(1, "Platz 1"),
                      _court_busy_doubles(2, "Platz 2"),
                      _court_empty(3, "Platz 3"))},
    {"name": "ebusy-ads — promotional image",
     # Full URL is required: draw_ads → fetch_by_url_with_cache → gateway.head
     # passes the URL through without prepending TABLEAU_SERVER_BASE_URL.
     "info": _ebusy_ads(f"{LAN_BASE_URL}/panel-image/test-xl1.png")},
] + [
    # Tiled flag pages — 55 27×18 flags per 320×96 panel, ~3 pages total.
    {"name": f"flags — page {p}/{_flag_page_count()}",
     "info": _idle(**{"image-url": f"panel-image/flags-page-{p}.png"})}
    for p in range(1, _flag_page_count() + 1)
] + [
] + [

    # --- Signage -------------------------------------------------------------
    # Signage uses score-sets / score-game / is-serving-t1 / match-status
    # (different schema from the scoreboard view).
    {"name": "signage — 1 court",
     "info": _signage(
         _signage_match_court("Court 1",
             _signage_team(_player("FEDERER", "CH")),
             _signage_team(_player("NADAL", "ES")),
             score_sets=[[6, 4], [7, 5]],
             score_game=("15", "40"),
             is_serving_t1=True,
             match_status="14:00"),
     )},
    {"name": "signage — 2 courts (court 2 = doubles)",
     "info": _signage(
         _signage_match_court("Court 1",
             _signage_team(_player("FEDERER", "CH")),
             _signage_team(_player("NADAL", "ES")),
             score_sets=[[6, 4], [7, 5]],
             score_game=("15", "40"),
             is_serving_t1=True,
             match_status="14:00"),
         _signage_match_court("Court 2",
             _signage_team(_player("KYRGIOS", "AU"), _player("BERG", "SE")),
             _signage_team(_player("ALCARAZ", "ES"), _player("NADAL", "ES")),
             score_sets=[[3, 6], [6, 4]],
             score_game=("40", "30"),
             is_serving_t1=False,
             match_status="14:30"),
     )},
    {"name": "signage — 4 courts (full grid)",
     "info": _signage(
         _signage_match_court("Court 1",
             _signage_team(_player("FEDERER", "CH")),
             _signage_team(_player("NADAL", "ES")),
             score_sets=[[6, 4], [7, 5]],
             score_game=("15", "40"),
             is_serving_t1=True,
             match_status="14:00"),
         _signage_match_court("Court 2",
             _signage_team(_player("KYRGIOS", "AU"), _player("SKUPSKI", "GB")),
             _signage_team(_player("ALCARAZ", "ES"), _player("NADAL", "ES")),
             score_sets=[[3, 6], [6, 4], [7, 5]],
             score_game=("40", "30"),
             is_serving_t1=False,
             match_status="14:30"),
         _signage_match_court("Court 3",
             _signage_team(_player("ZVEREV", "DE")),
             _signage_team(_player("FRITZ", "US")),
             score_sets=[[6, 4], [3, 6], [7, 5]],
             score_game=("A", "40"),
             is_serving_t1=True,
             match_status="Walko."),
         _signage_match_court("Court 4",
             _signage_team(_player("BERG", "SE")),
             _signage_team(_player("TSITSIPAS", "GR")),
             score_sets=[[6, 3], [4, 6]],
             score_game=("0", "30"),
             is_serving_t1=False,
             match_status="15:45"),
     )},
]


# Drop the now-unused legacy helper to avoid confusion.
del _signage_court


if EXCLUDE_FLAGS_DEMO:
    # Drop the dedicated tiled flag-page demo ("flags — page N"); keep every
    # other scenario (scoreboards, signage, clocks, messages, images, bookings,
    # standby, ebusy-ads).
    FIXTURES = [
        f for f in FIXTURES
        if not f["name"].startswith("flags")
    ]


# --- Server state -------------------------------------------------------------

class State:
    def __init__(self, interval: float, auto: bool):
        self.lock = threading.Lock()
        self.index = 0
        self.interval = interval
        self.auto = auto
        self.last_change = time.monotonic()

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "index": self.index,
                "name": FIXTURES[self.index]["name"],
                "auto": self.auto,
                "interval": self.interval,
                "count": len(FIXTURES),
            }

    def current_info(self) -> Dict[str, Any]:
        with self.lock:
            return FIXTURES[self.index]["info"]

    def next(self):
        with self.lock:
            self.index = (self.index + 1) % len(FIXTURES)
            self.last_change = time.monotonic()

    def prev(self):
        with self.lock:
            self.index = (self.index - 1) % len(FIXTURES)
            self.last_change = time.monotonic()

    def jump(self, i: int):
        with self.lock:
            self.index = i % len(FIXTURES)
            self.last_change = time.monotonic()

    def set_auto(self, auto: bool):
        with self.lock:
            self.auto = auto
            self.last_change = time.monotonic()


def _auto_advance_loop(state: State):
    while True:
        time.sleep(0.5)
        with state.lock:
            if state.auto and (time.monotonic() - state.last_change) >= state.interval:
                state.index = (state.index + 1) % len(FIXTURES)
                state.last_change = time.monotonic()


# --- HTTP handler -------------------------------------------------------------

STATE: State = None  # set at startup


class Handler(BaseHTTPRequestHandler):
    server_version = "SevenCourtsLEDPanelsTestServer/0.1"

    def log_message(self, fmt, *args):
        # Keep server output tidy; uncomment for verbose access logs.
        pass

    def _send_json(self, payload: Any, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, status: int = 200, ctype: str = "text/plain"):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_image_for_path(self, request_path: str, *, head_only: bool = False):
        """Serve a synthesized PNG sized appropriately for the requested fixture."""
        # /panel-image/flags-page-N.png → 320×96 grid of native-size flags.
        import re
        m = re.search(r"flags-page-(\d+)\.png$", request_path)
        if m:
            data = _synth_flags_page(int(m.group(1)))
        elif request_path.endswith("test-xl1-portrait.png"):
            # Narrower than the smallest W_LOGO_WITH_CLOCK (M1=120) so the
            # image-with-clock layout fits side-by-side on every panel type.
            data = _synth_image(90, 96, "90x96")
        else:
            data = _synth_image(320, 96, "320x96 XL1 TEST")
        etag = f'"{len(data)}-{request_path}"'
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("ETag", etag)
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    # --- routing ----------------------------------------------------------

    def do_POST(self):
        if self.path.rstrip("/") == "/panels":
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)  # discard body
            self._send_json({"id": "test-xl1"})
            return
        self._send_text("not found", 404)

    def do_HEAD(self):
        if self.path.startswith("/panel-image/") or self.path.startswith("/images/"):
            self._send_image_for_path(self.path, head_only=True)
            return
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        query = {}
        if "?" in self.path:
            for kv in self.path.split("?", 1)[1].split("&"):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    query[k] = v

        if path == "/":
            self._send_text(_render_ui(STATE.snapshot()), ctype="text/html")
            return
        if path == "/state":
            self._send_json(STATE.snapshot())
            return
        if path == "/control":
            cmd = query.get("cmd", "")
            if cmd == "next":
                STATE.next()
            elif cmd == "prev":
                STATE.prev()
            elif cmd == "jump":
                try:
                    STATE.jump(int(query.get("i", "0")))
                except ValueError:
                    pass
            elif cmd == "pause":
                STATE.set_auto(False)
            elif cmd == "resume":
                STATE.set_auto(True)
            self._send_json(STATE.snapshot())
            return
        if path == "/healthz":
            self._send_text("ok")
            return

        # /panels/<id>/match
        if path.startswith("/panels/") and path.endswith("/match"):
            self._send_json(STATE.current_info())
            return

        # Any image path the firmware tries to fetch — return the default test image.
        if path.startswith("/panel-image/") or path.startswith("/images/"):
            self._send_image_for_path(self.path)
            return

        self._send_text("not found", 404)


# --- Web UI -------------------------------------------------------------------

# Emulator browser-adapter ports for the embedded live previews. Start the
# emulators (one per panel type) on these ports and they appear in the UI.
# See `.runtime/emu/` working dirs / `make-emulators` helper.
EMULATORS = [
    {"key": "m1", "label": "M1 — 192×64", "port": 8888, "w": 768, "h": 256},
    {"key": "l1", "label": "L1 — 192×96", "port": 8889, "w": 768, "h": 384},
    {"key": "xl1", "label": "XL1 — 320×96", "port": 8890, "w": 1280, "h": 384},
]


def _render_ui(snap: Dict[str, Any]) -> str:
    rows = []
    for i, fx in enumerate(FIXTURES):
        sel = " selected" if i == snap["index"] else ""
        rows.append(f'<option value="{i}"{sel}>{i:02d} — {fx["name"]}</option>')

    # Each emulator preview is rendered at its native matrix size and scaled
    # down with a CSS transform so all three fit in the column. The iframe src
    # is set client-side from location.hostname so the previews work whether the
    # page is opened via localhost or the workstation's LAN IP.
    #
    # The emulator page wraps its canvas in an 8px body margin + a 1px image
    # border, so the iframe must be 18px larger than the canvas in each axis to
    # show the whole canvas without clipping; `scrolling=no` removes the
    # cross-origin scrollbars the overflow would otherwise add.
    scale = 0.5
    chrome = 18
    emu_blocks = []
    for e in EMULATORS:
        fw, fh = e["w"] + chrome, e["h"] + chrome
        emu_blocks.append(f"""
    <div class="emu">
      <div class="label">{e['label']} (:{e['port']})</div>
      <div class="frame" style="width:{int(fw*scale)}px;height:{int(fh*scale)}px;">
        <iframe id="emu-{e['key']}" data-port="{e['port']}" scrolling="no"
                style="width:{fw}px;height:{fh}px;transform:scale({scale});"></iframe>
      </div>
    </div>""")

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>SevenCourts LED panels test server</title>
<style>
body {{ font-family: sans-serif; margin: 0; background: #111; color: #eee; }}
header {{ padding: 10px 18px; background: #1b1b1f; border-bottom: 1px solid #333; }}
h1 {{ font-size: 1.25em; margin: 0; }}
.wrap {{ display: flex; flex-wrap: wrap; gap: 18px; padding: 18px; align-items: flex-start; }}
.control {{ flex: 0 0 320px; }}
.current {{ background: #1d2233; padding: 1em; border-radius: 6px; margin: 0 0 1em; }}
.current b {{ font-size: 1.2em; }}
button {{ font-size: .95em; padding: .5em .9em; margin: 0 .4em .4em 0; cursor: pointer; }}
select {{ font-size: 1em; padding: .3em; width: 100%; }}
.muted {{ color: #888; font-size: .85em; }}
.emus {{ display: flex; flex-direction: column; gap: 16px; }}
.emu .label {{ font-size: .85em; color: #9cf; margin-bottom: 4px; }}
.emu .frame {{ overflow: hidden; background: #000; border: 1px solid #333; border-radius: 6px; }}
.emu iframe {{ border: 0; transform-origin: top left; background: #000; display: block; }}
</style>
<script>
function applyState(s) {{
  document.getElementById('idx').textContent = s.index.toString().padStart(2,'0');
  document.getElementById('name').textContent = s.name;
  document.getElementById('auto').textContent = s.auto ? 'auto ('+s.interval+'s)' : 'paused';
  document.getElementById('sel').value = s.index;
}}
async function ctrl(cmd, extra='') {{
  const r = await fetch('/control?cmd=' + cmd + extra);
  applyState(await r.json());
}}
async function refresh() {{
  const r = await fetch('/state');
  applyState(await r.json());
}}
// Point each embedded emulator at the same host the page was loaded from.
window.addEventListener('DOMContentLoaded', () => {{
  document.querySelectorAll('iframe[data-port]').forEach(f => {{
    f.src = location.protocol + '//' + location.hostname + ':' + f.dataset.port + '/';
  }});
}});
setInterval(refresh, 1000);
</script>
</head><body>
<header><h1>SevenCourts LED panels test server</h1></header>
<div class="wrap">
  <div class="control">
    <div class="current">
      <div class="muted">current fixture (<span id="auto">{('auto ('+str(snap['interval'])+'s)') if snap['auto'] else 'paused'}</span>)</div>
      <b><span id="idx">{snap['index']:02d}</span> — <span id="name">{snap['name']}</span></b>
    </div>
    <p>
      <button onclick="ctrl('prev')">⏮ Prev</button>
      <button onclick="ctrl('next')">Next ⏭</button>
      <button onclick="ctrl('pause')">⏸ Pause</button>
      <button onclick="ctrl('resume')">▶ Resume</button>
    </p>
    <p class="muted">Jump to:</p>
    <select id="sel" onchange="ctrl('jump', '&i=' + this.value)">
    {''.join(rows)}
    </select>
    <p class="muted">{snap['count']} fixtures total. Panels poll /panels/&lt;id&gt;/match every ~1s.</p>
  </div>
  <div class="emus">{''.join(emu_blocks)}</div>
</div>
</body></html>
"""


# --- Entry point --------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--interval", type=float, default=3.0,
                        help="auto-advance interval in seconds (default 3)")
    parser.add_argument("--no-auto", action="store_true",
                        help="start paused (use Next/Jump in the web UI)")
    parser.add_argument("--only", default=None,
                        help="restrict to fixtures whose name contains this substring "
                             "(case-insensitive). e.g. --only scoreboard")
    args = parser.parse_args()

    if args.only:
        needle = args.only.lower()
        filtered = [f for f in FIXTURES if needle in f["name"].lower()]
        if not filtered:
            raise SystemExit(f"no fixtures match --only {args.only!r}")
        FIXTURES[:] = filtered

    global STATE
    STATE = State(interval=args.interval, auto=not args.no_auto)

    threading.Thread(target=_auto_advance_loop, args=(STATE,), daemon=True).start()

    httpd = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"SevenCourts LED panels test server on http://0.0.0.0:{args.port}/  ({len(FIXTURES)} fixtures, "
          f"{'auto-cycle' if STATE.auto else 'paused'}, interval={args.interval}s)")
    print(f"Point the panel at: TABLEAU_SERVER_BASE_URL=http://<this-host>:{args.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")


if __name__ == "__main__":
    main()
