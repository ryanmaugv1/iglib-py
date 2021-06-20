"""Enumerator for all supported IG trading account types.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from enum import Enum


class AccountType(Enum):
    """Enumerator of Supported IG Trading Account Types."""
    
    CFD = 1
    SPREADBET = 2
