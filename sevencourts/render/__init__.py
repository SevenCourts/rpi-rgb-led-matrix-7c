"""Draw a panel payload to a PNG: no hardware, no browser, no emulator window.

    from sevencourts.render import render
    png, draw_error = render(panel_info, now)

It runs the views of the firmware, so it has the firmware's two constraints:
the working directory must be the root of the app (fonts/, images/ and locale/
are opened by relative path), and one process draws one PANEL_TYPE, which is
frozen when sevencourts.m1.dimens is first imported.

See README.md in this directory.
"""

import os
import tempfile

# Pure-Python drawing code of RGBMatrixEmulator instead of the hardware
# library. Only its graphics module is used; its display adapters (browser,
# pygame, sixel, ...) are not installed here and must not complain about it.
os.environ.setdefault("USE_RGB_MATRIX_EMULATOR", "1")
os.environ.setdefault("RGBME_SUPPRESS_ADAPTER_LOAD_ERRORS", "1")
# sevencourts.images creates its cache directory at import; the panel's
# default, /opt/7c/cache-images, does not exist off a panel.
os.environ.setdefault(
    "IMAGES_CACHE_DIR", os.path.join(tempfile.gettempdir(), "7c-render-cache")
)

from sevencourts.render.canvas import RenderCanvas  # noqa: E402
from sevencourts.render.core import PANEL_SIZE, render  # noqa: E402

__all__ = ["PANEL_SIZE", "RenderCanvas", "render"]
