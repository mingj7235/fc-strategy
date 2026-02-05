"""
Comprehensive tests for API serializers.

Tests cover:
- UserSerializer
- MatchListSerializer with shots fields
- MatchDetailSerializer
- PlayerPerformanceSerializer with image URLs
- ShotDetailSerializer
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from api.models import User, Match, ShotDetail, PlayerPerformance
from api.serializers import (
    UserSerializer,
    MatchListSerializer,
    MatchDetailSerializer,
    PlayerPerformanceSerializer,
    ShotDetailSerializer
)


class UserSerializerTest(TestCase):
    """Test UserSerializer."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='serializer-test-user',
            nickname='SerializerPlayer',
            max_division=2200
        )

    def test_user_serialization(self):
        """Test serializing a user."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(data['ouid'], 'serializer-test-user')
        self.assertEqual(data['nickname'], 'SerializerPlayer')
        self.assertEqual(data['max_division'], 2200)

    def test_user_deserialization(self):
        """Test deserializing user data."""
        data = {
            'ouid': 'new-user',
            'nickname': 'NewPlayer',
            'max_division': 1800
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.nickname, 'NewPlayer')


class MatchListSerializerTest(TestCase):
    """Test MatchListSerializer including shots fields."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='match-serializer-user',
            nickname='MatchPlayer'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='match-serializer-123',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=3,
            goals_against=1,
            possession=60,
            shots=15,
            shots_on_target=8,
            pass_success_rate=Decimal('85.50'),
            opponent_nickname='OpponentPlayer',
            raw_data={}
        )

    def test_match_list_serialization(self):
        """Test serializing match for list view."""
        serializer = MatchListSerializer(self.match)
        data = serializer.data

        self.assertEqual(data['match_id'], 'match-serializer-123')
        self.assertEqual(data['result'], 'win')
        self.assertEqual(data['goals_for'], 3)
        self.assertEqual(data['goals_against'], 1)

        # Critical: shots and shots_on_target must be included (bug fix)
        self.assertEqual(data['shots'], 15)
        self.assertEqual(data['shots_on_target'], 8)

        # Opponent nickname must be included (bug fix)
        self.assertEqual(data['opponent_nickname'], 'OpponentPlayer')

    def test_shots_fields_not_missing(self):
        """
        Critical test: Verify shots and shots_on_target are in serializer fields.
        This prevents the 0/0 bug from recurring.
        """
        serializer = MatchListSerializer(self.match)

        # These fields must be present
        self.assertIn('shots', serializer.data)
        self.assertIn('shots_on_target', serializer.data)

        # Values should not be None or missing
        self.assertIsNotNone(serializer.data['shots'])
        self.assertIsNotNone(serializer.data['shots_on_target'])

    def test_opponent_nickname_field(self):
        """Test that opponent_nickname is serialized."""
        serializer = MatchListSerializer(self.match)

        self.assertIn('opponent_nickname', serializer.data)
        self.assertEqual(serializer.data['opponent_nickname'], 'OpponentPlayer')


