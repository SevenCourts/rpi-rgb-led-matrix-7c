"""Pixel mockups of the Playtomic Americano views (led-0jh), drawn with the
firmware's own fonts, text routine and the Padel Club Esslingen style, onto an
in-memory canvas. Not a view yet: the layout code here is the proposal that
led-u9b turns into sevencourts/m1/view_americano*.py.

    # once, from the anonymised 2026-10-15 timeline (outside git):
    USE_RGB_MATRIX_EMULATOR=1 .venv/bin/python tools/americano_mockups.py extract \
        ~/7c-playtomic-snapshots/timeline/c92304b5-70a1-42df-ba37-0a4a5c3e63e3/anon
    # render spec/americano/*.png from spec/americano/mockup-data.json:
    USE_RGB_MATRIX_EMULATOR=1 .venv/bin/python tools/americano_mockups.py render

Run from the repository root (fonts load from relative paths).
"""

import glob
import json
import os
import sys
from datetime import datetime, timedelta

from PIL import Image, ImageDraw

from sevencourts.rgbmatrix import (
    graphics,
    COLOR_BLACK,
    COLOR_GREY_DARK,
    FONT_XS_SPLEEN,
    FONT_S_SPLEEN,
    FONT_M_SPLEEN,
    FONT_L_SPLEEN,
    fill_rect,
    width_in_pixels,
    y_font_offset,
)
from sevencourts.club_styles import style_PadelClubEsslingen as STYLE

SPEC = "spec/americano"
DATA = os.path.join(SPEC, "mockup-data.json")
TZ_OFFSET = timedelta(hours=2)  # Europe/Berlin, summer time on 2026-10-15

C_TEXT = STYLE.ci.c_text  # cream
C_BOX = STYLE.ci.c_bg_1  # green
C_ACCENT = STYLE.ci.c_bg_2  # lime
C_DIM = COLOR_GREY_DARK


# --- canvas -----------------------------------------------------------------


class Canvas:
    """The four members the firmware views use, backed by a PIL image."""

    def __init__(self, w, h):
        self.width, self.height = w, h
        self.img = Image.new("RGB", (w, h))

    def Clear(self):
        self.img.paste((0, 0, 0), (0, 0, self.width, self.height))

    def SetPixel(self, x, y, r, g, b):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.img.putpixel((x, y), (r, g, b))

    def SetImage(self, image, x=0, y=0):
        self.img.paste(image.convert("RGB"), (x, y))

    def save(self, path, dot=6):
        """The native-resolution PNG and an LED-dot rendering next to it."""
        self.img.save(path)
        big = Image.new("RGB", (self.width * dot, self.height * dot), (8, 8, 8))
        d = ImageDraw.Draw(big)
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = self.img.getpixel((x, y))
                if (r, g, b) == (0, 0, 0):
                    r, g, b = 20, 20, 20  # an unlit LED is still visible
                d.ellipse(
                    (x * dot + 1, y * dot + 1, x * dot + dot - 2, y * dot + dot - 2),
                    fill=(r, g, b),
                )
        big.save(path.replace(".png", ".leds.png"))


# --- drawing helpers --------------------------------------------------------


def cap(font):
    return y_font_offset(font) or font.baseline


def text(cnv, x, y_top, s, font, color):
    """Draw s with its cap line at y_top; returns the width."""
    return graphics.DrawText(cnv, font, x, y_top + cap(font), color, s)


def text_in_row(cnv, x, y_row, h_row, s, font, color, right=False):
    """Draw s centred in a row by the font's full height, descenders included."""
    baseline = y_row + (h_row - font.height) // 2 + font.baseline
    if right:
        x -= width_in_pixels(font, s)
    return graphics.DrawText(cnv, font, x, baseline, color, s)


def text_right(cnv, x_right, y_top, s, font, color):
    return text(cnv, x_right - width_in_pixels(font, s), y_top, s, font, color)


def box(cnv, x, y, w, h):
    """The booking views' court-name box: green, rounded, lime underline."""
    fill_rect(cnv, x, y, w, h, C_BOX, round_corners=True)
    graphics.DrawLine(cnv, x + 2, y + h, x + w - 3, y + h, C_ACCENT)


def fit(fonts, s, w):
    """The largest font in which s fits into w pixels, else the smallest."""
    for f in fonts:
        if width_in_pixels(f, s) <= w:
            return f
    return fonts[-1]


