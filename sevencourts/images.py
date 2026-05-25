import os
from PIL import Image
import sevencourts.gateway as gateway
import sevencourts.logging as logging
from pathlib import Path
from sevencourts.m1.dimens import W_FLAG, H_FLAG

_log = logging.logger("images")

# Source flag PNGs ship at 18×12. Scale up at load time when the active panel
# advertises a larger flag size (e.g. XL1: 27×18). Nearest-neighbor preserves
# the pixel-art look and is cheap on the Pi.
_FLAG_SOURCE_W = 18
_FLAG_SOURCE_H = 12

CACHE_DIR = os.getenv("IMAGES_CACHE_DIR", "/opt/7c/cache-images")

os.makedirs(CACHE_DIR, exist_ok=True)
# The default 0o777 does not work,
# see https://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-in-python
os.chmod(CACHE_DIR, 0o777)


def _get_from_cache(path: str) -> Image:
    if os.path.isfile(path):
        _log.debug(f"get from cache {path}")
        return Image.open(path)
    else:
        return None


def _save_to_cache(image: Image, path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "png")
    _log.debug(f"saved to cache {path}")


def fetch_by_url_with_cache(url: str) -> Image:
    from urllib.parse import quote

    image_path = quote(url)

    cached_full_path = f"{CACHE_DIR}/internet/{image_path}.png"

    try:
        response = gateway.head(url)
        etag = response.headers["ETag"]
        if etag != None:
            cached_etag_path = f"{CACHE_DIR}/etag/{etag}.png"

            result = _get_from_cache(cached_etag_path)
            if result == None:
                result = Image.open(gateway.get_raw(url))
                _save_to_cache(result, cached_etag_path)
        else:
            result = Image.open(gateway.get_raw(url))

        _save_to_cache(result, cached_full_path)

    except Exception as ex:
        _log.error(f"❌ Error downloading image by url '{url}': {str(ex)}")
        # try to get from cache by original path
        result = _get_from_cache(cached_full_path)

    if result == None:
        # error stub
        result = Image.open("images/placeholder-82x64.png")

    return result


def fetch_by_path_with_cache(image_path: str) -> Image:

    cached_full_path = f"{CACHE_DIR}/{image_path}"

    try:
        response = gateway.head_by_path(image_path)
        etag = str(response.headers["ETag"])
        if etag != None:
            cached_etag_path = f"{CACHE_DIR}/etag/{etag}.png"

            result = _get_from_cache(cached_etag_path)
            if result == None:
                result = Image.open(gateway.get_raw_by_path(image_path))
                _save_to_cache(result, cached_etag_path)
                _save_to_cache(result, cached_full_path)
        else:
            result = Image.open(gateway.get_raw_by_path(image_path))

    except Exception as ex:
        _log.error(f"❌ Error downloading image {image_path}: {str(ex)}")
        # try to get from cache by original path
        result = _get_from_cache(cached_full_path)

    if result == None:
        # error stub
        result = Image.open("images/placeholder-82x64.png")

    return result


def scale_to_fit(image: Image, w: int, h: int) -> Image:
    """Scale image to fit within w×h, preserving aspect ratio. Scales up or down."""
    ratio = min(w / image.width, h / image.height)
    if ratio != 1:
        new_w = int(image.width * ratio)
        new_h = int(image.height * ratio)
        image = image.resize((new_w, new_h), Image.LANCZOS)
    return image


def shrink_to_fit(image: Image, w: int, h: int) -> Image:
    if image.width > w or image.height > h:
        image.thumbnail((w, h), Image.LANCZOS)
    return image


def load_flag_image(flag_code: str, size: tuple = None) -> Image:
    """Load a flag image at the requested target size.

    `size` is (width, height); defaults to the active panel's
    (W_FLAG, H_FLAG). When a native-size PNG exists under
    `images/flags_<W>x<H>/`, it is returned verbatim (no scaling). This is
    the path that preserves pixel-perfect hand-tuned / procedural art.
    Otherwise the 18×12 source is loaded and scaled: Lanczos when
    downscaling (small variants), nearest-neighbor when upscaling.
    """
    if size is None:
        size = (W_FLAG, H_FLAG)
    w, h = size
    code = flag_code or "VOID"

    native_dir = f"images/flags_{w}x{h}"
    native_path = f"{native_dir}/{code}.png"
    try:
        return Image.open(native_path).convert("RGB")
    except FileNotFoundError:
        pass
    except Exception as e:
        _log.exception(e)

    try:
        image = Image.open("images/flags/" + code + ".png").convert("RGB")
    except Exception as e:
        _log.exception(e)
        image = Image.open("images/flags/VOID.png").convert("RGB")

    if image.size != (w, h):
        src_w, src_h = image.size
        method = Image.LANCZOS if (w < src_w or h < src_h) else Image.NEAREST
        image = image.resize((w, h), method)
    return image


def _scale_flag_for_panel(image: Image) -> Image:
    """Scale source 18×12 flag to the active panel's W_FLAG×H_FLAG (nearest-neighbor).

    Kept for backward compatibility; new code should pass a size to
    `load_flag_image` directly.
    """
    if image.size == (W_FLAG, H_FLAG):
        return image
    return image.resize((W_FLAG, H_FLAG), Image.NEAREST)
