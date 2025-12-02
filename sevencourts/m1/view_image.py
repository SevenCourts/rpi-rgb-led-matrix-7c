from sevencourts.m1.dimens import *
from PIL import Image
import sevencourts.m1.view_clock as v_clock
import sevencourts.logging as logging
import sevencourts.images as imgs

_log = logging.logger("v_image")


def draw_image_from_url(cnv, idle_info, time_now):
    image_path = idle_info.get("image-url")  # FIXME this is a path, not url
    try:
        image = imgs.get_with_cache(image_path)

        _draw_image_and_maybe_clock(
            cnv, image, time_now, idle_info.get("clock") == True
        )

        # FIXME who loads this image? no usage!
        path = imgs.CACHE_DIR + "/latest_idle_image"
        image.save(path, "png")

    except Exception as ex:
        # TODO show an image stub (?)
        _log.error(f"Error downloading image {image_path}", ex)


def draw_image_preset(cnv, idle_info, time_now):
    path = "images/logos/" + idle_info.get("image-preset")
    image = Image.open(path)
    _draw_image_and_maybe_clock(cnv, image, time_now, idle_info.get("clock") == True)


def _can_show_clock(image: Image):
    return image.width < v_clock.W_LOGO_WITH_CLOCK


def _draw_image_and_maybe_clock(cnv, image: Image, time_now, try_to_show_clock: bool):

    show_clock = try_to_show_clock and _can_show_clock(image)

    image_max_width = v_clock.W_LOGO_WITH_CLOCK if show_clock else W_PANEL
    image = imgs.shrink_to_fit(image, image_max_width, H_PANEL)

    x = (image_max_width - image.width) // 2
    y = (H_PANEL - image.height) // 2
    cnv.SetImage(image.convert("RGB"), x, y)

    if try_to_show_clock and _can_show_clock(image):
        v_clock.draw_clock(cnv, time_now, None)
