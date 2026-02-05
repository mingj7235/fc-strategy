"""
Tests for participated players filtering (rating > 0).

Tests cover:
- Only players who actually participated (rating > 0) are returned
- Non-participated players (rating = 0) are excluded
- Match analysis returns only participated players
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Match, PlayerPerformance


class ParticipatedPlayersFilterTest(TestCase):
    """Test that only participated players (rating > 0) are shown."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            ouid='participated-test-user',
            nickname='ParticipatedTester'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='participated-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=55,
            shots=12,
            shots_on_target=6,
            pass_success_rate=Decimal('82.00'),
            raw_data={}
        )

        # Create 11 participated players (rating > 0)
        for i in range(11):
            PlayerPerformance.objects.create(
                match=self.match,
                user_ouid=self.user,
                spid=1000 + i,
                player_name=f'Player {i}',
                position=i,
                grade=7,
                rating=Decimal('7.0')  # Actually participated
            )

        # Create 7 non-participated players (rating = 0) - bench players
        for i in range(7):
            PlayerPerformance.objects.create(
                match=self.match,
                user_ouid=self.user,
                spid=2000 + i,
                player_name=f'Bench {i}',
                position=11 + i,
                grade=6,
                rating=Decimal('0.0')  # Did not participate
            )

    def test_only_participated_players_in_match_analysis(self):
        """
        Critical test: Match analysis should return only participated players (rating > 0).
        Non-participated players (rating = 0) should be excluded.
        """
        response = self.client.get(
            f'/api/matches/participated-match/analysis/',
            {'ouid': self.user.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only have 11 players (participated), not 18
        all_players = response.data['player_performances']['all_players']
        self.assertEqual(len(all_players), 11)

        # All players should have rating > 0
        for player in all_players:
            self.assertGreater(float(player['rating']), 0.0)
            self.assertIn('Player', player['player_name'])
            self.assertNotIn('Bench', player['player_name'])

    def test_top_performers_only_from_participated(self):
        """Test that top performers are selected only from participated players."""
        response = self.client.get(
            f'/api/matches/participated-match/analysis/',
            {'ouid': self.user.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        top_performers = response.data['player_performances']['top_performers']

        # Top performers should be from participated players only
        for player in top_performers:
            self.assertGreater(float(player['rating']), 0.0)

    def test_player_stats_endpoint_filters_participated(self):
        """Test that player-stats endpoint also filters to participated players only."""
        response = self.client.get(
            f'/api/matches/participated-match/player-stats/',
            {'ouid': self.user.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        all_players = response.data['all_players']
        self.assertEqual(len(all_players), 11)

        for player in all_players:
            self.assertGreater(float(player['rating']), 0.0)

    def test_bench_players_are_not_shown(self):
        """Explicitly test that bench players (rating = 0) are not shown."""
        response = self.client.get(
            f'/api/matches/participated-match/analysis/',
            {'ouid': self.user.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        all_players = response.data['player_performances']['all_players']
        player_names = [p['player_name'] for p in all_players]

        # No bench players should be in the list
        for i in range(7):
            self.assertNotIn(f'Bench {i}', player_names)

    def test_match_with_no_players_returns_empty(self):
        """
        Edge case: If a match has no player performance data,
        return empty list.
        """
        # Create match with no players
        match_no_players = Match.objects.create(
            ouid=self.user,
            match_id='no-players-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=1,
            goals_against=0,
            possession=50,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('80.00'),
            raw_data={}
        )

        response = self.client.get(
            f'/api/matches/no-players-match/analysis/',
            {'ouid': self.user.ouid}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should return empty list
        all_players = response.data['player_performances']['all_players']
        self.assertEqual(len(all_players), 0)
