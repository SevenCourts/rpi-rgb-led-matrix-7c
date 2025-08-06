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


class SevenCourtsM1(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SevenCourtsM1, self).__init__(*args, **kwargs)
        
    def run(self):
        logger.info("Starting M1 test instance")
        
        self.canvas = self.matrix.CreateFrameCanvas()

        while True:
            delay_s = 3
            self.canvas.SetImage(Image.open("images/rainbow_up_192x64.png").convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(delay_s)
            self.canvas.SetImage(Image.open("images/rainbow_down_192x64.png").convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(delay_s)
            self.canvas.SetImage(Image.open("images/white-192x64.png").convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(delay_s)

# Main function
if __name__ == "__main__":
    infoboard = SevenCourtsM1()
    if not infoboard.process():
        infoboard.print_help()
