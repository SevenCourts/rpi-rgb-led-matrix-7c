"""Tiny pixel-array Canvas used by the hand-authored flag modules."""

from __future__ import annotations

from typing import Iterable, Sequence

RGB = tuple[int, int, int]


class Canvas:
    def __init__(self, w: int, h: int, bg: RGB = (0, 0, 0)) -> None:
        self.w = w
        self.h = h
        self.px: list[list[RGB]] = [[bg for _ in range(w)] for _ in range(h)]

    def set(self, x: int, y: int, c: RGB) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def fill(self, c: RGB) -> None:
        for y in range(self.h):
            for x in range(self.w):
                self.px[y][x] = c

    def rect(self, x0: int, y0: int, x1: int, y1: int, c: RGB) -> None:
        """Filled rect, inclusive of both corners."""
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.px[y][x] = c

    def hline(self, x0: int, x1: int, y: int, c: RGB) -> None:
        if x0 > x1:
            x0, x1 = x1, x0
        for x in range(x0, x1 + 1):
            self.set(x, y, c)

    def vline(self, x: int, y0: int, y1: int, c: RGB) -> None:
        if y0 > y1:
            y0, y1 = y1, y0
        for y in range(y0, y1 + 1):
            self.set(x, y, c)

    def line(self, x0: int, y0: int, x1: int, y1: int, c: RGB) -> None:
        """Bresenham — kept simple; flags rarely need arbitrary lines."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def stamp(self, x0: int, y0: int, rows: Sequence[str], palette: dict[str, RGB]) -> None:
        """Paint a small bitmap from a list of strings using a palette.
        Use '.' or ' ' for transparent (skip)."""
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch in (".", " "):
                    continue
                c = palette.get(ch)
                if c is not None:
                    self.set(x0 + dx, y0 + dy, c)

    def to_rows(self) -> list[list[RGB]]:
        return self.px

    def to_pil(self):
        from PIL import Image
        img = Image.new("RGB", (self.w, self.h))
        flat: list[RGB] = []
        for row in self.px:
            flat.extend(row)
        img.putdata(flat)
        return img
