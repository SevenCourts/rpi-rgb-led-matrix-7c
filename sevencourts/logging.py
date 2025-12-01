"""
Logging factory
"""

import os
import logging

_logging_level = logging.DEBUG if os.getenv("TABLEAU_DEBUG") else logging.INFO


def logger(subcategory="n/a"):
    category = f"7C-{subcategory}>>>"

    # WTF: must call this, otherwise the logger will not do any output
    logging.debug(f"Creating logger '{category}' with level: {_logging_level}")

    result = logging.getLogger(category)
    result.setLevel(_logging_level)
    return result
