"""
TDD tests for:
  3. Response structure: stale field names in test_views + pass_analysis 404 → 200
  4. Nullable pass_success_rate: Match model, overview action, TacticalInsightsAnalyzer
"""
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache

from api.models import User, Match
from api.analyzers.tactical_analyzer import TacticalInsightsAnalyzer


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_match(user, match_id, result='win', days_ago=0,
               pass_success_rate=Decimal('80.00')):
    from datetime import timedelta
    return Match.objects.create(
        ouid=user,
        match_id=match_id,
        match_date=timezone.now() - timedelta(days=days_ago),
        match_type=50,
        result=result,
        goals_for=2 if result == 'win' else 0,
        goals_against=0 if result == 'win' else 2,
        possession=55,
        shots=10,
        shots_on_target=5,
        pass_success_rate=pass_success_rate,
        raw_data={'matchInfo': []},
    )


# ===========================================================================
# Issue 3 – pass_analysis returns 404 when no PlayerPerformance records
# ===========================================================================

class TestPassAnalysisNoPerformanceData(TestCase):
    """
    The pass_analysis endpoint currently returns 404 when no
    PlayerPerformance records exist for the user's matches.
    After the fix it must return 200 with an empty/default analysis.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='pass-no-perf-user', nickname='PassNoPerfTester')
        # Create 3 matches but NO PlayerPerformance records
        for i in range(3):
            make_match(self.user, f'pass-m-{i}', days_ago=i)
        cache.clear()

    def test_pass_analysis_returns_200_without_performance_data(self):
        """
        When matches exist but no PlayerPerformance records are in the DB,
        the endpoint must return 200 with a default/empty analysis structure
        instead of 404.
        """
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/passes/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pass_analysis_empty_response_has_required_keys(self):
        """
        The empty/default response must contain the standard analysis keys
        so the frontend can render a consistent (empty) state.
        """
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/passes/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall_stats', response.data)
        self.assertIn('matches_analyzed', response.data)

    def test_pass_analysis_returns_404_when_no_matches_at_all(self):
        """
        If there are absolutely no matches, the endpoint should return 404
        (the user has no data at all, not just missing PlayerPerformance).
        """
        other_user = User.objects.create(ouid='pass-empty-user', nickname='EmptyUser')
        with patch('api.views.UserViewSet._ensure_matches', return_value=[]):
            response = self.client.get(
                f'/api/users/{other_user.ouid}/analysis/passes/',
                {'matchtype': 50, 'limit': 10}
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ===========================================================================
# Issue 3 – shot_analysis response shape (zone_analysis, not shot_zones)
# ===========================================================================

class TestShotAnalysisResponseShape(TestCase):
    """
    Verify the shot_analysis endpoint returns the current field names.
    The old test checked for 'shot_zones' but the response uses 'zone_analysis'.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='shot-shape-user', nickname='ShotShapeTester')
        from api.models import ShotDetail
        match = make_match(self.user, 'shot-shape-m-1')
        ShotDetail.objects.create(
            match=match, x=Decimal('0.8'), y=Decimal('0.5'),
            result='goal', shot_type=3, goal_time=30,
        )
        cache.clear()

    def test_shot_analysis_uses_zone_analysis_key(self):
        """Response must contain 'zone_analysis', not old 'shot_zones'."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/shots/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('zone_analysis', response.data)
        self.assertNotIn('shot_zones', response.data)

    def test_shot_analysis_uses_total_shots_key(self):
        """Response must still contain 'total_shots' (unchanged)."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/shots/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_shots', response.data)


# ===========================================================================
# Issue 3 – style_analysis response shape (attack_pattern, not attack_style)
# ===========================================================================

