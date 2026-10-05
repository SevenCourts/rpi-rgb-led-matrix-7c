import sevencourts.images as imgs
from sevencourts.m1.model import PanelState
from sevencourts.m1.dimens import *

# Ads are an eBuSy-only feature, unlike the rest of this package, which draws
# the "booking" shape of any provider. The "ebusy-ads" key is part of the wire
# contract with the server and with panels in the field: do not rename it.


def draw(cnv, state: PanelState):
    ebusy_ads = state.panel_info.get("ebusy-ads", {})
    url = ebusy_ads.get("url")
    image = imgs.fetch_by_url_with_cache(url)

    x = (W_PANEL - image.width) // 2
    y = (H_PANEL - image.height) // 2

    cnv.SetImage(image.convert("RGB"), x, y)
