"""
Comprehensive tests for analyzer modules.

Tests cover:
- ShotAnalyzer (xG calculation, zone analysis)
- StyleAnalyzer (possession, attack patterns)
- TimelineAnalyzer (key moments, xG by period)
- TacticalInsightsAnalyzer (insights generation)
- StatisticsAnalyzer
"""
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from api.models import User, Match, ShotDetail, PlayerPerformance
from api.analyzers.shot_analyzer import ShotAnalyzer
from api.analyzers.style_analyzer import StyleAnalyzer
from api.analyzers.timeline_analyzer import TimelineAnalyzer
from api.analyzers.tactical_analyzer import TacticalInsightsAnalyzer
from api.analyzers.statistics import StatisticsAnalyzer


class ShotAnalyzerTest(TestCase):
    """Test ShotAnalyzer functionality."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='shot-analyzer-user',
            nickname='ShotTester'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='shot-test-match',
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

    def test_xg_calculation_for_goal(self):
        """Test xG calculation for a goal."""
        shot_data = {
            'x': 0.85,
            'y': 0.50,
            'result': 'goal',
            'shot_type': 3
        }

        xg = ShotAnalyzer._calculate_shot_xg(shot_data)

        # Goal from penalty box should have reasonable xG
        self.assertGreater(xg, 0.0)
        self.assertLessEqual(xg, 1.0)

    def test_xg_calculation_by_distance(self):
        """Test that xG decreases with distance."""
        # Close shot
        close_shot = {
            'x': 0.95,
            'y': 0.50,
            'result': 'on_target',
            'shot_type': 2
        }

        # Far shot
        far_shot = {
            'x': 0.60,
            'y': 0.50,
            'result': 'on_target',
            'shot_type': 2
        }

        close_xg = ShotAnalyzer._calculate_shot_xg(close_shot)
        far_xg = ShotAnalyzer._calculate_shot_xg(far_shot)

        # Closer shot should have higher xG
        self.assertGreater(close_xg, far_xg)

    def test_xg_calculation_by_angle(self):
        """Test that xG decreases with poor angle."""
        # Central shot
        central_shot = {
            'x': 0.85,
            'y': 0.50,
            'result': 'on_target',
            'shot_type': 2
        }

        # Wide angle shot
        wide_shot = {
            'x': 0.85,
            'y': 0.10,
            'result': 'on_target',
            'shot_type': 2
        }

        central_xg = ShotAnalyzer._calculate_shot_xg(central_shot)
        wide_xg = ShotAnalyzer._calculate_shot_xg(wide_shot)

        # Central shot should have higher xG
        self.assertGreater(central_xg, wide_xg)

    def test_shot_zone_classification(self):
        """Test shot zone classification."""
        # Penalty box shot
        penalty_shot = {
            'x': 0.85,
            'y': 0.50,
            'result': 'goal',
            'shot_type': 3
        }

        # Outside box shot
        outside_shot = {
            'x': 0.65,
            'y': 0.50,
            'result': 'on_target',
            'shot_type': 2
        }

        zone1 = ShotAnalyzer._get_shot_zone(penalty_shot)
        zone2 = ShotAnalyzer._get_shot_zone(outside_shot)

        # Zones should be different
        self.assertNotEqual(zone1, zone2)

    def test_analyze_shots_with_multiple_shots(self):
        """Test analyzing multiple shots."""
        # Create multiple shot details
        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.8500'),
            y=Decimal('0.5000'),
            result='goal',
            shot_type=3,
            goal_time=30
        )

        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.7000'),
            y=Decimal('0.4000'),
            result='on_target',
            shot_type=2,
            goal_time=45
        )

        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.9000'),
            y=Decimal('0.5000'),
            result='goal',
            shot_type=3,
            goal_time=60
        )

        matches = Match.objects.filter(ouid=self.user)
        analysis = ShotAnalyzer.analyze_shots(matches)

        self.assertIn('total_shots', analysis)
        self.assertIn('total_xg', analysis)
        self.assertIn('shot_zones', analysis)

        # Should have calculated total xG
        self.assertGreater(analysis['total_xg'], 0.0)


class StyleAnalyzerTest(TestCase):
    """Test StyleAnalyzer functionality."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='style-user',
            nickname='StyleTester'
        )

    def test_possession_style_classification(self):
        """Test possession style classification."""
        # High possession match
        high_poss_match = Match.objects.create(
            ouid=self.user,
            match_id='high-poss',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=65,
            shots=12,
            shots_on_target=6,
            pass_success_rate=Decimal('88.00'),
            raw_data={}
        )

        # Low possession match
        low_poss_match = Match.objects.create(
            ouid=self.user,
            match_id='low-poss',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=35,
            shots=8,
            shots_on_target=5,
            pass_success_rate=Decimal('70.00'),
            raw_data={}
        )

        matches = Match.objects.filter(ouid=self.user)
        analysis = StyleAnalyzer.analyze_style(matches)

        self.assertIn('possession_style', analysis)
        self.assertIn('attack_style', analysis)
        self.assertIn('avg_possession', analysis)

    def test_attack_pattern_detection(self):
        """Test attack pattern detection from shot locations."""
        match = Match.objects.create(
            ouid=self.user,
            match_id='attack-pattern',
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

        # Create wing shots
        for i in range(5):
            ShotDetail.objects.create(
                match=match,
                x=Decimal('0.8000'),
                y=Decimal('0.1000'),  # Wing area
                result='on_target',
                shot_type=2,
                goal_time=30 + i
            )

        # Create central shots
        for i in range(2):
            ShotDetail.objects.create(
                match=match,
                x=Decimal('0.8500'),
                y=Decimal('0.5000'),  # Central area
                result='goal',
                shot_type=3,
                goal_time=60 + i
            )

        matches = Match.objects.filter(match_id='attack-pattern')
        analysis = StyleAnalyzer.analyze_style(matches)

        # Should detect wing play tendency
        self.assertIn('attack_style', analysis)


class TimelineAnalyzerTest(TestCase):
    """Test TimelineAnalyzer functionality."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='timeline-user',
            nickname='TimelineTester'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='timeline-match',
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

    def test_xg_by_period_calculation(self):
        """Test xG calculation by period (first half vs second half)."""
        # First half shots
        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.8500'),
            y=Decimal('0.5000'),
            result='goal',
            shot_type=3,
            goal_time=30
        )

        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.8000'),
            y=Decimal('0.4000'),
            result='on_target',
            shot_type=2,
            goal_time=40
        )

        # Second half shots
        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.9000'),
            y=Decimal('0.5000'),
            result='goal',
            shot_type=3,
            goal_time=60
        )

        shot_details = list(ShotDetail.objects.filter(match=self.match).values())
        timeline = TimelineAnalyzer.analyze_timeline(shot_details)

        self.assertIn('xg_by_period', timeline)
        self.assertIn('first_half', timeline['xg_by_period'])
        self.assertIn('second_half', timeline['xg_by_period'])

        # Both periods should have xG > 0
        self.assertGreater(timeline['xg_by_period']['first_half'], 0.0)
        self.assertGreater(timeline['xg_by_period']['second_half'], 0.0)

    def test_key_moments_identification(self):
        """Test identification of key moments (goals and big chances)."""
        # Goal
        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.9500'),
            y=Decimal('0.5000'),
            result='goal',
            shot_type=3,
            goal_time=25
        )

        # Big chance (high xG)
        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.9000'),
            y=Decimal('0.5000'),
            result='on_target',
            shot_type=2,
            goal_time=55
        )

        # Low quality chance
        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.6000'),
            y=Decimal('0.2000'),
            result='off_target',
            shot_type=1,
            goal_time=70
        )

        shot_details = list(ShotDetail.objects.filter(match=self.match).values())
        timeline = TimelineAnalyzer.analyze_timeline(shot_details)

        self.assertIn('key_moments', timeline)

        # Should identify at least the goal
        key_moments = timeline['key_moments']
        self.assertGreater(len(key_moments), 0)

        # Check that goals are identified
        goal_moments = [m for m in key_moments if m['type'] == 'goal']
        self.assertGreater(len(goal_moments), 0)

    def test_timeline_data_generation(self):
        """Test timeline data point generation."""
        # Create shots at different times
        for i in range(0, 90, 15):
            ShotDetail.objects.create(
                match=self.match,
                x=Decimal('0.8000'),
                y=Decimal('0.5000'),
                result='on_target',
                shot_type=2,
                goal_time=i
            )

        shot_details = list(ShotDetail.objects.filter(match=self.match).values())
        timeline = TimelineAnalyzer.analyze_timeline(shot_details)

        self.assertIn('timeline_data', timeline)

        # Should have timeline data points
        timeline_data = timeline['timeline_data']
        self.assertIsInstance(timeline_data, list)


class TacticalInsightsAnalyzerTest(TestCase):
    """Test TacticalInsightsAnalyzer functionality."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='tactical-user',
            nickname='TacticalTester'
        )
        self.match = Match.objects.create(
            ouid=self.user,
            match_id='tactical-match',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=3,
            goals_against=1,
            possession=65,
            shots=18,
            shots_on_target=12,
            pass_success_rate=Decimal('88.00'),
            raw_data={}
        )

    def test_attack_pattern_detection(self):
        """Test attack pattern detection (wing vs central)."""
        # Create wing shots
        for i in range(8):
            ShotDetail.objects.create(
                match=self.match,
                x=Decimal('0.8000'),
                y=Decimal('0.1000') if i % 2 == 0 else Decimal('0.9000'),
                result='on_target',
                shot_type=2,
                goal_time=30 + i * 5
            )

        shot_details = list(ShotDetail.objects.filter(match=self.match).values())
        timeline = TimelineAnalyzer.analyze_timeline(shot_details)

        insights = TacticalInsightsAnalyzer.analyze_tactical_approach(
            self.match,
            shot_details,
            timeline
        )

        self.assertIn('attack_pattern', insights)
        self.assertIn('insights', insights)

        # Attack pattern should be detected
        self.assertIn(insights['attack_pattern'], ['wing_play', 'central_penetration', 'balanced'])

    def test_possession_style_analysis(self):
        """Test possession style analysis."""
        shot_details = list(ShotDetail.objects.filter(match=self.match).values())
        timeline = TimelineAnalyzer.analyze_timeline(shot_details)

        insights = TacticalInsightsAnalyzer.analyze_tactical_approach(
            self.match,
            shot_details,
            timeline
        )

        self.assertIn('possession_style', insights)

    def test_insights_generation_korean(self):
        """Test that insights are generated in Korean."""
        # Create some shot details
        ShotDetail.objects.create(
            match=self.match,
            x=Decimal('0.8500'),
            y=Decimal('0.5000'),
            result='goal',
            shot_type=3,
            goal_time=30
        )

        shot_details = list(ShotDetail.objects.filter(match=self.match).values())
        timeline = TimelineAnalyzer.analyze_timeline(shot_details)

        insights = TacticalInsightsAnalyzer.analyze_tactical_approach(
            self.match,
            shot_details,
            timeline
        )

        self.assertIn('insights', insights)
        insights_list = insights['insights']

        # Should have some insights
        self.assertGreater(len(insights_list), 0)

        # Insights should be in Korean (check for Korean characters)
        for insight in insights_list:
            self.assertIsInstance(insight, str)
            # Korean text should contain Hangul characters
            has_korean = any('\uac00' <= c <= '\ud7a3' for c in insight)
            self.assertTrue(has_korean, f"Insight should be in Korean: {insight}")

    def test_high_possession_insights(self):
        """Test insights for high possession matches."""
        high_poss_match = Match.objects.create(
            ouid=self.user,
            match_id='high-poss-tactical',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=1,
            goals_against=0,
            possession=70,
            shots=20,
            shots_on_target=8,
            pass_success_rate=Decimal('90.00'),
            raw_data={}
        )

        shot_details = []
        timeline = {'xg_by_period': {'first_half': 1.5, 'second_half': 1.2}}

        insights = TacticalInsightsAnalyzer.analyze_tactical_approach(
            high_poss_match,
            shot_details,
            timeline
        )

        # Should mention possession dominance
        insights_text = ' '.join(insights['insights'])
        self.assertIn('점유', insights_text)

    def test_shot_accuracy_insights(self):
        """Test insights based on shot accuracy."""
        # High accuracy match
        high_acc_match = Match.objects.create(
            ouid=self.user,
            match_id='high-acc',
            match_date=timezone.now(),
            match_type=50,
            result='win',
            goals_for=2,
            goals_against=1,
            possession=55,
            shots=10,
            shots_on_target=8,  # 80% accuracy
            pass_success_rate=Decimal('82.00'),
            raw_data={}
        )

        shot_details = []
        timeline = {'xg_by_period': {'first_half': 1.0, 'second_half': 1.0}}

        insights = TacticalInsightsAnalyzer.analyze_tactical_approach(
            high_acc_match,
            shot_details,
            timeline
        )

        # Should mention good shot accuracy
        insights_text = ' '.join(insights['insights'])
        self.assertIn('슈팅', insights_text)


