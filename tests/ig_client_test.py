""" IG Client Unit Tests

Test that API specification is up-to-date with what we expect and that
the conversions of API response to data wrappers remains valid.

Authored By TheCeriousBoi [TCB] (@theceriousboi)
"""
import unittest

from utility.constants import Constants
from iglib.enums.price_resolution import PriceResolution
from iglib.exceptions import IGServerException, IGClientException
from iglib.ig_client import IGClient


class IGClientTest(unittest.TestCase):

    def setUp(self) -> None:
        self.client = IGClient(
            Constants.DEMO_APP_KEY, Constants.DEMO_ID, Constants.DEMO_PASS, Constants.IS_DEMO, dry_run=True)
        self.client.authenticate()

    def tearDown(self) -> None:
        self.client = None

    def test_authentication(self):
        self.assertIsNotNone(self.client.account)
        self.assertIsNotNone(self.client.cst)
        self.assertIsNotNone(self.client.securityToken)

    def test_account_attributes_populated_correctly(self):
        account = self.client.account
        self.assertIsNotNone(account.client_id)
        self.assertIsNotNone(account.id)
        self.assertIsNotNone(account.account_type)
        self.assertIsNotNone(account.info)
        self.assertIsNotNone(account.currency_iso_code)
        self.assertIsNotNone(account.other_accounts)

    def test_account_info_attributes_populated_correctly(self):
        account_info = self.client.account.info
        self.assertIsNotNone(account_info.balance)
        self.assertIsNotNone(account_info.deposit)
        self.assertIsNotNone(account_info.profit_loss)
        self.assertIsNotNone(account_info.available)

    def test_other_account_attributes_populated_correctly(self):
        other_accounts = self.client.account.other_accounts
        self.assertTrue(len(other_accounts) != 0)

    def test_is_logged_in_is_truw_when_authenticated(self):
        self.assertTrue(self.client.is_logged_in())

    def test_get_account(self):
        self.assertIsNotNone(self.client.get_account())

    def test_switch_active_account(self):
        try:
            if self.client.account.id == Constants.CFD_ACCOUNT_ID:
                self.client.switch_active_account(Constants.SPREAD_BET_ACCOUNT_ID)
            else:
                self.client.switch_active_account(Constants.CFD_ACCOUNT_ID)
        except IGServerException:
            self.fail('IGClient switch_active_account() method test failed to due to response not OK.')

    def test_switching_active_account_to_current_active_account_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Account switch failed with following error: error.switch.accountId-must-be-different',
            self.client.switch_active_account,
            Constants.SPREAD_BET_ACCOUNT_ID
            if self.client.account.id == Constants.SPREAD_BET_ACCOUNT_ID else
            Constants.CFD_ACCOUNT_ID)

    def test_switching_active_account_with_invalid_account_id_format_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Account switch failed with following error: validation.pattern.invalid.accountSwitchRequest.accountId',
            self.client.switch_active_account,
            '123-invalid_account-id')

    def test_switching_active_account_with_non_existent_account_id_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Account switch failed with following error: error.client.account.switch.account-access-denied',
            self.client.switch_active_account,
            'ZY123')

    def test_get_market_instrument(self):
        instrument = self.client.get_market_instrument(search_term='EURUSD')
        self.assertIsNotNone(instrument)

    def test_get_market_instrument_populates_market_attributes_correctly(self):
        instrument = self.client.get_market_instrument(search_term='EURUSD')
        self.assertIsNotNone(instrument.bid_price)
        self.assertIsNotNone(instrument.delay_time)
        self.assertIsNotNone(instrument.epic)
        self.assertIsNotNone(instrument.expiry)
        self.assertIsNotNone(instrument.high_of_day)
        self.assertIsNotNone(instrument.low_of_day)
        self.assertIsNotNone(instrument.name)
        self.assertIsNotNone(instrument.type)
        self.assertIsNotNone(instrument.status)
        self.assertIsNotNone(instrument.net_change)
        self.assertIsNotNone(instrument.offer_price)
        self.assertIsNotNone(instrument.percentage_change)
        self.assertIsNotNone(instrument.scaling_factor)
        self.assertIsNotNone(instrument.streaming_prices_available)
        self.assertIsNotNone(instrument.local_update_time)

    def test_get_market_instrument_with_non_existent_search_term_fails(self):
        self.assertRaisesRegex(
            IGClientException,
            'Could not parse first entry because no market instruments matched given searchTerm: "TESTO-INV@LID".',
            self.client.get_market_instrument,
            'TESTO-INV@LID')

    def test_get_market_instrument_with_invalid_search_term_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Failed to fetch market instrument with following error: validation.null-not-allowed.epics',
            self.client.get_market_instrument,
            '')

    def test_get_market_instrument_dealing_rules(self):
        instrument = self.client.get_market_instrument('EURUSD')
        rules = self.client.get_market_instrument_dealing_rules(instrument.epic)
        self.assertIsNotNone(rules)

    def test_get_market_instrument_dealing_rules_populates_rule_attributes_correctly(self):
        instrument = self.client.get_market_instrument('EURUSD')
        rules = self.client.get_market_instrument_dealing_rules(instrument.epic)
        self.assertIsNotNone(rules.market_order_preference)
        self.assertIsNotNone(rules.max_stop_or_limit_distance)
        self.assertIsNotNone(rules.min_controlled_risk_stop_distance)
        self.assertIsNotNone(rules.min_deal_size)
        self.assertIsNotNone(rules.min_stop_or_limit_distance)
        self.assertIsNotNone(rules.min_step_distance)
        self.assertIsNotNone(rules.trailing_stop_preference)

    def test_get_market_instrument_dealing_rules_with_invalid_epic_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Failed to fetch market dealing rules with follow error: validation.pattern.invalid.epic',
            self.client.get_market_instrument_dealing_rules,
            '123')

    def test_get_market_instrument_dealing_rules_with_non_existent_epic_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Failed to fetch market dealing rules with follow error: '
            'error.service.marketdata.instrument.epic.unavailable',
            self.client.get_market_instrument_dealing_rules,
            'XX.X.XXXXXX.XXXXX.XX')

    def test_get_market_instrument_snapshot(self):
        instrument = self.client.get_market_instrument('EURUSD')
        snapshot = self.client.get_market_instrument_snapshot(instrument.epic)
        self.assertIsNotNone(snapshot)

    def test_get_market_instrument_snapshot_populates_attribute_correcly(self):
        instrument = self.client.get_market_instrument('EURUSD')
        snapshot = self.client.get_market_instrument_snapshot(instrument.epic)
        self.assertIsNotNone(snapshot.bid)
        if instrument.type == 'BINARY':
            self.assertIsNotNone(snapshot.binary_odds)
        self.assertIsNotNone(snapshot.controlled_risk_extra_spread)
        self.assertIsNotNone(snapshot.decimal_places_factor)
        self.assertIsNotNone(snapshot.delay_time)
        self.assertIsNotNone(snapshot.high)
        self.assertIsNotNone(snapshot.low)
        self.assertIsNotNone(snapshot.status)
        self.assertIsNotNone(snapshot.net_change)
        self.assertIsNotNone(snapshot.offer)
        self.assertIsNotNone(snapshot.percentage_change)
        self.assertIsNotNone(snapshot.scaling_factor)
        self.assertIsNotNone(snapshot.update_time)

    def test_get_market_instrument_snapshot_with_invalid_epic_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Failed to fetch market snapshot with follow error: validation.pattern.invalid.epic',
            self.client.get_market_instrument_snapshot,
            '123')

    def test_get_market_instrument_snapshot_with_non_existent_epic_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Failed to fetch market snapshot with follow error: error.service.marketdata.instrument.epic.unavailable',
            self.client.get_market_instrument_snapshot,
            'XX.X.XXXXXX.XXXXX.XX')

    def test_get_price_fetch_allowance(self):
        allowance = self.client.get_price_fetch_allowance()
        self.assertIsNotNone(allowance)

    def test_get_price_fetch_allowance_populates_attributes_correctly(self):
        allowance = self.client.get_price_fetch_allowance()
        self.assertIsNotNone(allowance.remaining_allowance)
        self.assertIsNotNone(allowance.total_allowance)
        self.assertIsNotNone(allowance.allowance_expiry)

    def test_get_historical_price(self):
        instrument = self.client.get_market_instrument('EURUSD')
        candles = self.client.get_historical_price(
            instrument.epic, PriceResolution.DAY, '2019-01-01 12:00:00', '2019-01-02 12:00:00')
        self.assertTrue(len(candles) == 1)
        self.assertIsNotNone(candles[0].open_price)
        self.assertIsNotNone(candles[0].open_price.bid)
        self.assertIsNotNone(candles[0].open_price.ask)

        self.assertIsNotNone(candles[0].close_price)
        self.assertIsNotNone(candles[0].close_price.bid)
        self.assertIsNotNone(candles[0].close_price.ask)

        self.assertIsNotNone(candles[0].low)
        self.assertIsNotNone(candles[0].low.bid)
        self.assertIsNotNone(candles[0].low.ask)

        self.assertIsNotNone(candles[0].high)
        self.assertIsNotNone(candles[0].high.bid)
        self.assertIsNotNone(candles[0].high.ask)

        self.assertIsNotNone(candles[0].last_traded_volume)
        self.assertIsNotNone(candles[0].snapshot_time)

    def test_get_historical_price_with_invalid_epic_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Failed to fetch historical price data with following error: error.unsupported.epic',
            self.client.get_historical_price,
            'XX.X.XXXXXX.XXXXX.XX',
            PriceResolution.DAY,
            '2019-01-01 12:00:00',
            '2019-01-02 12:00:00')

    def test_get_historical_price_with_invalid_date_range_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Failed to fetch historical price data with following error: error.invalid.daterange',
            self.client.get_historical_price,
            'XX.X.XXXXXX.XXXXX.XX',
            PriceResolution.DAY,
            '2019-01-02 12:00:00',
            '2019-01-01 12:00:00')

    def test_get_historical_price_with_invalid_date_format_fails(self):
        self.assertRaisesRegex(
            IGServerException,
            'Failed to fetch historical price data with following error: error.malformed.date',
            self.client.get_historical_price,
            'XX.X.XXXXXX.XXXXX.XX',
            PriceResolution.DAY,
            '2019-01-01',
            '2019-01-02')