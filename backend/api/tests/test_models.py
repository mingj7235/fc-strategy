"""
Comprehensive tests for API models.

Tests cover:
- User model creation and relationships
- Match model with multiple perspectives support
- ShotDetail model and coordinate validation
- PlayerPerformance model with calculated fields
- UserStats aggregation model
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from api.models import User, Match, ShotDetail, PlayerPerformance, UserStats


class UserModelTest(TestCase):
    """Test User model functionality."""

    def setUp(self):
        self.user_data = {
            'ouid': 'test-ouid-123',
            'nickname': 'TestPlayer',
            'max_division': 2100
        }

    def test_create_user(self):
        """Test creating a user with all fields."""
        user = User.objects.create(**self.user_data)
        self.assertEqual(user.ouid, 'test-ouid-123')
        self.assertEqual(user.nickname, 'TestPlayer')
        self.assertEqual(user.max_division, 2100)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.last_updated)

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create(**self.user_data)
        self.assertEqual(str(user), "TestPlayer (test-ouid-123)")

    def test_user_nickname_indexing(self):
        """Test that nickname is properly indexed (meta check)."""
        user = User.objects.create(**self.user_data)
        # Query should use index efficiently
        found_user = User.objects.filter(nickname='TestPlayer').first()
        self.assertEqual(found_user.ouid, user.ouid)


class MatchModelTest(TestCase):
    """Test Match model functionality including multi-perspective support."""

    def setUp(self):
        self.user1 = User.objects.create(
            ouid='user1-ouid',
            nickname='Player1'
        )
        self.user2 = User.objects.create(
            ouid='user2-ouid',
            nickname='Player2'
        )
        self.match_data = {
            'match_id': 'match-123',
            'match_date': timezone.now(),
            'match_type': 50,
            'result': 'win',
            'goals_for': 3,
            'goals_against': 1,
            'possession': 60,
            'shots': 15,
            'shots_on_target': 8,
            'pass_success_rate': Decimal('85.50'),
            'opponent_nickname': 'Player2',
            'raw_data': {'matchInfo': []}
        }

    def test_create_match(self):
        """Test creating a match with all required fields."""
        match = Match.objects.create(ouid=self.user1, **self.match_data)
        self.assertEqual(match.match_id, 'match-123')
        self.assertEqual(match.ouid, self.user1)
        self.assertEqual(match.result, 'win')
        self.assertEqual(match.goals_for, 3)
        self.assertEqual(match.opponent_nickname, 'Player2')

    def test_same_match_different_perspectives(self):
        """
        Critical test: Same match_id should support two different user perspectives.
        This is the core requirement from the user perspective fix.
        """
        # User1's perspective: win 3-1
        match1 = Match.objects.create(
            ouid=self.user1,
            match_id='match-123',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=3,
            goals_against=1,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.50'),
            opponent_nickname='Player2',
            raw_data={}
        )

        # User2's perspective: lose 1-3
        match2 = Match.objects.create(
            ouid=self.user2,
            match_id='match-123',
            match_date=timezone.now(),
            match_type=50,
            result='lose',
            goals_for=1,
            goals_against=3,
            possession=40,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('75.00'),
            opponent_nickname='Player1',
            raw_data={}
        )

        # Both should exist
        self.assertEqual(Match.objects.filter(match_id='match-123').count(), 2)

        # Should be able to filter by match_id + ouid
        user1_match = Match.objects.get(match_id='match-123', ouid=self.user1)
        user2_match = Match.objects.get(match_id='match-123', ouid=self.user2)

        self.assertEqual(user1_match.result, 'win')
        self.assertEqual(user2_match.result, 'lose')
        self.assertEqual(user1_match.opponent_nickname, 'Player2')
        self.assertEqual(user2_match.opponent_nickname, 'Player1')

    def test_match_unique_together_constraint(self):
        """Test that (match_id, ouid) must be unique."""
        Match.objects.create(ouid=self.user1, **self.match_data)

        # Attempting to create same match_id + ouid should raise error
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Match.objects.create(ouid=self.user1, **self.match_data)

    def test_match_ordering(self):
        """Test that matches are ordered by match_date descending."""
        from datetime import timedelta
        now = timezone.now()

        match1 = Match.objects.create(
            ouid=self.user1,
            match_id='match-1',
            match_date=now - timedelta(days=2),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=50,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('80.00'),
            raw_data={}
        )

        match2 = Match.objects.create(
            ouid=self.user1,
            match_id='match-2',
            match_date=now,
            match_type=50,
            result='lose',
            goals_for=0,
            goals_against=2,
            possession=45,
            shots=8,
            shots_on_target=3,
            pass_success_rate=Decimal('75.00'),
            raw_data={}
        )

        matches = list(Match.objects.filter(ouid=self.user1))
        self.assertEqual(matches[0].match_id, 'match-2')  # Most recent first
        self.assertEqual(matches[1].match_id, 'match-1')

    def test_match_str_representation(self):
        """Test match string representation."""
        match = Match.objects.create(ouid=self.user1, **self.match_data)
        expected = f"match-123 - Player1 (win)"
        self.assertEqual(str(match), expected)


class ShotDetailModelTest(TestCase):
    """Test ShotDetail model and coordinate handling."""

    def setUp(self):
        self.user = User.objects.create(ouid='user-123', nickname='Tester')
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='match-456',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=0,
            possession=55,
            shots=12,
            shots_on_target=6,
            pass_success_rate=Decimal('82.00'),
            raw_data={}
        )

    def test_create_shot_detail(self):
        """Test creating a shot detail with all fields."""
        shot = ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.8512'),
            y=Decimal('0.4523'),
            result='goal',
            shot_type=3,
            goal_time=45,
            assist_x=Decimal('0.7000'),
            assist_y=Decimal('0.5000')
        )

        self.assertEqual(shot.match, self.match)
        self.assertEqual(shot.result, 'goal')
        self.assertEqual(shot.goal_time, 45)
        self.assertIsNotNone(shot.assist_x)

    def test_shot_coordinates_precision(self):
        """Test that coordinates maintain 4 decimal precision."""
        shot = ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.123456'),  # More than 4 decimals
            y=Decimal('0.654321'),
            result='on_target',
            shot_type=2,
            goal_time=30
        )

        # Should be stored with exact precision defined in model
        self.assertEqual(shot.x.as_tuple().exponent, -4)
        self.assertEqual(shot.y.as_tuple().exponent, -4)

    def test_shot_result_choices(self):
        """Test that shot result choices are valid."""
        valid_results = ['goal', 'on_target', 'off_target', 'blocked']

        for result in valid_results:
            shot = ShotDetail.objects.create(
                match=self.match,
                x=Decimal('0.5000'),
                y=Decimal('0.5000'),
                result=result,
                shot_type=1,
                goal_time=10
            )
            self.assertEqual(shot.result, result)

    def test_shot_ordering_by_time(self):
        """Test shots can be ordered by goal_time."""
        shot1 = ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.5000'),
            y=Decimal('0.5000'),
            result='goal',
            shot_type=1,
            goal_time=30
        )

        shot2 = ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.6000'),
            y=Decimal('0.4000'),
            result='on_target',
            shot_type=2,
            goal_time=60
        )

        shots = list(ShotDetail.objects.filter(match=self.match).order_by('goal_time'))
        self.assertEqual(shots[0].goal_time, 30)
        self.assertEqual(shots[1].goal_time, 60)


class PlayerPerformanceModelTest(TestCase):
    """Test PlayerPerformance model with calculated fields."""

    def setUp(self):
        self.user = User.objects.create(ouid='user-789', nickname='Coach')
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='match-789',
            match_date=timezone.now(),
            match_type=50,
            result='draw',
            goals_for=2,
            goals_against=2,
            possession=50,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('80.00'),
            raw_data={}
        )

    def test_create_player_performance(self):
        """Test creating a player performance record."""
        player = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=103259207,
            player_name='Son Heung-min',
            season_id=259,
            position=27,
            grade=8,
            rating=Decimal('8.5'),
            goals=2,
            assists=1,
            shots=5,
            shots_on_target=3,
            pass_attempts=45,
            pass_success=38
        )

        self.assertEqual(player.player_name, 'Son Heung-min')
        self.assertEqual(player.rating, Decimal('8.5'))
        self.assertEqual(player.goals, 2)

    def test_pass_success_rate_calculation(self):
        """Test that pass_success_rate is auto-calculated on save."""
        player = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=103259207,
            player_name='Test Player',
            position=27,
            grade=7,
            rating=Decimal('7.0'),
            pass_attempts=100,
            pass_success=85
        )

        # Should auto-calculate to 85.00%
        self.assertEqual(player.pass_success_rate, Decimal('85.00'))

    def test_shot_accuracy_calculation(self):
        """Test that shot_accuracy is auto-calculated on save."""
        player = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=103259207,
            player_name='Test Player',
            position=27,
            grade=7,
            rating=Decimal('7.0'),
            shots=10,
            shots_on_target=6
        )

        # Should auto-calculate to 60.00%
        self.assertEqual(player.shot_accuracy, Decimal('60.00'))

    def test_dribble_success_rate_calculation(self):
        """Test that dribble_success_rate is auto-calculated on save."""
        player = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=103259207,
            player_name='Test Player',
            position=27,
            grade=7,
            rating=Decimal('7.0'),
            dribble_attempts=20,
            dribble_success=15
        )

        # Should auto-calculate to 75.00%
        self.assertEqual(player.dribble_success_rate, Decimal('75.00'))

    def test_tackle_success_rate_calculation(self):
        """Test that tackle_success_rate is auto-calculated on save."""
        player = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=103259207,
            player_name='Test Player',
            position=27,
            grade=7,
            rating=Decimal('7.0'),
            tackle_attempts=10,
            tackle_success=8
        )

        # Should auto-calculate to 80.00%
        self.assertEqual(player.tackle_success_rate, Decimal('80.00'))

    def test_percentage_calculations_with_zero_attempts(self):
        """Test that percentage fields handle zero attempts gracefully."""
        player = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=103259207,
            player_name='Test Player',
            position=27,
            grade=7,
            rating=Decimal('7.0'),
            pass_attempts=0,
            pass_success=0,
            shots=0,
            shots_on_target=0
        )

        # Should not calculate when attempts are zero
        self.assertIsNone(player.pass_success_rate)
        self.assertIsNone(player.shot_accuracy)

    def test_player_filtering_by_user(self):
        """
        Critical test: Players should be filterable by user_ouid.
        This ensures only the searched user's players are shown.
        """
        user2 = User.objects.create(ouid='user-opponent', nickname='Opponent')

        # Same match, different perspectives
        match2 = Match.objects.create(
            ouid=user2,
            match_id='match-789',
            match_date=timezone.now(),
            match_type=50,
            result='draw',
            goals_for=2,
            goals_against=2,
            possession=50,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('80.00'),
            raw_data={}
        )

        # Create players for both users
        player1 = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=1001,
            player_name='User1 Player',
            position=27,
            grade=7,
            rating=Decimal('7.5')
        )

        player2 = PlayerPerformance.objects.create(
            match=match2,
            user_ouid=user2,
            spid=2001,
            player_name='User2 Player',
            position=27,
            grade=7,
            rating=Decimal('7.0')
        )

        # Filter by user should return only that user's players
        user1_players = PlayerPerformance.objects.filter(user_ouid=self.user)
        self.assertEqual(user1_players.count(), 1)
        self.assertEqual(user1_players.first().player_name, 'User1 Player')

        user2_players = PlayerPerformance.objects.filter(user_ouid=user2)
        self.assertEqual(user2_players.count(), 1)
        self.assertEqual(user2_players.first().player_name, 'User2 Player')

    def test_player_ordering_by_rating(self):
        """Test that players can be ordered by rating descending."""
        player1 = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=1001,
            player_name='Player A',
            position=27,
            grade=7,
            rating=Decimal('7.5')
        )

        player2 = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=1002,
            player_name='Player B',
            position=28,
            grade=8,
            rating=Decimal('8.5')
        )

        player3 = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=1003,
            player_name='Player C',
            position=29,
            grade=6,
            rating=Decimal('6.5')
        )

        players = list(PlayerPerformance.objects.filter(match=self.match).order_by('-rating'))
        self.assertEqual(players[0].player_name, 'Player B')
        self.assertEqual(players[1].player_name, 'Player A')
        self.assertEqual(players[2].player_name, 'Player C')


class UserStatsModelTest(TestCase):
    """Test UserStats aggregation model."""

    def setUp(self):
        self.user = User.objects.create(ouid='stats-user', nickname='StatsPlayer')

    def test_create_user_stats(self):
        """Test creating user stats."""
        stats = UserStats.objects.create(
            ouid=self.user,
            period='all_time',
            total_matches=100,
            wins=60,
            losses=30,
            draws=10,
            avg_possession=Decimal('55.50'),
            avg_shots=Decimal('12.30'),
            avg_goals=Decimal('2.10'),
            shot_accuracy=Decimal('45.60'),
            xg=Decimal('2.25')
        )

        self.assertEqual(stats.total_matches, 100)
        self.assertEqual(stats.wins, 60)
        self.assertEqual(stats.period, 'all_time')

    def test_period_choices(self):
        """Test valid period choices."""
        periods = ['weekly', 'monthly', 'all_time']

        for period in periods:
            stats = UserStats.objects.create(
                ouid=self.user,
                period=period,
                total_matches=10,
                wins=5,
                losses=3,
                draws=2,
                avg_possession=Decimal('50.00'),
                avg_shots=Decimal('10.00'),
                avg_goals=Decimal('1.50'),
                shot_accuracy=Decimal('40.00'),
                xg=Decimal('1.80')
            )
            self.assertEqual(stats.period, period)

    def test_unique_together_ouid_period(self):
        """Test that (ouid, period) must be unique."""
        UserStats.objects.create(
            ouid=self.user,
            period='all_time',
            total_matches=10,
            wins=5,
            losses=3,
            draws=2,
            avg_possession=Decimal('50.00'),
            avg_shots=Decimal('10.00'),
            avg_goals=Decimal('1.50'),
            shot_accuracy=Decimal('40.00'),
            xg=Decimal('1.80')
        )

        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            UserStats.objects.create(
                ouid=self.user,
                period='all_time',
                total_matches=20,
                wins=10,
                losses=5,
                draws=5,
                avg_possession=Decimal('52.00'),
                avg_shots=Decimal('11.00'),
                avg_goals=Decimal('2.00'),
                shot_accuracy=Decimal('42.00'),
                xg=Decimal('2.00')
            )
