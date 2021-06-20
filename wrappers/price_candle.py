"""Wrapper for single price action candle. 

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations


class PriceSnapshot:
    """Wrapper for Price Snapshot Data.
    
    Attributes:
        ask: Ask price for market instrument.
        bid: Bid prices for market instrument.
        last_traded: Last traded price (null for non exchange-traded instruments).
    """

    def __init__(self, ask: float, bid: float, last_traded: float):
        self.ask = ask
        self.bid = bid
        self.last_traded = last_traded

    @staticmethod
    def parse_from_dict(res: dict) -> PriceSnapshot:
        """Parses price snapshot data into PriceSnapshot class.
        
        Args:
            res: Response dictionary containing price snapshot.
        Returns:
            PriceSnapshot class containing response price snapshot data.
        """
        return PriceSnapshot(res['ask'], res['bid'], res['lastTraded'])


class PriceCandle:
    """Wrapper for Single Price Action Candle Data.
    
    Attributes:
        open_price: Opening price of candle.
        close_price: Closing price of candle.
        low: Lowest price for candle.
        high: Highest price for candle.
        last_traded_volume: Last traded volume (null for non exchange-traded instruments).
        snapshot_time: Snapshot local time, format is yyyy/MM/dd hh:mm:ss.
    """

    def __init__(self,
                 open_price: PriceSnapshot,
                 close_price: PriceSnapshot,
                 low: PriceSnapshot,
                 high: PriceSnapshot,
                 last_traded_volume: float,
                 snapshot_time: str):
        self.open_price = open_price
        self.close_price = close_price
        self.low = low
        self.high = high
        self.last_traded_volume = last_traded_volume
        self.snapshot_time = snapshot_time

    @staticmethod
    def parse_from_dict(res: dict) -> [PriceCandle]:
        """Parses price candle response data into PriceCandle class.
        
        Args:
            res: Response dictionary containing price list.
        Returns:
            List of historical price parsed into PriceCandle wrappers.
        """
        if len(res['prices']) == 0:
            return []

        price_candles = []
        for priceEntry in res['prices']:
            price_candles.append(
                PriceCandle(
                    PriceSnapshot.parse_from_dict(priceEntry['openPrice']),
                    PriceSnapshot.parse_from_dict(priceEntry['closePrice']),
                    PriceSnapshot.parse_from_dict(priceEntry['lowPrice']),
                    PriceSnapshot.parse_from_dict(priceEntry['highPrice']),
                    priceEntry['lastTradedVolume'],
                    priceEntry['snapshotTime']))
        return price_candles
