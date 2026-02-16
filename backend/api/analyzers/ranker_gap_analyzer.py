"""
Ranker Gap Dashboard — D1
내 플레이의 모든 차원을 랭커와 비교하는 통합 대시보드.
"랭커까지의 거리" 단일 점수 (0-100) 제공.
"""
import math
from typing import List, Dict, Any, Optional


class RankerGapAnalyzer:
    """랭커 격차 대시보드 분석기"""

    # 종합 점수 계산을 위한 메트릭 가중치
    METRICS = {
        'avg_rating': {
            'label': '평균 평점',
            'weight': 3.0,
            'unit': '',
            'format': '{:.1f}',
        },
        'win_rate': {
            'label': '승률',
            'weight': 3.0,
            'unit': '%',
            'format': '{:.1f}%',
        },
        'goals_per_game': {
            'label': '경기당 득점',
            'weight': 2.5,
            'unit': '',
            'format': '{:.2f}',
        },
        'shot_accuracy': {
            'label': '슈팅 정확도',
            'weight': 2.0,
            'unit': '%',
            'format': '{:.1f}%',
        },
        'pass_accuracy': {
            'label': '패스 성공률',
            'weight': 1.5,
            'unit': '%',
            'format': '{:.1f}%',
        },
        'dribble_success_rate': {
            'label': '드리블 성공률',
            'weight': 1.0,
            'unit': '%',
            'format': '{:.1f}%',
        },
    }

    # 랭커 벤치마크 (등급별 — ranker-stats API 데이터 없는 경우 fallback)
    # division codes: 100=슈퍼챔피언, 200=챔피언, 300=슈퍼유, 400=유
    DIVISION_BENCHMARKS = {
        100: {  # 슈퍼챔피언
            'avg_rating': 7.2,
            'win_rate': 65.0,
            'goals_per_game': 2.3,
            'shot_accuracy': 52.0,
            'pass_accuracy': 85.0,
            'dribble_success_rate': 68.0,
        },
        200: {  # 챔피언
            'avg_rating': 6.9,
            'win_rate': 60.0,
            'goals_per_game': 2.0,
            'shot_accuracy': 48.0,
            'pass_accuracy': 82.0,
            'dribble_success_rate': 65.0,
        },
        300: {  # 슈퍼유
            'avg_rating': 6.7,
            'win_rate': 55.0,
            'goals_per_game': 1.7,
            'shot_accuracy': 44.0,
            'pass_accuracy': 79.0,
            'dribble_success_rate': 61.0,
        },
        400: {  # 유
            'avg_rating': 6.5,
            'win_rate': 50.0,
            'goals_per_game': 1.4,
            'shot_accuracy': 40.0,
            'pass_accuracy': 76.0,
            'dribble_success_rate': 57.0,
        },
    }

    # 랭커 스탯 표준편차 (fallback)
    RANKER_STD = {
        'avg_rating': 0.5,
        'win_rate': 12.0,
        'goals_per_game': 0.6,
        'shot_accuracy': 10.0,
        'pass_accuracy': 8.0,
        'dribble_success_rate': 12.0,
    }

    @staticmethod
    def _compute_my_aggregate_stats(
        matches: List[Dict],
        player_performances: List[Dict],
    ) -> Dict[str, float]:
        """매치 + 플레이어 퍼포먼스에서 내 통합 스탯 추출"""
        if not matches:
            return {}

        total = len(matches)
        wins = sum(1 for m in matches if m.get('result') == 'win')
        total_goals = sum(float(m.get('goals_for', 0)) for m in matches)
        total_shots = sum(float(m.get('shots', 1)) for m in matches)
        total_shots_on = sum(float(m.get('shots_on_target', 0)) for m in matches)
        total_pass_rate = sum(float(m.get('pass_success_rate', 0)) for m in matches)

        # Rating from performances
        avg_rating = 6.5  # default
        if player_performances:
            ratings = [float(p.get('rating', 0)) for p in player_performances if float(p.get('rating', 0)) > 0]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)

        # Dribble from performances
        total_dribble_try = sum(int(p.get('dribble_attempts', 0)) for p in player_performances)
        total_dribble_success = sum(int(p.get('dribble_success', 0)) for p in player_performances)

        return {
            'avg_rating': round(avg_rating, 2),
            'win_rate': round(wins / total * 100, 1),
            'goals_per_game': round(total_goals / total, 2),
            'shot_accuracy': round((total_shots_on / max(total_shots, 1)) * 100, 1),
            'pass_accuracy': round(total_pass_rate / total, 1),
            'dribble_success_rate': round(
                (total_dribble_success / max(total_dribble_try, 1)) * 100, 1
            ),
        }

    @staticmethod
    def _extract_ranker_benchmark_from_api(ranker_data_list: List[Dict]) -> Dict[str, Dict]:
        """
        ranker-stats API 응답에서 벤치마크 추출.
        여러 선수의 ranker stats를 합산하여 전반적인 벤치마크 생성.
        """
        if not ranker_data_list:
            return {}

        # Aggregate all ranker statuses across all player requests
        combined: Dict[str, List[float]] = {
            'avg_rating': [],
            'win_rate': [],
            'goals_per_game': [],
            'shot_accuracy': [],
            'pass_accuracy': [],
            'dribble_success_rate': [],
        }

        for player_entry in ranker_data_list:
            status_list = player_entry.get('status', [])
            if isinstance(status_list, list):
                for s in status_list:
                    combined['avg_rating'].append(float(s.get('spRating', 0)))
                    combined['goals_per_game'].append(float(s.get('goal', 0)))

                    shots = float(s.get('shoot', 0))
                    shots_on = float(s.get('effectiveShoot', 0))
                    combined['shot_accuracy'].append((shots_on / shots * 100) if shots > 0 else 0)

                    pass_try = float(s.get('passTry', 0))
                    pass_success = float(s.get('passSuccess', 0))
                    combined['pass_accuracy'].append((pass_success / pass_try * 100) if pass_try > 0 else 0)

                    dribble_try = float(s.get('dribbleTry', 0))
                    dribble_success = float(s.get('dribbleSuccess', 0))
                    combined['dribble_success_rate'].append(
                        (dribble_success / dribble_try * 100) if dribble_try > 0 else 0
                    )

        benchmark = {}
        for metric, values in combined.items():
            if values:
                n = len(values)
                avg = sum(values) / n
                variance = sum((v - avg) ** 2 for v in values) / n if n > 1 else 1.0
                std = math.sqrt(variance) if variance > 0 else 1.0
                benchmark[metric] = {'avg': round(avg, 3), 'std': round(std, 3)}

        return benchmark

    @classmethod
    def calculate_ranker_gap(
        cls,
        matches: List[Dict],
        player_performances: List[Dict],
        division: int = 300,
        ranker_api_data: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        랭커 격차 종합 점수 계산.

        Args:
            matches: Match 딕셔너리 목록
            player_performances: PlayerPerformance 딕셔너리 목록
            division: 현재 등급 (100=슈챔, 200=챔, 300=슈유, 400=유)
            ranker_api_data: ranker-stats API 응답 (없으면 fallback 사용)

        Returns:
            {ranker_distance_score, metric_breakdown, division_benchmark, insights, weekly_progress}
        """
        my_stats = cls._compute_my_aggregate_stats(matches, player_performances)
        if not my_stats:
            return cls._empty_result()

        # Get benchmark
        if ranker_api_data:
            api_benchmark = cls._extract_ranker_benchmark_from_api(ranker_api_data)
        else:
            api_benchmark = {}

        # Use API benchmark where available, fallback to division benchmark
        division_key = min(cls.DIVISION_BENCHMARKS.keys(), key=lambda k: abs(k - division))
        division_bench = cls.DIVISION_BENCHMARKS.get(division_key, cls.DIVISION_BENCHMARKS[300])

        metric_breakdown = {}
        z_scores = {}

        for metric, config in cls.METRICS.items():
            if metric not in my_stats:
                continue

            my_val = my_stats[metric]

            if metric in api_benchmark:
                ranker_avg = api_benchmark[metric]['avg']
                ranker_std = api_benchmark[metric]['std']
            else:
                ranker_avg = division_bench.get(metric, my_val)
                ranker_std = cls.RANKER_STD.get(metric, 1.0)

            z = (my_val - ranker_avg) / ranker_std if ranker_std > 0 else 0.0
            z_scores[metric] = z

            # Convert to 0-100 proximity score (50 = average ranker, 100 = far above)
            proximity = 50 + z * 15  # 1 std = 15 points
            proximity = max(0, min(100, proximity))

            metric_breakdown[metric] = {
                'label': config['label'],
                'my_value': round(my_val, 2),
                'ranker_avg': round(ranker_avg, 2),
                'ranker_std': round(ranker_std, 2),
                'z_score': round(z, 2),
                'proximity_score': round(proximity, 1),
                'status': cls._metric_status(z),
                'gap_description': cls._gap_description(metric, my_val, ranker_avg),
            }

        # Weighted overall ranker distance score (0-100)
        total_weight = sum(cls.METRICS[m]['weight'] for m in metric_breakdown)
        if total_weight > 0:
            weighted_proximity = sum(
                metric_breakdown[m]['proximity_score'] * cls.METRICS[m]['weight']
                for m in metric_breakdown
            ) / total_weight
        else:
            weighted_proximity = 50.0

        ranker_distance_score = round(weighted_proximity, 1)

        # Grade label
        grade = cls._distance_grade(ranker_distance_score)

        insights = cls._generate_insights(metric_breakdown, ranker_distance_score, grade, division)

        return {
            'ranker_distance_score': ranker_distance_score,
            'grade': grade,
            'my_stats': my_stats,
            'metric_breakdown': metric_breakdown,
            'division': division,
            'division_label': cls._division_label(division),
            'data_source': 'api' if ranker_api_data else 'fallback',
            'matches_analyzed': len(matches),
            'insights': insights,
        }

    @staticmethod
    def _metric_status(z: float) -> str:
        if z >= 1.0:
            return 'elite'
        elif z >= 0.0:
            return 'above_average'
        elif z >= -0.5:
            return 'average'
        elif z >= -1.0:
            return 'below_average'
        else:
            return 'needs_work'

    @staticmethod
    def _gap_description(metric: str, my_val: float, ranker_avg: float) -> str:
        diff = my_val - ranker_avg
        labels = {
            'avg_rating': ('평점', '점'),
            'win_rate': ('승률', '%'),
            'goals_per_game': ('경기당 득점', '골'),
            'shot_accuracy': ('슈팅 정확도', '%'),
            'pass_accuracy': ('패스 성공률', '%'),
            'dribble_success_rate': ('드리블 성공률', '%'),
        }
        label, unit = labels.get(metric, (metric, ''))
        if diff >= 0:
            return f"{label}이 랭커 평균보다 {abs(diff):.1f}{unit} 높습니다"
        else:
            return f"{label}이 랭커 평균보다 {abs(diff):.1f}{unit} 낮습니다"

    @staticmethod
    def _distance_grade(score: float) -> Dict:
        if score >= 80:
            return {'label': '랭커급', 'color': 'gold', 'emoji': '🏆', 'description': '랭커와 동등한 수준'}
        elif score >= 65:
            return {'label': '준랭커', 'color': 'green', 'emoji': '⭐', 'description': '랭커에 근접한 수준'}
        elif score >= 50:
            return {'label': '평균', 'color': 'blue', 'emoji': '📊', 'description': '평균적인 수준'}
        elif score >= 35:
            return {'label': '발전 중', 'color': 'yellow', 'emoji': '📈', 'description': '개선이 필요한 수준'}
        else:
            return {'label': '초보', 'color': 'red', 'emoji': '🎮', 'description': '기초 훈련이 필요'}

    @staticmethod
    def _division_label(division: int) -> str:
        labels = {100: '슈퍼챔피언', 200: '챔피언', 300: '슈퍼유', 400: '유', 500: '세미프로', 600: '프로'}
        closest = min(labels.keys(), key=lambda k: abs(k - division))
        return labels.get(closest, f'등급 {division}')

    @staticmethod
    def _generate_insights(
        breakdown: Dict,
        score: float,
        grade: Dict,
        division: int,
    ) -> List[str]:
        insights = []

        insights.append(
            f"🎯 랭커까지의 거리 점수: {score:.0f}/100 — {grade['label']} {grade['emoji']}"
        )

        # Best metric
        if breakdown:
            best_metric = max(breakdown.items(), key=lambda x: x[1]['z_score'])
            worst_metric = min(breakdown.items(), key=lambda x: x[1]['z_score'])

            bm = best_metric[1]
            if bm['z_score'] > 0:
                insights.append(
                    f"✅ 강점: {bm['label']} ({bm['my_value']} vs 랭커 {bm['ranker_avg']})"
                )

            wm = worst_metric[1]
            if wm['z_score'] < -0.5:
                insights.append(
                    f"🔴 최우선 개선 영역: {wm['label']} "
                    f"({wm['my_value']} vs 랭커 {wm['ranker_avg']})"
                )

        if score >= 65:
            insights.append("🔥 랭커 수준에 근접하고 있습니다. 현재 수준을 유지하고 세부 기술을 연마하세요!")
        elif score >= 50:
            insights.append("📈 평균 수준에 있습니다. 약점 집중 훈련으로 랭커에 도전하세요!")
        else:
            insights.append("💪 기본기 강화가 필요합니다. 슈팅과 패스 정확도부터 개선하세요.")

        return insights

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            'ranker_distance_score': 0,
            'grade': {'label': '데이터 없음', 'color': 'gray', 'emoji': '❓', 'description': ''},
            'my_stats': {},
            'metric_breakdown': {},
            'division': 300,
            'division_label': '슈퍼유',
            'data_source': 'none',
            'matches_analyzed': 0,
            'insights': ['분석할 경기 데이터가 없습니다.'],
        }
