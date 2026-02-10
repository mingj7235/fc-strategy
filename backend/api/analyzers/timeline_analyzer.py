"""
Timeline Analyzer
Analyzes shots and goals over time to provide timeline insights and xG trends
"""
from typing import List, Dict, Any
from decimal import Decimal
from api.analyzers.shot_analyzer import ShotAnalyzer


class TimelineAnalyzer:
    """Analyze match timeline and key moments"""

    @classmethod
    def analyze_timeline(cls, shot_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze match timeline from shot details

        Args:
            shot_details: List of shot detail dictionaries with goal_time

        Returns:
            Dictionary containing timeline analysis with:
            - xg_by_period: xG for first/second half
            - key_moments: List of important moments (goals, big chances)
            - timeline_data: Time-series data for visualization
        """
        if not shot_details:
            return {
                'xg_by_period': {
                    'first_half': 0.0,
                    'second_half': 0.0
                },
                'key_moments': [],
                'timeline_data': []
            }

        # Filter out shots with abnormal goal_time (>7200 seconds = 120 minutes)
        # Some Nexon API data has corrupted goalTime values
        valid_shots = [s for s in shot_details if s.get('goal_time', 0) <= 7200]

        if not valid_shots:
            return {
                'xg_by_period': {
                    'first_half': 0.0,
                    'second_half': 0.0
                },
                'key_moments': [],
                'timeline_data': []
            }

        # Sort shots by time
        sorted_shots = sorted(valid_shots, key=lambda s: s.get('goal_time', 0))

        # Calculate xG by period
        xg_by_period = cls._calculate_xg_by_period(sorted_shots)

        # Identify key moments
        key_moments = cls._identify_key_moments(sorted_shots)

        # Generate timeline data for charts
        timeline_data = cls._generate_timeline_data(sorted_shots)

        return {
            'xg_by_period': xg_by_period,
            'key_moments': key_moments,
            'timeline_data': timeline_data
        }

    @classmethod
    def _calculate_xg_by_period(cls, shot_details: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate xG for first half and second half"""
        first_half_xg = 0.0
        second_half_xg = 0.0

        for shot in shot_details:
            goal_time = shot.get('goal_time', 0)

            xg_value = ShotAnalyzer._calculate_advanced_xg(shot)

            # goal_time values in tests are in minutes (e.g. 30, 60).
            # Compare directly against the 45-minute half-time boundary.
            if goal_time < 45:
                first_half_xg += xg_value
            else:
                second_half_xg += xg_value

        return {
            'first_half': round(first_half_xg, 2),
            'second_half': round(second_half_xg, 2)
        }

    @classmethod
    def _identify_key_moments(cls, shot_details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify key moments (goals and big chances)

        A moment is considered "key" if:
        - It's a goal (result == 'goal')
        - It's a big chance (xG > 0.3)
        """
        moments = []

        for shot in shot_details:
            goal_time = shot.get('goal_time', 0)
            minute = goal_time // 60
            result = shot.get('result')
            xg = ShotAnalyzer._calculate_advanced_xg(shot)

            # Include goals or big chances
            if result == 'goal' or xg > 0.3:
                moment_type = 'goal' if result == 'goal' else 'big_chance'

                moments.append({
                    'minute': minute,
                    'type': moment_type,
                    'xg': round(xg, 2),
                    'x': float(shot.get('x', 0)),
                    'y': float(shot.get('y', 0)),
                    'result': result
                })

        return moments

    @classmethod
    def _generate_timeline_data(cls, shot_details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate cumulative xG timeline data for visualization

        Returns list of data points with:
        - minute: Match minute
        - cumulative_xg: Cumulative xG up to that minute
        - goals: Number of goals scored up to that minute
        """
        if not shot_details:
            return []

        timeline = []
        cumulative_xg = 0.0
        cumulative_goals = 0

        # Group shots by minute
        shots_by_minute = {}
        for shot in shot_details:
            goal_time = shot.get('goal_time', 0)
            minute = goal_time // 60

            if minute not in shots_by_minute:
                shots_by_minute[minute] = []
            shots_by_minute[minute].append(shot)

        # Generate cumulative data
        max_minute = max(shots_by_minute.keys()) if shots_by_minute else 90

        for minute in range(0, min(max_minute + 1, 121)):  # Up to 120 minutes for extra time
            if minute in shots_by_minute:
                for shot in shots_by_minute[minute]:
                    cumulative_xg += ShotAnalyzer._calculate_advanced_xg(shot)
                    if shot.get('result') == 'goal':
                        cumulative_goals += 1

            timeline.append({
                'minute': minute,
                'cumulative_xg': round(cumulative_xg, 2),
                'goals': cumulative_goals
            })

        return timeline

    @classmethod
    def generate_insights(cls, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate Korean-language insights from timeline analysis

        Args:
            analysis: Timeline analysis dictionary

        Returns:
            List of insight strings in Korean
        """
        insights = []

        xg_by_period = analysis.get('xg_by_period', {})
        first_half_xg = xg_by_period.get('first_half', 0)
        second_half_xg = xg_by_period.get('second_half', 0)
        key_moments = analysis.get('key_moments', [])

        # Period dominance analysis
        if first_half_xg > second_half_xg * 1.5:
            insights.append("전반전에 강력한 공격력을 보였습니다. 후반전 체력 관리를 고려하세요.")
        elif second_half_xg > first_half_xg * 1.5:
            insights.append("후반전에 더 많은 찬스를 만들었습니다. 초반부터 적극적인 공격을 시도해보세요.")
        elif abs(first_half_xg - second_half_xg) < 0.3 and first_half_xg > 0:
            insights.append("경기 내내 일관된 공격력을 유지했습니다.")

        # Big chances analysis
        big_chances = [m for m in key_moments if m['type'] == 'big_chance']
        goals = [m for m in key_moments if m['type'] == 'goal']

        if len(big_chances) > 3:
            insights.append(f"{len(big_chances)}개의 빅 찬스를 만들었습니다. 슈팅 마무리 연습이 필요합니다.")

        # Conversion rate
        if len(big_chances) > 0:
            goals_from_big_chances = len([m for m in key_moments if m['type'] == 'goal' and m['xg'] > 0.3])
            if goals_from_big_chances == 0:
                insights.append("빅 찬스를 골로 연결하지 못했습니다. 침착한 마무리가 필요합니다.")

        # Early/late goals
        if goals:
            early_goals = [g for g in goals if g['minute'] < 15]
            late_goals = [g for g in goals if g['minute'] > 75]

            if len(early_goals) >= 2:
                insights.append("초반 집중력이 우수합니다. 선제골로 경기를 유리하게 가져갔습니다.")
            if len(late_goals) >= 2:
                insights.append("후반 막판 골로 경기를 뒤집었습니다. 끝까지 집중력을 유지했습니다.")

        return insights
