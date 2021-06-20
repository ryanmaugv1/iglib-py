"""Enumerator for all supported HTTP request types.

Authored By TheCeriousBoi [TCB] (@theceriousboi)
"""

from enum import Enum


class RequestType(Enum):
    """Enumerator for all supported HTTP request types."""

    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