def truncate(font, s, w):
    while s and width_in_pixels(font, s) > w:
        s = s[:-1]
    return s


def display_names(state):
    """Full name -> what the panel shows: the first name, plus the surname's
    initial for everyone whose first name another player shares."""
    full = [r["name"] for r in state["leaderboard"]]
    firsts = [n.split()[0] for n in full]
    out = {}
    for n, first in zip(full, firsts):
        rest = n.split()[1:]
        out[n] = f"{first} {rest[0][0]}." if firsts.count(first) > 1 and rest else first
    return out


def team_name(team, names):
    return " & ".join(names.get(p, p.split()[0]) for p in team["players"])


def header(cnv, W, label, elapsed=None, title=None):
    """12 px: label in the booking views' court box, then elapsed time in
    lime, the tournament name, and the clock at the right."""
    f = FONT_S_SPLEEN
    w_box = width_in_pixels(f, label) + 6
    box(cnv, 0, 0, w_box, 11)
    text(cnv, 3, 2, label, f, C_TEXT)
    x = w_box + 6
    if elapsed is not None:
        x += text(cnv, x, 2, elapsed, f, C_ACCENT) + 8
    if title:
        text(cnv, x, 2, truncate(f, title, W - x - 36), f, C_TEXT)


def clock(cnv, W, state):
    text_right(cnv, W, 2, state["clock"], FONT_S_SPLEEN, C_TEXT)


def leaderboard(cnv, x0, y0, W, state, page, per_page=8):
    """Position, name, matches, wins, points; Spleen 5x8, 9 px rows, the top
    three in lime. No ranking before the first result."""
    fs = FONT_XS_SPLEEN
    names = display_names(state)
    rows = state["leaderboard"]
    started = any(r["matches"] for r in rows)
    if not started:
        rows = sorted(rows, key=lambda r: r["name"])
    pages = (len(rows) + per_page - 1) // per_page
    for title, cx, right in (("#", x0 + 10, True), ("Name", x0 + 14, False),
                             ("M", W - 38, True), ("W", W - 22, True), ("Pts", W, True)):
        (text_right if right else text)(cnv, cx, y0, title, fs, C_ACCENT)
    if pages > 1:
        text(cnv, x0 + 44, y0, f"{page + 1}/{pages}", fs, C_DIM)
    for k, r in enumerate(rows[page * per_page:(page + 1) * per_page]):
        y = y0 + 10 + k * 9
        c = C_ACCENT if started and r["position"] <= 3 else C_TEXT
        text_right(cnv, x0 + 10, y, str(r["position"]) if started else "-", fs, c)
        text(cnv, x0 + 14, y, truncate(fs, names[r["name"]], W - 40 - x0 - 14), fs, C_TEXT)
        text_right(cnv, W - 38, y, str(r["matches"]), fs, C_DIM)
        text_right(cnv, W - 22, y, str(r["wins"]), fs, C_DIM)
        text_right(cnv, W, y, str(r["points"]), fs, C_TEXT)


# --- M1: one court ----------------------------------------------------------


def m1_court(state, court, show_result=True):
    """192x64. Header: round, minutes since the round appeared, clock.
    Body: the two teams, one per line, the score right-aligned once entered."""
    W, H = 192, 64
    cnv = Canvas(W, H)
    names = display_names(state)
    m = next(x for x in state["matchups"] if x["court"] == court)
    header(cnv, W, f"Round {state['round']}", f"{state['round_elapsed_min']} min")
    clock(cnv, W, state)

    # teams: two rows of 24 px from y=14
    result = m.get("result") if show_result else None
    w_score = width_in_pixels(FONT_L_SPLEEN, "00") + 4 if result else 0
    w_names = W - w_score
    team_names = [team_name(t, names) for t in m["teams"]]
    # Both rows in the same font, the largest that fits the longer name.
    font = fit([FONT_L_SPLEEN, FONT_M_SPLEEN, FONT_S_SPLEEN], max(team_names, key=len), w_names)
    for i, name in enumerate(team_names):
        y_row = 14 + i * 26
        text_in_row(cnv, 0, y_row, 24, truncate(font, name, w_names), font, C_TEXT)
        if result:
            won = result[i] > result[1 - i]
            text_in_row(cnv, W, y_row, 24, str(result[i]), FONT_L_SPLEEN,
                        C_ACCENT if won else C_DIM, right=True)
    graphics.DrawLine(cnv, 0, 39, W - 1, 39, C_BOX)
    return cnv


