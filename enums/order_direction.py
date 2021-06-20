"""Enumerator for order direction.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from enum import Enum


class OrderDirection(Enum):
    """Enumerator for market order direction."""

    BUY = 1
    SELL = 2
