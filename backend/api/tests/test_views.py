"""
Comprehensive tests for API views and endpoints.

Tests cover:
- User search and retrieval
- Match listing with user perspective
- Match detail with ouid parameter support
- Match analysis endpoint with correct perspective
- Player stats filtering by user
- Timeline analysis
- Cache key generation with ouid
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Match, ShotDetail, PlayerPerformance
from django.core.cache import cache


class UserViewSetTest(TestCase):
    """Test UserViewSet endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(
            ouid='test-user-1',
            nickname='TestPlayer1',
            max_division=2100
        )
        self.user2 = User.objects.create(
            ouid='test-user-2',
            nickname='TestPlayer2',
            max_division=1900
        )

    def test_search_user_by_nickname(self):
        """Test searching user by nickname."""
        response = self.client.get('/api/users/search/', {'nickname': 'TestPlayer1'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'TestPlayer1')
        self.assertEqual(response.data['ouid'], 'test-user-1')

    def test_search_user_not_found(self):
        """Test searching for non-existent user."""
        response = self.client.get('/api/users/search/', {'nickname': 'NonExistent'})

        # Should return 404 or create new user via API
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK])

    def test_get_user_by_ouid(self):
        """Test retrieving user by ouid."""
        response = self.client.get(f'/api/users/{self.user1.ouid}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'TestPlayer1')
        self.assertEqual(response.data['max_division'], 2100)

    def test_user_overview_endpoint(self):
        """Test user overview endpoint."""
        # Create some matches for the user
        Match.objects.create(
            ouid=self.user1,
            match_id='match-1',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=3,
            goals_against=1,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.00'),
            raw_data={}
        )

        response = self.client.get(
            f'/api/users/{self.user1.ouid}/overview/',
            {'matchtype': 50, 'limit': 20}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)            # 현재 필드명 (구: user_info)
        self.assertIn('trends', response.data)          # recent_form은 trends 안에 있음
        self.assertIn('recent_form', response.data['trends'])


class MatchViewSetTest(TestCase):
    """Test MatchViewSet endpoints with perspective support."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(
            ouid='player1-ouid',
            nickname='창동소년'
        )
        self.user2 = User.objects.create(
            ouid='player2-ouid',
            nickname='ZinedineZidane05'
        )

        # Create same match from both perspectives
        self.match_date = timezone.now()

        # User1 perspective: lose 0-1
        self.match1 = Match.objects.create(
            ouid=self.user1,
            match_id='shared-match-123',
            match_date=self.match_date,
            match_type=50,
            result='lose',
            goals_for=0,
            goals_against=1,
            possession=45,
            shots=10,
            shots_on_target=4,
            pass_success_rate=Decimal('78.00'),
            opponent_nickname='ZinedineZidane05',
            raw_data={'matchInfo': []}
        )

        # User2 perspective: win 1-0
        self.match2 = Match.objects.create(
            ouid=self.user2,
            match_id='shared-match-123',
            match_date=self.match_date,
            match_type=50,
            result='win',
            goals_for=1,
            goals_against=0,
            possession=55,
            shots=12,
            shots_on_target=6,
            pass_success_rate=Decimal('82.00'),
            opponent_nickname='창동소년',
            raw_data={'matchInfo': []}
        )

    def test_match_detail_with_ouid_parameter(self):
        """
        Critical test: Match detail should return correct perspective based on ouid parameter.
        This tests the fix for the user perspective bug.
        """
        # Request from user1's perspective
        response = self.client.get(
            f'/api/matches/shared-match-123/detail/',
            {'ouid': self.user1.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see user1's perspective (lose, 0-1)
        self.assertEqual(response.data['result'], 'lose')
        self.assertEqual(response.data['goals_for'], 0)
        self.assertEqual(response.data['goals_against'], 1)
        self.assertEqual(response.data['opponent_nickname'], 'ZinedineZidane05')

        # Request from user2's perspective
        response = self.client.get(
            f'/api/matches/shared-match-123/detail/',
            {'ouid': self.user2.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see user2's perspective (win, 1-0)
        self.assertEqual(response.data['result'], 'win')
        self.assertEqual(response.data['goals_for'], 1)
        self.assertEqual(response.data['goals_against'], 0)
        self.assertEqual(response.data['opponent_nickname'], '창동소년')

    def test_match_detail_without_ouid_parameter(self):
        """Test match detail without ouid parameter (should return first match found)."""
        response = self.client.get(f'/api/matches/shared-match-123/detail/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return one of the perspectives (implementation dependent)
        self.assertIn(response.data['result'], ['win', 'lose'])

    def test_match_heatmap_with_ouid(self):
        """Test match heatmap endpoint with ouid parameter."""
        # Create shot details for user1's perspective
        ShotDetail.objects.create(
            match=self.match1,
            x=Decimal('0.8500'),
            y=Decimal('0.4500'),
            result='off_target',
            shot_type=2,
            goal_time=30
        )

        response = self.client.get(
            f'/api/matches/shared-match-123/heatmap/',
            {'ouid': self.user1.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if len(response.data) > 0:
            self.assertIn('x', response.data[0])
            self.assertIn('y', response.data[0])
            self.assertIn('result', response.data[0])

    def test_match_analysis_cache_key_includes_ouid(self):
        """
        Critical test: Cache keys must include ouid to prevent wrong perspective.
        This tests the cache key fix.
        """
        # Clear cache first
        cache.clear()

        # Create players for both perspectives
        PlayerPerformance.objects.create(
            match=self.match1,
            user_ouid=self.user1,
            spid=1001,
            player_name='User1 Player',
            position=27,
            grade=7,
            rating=Decimal('7.0')
        )

        PlayerPerformance.objects.create(
            match=self.match2,
            user_ouid=self.user2,
            spid=2001,
            player_name='User2 Player',
            position=27,
            grade=8,
            rating=Decimal('8.0')
        )

        # Request user1's analysis
        response1 = self.client.get(
            f'/api/matches/shared-match-123/analysis/',
            {'ouid': self.user1.ouid}
        )

        # Request user2's analysis
        response2 = self.client.get(
            f'/api/matches/shared-match-123/analysis/',
            {'ouid': self.user2.ouid}
        )

        # Both should return 200
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Should have different perspectives
        self.assertEqual(response1.data['match_overview']['result'], 'lose')
        self.assertEqual(response2.data['match_overview']['result'], 'win')

        self.assertEqual(response1.data['match_overview']['user_nickname'], '창동소년')
        self.assertEqual(response2.data['match_overview']['user_nickname'], 'ZinedineZidane05')

    def test_player_stats_filtered_by_user(self):
        """
        Critical test: Player stats should only return the specified user's players.
        This ensures only the searched user's 18 players are shown, not all 36.
        """
        # Create 3 players for user1
        for i in range(3):
            PlayerPerformance.objects.create(
                match=self.match1,
                user_ouid=self.user1,
                spid=1000 + i,
                player_name=f'User1 Player {i}',
                position=27,
                grade=7,
                rating=Decimal('7.0')
            )

        # Create 3 players for user2
        for i in range(3):
            PlayerPerformance.objects.create(
                match=self.match2,
                user_ouid=self.user2,
                spid=2000 + i,
                player_name=f'User2 Player {i}',
                position=27,
                grade=7,
                rating=Decimal('7.0')
            )

        # Request user1's players
        response = self.client.get(
            f'/api/matches/shared-match-123/player-stats/',
            {'ouid': self.user1.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only have user1's players
        all_players = response.data.get('all_players', [])
        self.assertEqual(len(all_players), 3)

        for player in all_players:
            self.assertIn('User1 Player', player['player_name'])
            self.assertNotIn('User2 Player', player['player_name'])

    def test_timeline_analysis(self):
        """Test timeline analysis endpoint."""
        # Create shot details with different times
        ShotDetail.objects.create(
            match=self.match1,
            x=Decimal('0.8500'),
            y=Decimal('0.4500'),
            result='goal',
            shot_type=3,
            goal_time=30  # First half
        )

        ShotDetail.objects.create(
            match=self.match1,
            x=Decimal('0.7500'),
            y=Decimal('0.5500'),
            result='on_target',
            shot_type=2,
            goal_time=60  # Second half
        )

        response = self.client.get(
            f'/api/matches/shared-match-123/timeline/',
            {'ouid': self.user1.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('xg_by_period', response.data)
        self.assertIn('key_moments', response.data)

        xg_by_period = response.data['xg_by_period']
        self.assertIn('first_half', xg_by_period)
        self.assertIn('second_half', xg_by_period)

    def test_match_analysis_comprehensive(self):
        """Test comprehensive match analysis endpoint with all sections."""
        # Create shot details
        ShotDetail.objects.create(
            match=self.match1,
            x=Decimal('0.8500'),
            y=Decimal('0.4500'),
            result='goal',
            shot_type=3,
            goal_time=45
        )

        # Create player performances
        PlayerPerformance.objects.create(
            match=self.match1,
            user_ouid=self.user1,
            spid=103259207,
            player_name='Test Player',
            position=27,
            grade=8,
            rating=Decimal('8.5'),
            goals=2,
            assists=1,
            pass_attempts=50,
            pass_success=42
        )

        response = self.client.get(
            f'/api/matches/shared-match-123/analysis/',
            {'ouid': self.user1.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check all required sections
        self.assertIn('match_overview', response.data)
        self.assertIn('player_performances', response.data)
        self.assertIn('timeline', response.data)
        self.assertIn('tactical_insights', response.data)

        # Verify match overview
        match_overview = response.data['match_overview']
        self.assertEqual(match_overview['user_nickname'], '창동소년')
        self.assertEqual(match_overview['opponent_nickname'], 'ZinedineZidane05')
        self.assertEqual(match_overview['result'], 'lose')

        # Verify player performances structure
        player_perfs = response.data['player_performances']
        self.assertIn('top_performers', player_perfs)
        self.assertIn('all_players', player_perfs)

    def test_get_user_matches(self):
        """Test getting user's match list."""
        response = self.client.get(
            f'/api/users/{self.user1.ouid}/matches/',
            {'matchtype': 50, 'limit': 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

        if len(response.data) > 0:
            match = response.data[0]
            self.assertIn('match_id', match)
            self.assertIn('result', match)
            self.assertIn('shots', match)  # Bug fix verification
            self.assertIn('shots_on_target', match)  # Bug fix verification
            self.assertIn('opponent_nickname', match)  # Bug fix verification


class AnalysisViewSetTest(TestCase):
    """Test various analysis endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            ouid='analysis-user',
            nickname='AnalysisPlayer'
        )

        # Create multiple matches for analysis
        for i in range(5):
            match = Match.objects.create(
                ouid=self.user,
                match_id=f'match-{i}',
                match_date=timezone.now(),
                match_type=50,
                result='win' if i % 2 == 0 else 'lose',
                goals_for=2,
                goals_against=1,
                possession=55,
                shots=12,
                shots_on_target=6,
                pass_success_rate=Decimal('80.00'),
                raw_data={'matchInfo': []}
            )

            # Add shot details
            ShotDetail.objects.create(
                match=match,
                x=Decimal('0.8000'),
                y=Decimal('0.5000'),
                result='goal',
                shot_type=3,
                goal_time=30
            )

    def test_shot_analysis_endpoint(self):
        """Test shot analysis endpoint uses current field names."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/shots/',
            {'matchtype': 50, 'limit': 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_shots', response.data)
        self.assertIn('zone_analysis', response.data)  # 현재 필드명 (구: shot_zones)

    def test_style_analysis_endpoint(self):
        """Test style analysis endpoint uses current field names."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/style/',
            {'matchtype': 50, 'limit': 20}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('possession_style', response.data)
        self.assertIn('attack_pattern', response.data)  # 현재 필드명 (구: attack_style)

    def test_power_rankings_endpoint(self):
        """Test power rankings endpoint."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/power-rankings/',
            {'matchtype': 50, 'limit': 20}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Power rankings should have position-based rankings

    def test_pass_analysis_endpoint(self):
        """Test pass analysis returns 200 even without PlayerPerformance data."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/passes/',
            {'matchtype': 50, 'limit': 20}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_statistics_endpoint(self):
        """Test user statistics endpoint."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/statistics/',
            {'matchtype': 50, 'limit': 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_matches', response.data)
        self.assertIn('win_rate', response.data)


class CacheTest(TestCase):
    """Test caching behavior."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            ouid='cache-test-user',
            nickname='CachePlayer'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='cache-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=55,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('80.00'),
            raw_data={}
        )

        cache.clear()

    def test_match_analysis_caching(self):
        """Test that match analysis is cached properly."""
        # First request - should hit database
        response1 = self.client.get(
            f'/api/matches/cache-match/analysis/',
            {'ouid': self.user.ouid}
        )

        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Second request - should hit cache
        response2 = self.client.get(
            f'/api/matches/cache-match/analysis/',
            {'ouid': self.user.ouid}
        )

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response2.data)

    def test_cache_invalidation_on_different_ouid(self):
        """Test that different ouids have separate cache entries."""
        user2 = User.objects.create(
            ouid='cache-test-user-2',
            nickname='CachePlayer2'
        )

        match2 = Match.objects.create(
            ouid=user2,
            match_id='cache-match',
            match_date=timezone.now(),
            match_type=50,
            result='lose',
            goals_for=1,
            goals_against=2,
            possession=45,
            shots=8,
            shots_on_target=3,
            pass_success_rate=Decimal('75.00'),
            raw_data={}
        )

        # Request for user1
        response1 = self.client.get(
            f'/api/matches/cache-match/analysis/',
            {'ouid': self.user.ouid}
        )

        # Request for user2
        response2 = self.client.get(
            f'/api/matches/cache-match/analysis/',
            {'ouid': user2.ouid}
        )

        # Should have different results (not sharing cache)
        self.assertNotEqual(
            response1.data['match_overview']['result'],
            response2.data['match_overview']['result']
        )
