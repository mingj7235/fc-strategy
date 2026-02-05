"""
Comprehensive tests for Django signals.

Tests cover:
- ShotDetail extraction on Match creation
- PlayerPerformance extraction on Match creation
- Signal triggering and data extraction
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from api.models import User, Match, ShotDetail, PlayerPerformance


class MatchSignalsTest(TestCase):
    """Test signals triggered on Match creation."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='signal-test-user',
            nickname='SignalTester'
        )

    def test_shot_detail_extraction_on_match_creation(self):
        """Test that ShotDetails are automatically created when Match is saved."""
        raw_data = {
            'matchInfo': [
                {
                    'ouid': 'signal-test-user',
                    'shootDetail': [
                        {
                            'goalTime': 30,
                            'x': 0.8512,
                            'y': 0.4523,
                            'type': 3,
                            'result': 1,  # goal
                            'assist': {
                                'x': 0.7000,
                                'y': 0.5000
                            }
                        },
                        {
                            'goalTime': 60,
                            'x': 0.7500,
                            'y': 0.5500,
                            'type': 2,
                            'result': 2,  # on_target
                        }
                    ]
                }
            ]
        }

        # Create match with raw_data containing shot details
        match = Match.objects.create(
            ouid=self.user,
            match_id='signal-match-shot',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.00'),
            raw_data=raw_data
        )

        # Signal should have created ShotDetails
        shot_details = ShotDetail.objects.filter(match=match)

        # Should have 2 shots
        self.assertEqual(shot_details.count(), 2)

        # Verify shot data
        shot1 = shot_details.get(goal_time=30)
        self.assertEqual(float(shot1.x), 0.8512)
        self.assertEqual(float(shot1.y), 0.4523)
        self.assertEqual(shot1.result, 'goal')
        self.assertIsNotNone(shot1.assist_x)

        shot2 = shot_details.get(goal_time=60)
        self.assertEqual(shot2.result, 'on_target')

    def test_player_performance_extraction_on_match_creation(self):
        """Test that PlayerPerformances are automatically created when Match is saved."""
        raw_data = {
            'matchInfo': [
                {
                    'ouid': 'signal-test-user',
                    'player': [
                        {
                            'spId': 103259207,
                            'spPosition': 27,
                            'spGrade': 8,
                            'status': {
                                'spRating': 8.5,
                                'goal': 2,
                                'assist': 1,
                                'shoot': {
                                    'shootTotal': 5,
                                    'effectiveShootTotal': 4,
                                    'shootOutScore': 0
                                },
                                'pass': {
                                    'passTry': 50,
                                    'passSuccess': 42,
                                    'shortPassTry': 35,
                                    'shortPassSuccess': 32,
                                    'longPassTry': 10,
                                    'longPassSuccess': 7,
                                    'throughPassTry': 5,
                                    'throughPassSuccess': 3
                                },
                                'dribble': {
                                    'dribbleTry': 10,
                                    'dribbleSuccess': 7
                                },
                                'defence': {
                                    'tackleTry': 5,
                                    'tackleSuccess': 3,
                                    'blockTry': 2,
                                    'block': 1
                                },
                                'aerialSuccess': 3,
                                'yellowCards': 0,
                                'redCards': 0
                            }
                        }
                    ]
                }
            ]
        }

        # Create match with raw_data containing player data
        match = Match.objects.create(
            ouid=self.user,
            match_id='signal-match-player',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.00'),
            raw_data=raw_data
        )

        # Signal should have created PlayerPerformances
        players = PlayerPerformance.objects.filter(match=match)

        # Should have 1 player
        self.assertGreaterEqual(players.count(), 1)

        # Verify player data
        player = players.first()
        self.assertEqual(player.spid, 103259207)
        self.assertEqual(player.position, 27)
        self.assertEqual(player.grade, 8)
        self.assertEqual(float(player.rating), 8.5)
        self.assertEqual(player.goals, 2)
        self.assertEqual(player.assists, 1)
        self.assertEqual(player.shots, 5)
        self.assertEqual(player.shots_on_target, 4)
        self.assertEqual(player.pass_attempts, 50)
        self.assertEqual(player.pass_success, 42)
        self.assertEqual(player.dribble_attempts, 10)
        self.assertEqual(player.dribble_success, 7)

    def test_no_signal_on_match_update(self):
        """Test that signals don't re-trigger on Match update."""
        raw_data = {
            'matchInfo': [
                {
                    'ouid': 'signal-test-user',
                    'shootDetail': [
                        {
                            'goalTime': 30,
                            'x': 0.8500,
                            'y': 0.5000,
                            'type': 3,
                            'result': 1
                        }
                    ]
                }
            ]
        }

        match = Match.objects.create(
            ouid=self.user,
            match_id='signal-update-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.00'),
            raw_data=raw_data
        )

        # Should have created 1 shot
        initial_count = ShotDetail.objects.filter(match=match).count()
        self.assertEqual(initial_count, 1)

        # Update match
        match.result = 'draw'
        match.save()

        # Should still have only 1 shot (signal should not re-trigger)
        updated_count = ShotDetail.objects.filter(match=match).count()
        self.assertEqual(updated_count, initial_count)

    def test_signal_with_empty_raw_data(self):
        """Test that signals handle empty raw_data gracefully."""
        match = Match.objects.create(
            ouid=self.user,
            match_id='empty-data-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.00'),
            raw_data={}
        )

        # Should not crash, should have 0 shots
        shot_count = ShotDetail.objects.filter(match=match).count()
        self.assertEqual(shot_count, 0)

        # Should not crash, should have 0 players
        player_count = PlayerPerformance.objects.filter(match=match).count()
        self.assertEqual(player_count, 0)

    def test_signal_with_malformed_raw_data(self):
        """Test that signals handle malformed raw_data gracefully."""
        raw_data = {
            'matchInfo': [
                {
                    # Missing required fields
                    'shootDetail': []
                }
            ]
        }

        # Should not crash
        match = Match.objects.create(
            ouid=self.user,
            match_id='malformed-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.00'),
            raw_data=raw_data
        )

        # Should handle gracefully
        shot_count = ShotDetail.objects.filter(match=match).count()
        self.assertEqual(shot_count, 0)

    def test_multiple_match_signal_isolation(self):
        """Test that signals for different matches don't interfere."""
        user2 = User.objects.create(
            ouid='signal-user-2',
            nickname='SignalTester2'
        )

        raw_data1 = {
            'matchInfo': [
                {
                    'ouid': 'signal-test-user',
                    'shootDetail': [
                        {
                            'goalTime': 30,
                            'x': 0.8500,
                            'y': 0.5000,
                            'type': 3,
                            'result': 1
                        }
                    ]
                }
            ]
        }

        raw_data2 = {
            'matchInfo': [
                {
                    'ouid': 'signal-user-2',
                    'shootDetail': [
                        {
                            'goalTime': 45,
                            'x': 0.7500,
                            'y': 0.4500,
                            'type': 2,
                            'result': 2
                        },
                        {
                            'goalTime': 60,
                            'x': 0.8000,
                            'y': 0.5000,
                            'type': 3,
                            'result': 1
                        }
                    ]
                }
            ]
        }

        match1 = Match.objects.create(
            ouid=self.user,
            match_id='isolation-match-1',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=1,
            goals_against=0,
            possession=55,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('80.00'),
            raw_data=raw_data1
        )

        match2 = Match.objects.create(
            ouid=user2,
            match_id='isolation-match-2',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=0,
            possession=60,
            shots=12,
            shots_on_target=6,
            pass_success_rate=Decimal('85.00'),
            raw_data=raw_data2
        )

        # Each match should have correct number of shots
        match1_shots = ShotDetail.objects.filter(match=match1).count()
        match2_shots = ShotDetail.objects.filter(match=match2).count()

        self.assertEqual(match1_shots, 1)
        self.assertEqual(match2_shots, 2)
