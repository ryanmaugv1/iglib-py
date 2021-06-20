"""IG Other Account Preview Wrapper Class.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations


class IGOtherAccount:
    """IG Other Account Wrapper Class.

    Wrapper around list of other trading accounts for this client.

    Attributes:
        account_id: Unique identifier for account.
        account_name: Account name which can be seen in dashboard.
        preferred: Whether this is marked as preferred trading account.
        account_type: Trading account type e.g. CFD or SPREAD etc.
    """

    def __init__(self,
                 account_id: str,
                 account_name: str,
                 preferred: bool,
                 account_type: str):
        self.account_id = account_id
        self.account_name = account_name
        self.preferred = preferred
        self.account_type = account_type

    @staticmethod
    def parse_from_dict(res: dict) -> [IGOtherAccount]:
        """ Parses other accounts from account response into list of IGOtherAccount's.

        Args:
            res: IG other account data response in dictionary format.
        Returns:
            List of IGOtherAccounts parsed from response dict.
        """
        other_accounts = []
        for account in res:
            other_accounts.append(
                IGOtherAccount(
                    account['accountId'],
                    account['accountName'],
                    account['preferred'],
                    account['accountType']))
        return other_accounts
