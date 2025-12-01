from PIL import Image
import sevencourts.gateway as gateway
import sevencourts.images as imgs
from sevencourts.m1.model import PanelState
from sevencourts.club_styles import *
from sevencourts.rgbmatrix import *
from sevencourts.m1.dimens import *
import sevencourts.m1.booking.ebusy.view_single as v_single
import sevencourts.m1.booking.ebusy.view_multiple as v_multiple
import sevencourts.logging as logging

_log = logging.logger("eBuSy")


def draw(cnv, state: PanelState):
    info = state.panel_info

    styles = {
        "SevenCourts": style_SevenCourts,
        "SV1845": style_SV1845,
        "TABB": style_TABB,
        "MatchCenter": style_MatchCenter,
    }
    style = styles.get(info.get("booking").get("style", "SevenCourts"))

    total_courts = len(info.get("booking").get("courts", []))
    if total_courts == 0:
        # logger.warning(f"No courts in booking info: {booking_info}")
        draw_text(cnv, 0, 10, "Please select court/s")
    elif total_courts == 1:
        v_single.draw(cnv, state, style)
    else:
        v_multiple.draw(cnv, state, style)


def draw_ads(cnv, state: PanelState):
    ebusy_ads = state.panel_info.get("ebusy-ads", {})
    id = ebusy_ads.get("id")
    url = ebusy_ads.get("url")
    path = imgs.IMAGE_CACHE_DIR + "/ebusy_" + str(id)

    try:
        if os.path.isfile(path):
            image = Image.open(path)
        else:
            image = Image.open(gateway.get_raw(url))
            image.save(path, "png")

        x = (W_PANEL - image.width) // 2
        y = (H_PANEL - image.height) // 2
        cnv.SetImage(image.convert("RGB"), x, y)

    except Exception as e:
        _log.debug(f"Error downloading image {url}", e)
        _log.exception(e)
