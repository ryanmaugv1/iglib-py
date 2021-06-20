"""Client wrapper for IG brokerage API.

Provides methods that abstract away API interface between application and
IG broker API. This client fully supports all requests available from API
and handles data conversions and formatting into wrappers for convenience.

Authored By Ryan Maugin (@ryanmaugv1)
"""
from __future__ import annotations

import json
from typing import Any

import jsonpickle
import requests
from absl import logging
from urllib.parse import urlencode, quote_plus

from iglib.exceptions import IGClientException
from iglib.exceptions import IGServerException
from iglib.enums.order_direction import OrderDirection
from iglib.enums.price_resolution import PriceResolution
from iglib.enums.request_type import RequestType
from iglib.wrappers.ig_working_order import IGWorkingOrder
from iglib.wrappers.ig_transaction import IGTransaction
from iglib.wrappers.ig_account import IGAccount
from iglib.wrappers.ig_activity import IGActivity
from iglib.wrappers.ig_watchlist import IGWatchlist
from iglib.wrappers.ig_market_instrument import IGMarketInstrument
from iglib.wrappers.ig_market_instrument import IGMarketDealingRules
from iglib.wrappers.ig_market_instrument import IGMarketInstrumentDetails
from iglib.wrappers.ig_market_instrument import IGMarketInstrumentSnapshot
from iglib.wrappers.ig_position import IGPosition
from iglib.wrappers.ig_price_allowance import IGPriceAllowance
from iglib.wrappers.price_candle import PriceCandle
from utility.constants import Constants


