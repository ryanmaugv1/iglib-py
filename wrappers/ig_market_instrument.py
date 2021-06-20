"""IG Market Instrument Data Wrapper Class.

Authored By Ryan Maugin (@ryanmaugv1)
"""

from __future__ import annotations

from iglib.exceptions import IGClientException


class IGMarketInstrument:
    """IG Market Instrument Data Wrapper Class.
    
    Attributes:
        bid_price: Bid price for instrument.
        delay_time: Price delay time if any.
        epic: Unique identifier for this market instrument e.g. DO.D.EURO.19.IP.
        expiry: Instrument expiry period.
        high_of_day: Highest price of day.
        low_of_day: Lowest price of day.
        name: Readable instrument name e.g. EUR/ISD
        type: Instrument type e.g. CURRENCIES, COMMODITIES, SHARES etc.
        status: Instrument status e.g. TRADEABLE, CLOSED, ON_AUCTION etc.
        net_change: Net price change since open.
        offer_price: Current instrument offer price.
        percentage_change: Percentage price change of day.
        scaling_factor: Multiplying factor to determine actual pip value.
        streaming_prices_available: True if streaming prices are available.
        local_update_time: Local time of last price change.
        update_time_utc: UTC locale time of last price change.
    """

    def __init__(self,
                 bid_price: float,
                 delay_time: float,
                 epic: str,
                 expiry: str,
                 high_of_day: float,
                 low_of_day: float,
                 name: str,
                 type: str,
                 status: str,
                 net_change: float,
                 offer_price: float,
                 percentage_change: float,
                 scaling_factor: float,
                 streaming_prices_available: bool,
                 local_update_time: str,
                 update_time_utc: str):
        self.bid_price = bid_price
        self.delay_time = delay_time
        self.epic = epic
        self.expiry = expiry
        self.high_of_day = high_of_day
        self.low_of_day = low_of_day
        self.name = name
        self.type = type
        self.status = status
        self.net_change = net_change
        self.offer_price = offer_price
        self.percentage_change = percentage_change
        self.scaling_factor = scaling_factor
        self.streaming_prices_available = streaming_prices_available
        self.local_update_time = local_update_time
        self.update_time_utc = update_time_utc

    @staticmethod
    def parse_first_entry_from_dict(search_term: str, market_instrument_res: dict) -> IGMarketInstrument:
        """Parses market instrument response into IGMarketInstrument.
        
        Args:
            search_term: Market instrument search query/term.
            market_instrument_res: List of returned market instruments matching searchTerm.
        Returns:
            IGMarketInstrument object parsed from HTTP response dictionary.
        Raises:
            Exception: If market instrument response is empty.
        """
        if len(market_instrument_res['markets']) == 0:
            raise IGClientException(
                'Could not parse first entry because no market instruments matched '
                + 'given searchTerm: "%s".' % search_term)
        entry = market_instrument_res['markets'][0]
        return IGMarketInstrument.parse_from_dict(entry)

    @staticmethod
    def parse_from_dict(res: dict) -> IGMarketInstrument:
        """Parses market instrument dict and returns IGMarketInstrument object.

        Args:
            res: IG market instrument data response in dictionary format.
        Returns:
            IG market instrument data wrapped into IGMarketInstrument object.
        """
        return IGMarketInstrument(
            res['bid'],
            res['delayTime'],
            res['epic'],
            res['expiry'],
            res['high'],
            res['low'],
            res['instrumentName'],
            res['instrumentType'],
            res['marketStatus'],
            res['netChange'],
            res['offer'],
            res['percentageChange'],
            res['scalingFactor'],
            res['streamingPricesAvailable'],
            res['updateTime'],
            res['updateTimeUTC'])


class UnitValPair:
    """Wrapper for Unit Value Pair Data."""

    def __init__(self, unit: str, value: float):
        self.unit = unit
        self.value = value

    @staticmethod
    def parse_from_dict(res: dict) -> UnitValPair:
        """Returns UnitValuePair parsed from response data."""
        return UnitValPair(res['unit'], res['value'])