class MatchDetailSerializerTest(TestCase):
    """Test MatchDetailSerializer."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='detail-user',
            nickname='DetailPlayer'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='detail-match',
            match_date=timezone.now(),
            match_type=50,
            result='draw',
            goals_for=2,
            goals_against=2,
            possession=50,
            shots=12,
            shots_on_target=6,
            pass_success_rate=Decimal('80.00'),
            opponent_nickname='DrawOpponent',
            raw_data={'matchInfo': [{'test': 'data'}]}
        )

    def test_match_detail_serialization(self):
        """Test serializing match detail."""
        serializer = MatchDetailSerializer(self.match)
        data = serializer.data

        self.assertEqual(data['match_id'], 'detail-match')
        self.assertEqual(data['result'], 'draw')
        self.assertIn('raw_data', data)
        self.assertEqual(data['opponent_nickname'], 'DrawOpponent')


class PlayerPerformanceSerializerTest(TestCase):
    """Test PlayerPerformanceSerializer with image URL generation."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='player-perf-user',
            nickname='PerfPlayer'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='perf-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=55,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('82.00'),
            raw_data={}
        )
        self.player = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=103259207,
            player_name='Son Heung-min',
            season_id=259,
            season_name='23TOTY',
            position=27,
            grade=8,
            rating=Decimal('8.5'),
            goals=2,
            assists=1,
            shots=5,
            shots_on_target=4,
            pass_attempts=45,
            pass_success=38,
            dribble_attempts=10,
            dribble_success=7,
            tackle_attempts=5,
            tackle_success=3
        )

    def test_player_performance_serialization(self):
        """Test serializing player performance."""
        serializer = PlayerPerformanceSerializer(self.player)
        data = serializer.data

        self.assertEqual(data['spid'], 103259207)
        self.assertEqual(data['player_name'], 'Son Heung-min')
        self.assertEqual(float(data['rating']), 8.5)
        self.assertEqual(data['goals'], 2)
        self.assertEqual(data['assists'], 1)

    def test_image_url_generation(self):
        """Test that image_url is generated correctly."""
        serializer = PlayerPerformanceSerializer(self.player)
        data = serializer.data

        self.assertIn('image_url', data)
        expected_url = f"https://photo.api.nexon.com/fifaonline4/{self.player.spid}.png"
        self.assertEqual(data['image_url'], expected_url)

    def test_calculated_percentages_serialization(self):
        """Test that calculated percentage fields are serialized."""
        serializer = PlayerPerformanceSerializer(self.player)
        data = serializer.data

        # These should be calculated on save
        self.assertIsNotNone(data.get('pass_success_rate'))
        self.assertIsNotNone(data.get('shot_accuracy'))
        self.assertIsNotNone(data.get('dribble_success_rate'))
        self.assertIsNotNone(data.get('tackle_success_rate'))

    def test_multiple_players_serialization(self):
        """Test serializing multiple players."""
        player2 = PlayerPerformance.objects.create(
            match=self.match,
            user_ouid=self.user,
            spid=103259208,
            player_name='Kane',
            position=27,
            grade=8,
            rating=Decimal('7.8'),
            goals=1,
            assists=0
        )

        players = [self.player, player2]
        serializer = PlayerPerformanceSerializer(players, many=True)
        data = serializer.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['player_name'], 'Son Heung-min')
        self.assertEqual(data[1]['player_name'], 'Kane')


class ShotDetailSerializerTest(TestCase):
    """Test ShotDetailSerializer."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='shot-user',
            nickname='ShotPlayer'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='shot-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=0,
            possession=60,
            shots=10,
            shots_on_target=5,
            pass_success_rate=Decimal('85.00'),
            raw_data={}
        )
        self.shot = ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.8512'),
            y=Decimal('0.4523'),
            result='goal',
            shot_type=3,
            goal_time=45,
            assist_x=Decimal('0.7000'),
            assist_y=Decimal('0.5000')
        )

    def test_shot_detail_serialization(self):
        """Test serializing shot detail."""
        serializer = ShotDetailSerializer(self.shot)
        data = serializer.data

        self.assertEqual(float(data['x']), 0.8512)
        self.assertEqual(float(data['y']), 0.4523)
        self.assertEqual(data['result'], 'goal')
        self.assertEqual(data['shot_type'], 3)
        self.assertEqual(data['goal_time'], 45)

    def test_shot_with_assist_coordinates(self):
        """Test shot with assist coordinates."""
        serializer = ShotDetailSerializer(self.shot)
        data = serializer.data

        self.assertIsNotNone(data['assist_x'])
        self.assertIsNotNone(data['assist_y'])
        self.assertEqual(float(data['assist_x']), 0.7000)

    def test_shot_without_assist_coordinates(self):
        """Test shot without assist coordinates."""
        shot_no_assist = ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.6000'),
            y=Decimal('0.5000'),
            result='on_target',
            shot_type=2,
            goal_time=30
        )

        serializer = ShotDetailSerializer(shot_no_assist)
        data = serializer.data

        self.assertIsNone(data['assist_x'])
        self.assertIsNone(data['assist_y'])

    def test_multiple_shots_serialization(self):
        """Test serializing multiple shots."""
        shot2 = ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.7000'),
            y=Decimal('0.6000'),
            result='off_target',
            shot_type=1,
            goal_time=60
        )

        shots = [self.shot, shot2]
        serializer = ShotDetailSerializer(shots, many=True)
        data = serializer.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['result'], 'goal')
        self.assertEqual(data[1]['result'], 'off_target')
