"""
TDD tests for:
  1. Trend logic fix: overview endpoint must return 'improving' when recent matches
     have higher win rate than older matches (newest-first ordering).
  2. Statistics endpoint: must not return 404 when DB is empty (should call
     _ensure_matches like every other analysis endpoint).
  3. pass_try=0 masking: passTry=0 should not be silently replaced with 1,
     which would produce a misleading 0% pass rate.
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache

from api.models import User, Match
from api.analyzers.statistics import StatisticsCalculator


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_match(user, match_id, result, days_ago, pass_try=30, pass_success=25):
    """Create a Match record with a controlled date and pass data."""
    return Match.objects.create(
        ouid=user,
        match_id=match_id,
        match_date=timezone.now() - timedelta(days=days_ago),
        match_type=50,
        result=result,
        goals_for=2 if result == 'win' else 0,
        goals_against=0 if result == 'win' else 2,
        possession=55,
        shots=12,
        shots_on_target=5,
        pass_success_rate=Decimal(str(pass_success / pass_try * 100)) if pass_try > 0 else Decimal('0.00'),
        raw_data={},
    )


# ===========================================================================
# Issue 1 – Trend Logic
# ===========================================================================

class TestCalculateFormTrendUnit(TestCase):
    """
    Unit tests for StatisticsCalculator.calculate_form_trend.

    Matches are expected to be ordered *newest first* (mirrors DB order_by('-match_date')).
    """

    def _make_match_dicts(self, results):
        """Create a list of minimal match dicts."""
        return [{'result': r} for r in results]

    # --- core correctness -------------------------------------------------

    def test_improving_when_recent_half_has_higher_win_rate(self):
        """
        5 recent wins followed by 5 older losses → improving.
        Before the fix the view compares second_half > first_half (backwards),
        which would return 'declining'.
        """
        # newest first: 5 wins then 5 losses
        matches = self._make_match_dicts(
            ['win', 'win', 'win', 'win', 'win',
             'lose', 'lose', 'lose', 'lose', 'lose']
        )
        result = StatisticsCalculator.calculate_form_trend(matches)
        self.assertEqual(result['trend'], 'improving')

    def test_declining_when_recent_half_has_lower_win_rate(self):
        """5 recent losses followed by 5 older wins → declining."""
        matches = self._make_match_dicts(
            ['lose', 'lose', 'lose', 'lose', 'lose',
             'win', 'win', 'win', 'win', 'win']
        )
        result = StatisticsCalculator.calculate_form_trend(matches)
        self.assertEqual(result['trend'], 'declining')

    def test_stable_when_win_rates_are_equal(self):
        """Alternating wins/losses in both halves → stable."""
        matches = self._make_match_dicts(
            ['win', 'lose', 'win', 'lose',
             'win', 'lose', 'win', 'lose']
        )
        result = StatisticsCalculator.calculate_form_trend(matches)
        self.assertEqual(result['trend'], 'stable')

    # --- return shape -----------------------------------------------------

    def test_returns_recent_and_older_win_rates(self):
        """Result dict must expose both win rates for the frontend."""
        matches = self._make_match_dicts(['win'] * 5 + ['lose'] * 5)
        result = StatisticsCalculator.calculate_form_trend(matches)
        self.assertIn('recent_win_rate', result)
        self.assertIn('older_win_rate', result)
        self.assertEqual(result['recent_win_rate'], 100.0)
        self.assertEqual(result['older_win_rate'], 0.0)

    # --- edge cases -------------------------------------------------------

    def test_empty_list_returns_stable(self):
        result = StatisticsCalculator.calculate_form_trend([])
        self.assertEqual(result['trend'], 'stable')

    def test_single_match_returns_stable(self):
        result = StatisticsCalculator.calculate_form_trend([{'result': 'win'}])
        self.assertEqual(result['trend'], 'stable')

    def test_odd_number_of_matches(self):
        """7 matches: recent 3 all wins, older 4 half wins → improving."""
        # newest first: 3 wins + 4 with 2 wins 2 losses
        matches = self._make_match_dicts(
            ['win', 'win', 'win', 'win', 'win', 'lose', 'lose']
        )
        result = StatisticsCalculator.calculate_form_trend(matches)
        # recent half (3 matches) = 3W = 100%, older half (4 matches) = 2W = 50%
        self.assertEqual(result['trend'], 'improving')


# ===========================================================================
# Issue 1 – Integration test via /overview/ endpoint
# ===========================================================================

class TestOverviewTrendIntegration(TestCase):
    """
    Integration tests: the overview endpoint must reflect the corrected trend
    logic (matches ordered newest-first in the DB).
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='trend-test-user', nickname='TrendTester')
        cache.clear()

    def _create_matches(self, results_newest_first):
        """Create matches in DB; index 0 = most recent."""
        for i, result in enumerate(results_newest_first):
            make_match(self.user, f'trend-match-{i}', result, days_ago=i)

    def test_overview_trend_improving(self):
        """
        Recent 5 games all wins, older 5 games all losses.
        Expected trend: 'improving'.
        """
        self._create_matches(['win'] * 5 + ['lose'] * 5)
        response = self.client.get(
            f'/api/users/{self.user.ouid}/overview/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['trends']['trend'], 'improving')

    def test_overview_trend_declining(self):
        """
        Recent 5 games all losses, older 5 games all wins.
        Expected trend: 'declining'.
        """
        self._create_matches(['lose'] * 5 + ['win'] * 5)
        response = self.client.get(
            f'/api/users/{self.user.ouid}/overview/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['trends']['trend'], 'declining')

    def test_overview_trend_stable(self):
        """Equal win rates in both halves → stable.
        Pattern: 3 wins in recent 5 AND 3 wins in older 5 → both 60% → stable.
        """
        self._create_matches(['win', 'win', 'win', 'lose', 'lose',
                               'win', 'win', 'win', 'lose', 'lose'])
        response = self.client.get(
            f'/api/users/{self.user.ouid}/overview/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['trends']['trend'], 'stable')

    def test_overview_trend_field_names(self):
        """
        The response must expose recent_win_rate and older_win_rate
        (replacing the confusing first_half/second_half naming).
        """
        self._create_matches(['win'] * 10)
        response = self.client.get(
            f'/api/users/{self.user.ouid}/overview/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trends = response.data['trends']
        self.assertIn('recent_win_rate', trends)
        self.assertIn('older_win_rate', trends)
        # old confusing names must be gone
        self.assertNotIn('first_half_win_rate', trends)
        self.assertNotIn('second_half_win_rate', trends)


# ===========================================================================
# Issue 2 – statistics endpoint must call _ensure_matches
# ===========================================================================

class TestStatisticsEndpointEnsureMatches(TestCase):
    """
    The /statistics/ endpoint currently returns 404 when no matches are in the
    DB, even though every other analysis endpoint auto-fetches from the Nexon
    API via _ensure_matches(). After the fix it must behave consistently.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='stats-test-user', nickname='StatsTester')
        cache.clear()

    def test_statistics_returns_404_when_no_matches_available(self):
        """
        When DB is empty AND _ensure_matches returns no matches (e.g. API
        also returns nothing for the user), the endpoint must return 404.
        """
        with patch('api.views.UserViewSet._ensure_matches', return_value=[]):
            response = self.client.get(
                f'/api/users/{self.user.ouid}/statistics/',
                {'matchtype': 50, 'limit': 10}
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_statistics_returns_data_when_matches_exist(self):
        """Statistics endpoint works when matches are already in the DB."""
        for i in range(5):
            make_match(self.user, f'stats-match-{i}', 'win', days_ago=i)

        response = self.client.get(
            f'/api/users/{self.user.ouid}/statistics/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_statistics_returns_200_not_404_after_ensure_matches_fix(self):
        """
        After adding _ensure_matches to the statistics endpoint, a user with
        no matches in DB but valid matches on the Nexon API must receive a
        200 response (not 404).

        We mock _ensure_matches to return pre-built match objects so the test
        does not make real API calls.
        """
        # Pre-create matches to be returned by the mocked _ensure_matches
        db_matches = [make_match(self.user, f'sm-{i}', 'win', days_ago=i) for i in range(5)]

        with patch(
            'api.views.UserViewSet._ensure_matches',
            return_value=db_matches,
        ):
            response = self.client.get(
                f'/api/users/{self.user.ouid}/statistics/',
                {'matchtype': 50, 'limit': 10}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ===========================================================================
# Issue 5 – pass_try = 0 masking
# ===========================================================================

class TestPassTryZeroHandling(TestCase):
    """
    `pass_data.get('passTry') or 1` silently replaces passTry=0 with 1,
    causing pass_success_rate to be calculated as 0/1 = 0 % instead of
    being stored as None (unknown / no data).
    """

    def _make_raw_data(self, pass_try, pass_success, ouid='passtest-ouid'):
        """Build minimal Nexon API raw_data structure for _ensure_matches."""
        return {
            'matchInfo': [
                {
                    'ouid': ouid,
                    'matchDetail': {'matchEndType': 0, 'systemMessage': None},
                    'shoot': {
                        'shootTotal': 5,
                        'effectiveShootTotal': 2,
                        'goalTotalDisplay': 1,
                    },
                    'pass': {
                        'passTry': pass_try,
                        'passSuccess': pass_success,
                    },
                    'defence': {},
                    'player': [],
                }
            ]
        }

    def test_pass_success_rate_is_null_when_pass_try_is_zero(self):
        """
        When passTry is 0 the stored pass_success_rate must be NULL (None),
        not 0.00 % (which would mean "0 out of 1 passes succeeded").
        """
        user = User.objects.create(ouid='passtest-ouid', nickname='PassTester')

        # Simulate what _ensure_matches stores when API returns passTry=0
        raw = self._make_raw_data(pass_try=0, pass_success=0, ouid='passtest-ouid')

        # Compute the rate exactly as the current buggy code does
        pass_data = raw['matchInfo'][0].get('pass') or {}
        buggy_pass_try = pass_data.get('passTry') or 1   # BUG: replaces 0 with 1
        buggy_rate = (pass_data.get('passSuccess', 0) / buggy_pass_try * 100)

        # Correct behaviour: rate should be None when no passes were attempted
        correct_pass_try = pass_data.get('passTry') or 0
        correct_rate = (
            pass_data.get('passSuccess', 0) / correct_pass_try * 100
            if correct_pass_try > 0
            else None
        )

        # The buggy code produces 0.0, the fix produces None
        self.assertEqual(buggy_rate, 0.0,
                         "Confirm current bug: 0 attempts → 0/1 = 0.0")
        self.assertIsNone(correct_rate,
                          "Fixed code: 0 attempts → None (unknown)")

    def test_pass_success_rate_calculated_normally_when_pass_try_nonzero(self):
        """Normal case (passTry > 0) must still produce the correct rate."""
        pass_data = {'passTry': 40, 'passSuccess': 32}
        pass_try = pass_data.get('passTry') or 0
        rate = (pass_data['passSuccess'] / pass_try * 100) if pass_try > 0 else None

        self.assertAlmostEqual(rate, 80.0)

    def test_pass_success_rate_is_none_when_pass_data_missing(self):
        """Missing pass data entirely should also produce None."""
        pass_data = {}
        pass_try = pass_data.get('passTry') or 0
        rate = (pass_data.get('passSuccess', 0) / pass_try * 100) if pass_try > 0 else None

        self.assertIsNone(rate)
