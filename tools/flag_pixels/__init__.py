"""Hand-authored pixel-perfect country flags for 27x18 and 13x9 LED output.

Each flag lives in its own module that exports `large()` -> 27x18 Canvas and
`small()` -> 13x9 Canvas. The runner `render_handdrawn_flags.py` and the
contact-sheet tool consume the FLAGS registry below.
"""

from __future__ import annotations

from . import (
    argentina,
    australia,
    brazil,
    denmark,
    fiji,
    finland,
    germany,
    great_britain,
    greece,
    israel,
    korea,
    mexico,
    new_zealand,
    norway,
    portugal,
    romania,
    spain,
    sri_lanka,
    sweden,
    switzerland,
    turkey,
    tuvalu,
    usa,
)


FLAGS = {
    "australia": australia,
    "new zealand": new_zealand,
    "great britain": great_britain,
    "fiji": fiji,
    "tuvalu": tuvalu,
    "sri lanka": sri_lanka,
    "mexico": mexico,
    "brazil": brazil,
    "spain": spain,
    "portugal": portugal,
    "argentina": argentina,
    "germany": germany,
    "switzerland": switzerland,
    "greece": greece,
    "sweden": sweden,
    "denmark": denmark,
    "finland": finland,
    "norway": norway,
    "usa": usa,
    "romania": romania,
    "israel": israel,
    "korea": korea,
    "turkey": turkey,
}
