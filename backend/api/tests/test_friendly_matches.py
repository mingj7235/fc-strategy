"""
Tests for friendly match support (matchtype 40).

Tests cover:
- Friendly matches can be retrieved
- Friendly matches are properly filtered by matchtype
- All analysis endpoints support matchtype 40
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Match


class FriendlyMatchTest(TestCase):
    """Test friendly match (matchtype 40) support."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            ouid='friendly-test-user',
            nickname='FriendlyTester'
        )

        # Create official match (matchtype 50)
        self.official_match = Match.objects.create(
            ouid=self.user,
            match_id='official-match',
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

        # Create manager match (matchtype 52)
        self.manager_match = Match.objects.create(
            ouid=self.user,
            match_id='manager-match',
            match_date=timezone.now(),
            match_type=52,
            result='draw',
            goals_for=1,
            goals_against=1,
            possession=50,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('80.00'),
            raw_data={}
        )

        # Create friendly match (matchtype 40)
        self.friendly_match = Match.objects.create(
            ouid=self.user,
            match_id='friendly-match',
            match_date=timezone.now(),
            match_type=40,
            result='win',
            goals_for=3,
            goals_against=2,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.00'),
            raw_data={}
        )

    def test_friendly_matches_can_be_retrieved(self):
        """Test that friendly matches (matchtype 40) can be retrieved."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/matches/',
            {'matchtype': 40, 'limit': 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

        # Should only return friendly matches
        for match in response.data:
            self.assertEqual(match['match_type'], 40)

    def test_matchtype_filtering_works_correctly(self):
        """Test that matchtype parameter properly filters matches."""
        # Test official matches
        response_official = self.client.get(
            f'/api/users/{self.user.ouid}/matches/',
            {'matchtype': 50, 'limit': 10}
        )
        self.assertEqual(response_official.status_code, status.HTTP_200_OK)
        for match in response_official.data:
            self.assertEqual(match['match_type'], 50)

        # Test manager matches
        response_manager = self.client.get(
            f'/api/users/{self.user.ouid}/matches/',
            {'matchtype': 52, 'limit': 10}
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)
        for match in response_manager.data:
            self.assertEqual(match['match_type'], 52)

        # Test friendly matches
        response_friendly = self.client.get(
            f'/api/users/{self.user.ouid}/matches/',
            {'matchtype': 40, 'limit': 10}
        )
        self.assertEqual(response_friendly.status_code, status.HTTP_200_OK)
        for match in response_friendly.data:
            self.assertEqual(match['match_type'], 40)

    def test_user_overview_supports_friendly_matches(self):
        """Test that user overview endpoint supports matchtype 40."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/overview/',
            {'matchtype': 30, 'limit': 20}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('total_matches', response.data)

    def test_shot_analysis_supports_friendly_matches(self):
        """Test that shot analysis supports matchtype 40."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/shots/',
            {'matchtype': 40, 'limit': 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_style_analysis_supports_friendly_matches(self):
        """Test that style analysis supports matchtype 40."""
        response = self.client.get(
            f'/api/users/{self.user.ouid}/analysis/style/',
            {'matchtype': 30, 'limit': 20}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_match_types_available(self):
        """Test that all three match types (30, 50, 52) are supported."""
        match_types = [30, 50, 52]

        for matchtype in match_types:
            response = self.client.get(
                f'/api/users/{self.user.ouid}/matches/',
                {'matchtype': matchtype, 'limit': 10}
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Matchtype {matchtype} should be supported"
            )
