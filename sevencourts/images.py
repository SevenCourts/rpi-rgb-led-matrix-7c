import os
from PIL import Image
import sevencourts.gateway as gateway
import sevencourts.logging as logging

_log = logging.logger("images")

CACHE_DIR = os.getenv("IMAGES_CACHE_DIR", "/opt/7c/cache-images")

os.makedirs(CACHE_DIR, exist_ok=True)
# The default 0o777 does not work,
# see https://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-in-python
os.chmod(CACHE_DIR, 0o777)


def get_with_cache(image_path: str) -> Image:

    log0 = logging.logger("images-get#" + image_path)

    try:
        response = gateway.head_image(image_path)
        etag = str(response.headers["ETag"])
        if etag != None:
            log0.debug(f"etag: {etag}")
            cached_path = CACHE_DIR + "/" + etag
            if os.path.isfile(cached_path):
                log0.debug(f"get from cache {cached_path}")
                result = Image.open(cached_path)
            else:
                log0.debug("not found in cache by etag, dowloading...")
                result = Image.open(gateway.get_raw_by_path(image_path))
                result.save(cached_path, "png")
        else:
            log0.debug("no etag, dowloading...")
            result = Image.open(gateway.get_raw_by_path(image_path))
        return result

    except Exception as ex:
        # TODO show an image stub (?)
        _log.error(f"Error downloading image {image_path}", ex)
        _log.exception(ex)


def save_to_cache(image: Image, path: str):
    cached_path = CACHE_DIR + "/" + path
    image.save(cached_path, "png")


def shrink_to_fit(image: Image, w: int, h: int) -> Image:
    # print (f"original w: {image.width}, h: {image.height}")
    if image.width > w or image.height > h:
        image.thumbnail((w, h), Image.LANCZOS)
    # print (f"result w: {image.width}, h: {image.height}")
    return image


def load_flag_image(flag_code: str) -> Image:
    try:
        return Image.open("images/flags/" + (flag_code or "VOID") + ".png").convert(
            "RGB"
        )
    except Exception as e:
        _log.exception(e)
        return Image.open("images/flags/VOID.png").convert("RGB")
