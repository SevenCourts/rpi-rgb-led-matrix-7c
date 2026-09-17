# Panel emulators

Run the firmware for all three panel types on this machine, against a fake
backend, and watch them side by side in the browser. No hardware needed.

```shell
tools/emulators/emulators.sh                             # everything, auto-advancing
tools/emulators/emulators.sh --only esslingen --no-auto  # one logo, stepped by hand
```

Then open <http://127.0.0.1:8000/>. Ctrl-C stops everything.

Needs [uv](https://docs.astral.sh/uv/) and nothing else: it fetches Python 3.9
and the dependencies on first run.

## What starts

| Process | Port | What it is |
|---|---|---|
| `fixture_server.py` | 8000 | Stands in for the SevenCourts backend. Serves a catalogue of panel scenarios and the control page that embeds all three emulators. |
| M1 emulator | 8888 | The real firmware (`sevencourts.m1.main`), drawing to RGBMatrixEmulator instead of LEDs. |
| L1 emulator | 8889 | ″ |
| XL1 emulator | 8890 | ″ |

Each emulator polls the fixture server exactly as a panel polls the real
backend, and registers as `m1`/`l1`/`xl1` so the server can hand each one its
own asset. They run from `.runtime/emu/<panel>/` (symlinks into the repo plus a
per-panel `emulator_config.json`), with logs in `.runtime/emu/*/run.log`.

## Fixtures

The control page has Next / Prev / Pause / Resume / Jump. `--interval` sets the
auto-advance seconds, `--no-auto` turns it off, `--only <substring>` keeps just
the matching fixtures (case-insensitive).

Logos laid out per panel under `images/logos/<name>/{m1,l1,xl1}/`, as written by
`logoprep render --by-panel` in the `sevencourts.logoprep` repo, are picked up
automatically and listed as `logo — <name> (full)` and `(with clock)`. The list
is built at startup, so restart after adding one.

## Caveat

The emulator shows raw pixel values. Real panels apply rgbmatrix's CIE1931
luminance correction, so this answers layout questions, not brightness ones.
