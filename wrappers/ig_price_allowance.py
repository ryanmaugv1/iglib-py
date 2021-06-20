"""IG API historical price request allowance data wrapper class.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations


class IGPriceAllowance:
    """Wrapper Class for IG API Historical Price Request Allowance.
    
    Attributes:
        remaining_allowance: Number of data points available to fetch within the
            current allowance period.
        total_allowance: Number of data points the API key and account combination 
            is allowed to fetch in any given allowance period.
        allowance_expiry: Number of seconds till the current allowance period will 
            end and the remaining allowance field is reset.
    """

    def __init__(self, remaining_allowance: float, total_allowance: float, allowance_expiry: float):
        self.remaining_allowance = remaining_allowance
        self.total_allowance = total_allowance
        self.allowance_expiry = allowance_expiry

    @staticmethod
    def parse_from_dict(res: dict) -> IGPriceAllowance:
        """Parses IG API historical price request allowance into wrapper object.

        Args:
            res: Dictionary of request allowance data.
        Returns:
            IGPriceAllowance object containing response dict data.
        """
        return IGPriceAllowance(
            res['remainingAllowance'],
            res['totalAllowance'],
            res['allowanceExpiry'])