"""A canvas the views can draw on, backed by a PIL image."""

from io import BytesIO

from PIL import Image

_BLACK = (0, 0, 0)


class RenderCanvas:
    """What the views and RGBMatrixEmulator's graphics functions need of a
    canvas: width, height, Clear, Fill, SetPixel and SetImage.

    Not RGBMatrixEmulator's own Canvas: that one needs an RGBMatrixOptions,
    which reads emulator_config.json from the working directory and ends the
    process when no display adapter can be loaded.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._image = Image.new("RGB", (width, height), _BLACK)
        self._pixels = self._image.load()

    def Clear(self):
        self.Fill(*_BLACK)

    def Fill(self, r, g, b):
        self._image.paste((int(r), int(g), int(b)), (0, 0, self.width, self.height))

    def SetPixel(self, x, y, r, g, b):
        # Views draw past the edges on purpose (clipped text, wide rows).
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        self._pixels[int(x), int(y)] = (int(r), int(g), int(b))

    def SetImage(self, image, offset_x=0, offset_y=0, *other):
        # No alpha mask, as on the emulator: a transparent pixel is drawn in
        # whatever colour it carries.
        self._image.paste(image, (int(offset_x), int(offset_y)))

    def image(self) -> Image.Image:
        """A copy of what has been drawn, at native resolution."""
        return self._image.copy()

    def png(self) -> bytes:
        out = BytesIO()
        self._image.save(out, format="PNG")
        return out.getvalue()
