from PIL import Image
import sevencourts.gateway as gateway
import sevencourts.images as imgs
from sevencourts.m1.model import PanelState
from sevencourts.club_styles import *
from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *
import sevencourts.m1.booking.view_single as v_single
import sevencourts.m1.booking.view_multiple as v_multiple
import sevencourts.logging as logging

_log = logging.logger("booking")


def draw(cnv, state: PanelState):
    info = state.panel_info

    style = style_for(info)

    total_courts = len(info.get("booking").get("courts", []))
    if total_courts == 0:
        # logger.warning(f"No courts in booking info: {booking_info}")
        draw_text(cnv, 0, 10, "Please select court/s")
    elif total_courts == 1:
        v_single.draw(cnv, state, style)
    else:
        v_multiple.draw(cnv, state, style)
