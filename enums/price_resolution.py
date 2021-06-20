"""Enumerator for all supported price time resolutions.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from enum import Enum


class PriceResolution(Enum):
    """Enumerator of Supported Price Time Resolution."""
    
    DAY = 1
    HOUR = 2
    HOUR_2 = 3
    HOUR_3 = 4
    HOUR_4 = 5
    MINUTE = 6
    MINUTE_2 = 7
    MINUTE_3 = 8
    MINUTE_5 = 9
    MINUTE_10 = 10
    MINUTE_15 = 11
    MINUTE_30 = 12
    WEEK = 13
    MONTH = 15
    SECOND = 16