class IGClient:
    """Client Wrapper for IG Broker API.

    Attributes:
        key: IG API key for account.
        identifier: API credential username/identifier for account.
        password: API credentials password for account.
        demo: Whether account we are authenticating into is demo API account.
    """

    def __init__(self, key: str, identifier: str, password: str, demo: bool = True, dry_run: bool = False):
        self.key = key
        self.identifier = identifier
        self.password = password
        self.demo = demo
        self.dry_run = dry_run
        self.account: IGAccount = None
        self.cst = None
        self.securityToken = None

    def serialize(self) -> dict:
        """Returns serialized client in JSON representation."""
        return jsonpickle.encode(self)

    @staticmethod
    def deserialize(encoding: dict) -> IGClient:
        """Deserializes JSON encoded/serialized client instance.

        Args:
            encoding: Serialized IGClient instance.
        Returns:
            Deserialized instance of IGClient class.
        """
        return jsonpickle.decode(encoding)

    def authenticate(self) -> None:
        """Authentication request to get tokens needed for subsequent requests.

        Raises:
            Exception: If request to authenticate into account failed.
        """
        logging.info(Constants.LOG_SEPARATOR)
        logging.info('AUTHENTICATING')
        logging.info(Constants.LOG_SEPARATOR)
        logging.info('Logging into "%s" account...', self.identifier)

        url = '%s/session' % self._get_base_api_url()
        headers = {'X-IG-API-KEY': self.key, 'VERSION': '2'}
        payload = {'identifier': self.identifier, 'password': self.password}
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        if not response.ok:
            raise IGServerException(
                'Failed to log_details into "%s" account with error: %s'
                % (self.identifier, response.json()['errorCode']))
        logging.info('Successfully logged into "%s" account.', self.identifier)

        self.cst = response.headers['CST']
        self.securityToken = response.headers['X-SECURITY-TOKEN']
        self.account = IGAccount.parse_from_dict(response.json())

        logging.info('CST Token: %s', self.cst)
        logging.info('Security Token: %s', self.securityToken)
        self.account.log_details()

    def is_logged_in(self):
        """Returns true if user is logged into IG account."""
        return self.account is not None

    def get_account(self) -> IGAccount:
        """Returns IGAccount object containing all account data."""
        return self.account

    def switch_active_account(self, account_id: str) -> None:
        """Switches active account and sets it as `default/preferred` account.

        Args:
            account_id: Identifier for account to switch to.
        Raises:
            Exception: If request to switch account failed.
        """
        url = '%s/session' % self._get_base_api_url()
        payload = {'accountId': account_id, 'defaultAccount': False if self.dry_run else True}
        response = self._request(RequestType.PUT, url, payload=payload, version=1)
        if response.ok:
            # Logout and authenticate into switched account.
            if not self.dry_run:
                self.authenticate()
        else:
            raise IGServerException('Account switch failed with following error: %s' % response.json()['errorCode'])

    def get_market_instrument(self, search_term: str) -> IGMarketInstrument:
        """Get first/top market entry for search term matches.

        Args:
            search_term: The term to be used in market search.
        Returns:
            First/top market entry which matches search term.
        Raises:
            Exception: If request to get market instrument data failed.
        """
        url = '%s/markets?searchTerm=%s' % (self._get_base_api_url(), quote_plus(search_term))
        response = self._request(RequestType.GET, url, version=1)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch market instrument with following error: %s' % response.json()['errorCode'])
        return IGMarketInstrument.parse_first_entry_from_dict(search_term, response.json())

    def get_market_instrument_dealing_rules(self, epic: str) -> IGMarketDealingRules:
        """Get market instrument dealing rules.

        Args:
            epic: The epic of the market instrument to retrieve dealing rules for.
        Returns:
            IGMarketDealing rule which wraps IG market dealing rules response data.
        Raises:
            Exception: If request to get market instrument dealing rules failed.
        """
        url = '%s/markets/%s' % (self._get_base_api_url(), quote_plus(epic))
        response = self._request(RequestType.GET, url, version=3)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch market dealing rules with follow error: %s' % response.json()['errorCode'])
        return IGMarketDealingRules.parse_from_dict(response.json())

    def get_market_instrument_details(self, epic: str) -> IGMarketInstrumentDetails:
        """Get market instrument details.

        Args:
            epic: The epic of the market instrument to retrieve details for.
        Returns:
            IGMarketInstrumentDetails which wraps IG market details response data.
        Raises:
            Exception: If request to get market instrument details failed.
        """
        url = '%s/markets/%s' % (self._get_base_api_url(), quote_plus(epic))
        response = self._request(RequestType.GET, url, version=3)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch market details with follow error: %s' % response.json()['errorCode'])
        return IGMarketInstrumentDetails.parse_from_dict(response.json())

    def get_market_instrument_snapshot(self, epic: str) -> IGMarketInstrumentSnapshot:
        """Get market instrument snapshot.

        Args:
            epic: The epic of the market instrument to retrieve snapshot for.
        Returns:
            IGMarketInstrumentSnapshot which wraps IG market snapshot response data.
        Raises:
            Exception: If request to get market instrument snapshot failed.
        """
        url = '%s/markets/%s' % (self._get_base_api_url(), quote_plus(epic))
        response = self._request(RequestType.GET, url, version=3)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch market snapshot with follow error: %s' % response.json()['errorCode'])
        return IGMarketInstrumentSnapshot.parse_from_dict(response.json())

    def get_price_fetch_allowance(self) -> IGPriceAllowance:
        """Returns dictionary containing API price fetch allowance data.

        Performs a request for historical price data with hardcoded parameters
        but only accesses the allowance property and returns it.

        Returns:
            IGPriceAllowance object containing all data related to API allowance.
        Raises:
            Exception: If request to get price fetch allowance failed.
        """
        url = '%s/prices/%s/%s/%s/%s' % (
            self._get_base_api_url(),
            'DO.D.EURO.19.IP', 'DAY', '2020-01-01 11:00:00', '2020-01-01 12:00:00')
        response = self._request(RequestType.GET, url, version=2)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch price allowance with following error: %s' % response.json()['errorCode'])
        return IGPriceAllowance.parse_from_dict(response.json()['allowance'])

    def get_historical_price(
            self, epic: str, resolution: PriceResolution, from_date: str, to_date: str) -> [PriceCandle]:
        """Get historical candle price data within specific date range.

        Fetch historical price candle data between specified time range using
        specific resolution e.g. MINUTE_15 will fetch all 15 minute candles price
        data within time range.

        Args:
            epic: Unique instrument identifier e.g. DO.D.EURO.19.IP.
            resolution: Price/time resolution for each candle to fetch.
            from_date: Start date (yyyy-MM-dd HH:mm:ss).
            to_date: End date (must be later then the start date).
        Returns:
            List of all PriceCandle's fetched price candles between date range.
        Raises:
            Exception: If request to get historical price data failed.
        """
        url = '%s/prices/%s/%s/%s/%s' % (self._get_base_api_url(), epic, resolution.name, from_date, to_date)
        response = self._request(RequestType.GET, url)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch historical price data with following error: %s' % response.json()['errorCode'])
        return PriceCandle.parse_from_dict(response.json())

    def get_all_working_orders(self) -> [IGWorkingOrder]:
        """Returns all working orders for account.

        Raises:
            Exception: If request to get all working orders failed.
        """
        url = '%s/workingorders' % self._get_base_api_url()
        response = self._request(RequestType.GET, url)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch working orders data with following error: %s' % response.json()['errorCode'])
        return IGWorkingOrder.parse_from_dict(response.json())

    def get_all_open_positions(self) -> [IGPosition]:
        """Returns list of IGPosition objects containing all open account positions.

        Raises:
            Exception: If request to get all open positions failed.
        """
        url = '%s/positions' % self._get_base_api_url()
        response = self._request(RequestType.GET, url)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch account positions with following error: %s' % response.json()['errorCode'])
        return IGPosition.parse_from_dict(response.json())

    def get_open_position_by_deal_ref(self, deal_ref: str) -> IGPosition:
        """Get open position by deal reference.

        Args:
            deal_ref: Deal reference for open position to get.
        Returns:
            IGPosition if an open position with specified deal reference was found else None.
        Raises:
            Exception: if no open position with given deal reference was found.
        """
        open_positions = self.get_all_open_positions()
        target_position = None
        for position in open_positions:
            if position.deal_reference == deal_ref:
                target_position = position
        if target_position is None:
            raise IGClientException(
                'Cannot get open position with deal reference: %s because it does not exist.' % deal_ref)
        return target_position

    def open_market_order(self,
                          deal_reference: str,
                          market_instrument: IGMarketInstrument,
                          direction: OrderDirection,
                          size: float,
                          limit_distance: float = None,
                          stop_distance: float = None,
                          limit_level: float = None,
                          stop_level: float = None,
                          guaranteed_stop: float = False,
                          time_in_force: str = "FILL_OR_KILL") -> dict:
        """Creates an other-the-counter (OTC) limit position.

        Args:
            deal_reference: A user-defined reference identifying the submission of the order.
            market_instrument: Market instrument to open position on.
            direction: Deal direction e.g. BUY or SELL.
            size: Deal size specified in points.
            limit_distance: Take profit limit distance from order level in points e.g. 10 = $10.
            stop_distance: Stop loss level distance from order level in points.
            limit_level: Order limit level.
            stop_level: Order stop level.
            guaranteed_stop: True if a guaranteed stop is required (comes with increased spreads).
            time_in_force: The time in force determines the order fill strategy e.g.
                FILL_OR_KILL or EXECUTE_AND_ELIMINATE.
        Returns:
            Returns dict containing deal reference if operation succeeded else empty dict.
        Raises:
            Exception: If request to create OTC position failed.
        """
        payload = {
            'dealReference': deal_reference,
            "epic": market_instrument.epic,
            "expiry": market_instrument.expiry,
            "direction": direction.name,
            "size": size,
            "orderType": "MARKET",
            "timeInForce": time_in_force,
            "guaranteedStop": guaranteed_stop,
            "forceOpen": True,
            "currencyCode": "GBP"
        }

        if market_instrument.status == 'CLOSED':
            raise IGClientException("Cannot place order on CLOSED market instrument.")
        if limit_distance is not None and limit_level is not None:
            raise IGClientException('Only one "limit_level" or "limit_distance" can be set on order.')
        if stop_distance is not None and stop_level is not None:
            raise IGClientException('Only one "stop_level" or "stop_distance" can be on order.')
        if stop_distance is None and stop_level is None:
            raise IGClientException('One of "stop_level" or "stop_distance" must be set on order.')
        if limit_distance is None and limit_level is None:
            raise IGClientException('One of "limit_level" or "limit_distance" must be set on order.')

        payload = self._add_if_not_none(payload, 'limitDistance', limit_distance)
        payload = self._add_if_not_none(payload, 'stopDistance', stop_distance)
        payload = self._add_if_not_none(payload, 'limitLevel', limit_level)
        payload = self._add_if_not_none(payload, 'stopLevel', stop_level)

        self._validate_order_limit_params(
            market_instrument,
            size,
            direction,
            limit_distance=limit_distance,
            stop_distance=stop_distance,
            stop_level=stop_level,
            limit_level=limit_level)

        url = '%s/positions/otc' % self._get_base_api_url()
        response = self._request(RequestType.POST, url, payload=payload)
        if not response.ok:
            raise IGServerException(
                'Failed to open market OTC position with following error: %s' % response.json()['errorCode'])
        return response.json()

    def open_trailing_market_order(self,
                                   deal_reference: str,
                                   market_instrument: IGMarketInstrument,
                                   direction: OrderDirection,
                                   size: float,
                                   stop_distance: float,
                                   stop_increment: float,
                                   limit_level: float = None,
                                   limit_distance: float = None,
                                   time_in_force: str = 'FILL_OR_KILL') -> dict:
        """ """
        payload = {
            'dealReference': deal_reference,
            'epic': market_instrument.epic,
            'expiry': market_instrument.expiry,
            'direction': direction.name,
            'size': size,
            'trailingStop': True,
            'stopDistance': stop_distance,
            'trailingStopIncrement': stop_increment,
            'limitDistance': limit_distance,
            'limitLevel': limit_level,
            'timeInForce': time_in_force,
            'forceOpen': True,
            'guaranteedStop': False,
            'orderType': 'MARKET',
            'currencyCode': 'GBP'
        }

        if market_instrument.status == 'CLOSED':
            raise IGClientException("Cannot place order on CLOSED market instrument.")
        if limit_distance is not None and limit_level is not None:
            raise IGClientException('Only one "limit_level" or "limit_distance" can be set on order.')
        if limit_distance is None and limit_level is None:
            raise IGClientException('One of "limit_level" or "limit_distance" must be set on order.')

        payload = self._add_if_not_none(payload, 'limitDistance', limit_distance)
        payload = self._add_if_not_none(payload, 'limitLevel', limit_level)

        self._validate_order_limit_params(
            market_instrument,
            size,
            direction,
            limit_level=limit_level,
            limit_distance=limit_distance,
            stop_distance=stop_distance,
            stop_increment=stop_increment)

        url = '%s/positions/otc' % self._get_base_api_url()
        response = self._request(RequestType.POST, url, payload=payload)
        if not response.ok:
            raise IGServerException(
                'Failed to open trailing market OTC position with following error: %s' % response.json()['errorCode'])
        return response.json()

    def close_market_order(self, position: IGPosition, size: float = None, time_in_force: str = 'FILL_OR_KILL') -> dict:
        """Creates a close market order for other-the-counter (OTC) position.

        Args:
            position: Reference to position to close.
            size: Size of the order to sell (must be smaller or equal to position size).
            time_in_force: The time in force determines the order fill strategy.
        Returns:
            Returns dict containing deal reference if operation succeeded else empty dict.
        Raises:
            Exception: If request to create close order for OTC position failed or size arg is invalid.
        """
        if position.market.status == 'CLOSED':
            raise IGClientException("Cannot close order on CLOSED market instrument.")
        if size <= 0:
            raise IGClientException('Close order size must be positive and greater than 0.')
        if size > position.size:
            raise IGClientException(
                'Close order size (%s) cannot exceed that of position (%s).' % (size, position.size))

        payload = {
            'dealId': position.deal_id,
            'direction': 'SELL' if position.direction == OrderDirection.BUY else 'BUY',
            'size': position.size,
            'timeInForce': time_in_force,
            'orderType': "MARKET"
        }

        # Update the position size to sell ti a custom amount.
        if size is not None:
            payload['size'] = size

        url = '%s/positions/otc' % self._get_base_api_url()
        response = self._request(RequestType.DELETE, url, payload, version=1)
        if not response.ok:
            raise IGServerException(
                'Failed to create close market order with following error: %s' % response.json()['errorCode'])
        return response.json()

    def update_position(self, position: IGPosition, limit_level: float = None, stop_level: bool = None) -> dict:
        """Updates an open non-trailing OTC position.

        Args:
            position: Position to be updated.
            limit_level: New limit level.
            stop_level: New stop level.
        Returns:
            Returns dict containing deal reference if operation succeeded else empty dict.
        Raises:
            Exception: If request to update position failed.
        """
        payload = {
            'limitLevel': limit_level if limit_level is not None else position.limit_level,
            'stopLevel': stop_level if stop_level is not None else position.stop_level,
            'trailingStop': False
        }

        if position.market.status == 'CLOSED':
            raise IGClientException("Cannot update position on CLOSED market instrument.")

        self._validate_order_limit_params(
            position.market,
            position.size,
            position.direction,
            limit_level=limit_level,
            stop_level=stop_level)

        url = '%s/positions/otc/%s' % (self._get_base_api_url(), position.deal_id)
        response = self._request(RequestType.PUT, url, payload)
        if not response.ok:
            raise IGServerException(
                'Failed request to update position with following error: %s' % response.json()['errorCode'])
        return response.json()

    def update_trailing_position(self,
                                 position: IGPosition,
                                 stop_level: float = None,
                                 trail_distance: float = None,
                                 trail_increment: float = None) -> dict:
        """Updates an open trailing stop position.

        Args:
            position: Position to be updated.
            stop_level: New stop level.
            trail_distance: New trailing stop distance.
            trail_increment: New trailing stop increment.
        Returns:
            Returns dict containing deal reference if operation succeeded else empty dict.
        Raises:
            Exception: if request to update position failed.
        """
        payload = {
            'stopLevel': stop_level if stop_level is not None else position.stop_level,
            'trailingStopDistance': trail_distance if trail_distance is not None else position.trailing_stop_distance,
            'trailingStopIncrement': trail_increment if trail_increment is not None else position.trailing_step_size,
            'trailingStop': False
        }

        if position.market.status == 'CLOSED':
            raise IGClientException("Cannot update order on CLOSED market instrument.")

        self._validate_order_limit_params(
            position.market,
            position.size,
            position.direction,
            stop_level=stop_level,
            stop_distance=trail_distance,
            stop_increment=trail_increment)

        url = '%s/positions/otc/%s' % (self._get_base_api_url(), position.deal_id)
        response = self._request(RequestType.PUT, url, payload)
        if not response.ok:
            raise IGServerException(
                'Failed request to update position with following error: %s' % response.json()['errorCode'])
        return response.json()

    def get_activity(self, from_date: str, to_date: str = None, detailed: bool = False) -> [IGActivity]:
        """Get all historical account activity within date range.

        Args:
            from_date: Start date e.g. yyyy-MM-dd HH:mm:ss.
            to_date: End date (Default = current time).
            detailed: Retrieve additional details about the activity.
        Returns:
            Returns list of IGActivity from response.
        Raises:
            Exception: If request to get activity failed.
        """
        if to_date is not None:
            payload = {'from': from_date, 'to': to_date, 'detailed': detailed}
        else:
            payload = {'from': from_date, 'detailed': detailed}

        url = '%s/history/activity?%s' % (self._get_base_api_url(), urlencode(payload))
        response = self._request(RequestType.GET, url, version=3)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch account activity with following error: %s' % response.json()['errorCode'])
        return IGActivity.parse_from_dict(response.json())

    def get_activity_from_deal_id(
            self, deal_id: str, from_date: str, to_date: str = None, detailed: bool = False) -> IGActivity:
        """Get historical account activity with matching dealId within specified timeframe.

        Args:
            deal_id: Unique deal identifier for activity.
            from_date: Start date e.g. yyyy-MM-dd HH:mm:ss.
            to_date: End date (Default = current time).
            detailed: Retrieve additional details about the activity.
        Returns:
            IGActivity matching specified dealId or None if no match found.
        Raises:
            Exception: If request to get activity failed.
        """
        payload = {'dealId': deal_id, 'from': from_date, 'detailed': detailed}
        if to_date is not None:
            payload = {'to': to_date}

        url = '%s/history/activity?%s' % (self._get_base_api_url(), urlencode(payload))
        response = self._request(RequestType.GET, url, version=3)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch account activity with following error: %s' % response.json()['errorCode'])
        return IGActivity.parse_from_dict(response.json())[0]

    def get_activity_from_filter(
            self, fiql: str, from_date: str, to_date: str = None, detailed: bool = False) -> IGActivity:
        """Get all historical account activity.

        Performs a request for activities using very simple FIQL query syntax.

        Examples:

        channel == SYSTEM; type == POSITION
        (Fetch activity which have SYSTEM channel AND have type POSITION).

        channel == SYSTEM, type == POSITION
        (Fetch activity which have SYSTEM channel OR have type POSITION)

        Find out more:
        https://fiql-parser.readthedocs.io/en/stable/usage.html

        Args:
            fiql: FIQL filter (supported operators: ==|!=|,|;).
            from_date: Start date e.g. yyyy-MM-dd HH:mm:ss.
            to_date: End date (Default = current time).
            detailed: Retrieve additional details about the activity.
        Returns:
            List of IGActivity's matching filter else `None` if no matches found.
        Raises:
            Exception: If request to get activity failed.
        """
        payload = {'filter': fiql, 'from': from_date, 'detailed': detailed}
        if to_date is not None:
            payload = {'to': to_date}

        url = '%s/history/activity?%s' % (self._get_base_api_url(), urlencode(payload))
        response = self._request(RequestType.GET, url, version=3)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch account activity with following error: %s' % response.json()['errorCode'])
        return IGActivity.parse_from_dict(response.json())

    def get_transactions(self, from_date: str, to_date: str = None) -> [IGTransaction]:
        """ Get all account transactions within specified date range.

        Args:
            from_date: Start date e.g. yyyy-MM-dd HH:mm:ss.
            to_date: End date (Default = current time).
        Returns:
            List of IGTransaction's found within searched time range.
        Raises:
            Exception: If request to get transactions failed.
        """
        payload = {'from': from_date}
        if to_date is not None:
            payload['to'] = to_date

        url = '%s/history/transactions?%s' % (self._get_base_api_url(), urlencode(payload))
        response = self._request(RequestType.GET, url)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch account transaction with following error: %s' % response.json()['errorCode'])
        return IGTransaction.parse_from_dict(response.json())

    def get_transactions_by_type(self, transaction_type: str, from_date: str, to_date: str = None) -> [IGTransaction]:
        """ Get all account transactions within specified date range.

        Args:
            transaction_type: Transaction types to filter for e.g. WITHDRAWAL, DEPOSIT, ALL etc.
            from_date: Start date e.g. yyyy-MM-dd HH:mm:ss.
            to_date: End date (Default = current time).
        Returns:
            List of IGTransaction's found within searched time range.
        Raises:
            Exception: If request to get transactions failed.
        """
        payload = {'from': from_date, 'type': transaction_type}
        if to_date is not None:
            payload['to'] = to_date

        url = '%s/history/transactions?%s' % (self._get_base_api_url(), urlencode(payload))
        response = self._request(RequestType.GET, url)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch account transaction with following error: %s' % response.json()['errorCode'])
        return IGTransaction.parse_from_dict(response.json())

    def get_watchlist(self, name: str) -> [IGMarketInstrument]:
        """Get all market instruments within watchlist.

        Args:
            name: Watchlist name.
        Returns:
            List of IGMarketInstrument objects for all market instruments within watchlist.
        Raises:
            Exception: If request to get watchlist failed.
        """
        target_watchlist = self._get_watchlist(name)
        url = '%s/watchlists/%s' % (self._get_base_api_url(), target_watchlist.id)
        response = self._request(RequestType.GET, url, version=1)
        if not response.ok:
            raise IGServerException(
                'Failed to get watchlist instruments with following error: %s' % response.json()['errorCode'])
        return [IGMarketInstrument.parse_from_dict(market) for market in response.json()['markets']]

    def get_all_watchlists(self) -> [IGWatchlist]:
        """Get all watchlists belonging to the active account.

        Returns:
            List of IGWatchlist wrappers containing account watchlist data.
        Raises:
            Exception: If request to get watchlists failed.
        """
        url = '%s/watchlists' % self._get_base_api_url()
        response = self._request(RequestType.GET, url, version=1)
        if not response.ok:
            raise IGServerException(
                'Failed to fetch account watchlists with following error: %s' % response.json()['errorCode'])
        return IGWatchlist.parse_from_dict(response.json())

    def create_watchlist(self, name: str, epics: str = None) -> dict:
        """Create a new watchlist.

        Args:
            name: Name of watchlist to create.
            epics: List of epics to pre-populate watchlist with.
        Returns:
            Object containing creation `status` and newly created `watchlistId` if successful.
        Raises:
            Exception: If request to create watchlist failed.
        """
        payload = {'name': name}
        if epics is not None:
            payload['epics'] = epics

        url = '%s/watchlists' % self._get_base_api_url()
        response = self._request(RequestType.POST, url, payload=payload, version=1)
        if not response.ok:
            raise IGServerException(
                'Failed to create new watchlist "%s" with following error: %s' % (name, response.json()['errorCode']))
        return response.json()

    def delete_watchlist(self, name: str) -> bool:
        """Deletes a watchlist.

        Args:
            name: Name for watchlist to delete.
        Returns:
            True if operation succeeded.
        """
        target_watchlist = self._get_watchlist(name)
        url = '%s/watchlists/%s' % (self._get_base_api_url(), target_watchlist.id)
        response = self._request(RequestType.DELETE, url, version=1)
        if not response.ok:
            raise IGServerException(
                'Failed to delete watchlist with following error: %s' % response.json()['errorCode'])
        return True if response.json()['status'] == 'SUCCESS' else False

    def add_market_to_watchlist(self, name: str, epic: str) -> bool:
        """Add market instruments to existing watchlist.

        Args:
            name: Watchlist name to add market instrument to.
            epic: Epic identifier for market instrument to add.
        Returns:
            True if market instrument was successfully added to watchlist.
        Raises:
            Exception: If request to add market to watchlist failed.
        """
        watchlist = self._get_watchlist(name)
        url = '%s/watchlists/%s' % (self._get_base_api_url(), quote_plus(watchlist.id))
        payload = {'epic': epic}
        response = self._request(RequestType.PUT, url, payload, version=1)
        if not response.ok:
            raise IGServerException(
                'Failed to add market to watchlist with following error: %s' % response.json()['errorCode'])
        return True if response.json()['status'] == 'SUCCESS' else False

    def remove_markets_from_watchlist(self, name: str, epic: str) -> bool:
        """Remove market instruments from existing watchlist.

       Args:
           name: Watchlist name to remove market instrument from.
           epic: Epic identifier for market instrument to remove.
       Returns:
           True if market instrument was successfully removed from watchlist.
       Raises:
           Exception: If request to remove market to watchlist failed.
       """
        watchlist = self._get_watchlist(name)
        url = '%s/watchlists/%s/%s' % (
            self._get_base_api_url(), quote_plus(watchlist.id), quote_plus(epic))
        response = self._request(RequestType.DELETE, url, version=1)
        if not response.ok:
            raise IGServerException(
                'Failed to remove market to watchlist with following error: %s' % response.json()['errorCode'])
        return True if response.json()['status'] == 'SUCCESS' else False

    def _validate_order_limit_params(self,
                                     market: IGMarketInstrument,
                                     size: float,
                                     order_direction: OrderDirection,
                                     limit_distance: float = None,
                                     stop_distance: float = None,
                                     stop_increment: float = None,
                                     limit_level: float = None,
                                     stop_level: float = None) -> None:
        """Validates order limit parameters based on specified market instrument range limits.

        Args:
            market: Market instrument object.
            size: Order size.
            order_direction: Order direction e.g. BUY or SELL.
            limit_distance: Take profit distance from current market level.
            limit_level: Take profit price level.
            stop_distance: Stop loss distance from current market level.
            stop_level: Stop loss price level.
            stop_increment: Trailing stop loss increment.
        Raises:
            Exception: if parameter does not satisfy market instrument ranges.
        """
        rules = self.get_market_instrument_dealing_rules(market.epic)

        if size < rules.min_deal_size.value:
            raise IGClientException(
                'Order size of "%s" must not be lesser than market allowed minimum of "%s".'
                % (size, rules.min_deal_size.value))

        if limit_distance is not None:
            if limit_distance > rules.max_stop_or_limit_distance.value:
                raise IGClientException(
                    'Order limit distance of "%s" must be lesser than market allowed maximum of "%s".'
                    % (limit_distance, rules.max_stop_or_limit_distance.value))
            if limit_distance < rules.min_stop_or_limit_distance.value:
                raise IGClientException(
                    'Order limit distance of "%s" must be greater than market allowed minimum of "%s".'
                    % (limit_distance, rules.min_stop_or_limit_distance.value))

        if stop_distance is not None:
            if stop_distance > rules.max_stop_or_limit_distance.value:
                raise IGClientException(
                    'Order stop limit distance of "%s" must be lesser than market allowed maximum of "%s".'
                    % (stop_distance, rules.max_stop_or_limit_distance.value))
            if stop_distance < rules.min_stop_or_limit_distance.value:
                raise IGClientException(
                    'Order stop limit distance of "%s" must be greater than market allowed minimum of "%s".'
                    % (stop_distance, rules.min_stop_or_limit_distance.value))

        if limit_level is not None:
            limit_level -= market.bid_price if order_direction is OrderDirection.BUY else market.offer_price
            if limit_level > rules.max_stop_or_limit_distance.value:
                raise IGClientException(
                    'Order level distance of "%s" must be lesser than market allowed maximum of "%s".'
                    % (limit_level, rules.max_stop_or_limit_distance.value))
            if limit_level < rules.min_stop_or_limit_distance.value:
                raise IGClientException(
                    'Order level distance of "%s" must be greater than market allowed minimum of "%s".'
                    % (limit_level, rules.min_stop_or_limit_distance.value))

        if stop_level is not None:
            if order_direction is OrderDirection.BUY:
                stop_level = market.bid_price - stop_level
            else:
                stop_level = market.offer_price - stop_level
            if stop_level > rules.max_stop_or_limit_distance.value:
                raise IGClientException(
                    'Order stop level distance of "%s" must be lesser than market allowed maximum of "%s".'
                    % (stop_level, rules.max_stop_or_limit_distance.value))
            if stop_level < rules.min_stop_or_limit_distance.value:
                raise IGClientException(
                    'Order limit level distance of "%s" must be greater than market allowed minimum of "%s".'
                    % (stop_level, rules.min_stop_or_limit_distance.value))

        if stop_increment is not None:
            if stop_increment < rules.min_step_distance.value:
                raise IGClientException(
                    'Order trailing step distance of "%s" must be greater than market allowed minimum of "%s".'
                    % (stop_increment, rules.min_step_distance.value))

    def _get_watchlist(self, name: str) -> IGWatchlist:
        """Get watchlist by name.

        Args:
            name: Watchlist name.
        Returns:
            IGWatchlist if watchlist with given name was found.
        Raises:
            Exception: If watchlist with given name could not be found.
        """
        for watchlist in self.get_all_watchlists():
            if watchlist.name == name:
                return watchlist
        raise IGClientException('Could not get watchlist with name "%s" because it doesn\'t exist.' % name)

    @staticmethod
    def _add_if_not_none(payload: dict, key: Any, value: Any) -> dict:
        """Adds new `key` `value` entry if `value` is not None and returns dict."""
        if value is not None:
            payload[key] = value
        return payload

    def _request(self,
                 request_type: RequestType,
                 url: str,
                 payload: dict = None,
                 version: int = 2) -> requests.Response:
        """Helper method for formatting and performing request.

        Args:
            request_type: Type of HTTP request to perform e.g. POST or GET.
            url: Request URL.
            payload: JSON formatted data payload to attach to request.
            version: API version to use (default = 1).
        Returns:
            Response object from request.
        Raises:
            Exception: If unsupported/unimplemented request type is passed in.
        """
        if payload is None:
            payload = {}

        headers = {
            'X-IG-API-KEY': self.key,
            'CST': self.cst,
            'X-SECURITY-TOKEN': self.securityToken,
            'Version': str(version),
            "Content-Type": "application/json",
            "Accept": "application/json; charset=UTF-8"
        }

        if request_type == RequestType.GET:
            return requests.get(url, headers=headers, data=json.dumps(payload))
        elif request_type == RequestType.POST:
            return requests.post(url, headers=headers, data=json.dumps(payload))
        elif request_type == RequestType.PUT:
            return requests.put(url, headers=headers, data=json.dumps(payload))
        elif request_type == RequestType.DELETE:
            headers['_method'] = 'DELETE'
            return requests.post(url, headers=headers, data=json.dumps(payload))
        raise IGClientException('Unsupported request type of %s found' % request_type)

    def _get_base_api_url(self) -> str:
        """Returns demo or production API base URL."""
        return 'https://demo-api.ig.com/gateway/deal' if self.demo else 'https://api.ig.com/gateway/deal'
