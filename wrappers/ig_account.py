"""IG Account Data Wrapper Class.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations

from absl import logging

from utility.constants import Constants
from iglib.enums.account_type import AccountType
from iglib.wrappers.ig_account_info import IGAccountInfo
from iglib.wrappers.ig_other_account import IGOtherAccount 


class IGAccount:
    """Wrapper Class For IG Account Data.
    
    Attributes:
        client_id: Unique identifier for client.
        id: Unique identifier for authenticated account.
        type: Type of trading account e.g. CFD or SPREAD.
        info: Object containing monetary account info.
        currency_iso_code: Base currency for account.
        lightstreamer_endpoint: URL for async data streaming API.
        other_accounts: Preview of all other account belonging to client.
    """

    def __init__(self,
                 client_id: str,
                 id: str,
                 type: str,
                 info: IGAccountInfo,
                 currency_iso_code: str,
                 lightstreamer_endpoint: str,
                 other_accounts: [IGOtherAccount]):
        self.client_id = client_id
        self.id = id
        self.account_type = type
        self.info = info
        self.currency_iso_code = currency_iso_code
        self.lightstreamer_endpoint = lightstreamer_endpoint
        self.other_accounts = other_accounts

    def log_details(self) -> None:
        """Formats and logs all account details."""
        logging.info(Constants.LOG_SEPARATOR)
        logging.info('CURRENT ACCOUNT INFORMATION')
        logging.info(Constants.LOG_SEPARATOR)
        logging.info('Client ID: %s', self.client_id)
        logging.info('Account ID: %s', self.id)
        logging.info('Account Type: %s', self.account_type.name)
        logging.info('Account Info:')
        logging.info('  Balance: %s', self.info.balance)
        logging.info('  Deposit: %s', self.info.deposit)
        logging.info('  Profit Loss: %s', self.info.profit_loss)
        logging.info('  Available: %s', self.info.available)
        logging.info('Currency ISO Code: %s', self.currency_iso_code)
        logging.info('Lighstreamer Endpoint: %s', self.lightstreamer_endpoint)
        logging.info('Other Accounts: %s', "None" if len(self.other_accounts) == 0 else "")
        for x in range(0, len(self.other_accounts)):
            account = self.other_accounts[x]
            logging.info('  Account #%s', x + 1)
            logging.info('      Account ID: %s', account.account_id)
            logging.info('      Account Name: %s', account.account_name)
            logging.info('      Preferred: %s', account.preferred)
            logging.info('      Account Type: %s', account.account_type)
        logging.info(Constants.LOG_SEPARATOR)

    @staticmethod
    def parse_from_dict(res: dict) -> IGAccount:
        """Parses account response into IGAccount wrapper class. 

        Args:
            res: IG account data response in dictionary format.

        Returns:
            IGAccount wrapper class populated with data from account response dict.
        """
        return IGAccount(
            res['clientId'],
            res['currentAccountId'],
            AccountType[res['accountType']],
            IGAccountInfo.parse_from_dict(res['accountInfo']),
            res['currencyIsoCode'],
            res['lightstreamerEndpoint'],
            IGOtherAccount.parse_from_dict(res['accounts']))