class TestStyleAnalysisResponseShape(TestCase):
    """
    Verify the style_analysis endpoint returns the current field names.
    The old test checked for 'attack_style' but the response uses 'attack_pattern'.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='style-shape-user', nickname='StyleShapeTester')
        for i in range(3):
            make_match(self.user, f'style-shape-m-{i}', days_ago=i)
        cache.clear()

    def test_style_analysis_uses_attack_pattern_key(self):
        """Response must contain 'attack_pattern', not old 'attack_style'."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/style/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attack_pattern', response.data)
        self.assertNotIn('attack_style', response.data)

    def test_style_analysis_has_possession_style_key(self):
        """Response must still contain 'possession_style' (unchanged)."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/style/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('possession_style', response.data)


# ===========================================================================
# Issue 4 – pass_success_rate nullable: Match model
# ===========================================================================

class TestMatchNullPassSuccessRate(TestCase):
    """
    Match.pass_success_rate should be nullable (null=True, blank=True).
    Currently the field is NOT nullable; saving None raises IntegrityError.
    """

    def setUp(self):
        self.user = User.objects.create(ouid='null-psr-user', nickname='NullPSRTester')

    def test_match_can_be_created_with_null_pass_success_rate(self):
        """
        A Match with pass_success_rate=None must be saveable to the DB.
        This is the correct state when passTry==0 (no passes attempted).
        """
        match = Match.objects.create(
            ouid=self.user,
            match_id='null-psr-m-1',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=1,
            goals_against=0,
            possession=55,
            shots=5,
            shots_on_target=3,
            pass_success_rate=None,   # ← must not raise IntegrityError
            raw_data={},
        )
        match.refresh_from_db()
        self.assertIsNone(match.pass_success_rate)

    def test_match_pass_success_rate_still_works_with_value(self):
        """Saving a non-None value must still work after making field nullable."""
        match = Match.objects.create(
            ouid=self.user,
            match_id='null-psr-m-2',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=1,
            goals_against=0,
            possession=55,
            shots=5,
            shots_on_target=3,
            pass_success_rate=Decimal('82.50'),
            raw_data={},
        )
        match.refresh_from_db()
        self.assertEqual(match.pass_success_rate, Decimal('82.50'))


# ===========================================================================
# Issue 4 – overview endpoint must not crash when pass_success_rate is None
# ===========================================================================

class TestOverviewWithNullPassSuccessRate(TestCase):
    """
    The overview endpoint crashes with TypeError when any match in the
    result set has pass_success_rate = None.
    After the fix, it must return 200 and treat None as 0.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='overview-null-psr', nickname='OverviewNullPSR')
        cache.clear()

    def test_overview_returns_200_when_pass_success_rate_is_none(self):
        """
        Matches with None pass_success_rate must not crash the overview action.
        The avg_pass_success calculation must treat None as 0.
        """
        # Create a mix: one match with data, one with None pass_success_rate
        make_match(self.user, 'ov-psr-1', pass_success_rate=Decimal('80.00'))
        make_match(self.user, 'ov-psr-2', pass_success_rate=None, days_ago=1)

        response = self.client.get(
            f'/api/users/{self.user.ouid}/overview/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # avg_pass_success should be (80+0)/2 = 40
        self.assertAlmostEqual(
            response.data['statistics']['avg_pass_success'],
            40.0,
            places=0
        )

    def test_overview_all_null_pass_success_rate_returns_200(self):
        """All matches having None pass_success_rate must still return 200."""
        make_match(self.user, 'ov-all-null-1', pass_success_rate=None)
        make_match(self.user, 'ov-all-null-2', pass_success_rate=None, days_ago=1)

        response = self.client.get(
            f'/api/users/{self.user.ouid}/overview/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ===========================================================================
# Issue 4 – TacticalInsightsAnalyzer must not crash with None pass_success_rate
# ===========================================================================

class TestTacticalAnalyzerNullPassSuccessRate(TestCase):
    """
    TacticalInsightsAnalyzer._analyze_possession_style and
    _generate_insights directly compare match.pass_success_rate >= 85 etc.
    When the value is None, these comparisons raise TypeError.
    After the fix, None must be treated as 0 (or skipped).
    """

    def setUp(self):
        self.user = User.objects.create(ouid='tactical-null-psr', nickname='TacticalNullPSR')

    def _make_match_obj(self, pass_success_rate):
        return Match(
            ouid=self.user,
            match_id='tactical-test',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=0,
            possession=55,
            shots=10,
            shots_on_target=5,
            pass_success_rate=pass_success_rate,
            raw_data={},
        )

    def test_analyze_possession_style_with_none_pass_success_rate(self):
        """
        _analyze_possession_style must not raise TypeError when
        pass_success_rate is None.
        """
        try:
            result = TacticalInsightsAnalyzer._analyze_possession_style(55, None)
        except TypeError as e:
            self.fail(
                f"_analyze_possession_style raised TypeError with None: {e}"
            )
        self.assertIn('type', result)

    def test_generate_insights_with_none_pass_success_rate(self):
        """
        _generate_insights must not raise TypeError when
        match.pass_success_rate is None.
        """
        match = self._make_match_obj(pass_success_rate=None)
        attack_pattern = {'type': 'balanced', 'wing_shots': 3, 'central_shots': 3}
        possession_style = {'type': 'balanced'}
        try:
            TacticalInsightsAnalyzer._generate_insights(match, {}, attack_pattern, possession_style)
        except TypeError as e:
            self.fail(
                f"_generate_insights raised TypeError with None: {e}"
            )

    def test_analyze_tactical_approach_with_none_pass_success_rate(self):
        """
        Full analyze_tactical_approach must not raise TypeError when
        match.pass_success_rate is None.
        """
        match = self._make_match_obj(pass_success_rate=None)
        try:
            TacticalInsightsAnalyzer.analyze_tactical_approach(match, [], {})
        except TypeError as e:
            self.fail(
                f"analyze_tactical_approach raised TypeError with None: {e}"
            )
