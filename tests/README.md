# Tests

Automated checks: they assert and fail. Anything you run to *look* at a panel
lives in [`tools/emulators/`](../tools/emulators/README.md) instead.

## Unit tests

Plain `unittest`, no external services, no hardware. They set
`USE_RGB_MATRIX_EMULATOR` themselves, so they run anywhere:

```shell
python3 -m unittest discover -s tests -t .      # all of them
python3 -m unittest tests.test_view_image       # one module
```

| Module | Covers |
|---|---|
| `test_booking_interchange.py` | current and next booking take turns every 10 seconds in the last 5 minutes |
| `test_booking_prompt.py` | free-court prompt stays on the panel when it wraps to two rows |
| `test_layouts.py` | scoreboard layout geometry |
| `test_model_rtc.py` | RTC-backed clock state in the panel model |
| `test_network_vpn_ip.py` | VPN tunnel IP reported at registration |
| `test_panel_info_empty.py` | clock keeps ticking when the server sends false/null/empty panel info |
| `test_render.py` | the headless renderer (`sevencourts/render/`): golden PNGs per panel type, same pixels as the emulator, time taken from `now` |
| `test_view_image.py` | the image + clock split decision |

## Integration tests (`hurl/`)

[Hurl](https://hurl.dev/) scripts that drive a **live panel** through the
backend API and exercise the scoreboard rendering modes. They need a running
panel and a target set via `HURL_7c_target_panel` (base64 hostname) — see
[hurl/README.md](hurl/README.md).

```shell
cd tests/hurl && hurl --test *.hurl      # Windows: run_full.cmd
```

## Golden PNGs (`golden/`)

`test_render.py` draws a list of screens for M1, L1 and XL1 and compares each
with `golden/<type>/<screen>.png`. The screens are defined in
`render_goldens.py`, from the fixture catalogue of `tools/emulators`. When a
check fails, what was drawn instead is left in `.runtime/render-actual/`.

After a deliberate change to a view, rewrite them and look at the diff of the
PNGs before committing:

```shell
python -m tests.render_goldens --update
```

This repository is public: goldens use the SevenCourts style only, no club
logos or names.

## CI

`.github/workflows/test.yml` runs the unit tests on every pull request and on
master, on Python 3.9 (the firmware) and 3.12 (the server-side renderer), with
the dependencies of `sevencourts/render/requirements.txt`. The Hurl suite needs
a live panel and does not run in CI.