class IGMarketDealingRules:
    """IG Market Instrument Dealing Rules Data Wrapper.

    Attributes:
        market_order_preference: Client's market order trading preference.
        max_stop_or_limit_distance: Max stop or limit distance allowed for order.
        min_controlled_risk_stop_distance: Min stop distance allowed for order.
        min_deal_size: Min allowed deal size for order.
        min_stop_or_limit_distance: Min stop or limit distance allowed for order.
        min_step_distance: Min step distance allowed on trailing stop order.
        trailing_stop_preference: Trailing stops trading preference for specified market.
    """

    def __init__(self,
                 market_order_preference: str,
                 max_stop_or_limit_distance: UnitValPair,
                 min_controlled_risk_stop_distance: UnitValPair,
                 min_deal_size: UnitValPair,
                 min_stop_or_limit_distance: UnitValPair,
                 min_step_distance: UnitValPair,
                 trailing_stop_preference: str):
        self.market_order_preference = market_order_preference
        self.max_stop_or_limit_distance = max_stop_or_limit_distance
        self.min_controlled_risk_stop_distance = min_controlled_risk_stop_distance
        self.min_deal_size = min_deal_size
        self.min_stop_or_limit_distance = min_stop_or_limit_distance
        self.min_step_distance = min_step_distance
        self.trailing_stop_preference = trailing_stop_preference

    @staticmethod
    def parse_from_dict(res: dict) -> IGMarketDealingRules:
        """Parses market dealing rules dict and returns IGMarketDealingRules object.

        Args:
            res: IG market dealing rules data response in dictionary format.
        Returns:
            IG market dealing rules data wrapped into IGMarketDealingRules object.
        """
        rules = res['dealingRules']
        return IGMarketDealingRules(
            rules['marketOrderPreference'],
            UnitValPair.parse_from_dict(rules['maxStopOrLimitDistance']),
            UnitValPair.parse_from_dict(rules['minControlledRiskStopDistance']),
            UnitValPair.parse_from_dict(rules['minDealSize']),
            UnitValPair.parse_from_dict(rules['minNormalStopOrLimitDistance']),
            UnitValPair.parse_from_dict(rules['minStepDistance']),
            rules['trailingStopsPreference'])


class IGMarketInstrumentDetails:
    """IG Market Instrument Details Data Wrapper.

    Attributes:
        chart_code: Chart code.
        contract_size: Contract size.
        controlled_risk_allowed: True if controlled risk trades are allowed.
        country: Country.
        currencies: Traded currencies details.
        epic: Unique identifier for this market instrument e.g. DO.D.EURO.19.IP.
        expiry: Instrument expiry period.
        expiry_details: Market expiry details.
        force_open_allowed: True if force open is allowed.
        limited_risk_premium: The limited risk premium.
        lot_size: Single lot size.
        margin_deposit_bands: Object containing margin deposit bands.
        margin_factor: Margin requirement factor.
        margin_factor_unit: Describes the dimension for a dealing rule value.
        market_id: Market identifier.
        name: Market instrument name.
        news_code: Reuters news code.
        one_pip_means: Meaning of one pip.
        opening_hours: Market open and close times.
        rollover_details: Market rollover details.
        slippage_factor: Slippage factor details for a given market.
        special_info: List of special information notices.
        sprint_market_max_expiry_time: For sprint markets only, the maximum
            value to be specified as the expiry of a sprint markets trade.
        sprint_market_min_expiry_time: For sprint markets only, the minimum
            value to be specified as the expiry of a sprint markets trade.
        stop_limits_allowed: True if stops and limits are allowed.
        streaming_prices_available: True if streaming prices are available.
        type: Instrument type.
        unit: Unit used to qualify the size of a trade.
        value_of_one_pip: Value of one pip.
    """

    def __init__(self,
                 chart_code: str,
                 contract_size: str,
                 controlled_risk_allowed: bool,
                 country: str,
                 currencies: [dict],
                 epic: str,
                 expiry: str,
                 expiry_details: dict,
                 force_open_allowed: bool,
                 limited_risk_premium: dict,
                 lot_size: float,
                 margin_deposit_bands: [dict],
                 margin_factor: float,
                 margin_factor_unit: str,
                 market_id: str,
                 name: str,
                 news_code: str,
                 one_pip_means: str,
                 opening_hours: dict,
                 rollover_details: dict,
                 slippage_factor: UnitValPair,
                 special_info: [dict],
                 sprint_market_max_expiry_time: float,
                 sprint_market_min_expiry_time: float,
                 stop_limits_allowed: bool,
                 streaming_prices_available: bool,
                 type: str,
                 unit: str,
                 value_of_one_pip: str):
        self.chart_code = chart_code
        self.contract_size = contract_size
        self.controlled_risk_allowed = controlled_risk_allowed
        self.country = country
        self.currencies = currencies
        self.epic = epic
        self.expiry = expiry
        self.expiry_details = expiry_details
        self.force_open_allowed = force_open_allowed
        self.limited_risk_premium = limited_risk_premium
        self.lot_size = lot_size
        self.margin_deposit_bands = margin_deposit_bands
        self.margin_factor = margin_factor
        self.margin_factor_unit = margin_factor_unit
        self.market_id = market_id
        self.name = name
        self.news_code = news_code
        self.one_pip_means = one_pip_means
        self.opening_hours = opening_hours
        self.rollover_details = rollover_details
        self.slippage_factor = slippage_factor
        self.special_info = special_info
        self.sprint_market_max_expiry_time = sprint_market_max_expiry_time
        self.sprint_market_min_expiry_time = sprint_market_min_expiry_time
        self.stop_limits_allowed = stop_limits_allowed
        self.streaming_prices_available = streaming_prices_available
        self.type = type
        self.unit = unit
        self.value_of_one_pip = value_of_one_pip

    @staticmethod
    def parse_from_dict(res: dict) -> IGMarketInstrumentDetails:
        """Parses market details dict and returns IGMarketInstrumentDetails object.

        Args:
            res: IG market details data response in dictionary format.
        Returns:
            IG market detail data wrapped into IGMarketInstrumentDetails object.
        """
        details = res['instrument']
        return IGMarketInstrumentDetails(
            details['chartCode'],
            details['contractSize'],
            details['controlledRiskAllowed'],
            details['country'],
            details['currencies'],
            details['epic'],
            details['expiry'],
            details['expiryDetails'],
            details['forceOpenAllowed'],
            details['limitedRiskPremium'],
            details['lotSize'],
            details['marginDepositBands'],
            details['marginFactor'],
            details['marginFactorUnit'],
            details['marketId'],
            details['name'],
            details['newsCode'],
            details['onePipMeans'],
            details['openingHours'],
            details['rolloverDetails'],
            details['slippageFactor'],
            details['specialInfo'],
            details['sprintMarketsMaximumExpiryTime'],
            details['sprintMarketsMinimumExpiryTime'],
            details['stopsLimitsAllowed'],
            details['streamingPricesAvailable'],
            details['type'],
            details['unit'],
            details['valueOfOnePip'])