def m1_final(state):
    """192x64, once the organiser presses Finish: the top three."""
    W, H = 192, 64
    cnv = Canvas(W, H)
    names = display_names(state)
    header(cnv, W, "Final results")
    clock(cnv, W, state)
    f = FONT_M_SPLEEN
    for k, r in enumerate(state["leaderboard"][:3]):
        y_row = 14 + k * 17
        text_in_row(cnv, 0, y_row, 16, str(r["position"]), f, C_ACCENT)
        text_in_row(cnv, 14, y_row, 16, truncate(f, names[r["name"]], W - 14 - 60), f, C_TEXT)
        text_in_row(cnv, W, y_row, 16, f"{r['points']} pts", f, C_ACCENT if k == 0 else C_TEXT, right=True)
    return cnv


# --- XL1: overview ----------------------------------------------------------

X_SPLIT = 186


def xl1_overview(state, page, per_page=8):
    """320x96. Header across the panel; current round left, one row per court
    (three courts); leaderboard right, paged."""
    W, H = 320, 96
    cnv = Canvas(W, H)
    f = FONT_S_SPLEEN
    names = display_names(state)
    header(cnv, W, f"Round {state['round']}", f"{state['round_elapsed_min']} min", state["name"])
    clock(cnv, W, state)

    fs = FONT_XS_SPLEEN
    w_court = width_in_pixels(fs, "Double 3") + 4
    for i, m in enumerate(state["matchups"][:3]):
        y = 15 + i * 27
        box(cnv, 0, y, w_court, 25)
        court = m["court"].split()
        text(cnv, 2, y + 3, court[0], fs, C_TEXT)
        text(cnv, 2, y + 14, " ".join(court[1:]), FONT_S_SPLEEN, C_ACCENT)
        x_names = w_court + 4
        result = m.get("result")
        w_names = X_SPLIT - x_names - (16 if result else 4)
        for j, t in enumerate(m["teams"]):
            yy = y + 1 + j * 12
            text(cnv, x_names, yy, truncate(f, team_name(t, names), w_names), f, C_TEXT)
            if result:
                won = result[j] > result[1 - j]
                text_right(cnv, X_SPLIT - 4, yy, str(result[j]), f, C_ACCENT if won else C_DIM)

    graphics.DrawLine(cnv, X_SPLIT, 15, X_SPLIT, H - 1, C_BOX)
    leaderboard(cnv, X_SPLIT + 4, 15, W, state, page, per_page)
    return cnv


