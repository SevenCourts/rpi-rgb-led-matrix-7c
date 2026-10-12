# sevencourts.render

Draws a panel payload to a PNG with the views of the firmware. No hardware, no
browser, no emulator window. It is the base of the panel preview in the tableau
Panel Admin UI (`hub-0a0p`).

```python
from datetime import datetime
from sevencourts.render import render

png, draw_error = render(
    panel_info,                                    # body of GET /panels/<id>/match
    datetime.fromisoformat("2026-05-25T14:30:00+02:00"),
    weather={"city": "Stuttgart,DE", "temperature": 21},   # optional
    comm_error=False,                              # the "server unreachable" dot
)
```

`png` has the panel's native resolution (`sevencourts.render.PANEL_SIZE`).
`draw_error` is `None`, or the message of the exception a view raised; the PNG
then shows the error screen a panel would show.

## What the caller has to provide

| | |
|---|---|
| Working directory | The root of the app: `fonts/`, `images/` and `locale/` are opened by relative path. |
| `PANEL_TYPE` | `M1`, `L1` or `XL1`, set before the first import. It is frozen at import, so **one process draws one type**. |
| `TABLEAU_SERVER_BASE_URL` | Where the views download `image-url` from. |
| `IMAGES_CACHE_DIR` | The image cache. Defaults to a directory under the system's temporary directory; give each process its own. |
| `commit-id`, `commit-date` | Files in the working directory. Without them `sevencourts.gateway` asks `git` at import. |

Dependencies are in [`requirements.txt`](requirements.txt), to be installed
with `pip install --no-deps -r`.

## What it does and does not show

The time is the `now` argument, shown in the time zone of the panel. A booking
payload without `_dev_timestamp` gets `now` as its timestamp, so that the
booking views do not read the clock string as a time of the process's own day.

The pixels are the ones [`tools/emulators`](../../tools/emulators/README.md)
shows: a test compares the canvas with RGBMatrixEmulator's own. As there, they
are raw values without the luminance correction of a real panel. The BLE and
WiFi set-up overlay is never drawn, and nothing is fetched from OpenWeatherMap.

## Tests

`tests/test_render.py`, with golden PNGs per panel type under `tests/golden/`.
After a deliberate change to a view:

```shell
python -m tests.render_goldens --update     # then look at the PNG diff
```