class IGMarketInstrumentSnapshot:
    """IG Market Instrument Snapshot Data Wrapper.

    Attributes:
        bid: Bid price.
        binary_odds: Binary odds.
        controlled_risk_extra_spread:number of points to add on each
            side of the market as an additional spread when placing a
            guaranteed stop trade.
        decimal_places_factor: Number of decimal positions for market levels.
        delay_time: Price delay time.
        high: Highest price of day.
        low: Lowest price of day.
        status: Describes the current status of a given market.
        net_change: Net price change on the day.
        offer: Offer price.
        percentage_change: Percentage price change on the day.
        scaling_factor: Percentage price change on the day. Multiplying factor
            to determine actual pip value for the levels used by the instrument.
        update_time: Price last update time (hh:mm:ss).
    """

    def __init__(self,
                 bid: float,
                 binary_odds: float,
                 controlled_risk_extra_spread: float,
                 decimal_places_factor: float,
                 delay_time: float,
                 high: float,
                 low: float,
                 status: str,
                 net_change: float,
                 offer: float,
                 percentage_change: float,
                 scaling_factor: float,
                 update_time: str):
        self.bid = bid
        self.binary_odds = binary_odds
        self.controlled_risk_extra_spread = controlled_risk_extra_spread
        self.decimal_places_factor = decimal_places_factor
        self.delay_time = delay_time
        self.high = high
        self.low = low
        self.status = status
        self.net_change = net_change
        self.offer = offer
        self.percentage_change = percentage_change
        self.scaling_factor = scaling_factor
        self.update_time = update_time

    @staticmethod
    def parse_from_dict(res: dict) -> IGMarketInstrumentSnapshot:
        """Parses market snapshot dict and returns IGMarketInstrumentSnapshot object.

        Args:
            res: IG market snapshot data response in dictionary format.
        Returns:
            IG market snapshot data wrapped into IGMarketInstrumentSnapshot object.
        """
        snapshot = res['snapshot']
        return IGMarketInstrumentSnapshot(
            snapshot['bid'],
            snapshot['binaryOdds'],
            snapshot['controlledRiskExtraSpread'],
            snapshot['decimalPlacesFactor'],
            snapshot['delayTime'],
            snapshot['high'],
            snapshot['low'],
            snapshot['marketStatus'],
            snapshot['netChange'],
            snapshot['offer'],
            snapshot['percentageChange'],
            snapshot['scalingFactor'],
            snapshot['updateTime'])
