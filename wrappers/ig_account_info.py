"""IG Account Info Data Wrapper Class.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations


class IGAccountInfo:
    """Wrapper Class For IG Account Info Data.

    Attributes:
        balance: Current account balance (not including open position P/L).
        deposit: Initial account deposit amount.
        profit_loss: Profit and loss amount relative to deposit.
        available: Funds available from balance that can be used to open new positions.
    """

    def __init__(self,
                 balance: float,
                 deposit: float,
                 profit_loss: float,
                 available: float):
        self.balance = balance
        self.deposit = deposit
        self.profit_loss = profit_loss
        self.available = available

    @staticmethod
    def parse_from_dict(res: dict) -> IGAccountInfo:
        """ Parses account info from account response into IGAccountInfo class.

        Args:
            res: IG account info data response in dictionary format.
        Returns:
            IGAccountInfo parsed from response dict.
        """
        return IGAccountInfo(
            res['balance'],
            res['deposit'],
            res['profitLoss'],
            res['available'])
