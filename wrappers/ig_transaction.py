"""IG Account Transaction Data Wrapper Class.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations


class IGTransaction:
    """Wrapper for IG Account Transaction Data.

    Attributes:
        cash_transaction: True if this was a cash transaction
        close_level: Level at which the order was closed
        currency: Order currency.
        date: Local date for transaction.
        date_utc: UTC locale date for transaction.
        instrument_name: Instrument name.
        open_date_utc: Position opened date (UTC locale).
        open_level: Level at which the order was opened.
        period: Transaction expiration.
        profit_loss: Profit & Loss for transaction.
        reference: Reference.
        size: Formatted order size, including direction (+ = buy, - = sell).
        transaction_type: Transaction type.
    """

    def __init__(self,
                 cash_transaction: bool,
                 close_level: str,
                 currency: str,
                 date: str,
                 date_utc: str,
                 instrument_name: str,
                 open_date_utc: str,
                 open_level: str,
                 period: str,
                 profit_loss: str,
                 reference: str,
                 size: str,
                 transaction_type: str):
        self.cash_transaction = cash_transaction
        self.close_level = close_level
        self.currency = currency
        self.date = date
        self.date_utc = date_utc
        self.instrument_name = instrument_name
        self.open_date_utc = open_date_utc
        self.open_level = open_level
        self.period = period
        self.profit_loss = profit_loss
        self.reference = reference
        self.size = size
        self.transaction_type = transaction_type

    @staticmethod
    def parse_from_dict(res: dict) -> [IGTransaction]:
        transactions = []
        for transaction in res['transactions']:
            transactions.append(
                IGTransaction(
                    transaction['cashTransaction'],
                    transaction['closeLevel'],
                    transaction['currency'],
                    transaction['date'],
                    transaction['dateUtc'],
                    transaction['instrumentName'],
                    transaction['openDateUtc'],
                    transaction['openLevel'],
                    transaction['period'],
                    transaction['profitAndLoss'],
                    transaction['reference'],
                    transaction['size'],
                    transaction['transactionType']))
        return transactions
