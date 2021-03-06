import re
import random

from django.utils.encoding import smart_text
from django.utils.deprecation import MiddlewareMixin

from .. import defaults

extensions = defaults.FRESHLY_ASSETS_EXTENTIONS + [
    i for i in defaults.FRESHLY_ASSETS_EXTENTIONS_EXTRA
    if i not in defaults.FRESHLY_ASSETS_EXTENTIONS
]

ASSETS_PATTERNS = (
    '(\<.*?)'           # anything after the opening < [group 1]
    '(\.)'              # the dot just before the extension [group 2]
    '(?i)'              # ignore extension's case (case-insensitive, png or PNG) [no group]
    '({})'              # extension(s) to append version number to [group 3]
    '(?!\?)'            # immediately after the extension, we shouldn't see anything but space, or ', or " [no group]
    '(.*?\>)'           # anything else before the closing > [group 4]
    .format('|'.join(extensions))
)


class AssetVersioningMiddleware(MiddlewareMixin):
    """
    A Django middleware that adds a version number to assets within the response content.
    """
    def process_response(self, request, response):
        if defaults.FRESHLY_ASSETS_ALWAYS_FRESH:
            ver = 'v' + str(random.choice([x for x in range(1000, 10000000)]))
        else:
            ver = defaults.FRESHLY_ASSETS_VERSION
        if ver and response.status_code == 200 and response["content-type"].startswith("text/html"):
            response.content = re.sub(ASSETS_PATTERNS, '\\1\\2\\3{}{}\\4'.format('?', ver),
                smart_text(response.content))
        return response
