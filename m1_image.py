from sevencourts import *
import m1_clock
import requests
import urllib.request

logger = m1_logging.logger("image")

LATEST_IDLE_MODE_IMAGE_PATH = IMAGE_CACHE_DIR + '/latest_idle_image'

def draw_idle_mode_image_preset(canvas, idle_info, tz):
    image_preset = idle_info.get('image-preset')
    path = "images/logos/" + image_preset
    image = Image.open(path)
    is_enough_space_for_clock = image.width < m1_clock.W_LOGO_WITH_CLOCK
    _display_logo(canvas, image, is_enough_space_for_clock)
    if is_enough_space_for_clock and idle_info.get('clock') == True:
        m1_clock.draw_clock(canvas, idle_info.get('clock'), tz)            

def _display_logo(canvas, image, show_clock):
    w = W_PANEL
    if show_clock:
        w = m1_clock.W_LOGO_WITH_CLOCK

    x = (w - image.width) / 2
    y = (H_PANEL - image.height) / 2
    canvas.SetImage(image.convert('RGB'), x, y)


def _download_idle_mode_image(image_url):
    return Image.open(requests.get(image_url, stream=True).raw)

def _save_idle_mode_image(image):
    show_clock = image.width < m1_clock.W_LOGO_WITH_CLOCK
    image_max_width = m1_clock.W_LOGO_WITH_CLOCK if show_clock else W_PANEL
    image = _thumbnail(image, image_max_width)
    image.save(LATEST_IDLE_MODE_IMAGE_PATH, 'png')
    return (image, show_clock)

def draw_idle_mode_image_url(canvas, idle_info, panel_tz):
    image_url = idle_info.get('image-url')
    image_url = BASE_URL + "/" + image_url

    try:
        request = urllib.request.Request(image_url, method="HEAD")
        response = urllib.request.urlopen(request)
        etag = str(response.headers["ETag"])

        if etag != None:
            path = IMAGE_CACHE_DIR + "/" + etag
            if (os.path.isfile(path)):
                image = Image.open(path)
                show_clock = _save_idle_mode_image(image)[1]
            else:
                saved = _save_idle_mode_image(_download_idle_mode_image(image_url))
                image = saved[0]
                show_clock = saved[1]
                image.save(path, 'png')
        else:
            saved = _save_idle_mode_image(_download_idle_mode_image(image_url))
            image = saved[0]
            show_clock = saved[1]

        _display_logo(canvas, image, show_clock)
        if show_clock and idle_info.get('clock') == True:
            m1_clock.draw_clock(canvas, idle_info.get('clock'), panel_tz)
            
    except Exception as ex:
        # TODO show an image stub (?)
        logger.exception(ex)
        logger.error(f"Error downloading image {image_url}", ex)

def _thumbnail(image, w=W_PANEL, h=H_PANEL):
    # print ("original w: {0}, h: {1}".format(image.width, image.height))
    if image.width > w or image.height > h:
        image.thumbnail((w, h), Image.LANCZOS)
    # print ("result w: {0}, h: {1}".format(image.width, image.height))
    return image