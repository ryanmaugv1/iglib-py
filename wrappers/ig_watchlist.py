"""IG Eatchlist Data Wrapper Class.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations

from typing import List


class IGWatchlist:
    """IG Watchlist Data Wrapper Class.

    Attributes:
        default_system_watchlist: True if this watchlist is a system predefined one.
        deletable: True if this watchlist can be deleted by the user.
        editable: True if this watchlist can be altered by the user.
        id: Watchlist identifier.
        name: Watchlist name.
    """

    def __init__(self, default_system_watchlist: bool, deletable: bool, editable: bool, id: str, name: str):
        self.default_system_watchlist = default_system_watchlist
        self.deletable = deletable
        self.editable = editable
        self.id = id
        self.name = name

    @staticmethod
    def parse_from_dict(res: dict) -> List[IGWatchlist]:
        """Parses market watchlist dict and returns list of IGWatchlist object.

        Args:
            res: IG watchlist data response in dictionary format.
        Returns:
            List of IG watchlist data wrapped into IGMarketInstrument object.
        """
        watchlists = []
        for watchlist in res['watchlists']:
            watchlists.append(
                IGWatchlist(
                    watchlist['defaultSystemWatchlist'],
                    watchlist['deleteable'],
                    watchlist['editable'],
                    watchlist['id'],
                    watchlist['name']))
        return watchlists
