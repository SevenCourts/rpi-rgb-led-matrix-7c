#!/usr/bin/env python3

import os

# Set the environment variable USE_RGB_MATRIX_EMULATOR to use with
# emulator https://github.com/ty-porter/RGBMatrixEmulator
# Do not set to use with real SDK https://github.com/hzeller/rpi-rgb-led-matrix
if os.getenv('USE_RGB_MATRIX_EMULATOR', False):
    from RGBMatrixEmulator import graphics # type: ignore
else:
    from rgbmatrix import graphics # type: ignore
from samplebase import SampleBase
from sevencourts import *
import time

logger = m1_logging.logger()


class SevenCourtsLedTest(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SevenCourtsLedTest, self).__init__(*args, **kwargs)
        
    def load_test_image(self, name):
        # Prefer an image matching the panel resolution (e.g. 192x64 for M1,
        # 320x96 for XL1); otherwise scale the M1 image to the panel size.
        w, h = self.matrix.width, self.matrix.height
        path = "images/%s_%dx%d.png" % (name, w, h)
        if not os.path.isfile(path):
            path = "images/%s_192x64.png" % name
        image = Image.open(path).convert('RGB')
        if image.size != (w, h):
            image = image.resize((w, h))
        return image

    def run(self):
        logger.info("Starting LED test instance (%dx%d)" % (self.matrix.width, self.matrix.height))

        self.canvas = self.matrix.CreateFrameCanvas()

        w, h = self.matrix.width, self.matrix.height
        test_images = [
            self.load_test_image("rainbow_up"),
            self.load_test_image("rainbow_down"),
            Image.new('RGB', (w, h), (255, 255, 255)),
        ]

        while True:
            delay_s = 3
            for image in test_images:
                self.canvas.SetImage(image, 0, 0)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(delay_s)

# Main function
if __name__ == "__main__":
    infoboard = SevenCourtsLedTest()
    if not infoboard.process():
        infoboard.print_help()
