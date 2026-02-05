"""
TDD tests for advanced analysis endpoints previously missing test coverage.

Covers per-match endpoints:
  - assist-network, shot-types, pass-types, heading-analysis

Per-user analysis endpoints:
  - set-pieces, defense, pass-variety, shooting-quality, controller

Global endpoints:
  - tier-info, search-players
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from api.models import User, Match, ShotDetail


# ---------------------------------------------------------------------------
# Shared raw_data fixture – used by most tests
# ---------------------------------------------------------------------------
FULL_RAW_DATA = {
    'matchInfo': [
        {
            'ouid': 'adv-user',
            'shoot': {
                'shootTotal': 15,
                'effectiveShootTotal': 8,
                'goalTotalDisplay': 3,
                'ownGoal': 0,
                'shootHeading': 3,
                'goalHeading': 1,
                'shootFreekick': 2,
                'goalFreekick': 0,
                'shootInPenalty': 10,
                'goalInPenalty': 2,
                'shootOutPenalty': 5,
                'goalOutPenalty': 1,
                'shootPenalty': 0,
                'goalPenalty': 0,
            },
            'pass': {
                'passTry': 60,
                'passSuccess': 50,
                'shortPassTry': 35,
                'shortPassSuccess': 31,
                'longPassTry': 15,
                'longPassSuccess': 11,
                'throughPassTry': 6,
                'throughNogoalTry': 3,
                'throughPassSuccess': 4,
                'lobbedThroughPassTry': 2,
                'lobbedThroughPassSuccess': 1,
                'drivenGroundPassTry': 3,
                'drivenGroundPassSuccess': 2,
            },
            'defence': {
                'tackleTry': 12,
                'tackleSuccess': 8,
                'blockTry': 5,
                'block': 3,
                'intercept': 4,
            },
            'player': [],
        }
    ]
}


def make_match(user, match_id, raw_data=None, result='win', goals_for=2, goals_against=1):
    """Helper to create a Match for testing."""
    return Match.objects.create(
        ouid=user,
        match_id=match_id,
        match_date=timezone.now(),
        match_type=50,
        result=result,
        goals_for=goals_for,
        goals_against=goals_against,
        possession=60,
        shots=15,
        shots_on_target=8,
        pass_success_rate=Decimal('85.00'),
        raw_data=raw_data or FULL_RAW_DATA,
    )


# ---------------------------------------------------------------------------
# Per-match: assist-network
# ---------------------------------------------------------------------------
class AssistNetworkEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='adv-user', nickname='AdvPlayer')
        self.match = make_match(self.user, 'adv-match-001')

        # Shots with assist data
        for i in range(3):
            ShotDetail.objects.create(
                match=self.match,
                x=Decimal('0.8500'), y=Decimal('0.5000'),
                result='goal', shot_type=3,
                goal_time=30 + i * 10,
                assist_x=Decimal('0.7000'), assist_y=Decimal('0.5000'),
                assist_spid=103259207, shooter_spid=103259208,
            )
        # Shots without assist data
        for i in range(4):
            ShotDetail.objects.create(
                match=self.match,
                x=Decimal('0.7000'), y=Decimal('0.5000'),
                result='on_target', shot_type=2,
                goal_time=60 + i * 5,
            )

    def test_returns_200(self):
        resp = self.client.get(f'/api/matches/adv-match-001/assist-network/?ouid=adv-user')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_required_keys(self):
        resp = self.client.get(f'/api/matches/adv-match-001/assist-network/?ouid=adv-user')
        data = resp.data
        self.assertIn('assist_heatmap', data)
        self.assertIn('player_network', data)
        self.assertIn('top_playmakers', data)

    def test_empty_shots_returns_200_not_500(self):
        """Match with no ShotDetails must not crash — return empty analysis."""
        match_empty = make_match(self.user, 'adv-match-empty')
        resp = self.client.get(f'/api/matches/adv-match-empty/assist-network/?ouid=adv-user')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('assist_heatmap', resp.data)


# ---------------------------------------------------------------------------
# Per-match: shot-types
# ---------------------------------------------------------------------------
class ShotTypesEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='adv-user2', nickname='ShotTypePlayer')
        self.match = make_match(self.user, 'shot-type-match')

        for shot_type, result in [(3, 'goal'), (2, 'on_target'), (1, 'off_target'), (3, 'blocked')]:
            ShotDetail.objects.create(
                match=self.match,
                x=Decimal('0.8500'), y=Decimal('0.5000'),
                result=result, shot_type=shot_type,
                in_penalty=True, hit_post=False,
                goal_time=30,
            )

    def test_returns_200(self):
        resp = self.client.get(f'/api/matches/shot-type-match/shot-types/?ouid=adv-user2')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_type_breakdown(self):
        resp = self.client.get(f'/api/matches/shot-type-match/shot-types/?ouid=adv-user2')
        self.assertIn('type_breakdown', resp.data)

    def test_empty_shots_returns_200(self):
        match_empty = make_match(self.user, 'shot-type-empty')
        resp = self.client.get(f'/api/matches/shot-type-empty/shot-types/?ouid=adv-user2')
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Per-match: pass-types
# ---------------------------------------------------------------------------
PASS_RAW_DATA_USER3 = {
    'matchInfo': [
        {
            'ouid': 'adv-user3',
            'pass': {
                'passTry': 60,
                'passSuccess': 50,
                'shortPassTry': 35,
                'shortPassSuccess': 31,
                'longPassTry': 15,
                'longPassSuccess': 11,
                'throughPassTry': 6,
                'throughNogoalTry': 3,
                'throughPassSuccess': 4,
                'lobbedThroughPassTry': 2,
                'lobbedThroughPassSuccess': 1,
                'drivenGroundPassTry': 3,
                'drivenGroundPassSuccess': 2,
            },
        }
    ]
}


class PassTypesEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='adv-user3', nickname='PassTypePlayer')
        # Match with pass data — raw_data ouid must match self.user.ouid
        self.match = make_match(self.user, 'pass-type-match', raw_data=PASS_RAW_DATA_USER3)

    def test_returns_200_with_pass_data(self):
        resp = self.client.get(f'/api/matches/pass-type-match/pass-types/?ouid=adv-user3')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_pass_breakdown(self):
        resp = self.client.get(f'/api/matches/pass-type-match/pass-types/?ouid=adv-user3')
        self.assertIn('pass_breakdown', resp.data)

    def test_no_raw_data_returns_error(self):
        """Match with empty raw_data should return 4xx."""
        match_no_raw = Match.objects.create(
            ouid=self.user,
            match_id='pass-type-no-raw',
            match_date=timezone.now(),
            match_type=50,
            result='draw',
            goals_for=1, goals_against=1,
            possession=50, shots=10, shots_on_target=5,
            raw_data={},
        )
        resp = self.client.get(f'/api/matches/pass-type-no-raw/pass-types/?ouid=adv-user3')
        self.assertIn(resp.status_code, [400, 404])


# ---------------------------------------------------------------------------
# Per-match: heading-analysis
# ---------------------------------------------------------------------------
class HeadingAnalysisEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='adv-user4', nickname='HeadingPlayer')
        self.match = make_match(self.user, 'heading-match')

        # Heading shots (shot_type == 3 is power shot; heading shots are shot_type == 1)
        for i in range(3):
            ShotDetail.objects.create(
                match=self.match,
                x=Decimal('0.8500'), y=Decimal('0.5000'),
                result='goal' if i == 0 else 'on_target',
                shot_type=1,  # Header type
                goal_time=30 + i * 10,
                assist_x=Decimal('0.2000'), assist_y=Decimal('0.1000'),
            )

    def test_returns_200(self):
        resp = self.client.get(f'/api/matches/heading-match/heading-analysis/?ouid=adv-user4')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_heading_stats(self):
        resp = self.client.get(f'/api/matches/heading-match/heading-analysis/?ouid=adv-user4')
        self.assertIn('heading_stats', resp.data)

    def test_empty_shots_returns_200(self):
        match_empty = make_match(self.user, 'heading-match-empty')
        resp = self.client.get(f'/api/matches/heading-match-empty/heading-analysis/?ouid=adv-user4')
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Per-user: set-pieces
# ---------------------------------------------------------------------------
class SetPiecesEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='sp-user', nickname='SetPiecePlayer')
        # Create several matches so _ensure_matches has data
        for i in range(5):
            make_match(self.user, f'sp-match-{i}')

    def test_returns_200(self):
        resp = self.client.get(f'/api/users/sp-user/analysis/set-pieces/?matchtype=50&limit=5')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_required_keys(self):
        resp = self.client.get(f'/api/users/sp-user/analysis/set-pieces/?matchtype=50&limit=5')
        data = resp.data
        self.assertIn('matchtype', data)
        self.assertIn('matches_analyzed', data)
        self.assertIn('freekick_analysis', data)

    def test_no_matches_returns_404(self):
        user_empty = User.objects.create(ouid='sp-empty', nickname='EmptyPlayer')
        resp = self.client.get(f'/api/users/sp-empty/analysis/set-pieces/?matchtype=50&limit=5')
        self.assertEqual(resp.status_code, 404)


# ---------------------------------------------------------------------------
# Per-user: defense
# ---------------------------------------------------------------------------
class DefenseEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='def-user', nickname='DefensePlayer')
        for i in range(5):
            make_match(self.user, f'def-match-{i}')

    def test_returns_200(self):
        resp = self.client.get(f'/api/users/def-user/analysis/defense/?matchtype=50&limit=5')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_tackle_stats(self):
        resp = self.client.get(f'/api/users/def-user/analysis/defense/?matchtype=50&limit=5')
        data = resp.data
        self.assertIn('tackle_stats', data)
        self.assertIn('matches_analyzed', data)


# ---------------------------------------------------------------------------
# Per-user: pass-variety
# ---------------------------------------------------------------------------
class PassVarietyEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='pv-user', nickname='PassVarietyPlayer')
        for i in range(5):
            make_match(self.user, f'pv-match-{i}')

    def test_returns_200(self):
        resp = self.client.get(f'/api/users/pv-user/analysis/pass-variety/?matchtype=50&limit=5')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_pass_distribution(self):
        resp = self.client.get(f'/api/users/pv-user/analysis/pass-variety/?matchtype=50&limit=5')
        data = resp.data
        self.assertIn('pass_distribution', data)
        self.assertIn('matches_analyzed', data)


# ---------------------------------------------------------------------------
# Per-user: shooting-quality
# ---------------------------------------------------------------------------
class ShootingQualityEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='sq-user', nickname='ShootingQualityPlayer')
        for i in range(5):
            make_match(self.user, f'sq-match-{i}')

    def test_returns_200(self):
        resp = self.client.get(f'/api/users/sq-user/analysis/shooting-quality/?matchtype=50&limit=5')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_location_analysis(self):
        resp = self.client.get(f'/api/users/sq-user/analysis/shooting-quality/?matchtype=50&limit=5')
        data = resp.data
        self.assertIn('location_analysis', data)
        self.assertIn('matches_analyzed', data)


# ---------------------------------------------------------------------------
# Per-user: controller
# ---------------------------------------------------------------------------
class ControllerEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(ouid='ctrl-user', nickname='ControllerPlayer')
        for i in range(5):
            make_match(self.user, f'ctrl-match-{i}')

    def test_returns_200(self):
        resp = self.client.get(f'/api/users/ctrl-user/analysis/controller/?matchtype=50&limit=5')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_controller_stats(self):
        resp = self.client.get(f'/api/users/ctrl-user/analysis/controller/?matchtype=50&limit=5')
        data = resp.data
        self.assertIn('controller_stats', data)
        self.assertIn('matches_analyzed', data)


# ---------------------------------------------------------------------------
# Global: tier-info
# ---------------------------------------------------------------------------
class TierInfoEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_returns_200(self):
        resp = self.client.get('/api/tier-info/')
        self.assertEqual(resp.status_code, 200)

    def test_response_has_tiers_and_total(self):
        resp = self.client.get('/api/tier-info/')
        data = resp.data
        self.assertIn('tiers', data)
        self.assertIn('total_tiers', data)
        self.assertIsInstance(data['tiers'], list)
        self.assertGreater(data['total_tiers'], 0)


# ---------------------------------------------------------------------------
# Global: search-players
# ---------------------------------------------------------------------------
class SearchPlayersEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_missing_query_returns_400(self):
        resp = self.client.get('/api/search-players/')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.data)

    def test_single_char_query_returns_400(self):
        """Query must be at least 2 characters."""
        resp = self.client.get('/api/search-players/?q=a')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.data)

    def test_valid_query_returns_200(self):
        """A valid query must return 200 with the expected structure."""
        resp = self.client.get('/api/search-players/?q=Son')
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        self.assertIn('query', data)
        self.assertIn('count', data)
        self.assertIn('players', data)
        self.assertIsInstance(data['players'], list)

    def test_valid_query_result_structure(self):
        """If players are found, each result has the expected fields."""
        resp = self.client.get('/api/search-players/?q=Son&limit=5')
        self.assertEqual(resp.status_code, 200)
        players = resp.data['players']
        for player in players:
            self.assertIn('spid', player)
            self.assertIn('name', player)
            self.assertIn('image_url', player)
