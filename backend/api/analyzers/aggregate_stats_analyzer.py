"""
Aggregate Stats Analyzer
대량 매치 데이터 기반 통합 통계 분석
"""
from typing import Dict, Any, List
from collections import defaultdict, Counter


class AggregateStatsAnalyzer:
    """
    전체 경기 통합 통계 분석기
    - 어시스트 네트워크 집계
    - 헤딩 전문가 통계
    - 슈팅 효율성 트렌드
    - 패스 타입 평균 분포
    - 시간대별 골 패턴
    """

    # Shot types
    HEADING_TYPE = 3

    @classmethod
    def analyze_assist_network_aggregate(cls, shot_details: List[Dict]) -> Dict[str, Any]:
        """
        전체 경기의 어시스트 네트워크 집계 (상세 분석)

        Args:
            shot_details: 모든 경기의 ShotDetail 데이터

        Returns:
            어시스트 네트워크 집계 통계
        """
        # Filter goals with valid assists (assist_spid exists and != -1)
        assist_shots = [
            shot for shot in shot_details
            if shot.get('result') == 'goal'
            and shot.get('assist_spid') is not None
            and shot.get('assist_spid') != -1
        ]

        total_goals = len([s for s in shot_details if s.get('result') == 'goal'])

        if not assist_shots:
            return {
                'total_assisted_goals': 0,
                'total_goals': total_goals,
                'unassisted_goals': total_goals,
                'top_combinations': [],
                'top_playmakers': [],
                'assist_coverage': 0
            }

        # Count combinations (assister -> scorer) if shooter_spid is available
        combinations = Counter()
        playmaker_assists = Counter()

        for shot in assist_shots:
            assist_spid = shot.get('assist_spid')
            shooter_spid = shot.get('shooter_spid')

            # Count assists by playmaker
            if assist_spid:
                playmaker_assists[assist_spid] += 1

            # Count combinations if both players are known
            if assist_spid and shooter_spid:
                combinations[(assist_spid, shooter_spid)] += 1

        # Top playmakers (top 10)
        top_playmakers = [
            {'spid': spid, 'assists': count}
            for spid, count in playmaker_assists.most_common(10)
        ]

        # Top combinations (top 5)
        top_combinations = [
            {'from_spid': combo[0], 'to_spid': combo[1], 'assists': count}
            for combo, count in combinations.most_common(5)
        ]

        assisted_goals_count = len(assist_shots)
        unassisted_goals = total_goals - assisted_goals_count
        assist_coverage = round((assisted_goals_count / total_goals * 100), 1) if total_goals > 0 else 0

        return {
            'total_assisted_goals': assisted_goals_count,
            'total_goals': total_goals,
            'unassisted_goals': unassisted_goals,
            'top_combinations': top_combinations,
            'top_playmakers': top_playmakers,
            'assist_coverage': assist_coverage
        }

    @classmethod
    def analyze_heading_specialists(cls, shot_details: List[Dict]) -> Dict[str, Any]:
        """
        헤딩 전문가 통계 (상세 분석)

        Args:
            shot_details: 모든 경기의 ShotDetail 데이터

        Returns:
            헤딩 전문 통계
        """
        # Filter heading shots (shot_type == 3)
        heading_shots = [shot for shot in shot_details if shot.get('shot_type') == cls.HEADING_TYPE]

        if not heading_shots:
            return {
                'total_headers': 0,
                'heading_goals': 0,
                'heading_on_target': 0,
                'heading_off_target': 0,
                'heading_blocked': 0,
                'heading_success_rate': 0,
                'heading_conversion_rate': 0,
                'cross_dependency': 0,
                'box_headers': 0,
                'box_header_percentage': 0
            }

        # Count by result type
        heading_goals = sum(1 for shot in heading_shots if shot.get('result') == 'goal')
        heading_on_target = sum(1 for shot in heading_shots if shot.get('result') == 'on_target')
        heading_off_target = sum(1 for shot in heading_shots if shot.get('result') == 'off_target')
        heading_blocked = sum(1 for shot in heading_shots if shot.get('result') == 'blocked')

        # Total on target (goals + on_target)
        total_on_target = heading_goals + heading_on_target

        # Headers with assists (cross dependency)
        headers_with_assist = sum(
            1 for shot in heading_shots
            if shot.get('assist_spid') is not None and shot.get('assist_spid') != -1
        )

        # Headers inside the box
        box_headers = sum(1 for shot in heading_shots if shot.get('in_penalty') is True)

        total_headers = len(heading_shots)
        success_rate = round((total_on_target / total_headers * 100), 1) if total_headers > 0 else 0
        conversion_rate = round((heading_goals / total_headers * 100), 1) if total_headers > 0 else 0
        cross_dependency = round((headers_with_assist / total_headers * 100), 1) if total_headers > 0 else 0
        box_percentage = round((box_headers / total_headers * 100), 1) if total_headers > 0 else 0

        return {
            'total_headers': total_headers,
            'heading_goals': heading_goals,
            'heading_on_target': heading_on_target,
            'heading_off_target': heading_off_target,
            'heading_blocked': heading_blocked,
            'heading_success_rate': success_rate,  # (goals + on_target) / total
            'heading_conversion_rate': conversion_rate,  # goals / total
            'cross_dependency': cross_dependency,  # headers with assists / total
            'box_headers': box_headers,
            'box_header_percentage': box_percentage
        }

    @classmethod
    def analyze_shooting_efficiency_trend(cls, shot_details: List[Dict]) -> Dict[str, Any]:
        """
        슈팅 효율성 트렌드 (상세 분석)

        Args:
            shot_details: 모든 경기의 ShotDetail 데이터

        Returns:
            슈팅 효율성 통계
        """
        if not shot_details:
            return {
                'total_shots': 0,
                'total_goals': 0,
                'overall_conversion': 0,
                'accuracy': 0,
                'inside_box_shots': 0,
                'inside_box_goals': 0,
                'inside_box_efficiency': 0,
                'outside_box_shots': 0,
                'outside_box_goals': 0,
                'outside_box_efficiency': 0,
                'shot_breakdown': {
                    'goals': 0,
                    'on_target': 0,
                    'off_target': 0,
                    'blocked': 0
                }
            }

        total_shots = len(shot_details)

        # Count by result type
        goals_count = sum(1 for shot in shot_details if shot.get('result') == 'goal')
        on_target_count = sum(1 for shot in shot_details if shot.get('result') == 'on_target')
        off_target_count = sum(1 for shot in shot_details if shot.get('result') == 'off_target')
        blocked_count = sum(1 for shot in shot_details if shot.get('result') == 'blocked')

        # Total shots on target (goals + on_target)
        total_on_target = goals_count + on_target_count

        # Inside vs outside box (handle None values)
        inside_box_shots = [shot for shot in shot_details if shot.get('in_penalty') is True]
        outside_box_shots = [shot for shot in shot_details if shot.get('in_penalty') is not True]

        inside_goals = sum(1 for shot in inside_box_shots if shot.get('result') == 'goal')
        outside_goals = sum(1 for shot in outside_box_shots if shot.get('result') == 'goal')

        inside_on_target = sum(1 for shot in inside_box_shots if shot.get('result') in ['goal', 'on_target'])
        outside_on_target = sum(1 for shot in outside_box_shots if shot.get('result') in ['goal', 'on_target'])

        return {
            'total_shots': total_shots,
            'total_goals': goals_count,
            'overall_conversion': round((goals_count / total_shots * 100), 1) if total_shots > 0 else 0,
            'accuracy': round((total_on_target / total_shots * 100), 1) if total_shots > 0 else 0,

            # Inside box stats
            'inside_box_shots': len(inside_box_shots),
            'inside_box_goals': inside_goals,
            'inside_box_on_target': inside_on_target,
            'inside_box_efficiency': round((inside_goals / len(inside_box_shots) * 100), 1) if inside_box_shots else 0,
            'inside_box_accuracy': round((inside_on_target / len(inside_box_shots) * 100), 1) if inside_box_shots else 0,

            # Outside box stats
            'outside_box_shots': len(outside_box_shots),
            'outside_box_goals': outside_goals,
            'outside_box_on_target': outside_on_target,
            'outside_box_efficiency': round((outside_goals / len(outside_box_shots) * 100), 1) if outside_box_shots else 0,
            'outside_box_accuracy': round((outside_on_target / len(outside_box_shots) * 100), 1) if outside_box_shots else 0,

            # Shot result breakdown
            'shot_breakdown': {
                'goals': goals_count,
                'on_target': on_target_count,
                'off_target': off_target_count,
                'blocked': blocked_count
            }
        }

    @classmethod
    def analyze_pass_type_distribution(cls, matches_data: List[Dict]) -> Dict[str, Any]:
        """
        패스 타입 평균 분포

        Args:
            matches_data: 모든 경기의 raw_data

        Returns:
            패스 타입 평균 분포
        """
        total_matches = len(matches_data)
        if total_matches == 0:
            return {
                'avg_short_pass_rate': 0,
                'avg_long_pass_rate': 0,
                'avg_through_pass_rate': 0,
                'avg_pass_diversity': 0
            }

        short_pass_rates = []
        long_pass_rates = []
        through_pass_rates = []

        for match_data in matches_data:
            match_info = match_data.get('matchInfo', [])
            if not match_info:
                continue

            user_info = match_info[0]
            pass_data = user_info.get('pass', {})

            if not pass_data:
                continue

            # Handle None values by converting to 0
            short_try = pass_data.get('shortPassTry') or 0
            short_success = pass_data.get('shortPassSuccess') or 0
            long_try = pass_data.get('longPassTry') or 0
            long_success = pass_data.get('longPassSuccess') or 0
            through_try = pass_data.get('throughPassTry') or 0
            through_success = pass_data.get('throughPassSuccess') or 0

            if short_try > 0:
                short_pass_rates.append((short_success / short_try) * 100)
            if long_try > 0:
                long_pass_rates.append((long_success / long_try) * 100)
            if through_try > 0:
                through_pass_rates.append((through_success / through_try) * 100)

        return {
            'avg_short_pass_rate': round(sum(short_pass_rates) / len(short_pass_rates), 1) if short_pass_rates else 0,
            'avg_long_pass_rate': round(sum(long_pass_rates) / len(long_pass_rates), 1) if long_pass_rates else 0,
            'avg_through_pass_rate': round(sum(through_pass_rates) / len(through_pass_rates), 1) if through_pass_rates else 0,
            'matches_analyzed': total_matches
        }

    @classmethod
    def analyze_time_based_goal_patterns(cls, shot_details: List[Dict]) -> Dict[str, Any]:
        """
        시간대별 골 패턴 분석

        Args:
            shot_details: 모든 경기의 ShotDetail 데이터

        Returns:
            시간대별 골 통계
        """
        # Count ALL goals - must match shooting_efficiency.total_goals
        all_goals = [shot for shot in shot_details if shot.get('result') == 'goal']
        total_goals = len(all_goals)

        if not all_goals:
            return {
                'total_goals': 0,
                'first_half_goals': 0,
                'second_half_goals': 0,
                'early_goals': 0,
                'late_goals': 0,
                'goal_timing_pattern': 'insufficient_data'
            }

        # For time-based breakdowns, only use goals with valid time data.
        # Nexon API sometimes returns 0xFFFFFF (16777215) or other large sentinel values
        # for unknown time. Also exclude goal_time == 0 (time not recorded).
        # 10800 seconds = 180 minutes covers all game modes including extra time.
        MAX_VALID_TIME = 10800
        goals_with_time = [
            g for g in all_goals
            if 0 < (g.get('goal_time') or 0) <= MAX_VALID_TIME
        ]

        if not goals_with_time:
            return {
                'total_goals': total_goals,
                'first_half_goals': 0,
                'second_half_goals': 0,
                'early_goals': 0,
                'late_goals': 0,
                'goal_timing_pattern': 'insufficient_data'
            }

        # Time periods (goal_time is in SECONDS, not minutes)
        # 45 minutes = 2700 seconds
        # 30 minutes = 1800 seconds
        # 60 minutes = 3600 seconds
        first_half = [g for g in goals_with_time if (g.get('goal_time') or 0) < 2700]
        second_half = [g for g in goals_with_time if (g.get('goal_time') or 0) >= 2700]
        early_goals = [g for g in goals_with_time if (g.get('goal_time') or 0) < 1800]
        late_goals = [g for g in goals_with_time if (g.get('goal_time') or 0) >= 3600]

        # Determine pattern based on goals that have valid time data
        timed_count = len(goals_with_time)
        first_half_count = len(first_half)
        second_half_count = len(second_half)
        early_count = len(early_goals)
        late_count = len(late_goals)

        if early_count > late_count * 1.5 and early_count >= timed_count * 0.3:
            pattern = 'early_dominant'
        elif late_count > early_count * 1.5 and late_count >= timed_count * 0.3:
            pattern = 'late_surge'
        elif first_half_count > second_half_count * 1.3:
            pattern = 'first_half_strong'
        elif second_half_count > first_half_count * 1.3:
            pattern = 'second_half_strong'
        else:
            pattern = 'balanced'

        return {
            'total_goals': total_goals,       # ALL goals, consistent with shooting_efficiency
            'first_half_goals': first_half_count,
            'second_half_goals': second_half_count,
            'early_goals': early_count,        # 0-30분
            'late_goals': late_count,          # 60-90분
            'goal_timing_pattern': pattern
        }
