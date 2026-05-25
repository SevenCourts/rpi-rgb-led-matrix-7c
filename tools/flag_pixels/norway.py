"""Norway — red field, white-bordered blue Scandinavian cross.

Cross is blue with a white outline, so it reads on the red field at a glance.
At 27×18 the white outline is 1 px on each side of the blue cross arms;
at 13×9 there isn't room for an outline so the cross is just blue.
"""

from ._canvas import Canvas

NO_RED = (186, 12, 47)
NO_BLUE = (0, 32, 91)
WHITE = (255, 255, 255)


def large() -> Canvas:
    c = Canvas(27, 18, NO_RED)
    # Outer white cross: 5 wide × 5 tall arms
    c.rect(7, 0, 11, 17, WHITE)
    c.rect(0, 6, 26, 10, WHITE)
    # Inner blue cross: 3 wide × 3 tall arms (1 px white border each side)
    c.rect(8, 0, 10, 17, NO_BLUE)
    c.rect(0, 7, 26, 9, NO_BLUE)
    return c


def small() -> Canvas:
    c = Canvas(13, 9, NO_RED)
    # No room for tri-color: just a blue cross on red (drop white border)
    c.vline(4, 0, 8, NO_BLUE)
    c.hline(0, 12, 4, NO_BLUE)
    return c
