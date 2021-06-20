"""IG Account Working Order Data Wrapper Class.

Authored By TheCeriousBoi [TCB] (@theceriousboi)
"""

from __future__ import annotations

from iglib.wrappers.ig_position import IGPosition
from iglib.wrappers.ig_market_instrument import IGMarketInstrument


class IGWorkingOrder:
    """Wrapper Class for IG Account Working Orders.

    Attributes:
        is_dma: True if this is a DMA working order.
        good_till_date: Datetime (yyyy/MM/dd hh:mm) the WO will be deleted if not triggered.
        good_till_date_iso: Datetime the working order will be deleted if not triggered.
        market_data: Working order market data.
        position_data: Working order position data.
    """

    def __init__(self,
                 is_dma: bool,
                 good_till_date: str,
                 good_till_date_iso: str,
                 market_data: IGMarketInstrument,
                 position_data: IGPosition):
        self.is_dma = is_dma
        self.good_till_date = good_till_date
        self.good_till_date_iso = good_till_date_iso
        self.market_data = market_data
        self.position_data = position_data

    @staticmethod
    def parse_from_dict(res: dict) -> [IGWorkingOrder]:
        """Parses market instrument dict and returns IGMarketInstrument object.

        Args:
            res: IG market instrument data response in dictionary format.
        Returns:
            IG market instrument data wrapped into IGMarketInstrument object.
        """
        working_orders = []
        for working_order in res['workingOrders']:
            working_orders.append(
                IGWorkingOrder(
                    working_order['workingOrderData']['dma'],
                    working_order['workingOrderData']['goodTillDate'],
                    working_order['workingOrderData']['goodTillDateISO'],
                    IGMarketInstrument.parse_from_dict(working_order['marketData']),
                    IGPosition.parse_from_dict(working_order['workingOrderData'])))
        return working_orders
