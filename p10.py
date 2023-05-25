#!/usr/bin/env python3

from rgbmatrix import graphics

from samplebase import SampleBase
from sevencourts import *
import time
from datetime import datetime

class P10Test(SampleBase):
    def __init__(self, *args, **kwargs):
        super(P10Test, self).__init__(*args, **kwargs)

    def run(self):
        self.canvas = self.matrix.CreateFrameCanvas()

        while True:
            self.canvas.Clear()
            

            fill_rect(self.canvas, 0, 0, 32, 16, COLOR_YELLOW)
            draw_text(self.canvas, 0, 12, "Hola", FONT_M, COLOR_RED)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(1)


if __name__ == "__main__":
    infoboard = P10Test()
    if (not infoboard.process()):
        infoboard.print_help()