class StatisticsAnalyzerTest(TestCase):
    """Test StatisticsAnalyzer functionality."""

    def setUp(self):
        self.user = User.objects.create(
            ouid='stats-analyzer-user',
            nickname='StatsTester'
        )

        # Create multiple matches
        for i in range(10):
            Match.objects.create(
                ouid=self.user,
                match_id=f'stats-match-{i}',
                match_date=timezone.now(),
                match_type=50,
                result='win' if i % 2 == 0 else 'lose',
                goals_for=2 if i % 2 == 0 else 1,
                goals_against=1 if i % 2 == 0 else 2,
                possession=55 + i,
                shots=10 + i,
                shots_on_target=5 + i // 2,
                pass_success_rate=Decimal('80.00') + i,
                raw_data={}
            )

    def test_overall_statistics_calculation(self):
        """Test calculation of overall statistics."""
        matches = Match.objects.filter(ouid=self.user)
        stats = StatisticsAnalyzer.calculate_statistics(matches)

        self.assertIn('total_matches', stats)
        self.assertIn('wins', stats)
        self.assertIn('losses', stats)
        self.assertIn('draws', stats)
        self.assertIn('win_rate', stats)

        # Should have correct counts
        self.assertEqual(stats['total_matches'], 10)
        self.assertEqual(stats['wins'], 5)
        self.assertEqual(stats['losses'], 5)

        # Win rate should be 50%
        self.assertEqual(stats['win_rate'], 50.0)

    def test_average_calculations(self):
        """Test average statistics calculations."""
        matches = Match.objects.filter(ouid=self.user)
        stats = StatisticsAnalyzer.calculate_statistics(matches)

        self.assertIn('avg_possession', stats)
        self.assertIn('avg_shots', stats)
        self.assertIn('avg_goals', stats)

        # Averages should be reasonable
        self.assertGreater(stats['avg_possession'], 0)
        self.assertGreater(stats['avg_shots'], 0)

    def test_form_calculation(self):
        """Test recent form calculation."""
        matches = Match.objects.filter(ouid=self.user).order_by('-match_date')
        form = StatisticsAnalyzer.calculate_recent_form(matches, limit=5)

        self.assertIsInstance(form, list)
        self.assertLessEqual(len(form), 5)

        # Form should contain W, L, or D
        for result in form:
            self.assertIn(result, ['W', 'L', 'D'])
