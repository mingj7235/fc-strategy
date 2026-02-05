"""
Regression tests for MultipleObjectsReturned bug in MatchViewSet.

Root cause: After migration 0009, Match.match_id is NOT unique alone — only
the (match_id, ouid) pair is unique.  When two users play the same match,
both rows share the same match_id but have different ouid values.

All MatchViewSet detail actions previously called:
    get_object_or_404(Match, match_id=match_id)          # DANGEROUS
which raises Match.MultipleObjectsReturned when 2 rows exist.

Fix: replaced with _get_match_safely() which uses filter().first() and
filters by ouid when available.
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache

from api.models import User, Match, ShotDetail


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_user(ouid, nickname):
    return User.objects.create(ouid=ouid, nickname=nickname)


def make_match(user, match_id, raw_data=None):
    return Match.objects.create(
        ouid=user,
        match_id=match_id,
        match_date=timezone.now(),
        match_type=50,
        result='win',
        goals_for=2,
        goals_against=0,
        possession=55,
        shots=8,
        shots_on_target=4,
        pass_success_rate=Decimal('80.00'),
        raw_data=raw_data or {'matchInfo': []},
    )


SHARED_MATCH_ID = 'shared-match-001'

ENDPOINTS = [
    'heatmap',
    'player-stats',
    'timeline',
    'assist-network',
    'shot-types',
    'pass-types',
    'heading-analysis',
    'analysis',
]


class TestMatchViewSetNoMultipleObjectsReturned(TestCase):
    """
    Verify that all MatchViewSet detail endpoints return 200 (or a safe
    non-500 code) when the same match_id exists for two different users.

    Before the fix every endpoint raised Match.MultipleObjectsReturned → 500.
    """

    def setUp(self):
        self.client = APIClient()

        # Two users, same match_id
        self.user_a = make_user('user-a-ouid', 'UserA')
        self.user_b = make_user('user-b-ouid', 'UserB')

        self.match_a = make_match(self.user_a, SHARED_MATCH_ID)
        self.match_b = make_match(self.user_b, SHARED_MATCH_ID)

        # Add a shot for the match so shot-dependent endpoints have data
        ShotDetail.objects.create(
            match=self.match_a,
            x=Decimal('0.8'), y=Decimal('0.5'),
            result='goal', shot_type=3, goal_time=30,
        )

        cache.clear()

    def _url(self, endpoint):
        return f'/api/matches/{SHARED_MATCH_ID}/{endpoint}/'

    def test_heatmap_no_500_with_ouid(self):
        resp = self.client.get(self._url('heatmap'), {'ouid': self.user_a.ouid})
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_heatmap_no_500_without_ouid(self):
        resp = self.client.get(self._url('heatmap'))
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_player_stats_no_500_with_ouid(self):
        resp = self.client.get(self._url('player-stats'), {'ouid': self.user_a.ouid})
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_player_stats_no_500_without_ouid(self):
        resp = self.client.get(self._url('player-stats'))
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeline_no_500_with_ouid(self):
        resp = self.client.get(self._url('timeline'), {'ouid': self.user_a.ouid})
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeline_no_500_without_ouid(self):
        resp = self.client.get(self._url('timeline'))
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_assist_network_no_500_with_ouid(self):
        resp = self.client.get(self._url('assist-network'), {'ouid': self.user_a.ouid})
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_assist_network_no_500_without_ouid(self):
        resp = self.client.get(self._url('assist-network'))
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_shot_types_no_500_with_ouid(self):
        resp = self.client.get(self._url('shot-types'), {'ouid': self.user_a.ouid})
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_shot_types_no_500_without_ouid(self):
        resp = self.client.get(self._url('shot-types'))
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_pass_types_no_500_with_ouid(self):
        resp = self.client.get(self._url('pass-types'), {'ouid': self.user_a.ouid})
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_pass_types_no_500_without_ouid(self):
        resp = self.client.get(self._url('pass-types'))
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_heading_analysis_no_500_with_ouid(self):
        resp = self.client.get(self._url('heading-analysis'), {'ouid': self.user_a.ouid})
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_heading_analysis_no_500_without_ouid(self):
        resp = self.client.get(self._url('heading-analysis'))
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_match_analysis_no_500_with_ouid(self):
        resp = self.client.get(self._url('analysis'), {'ouid': self.user_a.ouid})
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_match_analysis_no_500_without_ouid(self):
        resp = self.client.get(self._url('analysis'))
        self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestGetMatchSafelyHelper(TestCase):
    """Unit tests for MatchViewSet._get_match_safely"""

    def setUp(self):
        self.user_a = make_user('helper-user-a', 'HelperA')
        self.user_b = make_user('helper-user-b', 'HelperB')
        self.match_a = make_match(self.user_a, 'helper-match-001')
        self.match_b = make_match(self.user_b, 'helper-match-001')
        cache.clear()

    def _viewset(self):
        from api.views import MatchViewSet
        return MatchViewSet()

    def test_returns_correct_match_when_ouid_given(self):
        vs = self._viewset()
        match = vs._get_match_safely('helper-match-001', self.user_a.ouid)
        self.assertEqual(match.ouid, self.user_a)

    def test_returns_different_match_for_other_user(self):
        vs = self._viewset()
        match = vs._get_match_safely('helper-match-001', self.user_b.ouid)
        self.assertEqual(match.ouid, self.user_b)

    def test_returns_first_match_when_no_ouid(self):
        """Without ouid, first() is used — no MultipleObjectsReturned."""
        vs = self._viewset()
        try:
            match = vs._get_match_safely('helper-match-001')
        except Exception as exc:
            self.fail(f'_get_match_safely raised {type(exc).__name__}: {exc}')
        self.assertIsNotNone(match)

    def test_raises_http404_for_nonexistent_match(self):
        from django.http import Http404
        vs = self._viewset()
        with self.assertRaises(Http404):
            vs._get_match_safely('nonexistent-match-xyz')

    def test_raises_http404_when_ouid_not_owner(self):
        """If the match exists but belongs to a different user, raise Http404."""
        from django.http import Http404
        vs = self._viewset()
        other = make_user('helper-user-c', 'HelperC')
        with self.assertRaises(Http404):
            vs._get_match_safely('helper-match-001', other.ouid)
