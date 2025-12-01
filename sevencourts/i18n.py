"""
Internationalization utils
"""

import os
import gettext
import sevencourts.logging as logging

_log = logging.logger("i18n")

LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")


# Set up gettext
def setup_i18n(lang="en"):
    try:
        _log.debug(f"Locale dir: {LOCALE_DIR}")
        # Bind the domain to the locale directory for the specified language
        translator = gettext.translation(
            "messages", LOCALE_DIR, languages=[lang], fallback=True
        )
        # Install the translation, making the '_' function available globally
        translator.install()
        _log.debug(f"Translation for '{lang}' installed")
        return translator
    except FileNotFoundError:
        _log.warning(
            f"Translation for '{lang}' not found in '{LOCALE_DIR}', using defaults."
        )
        # If translation files are not found, provide a dummy _ function returning the key
        import builtins

        builtins._ = lambda x: x
        return None


setup_i18n("de")  # FIXME configuration