def xl1_final(state, page, per_page=8):
    """320x96, once the organiser presses Finish: a podium left (2nd, 1st,
    3rd, as Manager draws it), the final standings right, paged."""
    W, H = 320, 96
    cnv = Canvas(W, H)
    names = display_names(state)
    header(cnv, W, "Final", title=state["name"])
    clock(cnv, W, state)

    top = state["leaderboard"][:3]
    w_col = (X_SPLIT - 8) // 3
    heights = {1: 40, 2: 30, 3: 22}
    for r, col in zip(top, (1, 0, 2)):
        x = 2 + col * (w_col + 2)
        h = heights[r["position"]]
        y = H - h
        box(cnv, x, y, w_col, h - 1)
        f_pos = FONT_L_SPLEEN if r["position"] == 1 else FONT_M_SPLEEN
        pos = str(r["position"])
        text(cnv, x + (w_col - width_in_pixels(f_pos, pos)) // 2, y + 3, pos, f_pos, C_ACCENT)
        # name, then points, above the block
        pts = f"{r['points']} pts"
        text(cnv, x + (w_col - width_in_pixels(FONT_XS_SPLEEN, pts)) // 2, y - 9, pts,
             FONT_XS_SPLEEN, C_ACCENT if r["position"] == 1 else C_DIM)
        name = truncate(FONT_S_SPLEEN, names[r["name"]], w_col)
        text(cnv, x + (w_col - width_in_pixels(FONT_S_SPLEEN, name)) // 2, y - 21, name,
             FONT_S_SPLEEN, C_TEXT)

    graphics.DrawLine(cnv, X_SPLIT, 15, X_SPLIT, H - 1, C_BOX)
    leaderboard(cnv, X_SPLIT + 4, 15, W, state, page, per_page)
    return cnv


# --- data -------------------------------------------------------------------


def extract(timeline_dir):
    """Turn the anonymised timeline into the small, id-free states the mockups
    need: per 5-minute slot, the current round's matchups and the leaderboard.
    Once the tournament is FINISHED, Playtomic's final_standings decide the
    order (they break full ties our points-then-wins order cannot)."""
    snaps = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(timeline_dir, "*.json")))]
    first_seen = {}
    states = []
    for s in snaps:
        op = s["operative"]
        t = datetime.strptime(s["t"], "%Y-%m-%dT%H:%M:%SZ")
        for n in range(1, len(op["rounds"]) + 1):
            first_seen.setdefault(n, t)
        courts = {c["court_id"]: c["display_name"] for c in op["courts"]}
        party_names = {
            p["party_id"]: [s["players"][pid]["name"] for pid in p["player_ids"]]
            for p in op["parties"]
        }

        def matchups(r):
            out = []
            for m in r["matchups"]:
                res = None
                if m["team_results"]:
                    by = {x["team_id"]: x["score"][0] for x in m["team_results"]}
                    res = [by[t["team_id"]] for t in m["teams"]]
                out.append({
                    "court": courts[m["court_id"]],
                    "teams": [{"players": sum((party_names[p] for p in t["party_ids"]), [])} for t in m["teams"]],
                    "result": res,
                })
            return sorted(out, key=lambda m: m["court"])

        finished = op["operative_status"] == "FINISHED" and op["final_standings"]
        board = s["leaderboard"]
        if finished:
            pos = {x["party_id"]: x["position"] for x in op["final_standings"]}
            board = sorted((dict(r, position=pos[r["party_id"]]) for r in board),
                           key=lambda r: r["position"])
        n = len(op["rounds"])
        states.append({
            "t": s["t"],
            "kind": s["kind"],
            "finished": bool(finished),
            "clock": (t + TZ_OFFSET).strftime("%H:%M"),
            "name": "Fortgeschritten Americano",
            "round": n,
            "round_elapsed_min": int((t - first_seen[n]).total_seconds() // 60),
            "matchups": matchups(op["rounds"][-1]),
            "previous_round": matchups(op["rounds"][-2]) if n > 1 else None,
            "leaderboard": [
                {"position": r["position"], "name": party_names[r["party_id"]][0],
                 "matches": r["matches"], "wins": r["wins"], "points": r["points"]}
                for r in board
            ],
        })
    os.makedirs(SPEC, exist_ok=True)
    json.dump(states, open(DATA, "w"), indent=1, ensure_ascii=False)
    print(f"{len(states)} states -> {DATA}")


def render():
    states = json.load(open(DATA))
    final = states[-1]
    assert final["finished"], "the last state should be the finished tournament"
    live = [s for s in states if not s["finished"]][-1]
    start = states[0]
    for f in glob.glob(os.path.join(SPEC, "*.png")):
        os.remove(f)
    out = []

    def save(cnv, name):
        p = os.path.join(SPEC, name + ".png")
        cnv.save(p)
        out.append(p)

    # M1: the current round on Double 1, no result yet
    save(m1_court(live, "Double 1"), "m1-court-round-in-progress")
    # M1: the previous round with its result, as shown until the next round exists
    between = dict(live, round=live["round"] - 1, matchups=live["previous_round"],
                   round_elapsed_min=live["round_elapsed_min"] + 5)
    save(m1_court(between, "Double 2"), "m1-court-result-entered")
    # M1: long names fall back to a smaller font
    long = dict(live, matchups=[{"court": "Double 3", "result": None, "teams": [
        {"players": ["Maximilian X", "Konstantin X"]}, {"players": ["Anna-Lena X", "Christopher X"]}]}])
    save(m1_court(long, "Double 3"), "m1-court-long-names")
    # M1: the final screen
    save(m1_final(final), "m1-final")
    # XL1: both leaderboard pages of the live state, the start, the final
    save(xl1_overview(live, 0), "xl1-overview-page1")
    save(xl1_overview(live, 1), "xl1-overview-page2")
    save(xl1_overview(start, 0), "xl1-overview-round1")
    save(xl1_final(final, 0), "xl1-final-page1")
    save(xl1_final(final, 1), "xl1-final-page2")
    # Two players named Kai: both get their surname's initial, everywhere
    clash = json.loads(json.dumps(live).replace("Elias Brandt", "Kai Brandt"))
    save(xl1_overview(clash, 0), "xl1-overview-name-clash")
    print("\n".join(out))


if __name__ == "__main__":
    {"extract": lambda: extract(sys.argv[2]), "render": render}[sys.argv[1]]()
