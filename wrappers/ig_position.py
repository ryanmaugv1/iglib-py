"""IG Account Positions Data Wrapper Class.

Authored By TheCeriousBoi [TCB] (@theceriousboi)
"""

from __future__ import annotations

from iglib.enums.order_direction import OrderDirection
from iglib.wrappers.ig_market_instrument import IGMarketInstrument


class IGPosition:
    """Wrapper Class for IG Account Positions.

    Attributes:
        market: IGMarketInstrument whom this order is for.
        contract_size: Size of contract in points.
        controlled_risk: True if position is risk controlled
        created_date: Local date the position was opened
        created_date_utc: Date the position was opened
        currency: Position currency ISO code
        deal_id: Unique deal identifier.
        deal_reference: Reference to deal.
        direction: Deal order direction e.g. BUY or SELL.
        level: Level at which the position was opened.
        limit_level: Level at which order limit is set.
        size: Size of deal.
        stop_level: Level at which stop limit is set.
        trailing_step_size: Trailing stop step size.
        trailing_stop_distance: Distance between order level and trailing stop level.
    """

    def __init__(self,
                 market: IGMarketInstrument,
                 contract_size: float,
                 controlled_risk: bool,
                 created_date: str,
                 created_date_utc: str,
                 currency: str,
                 deal_id: str,
                 deal_reference: str,
                 direction: OrderDirection,
                 level: float,
                 limit_level: float,
                 size: float,
                 stop_level: float,
                 trailing_step_size: float,
                 trailing_stop_distance: float):
        self.market = market
        self.contract_size = contract_size
        self.controlled_risk = controlled_risk
        self.created_date = created_date
        self.created_date_utc = created_date_utc
        self.currency = currency
        self.deal_id = deal_id
        self.deal_reference = deal_reference
        self.direction = direction
        self.level = level
        self.limit_level = limit_level
        self.size = size
        self.stop_level = stop_level
        self.trailing_step_size = trailing_step_size
        self.trailing_stop_distance = trailing_stop_distance

    @staticmethod
    def parse_from_dict(res: dict) -> [IGPosition]:
        """ Parses IGPosition from positions response dictionary.

        Args:
            res: Position response dictionary.
        Returns:
            List of IGPositions wrapping all account position data.
        """
        positions = []
        for position_entry in res['positions']:
            position = position_entry['position']
            market = IGMarketInstrument.parse_from_dict(position_entry['market'])
            positions.append(
                IGPosition(
                    market,
                    position['contractSize'],
                    position['controlledRisk'],
                    position['createdDate'],
                    position['createdDateUTC'],
                    position['currency'],
                    position['dealId'],
                    position['dealReference'],
                    OrderDirection[position['direction']],
                    position['level'],
                    position['limitLevel'],
                    position['size'],
                    position['stopLevel'],
                    position['trailingStep'],
                    position['trailingStopDistance']))
        return positions
