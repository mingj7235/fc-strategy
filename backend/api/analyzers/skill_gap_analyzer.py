"""
Skill Gap Analyzer — B2
내가 사용하는 선수로 랭커가 동일 선수로 내는 성적과 내 성적을 비교,
구체적인 실력 격차를 Z-score로 수치화.
"""
import math
from typing import List, Dict, Any


class SkillGapAnalyzer:
    """랭커 대비 내 선수 활용 격차 분석기"""

    METRICS_CONFIG = {
        'avg_rating': {
            'label': '평균 평점',
            'description': 'spRating 기준 경기 평점 (0~10)',
            'higher_better': True,
            'weight': 2.5,
        },
        'goals_per_game': {
            'label': '경기당 득점',
            'description': '경기당 평균 골 수',
            'higher_better': True,
            'weight': 2.0,
        },
        'assists_per_game': {
            'label': '경기당 어시스트',
            'description': '경기당 평균 어시스트 수',
            'higher_better': True,
            'weight': 1.5,
        },
        'shot_accuracy': {
            'label': '슈팅 정확도',
            'description': '유효슛 / 총 슛 비율 (%)',
            'higher_better': True,
            'weight': 1.5,
        },
        'pass_accuracy': {
            'label': '패스 성공률',
            'description': '패스 성공 / 패스 시도 비율 (%)',
            'higher_better': True,
            'weight': 1.0,
        },
        'dribble_success_rate': {
            'label': '드리블 성공률',
            'description': '드리블 성공 / 드리블 시도 비율 (%)',
            'higher_better': True,
            'weight': 1.0,
        },
    }

    GAP_LEVEL_LABELS = {
        'ranker_level': {'label': '랭커급', 'color': 'gold', 'emoji': '🏆'},
        'near_ranker': {'label': '랭커 근접', 'color': 'green', 'emoji': '✅'},
        'slight_gap': {'label': '소폭 격차', 'color': 'yellow', 'emoji': '📈'},
        'moderate_gap': {'label': '중간 격차', 'color': 'orange', 'emoji': '⚠️'},
        'significant_gap': {'label': '큰 격차', 'color': 'red', 'emoji': '🔴'},
        'large_gap': {'label': '매우 큰 격차', 'color': 'darkred', 'emoji': '🚨'},
    }

    @staticmethod
    def _extract_my_stats(performances: List[Dict]) -> Dict[str, float]:
        """PlayerPerformance 리스트에서 평균 통계 추출"""
        if not performances:
            return {}

        total = len(performances)
        total_rating = sum(float(p.get('rating', 0)) for p in performances)
        total_goals = sum(int(p.get('goals', 0)) for p in performances)
        total_assists = sum(int(p.get('assists', 0)) for p in performances)
        total_shots = sum(int(p.get('shots', 0)) for p in performances)
        total_shots_on = sum(int(p.get('shots_on_target', 0)) for p in performances)
        total_pass_try = sum(int(p.get('pass_attempts', 0)) for p in performances)
        total_pass_success = sum(int(p.get('pass_success', 0)) for p in performances)
        total_dribble_try = sum(int(p.get('dribble_attempts', 0)) for p in performances)
        total_dribble_success = sum(int(p.get('dribble_success', 0)) for p in performances)

        return {
            'avg_rating': total_rating / total,
            'goals_per_game': total_goals / total,
            'assists_per_game': total_assists / total,
            'shot_accuracy': (total_shots_on / total_shots * 100) if total_shots > 0 else 0,
            'pass_accuracy': (total_pass_success / total_pass_try * 100) if total_pass_try > 0 else 0,
            'dribble_success_rate': (total_dribble_success / total_dribble_try * 100) if total_dribble_try > 0 else 0,
        }

    # Estimated std values for each metric (used when API returns pre-aggregated avg only)
    METRIC_STDS = {
        'avg_rating': 0.6,
        'goals_per_game': 0.35,
        'assists_per_game': 0.25,
        'shot_accuracy': 18.0,
        'pass_accuracy': 10.0,
        'dribble_success_rate': 15.0,
    }

    # Ranker avg rating (spRating not in ranker-stats API, use domain estimate)
    RANKER_AVG_RATING = 7.2

    @classmethod
    def _extract_ranker_stats(cls, ranker_status_list: List[Dict]) -> Dict[str, Dict[str, float]]:
        """
        랭커 status에서 각 메트릭의 평균 추출.
        Nexon API ranker-stats는 선수별 랭커 평균을 pre-aggregated dict 하나로 반환함.
        """
        if not ranker_status_list:
            return {}

        metrics: Dict[str, List[float]] = {
            'avg_rating': [],
            'goals_per_game': [],
            'assists_per_game': [],
            'shot_accuracy': [],
            'pass_accuracy': [],
            'dribble_success_rate': [],
        }

        for s in ranker_status_list:
            # spRating은 ranker-stats API에 없으므로 도메인 추정값 사용
            # (개별 stat dict에 있다면 그걸 쓰고, 없으면 상수)
            rating = float(s.get('spRating', cls.RANKER_AVG_RATING))
            metrics['avg_rating'].append(rating)

            # Goals / Assists (API 필드: goal, assist)
            metrics['goals_per_game'].append(float(s.get('goal', 0)))
            metrics['assists_per_game'].append(float(s.get('assist', 0)))

            # Shot accuracy: effectiveShoot / shoot (%)
            shots = float(s.get('shoot', 0))
            shots_on = float(s.get('effectiveShoot', 0))
            metrics['shot_accuracy'].append((shots_on / shots * 100) if shots > 0 else 0)

            # Pass accuracy: passSuccess / passTry (%)
            pass_try = float(s.get('passTry', 0))
            pass_success = float(s.get('passSuccess', 0))
            metrics['pass_accuracy'].append((pass_success / pass_try * 100) if pass_try > 0 else 0)

            # Dribble success rate: dribbleSuccess / dribbleTry (%)
            dribble_try = float(s.get('dribbleTry', 0))
            dribble_success = float(s.get('dribbleSuccess', 0))
            metrics['dribble_success_rate'].append(
                (dribble_success / dribble_try * 100) if dribble_try > 0 else 0
            )

        result = {}
        for metric, values in metrics.items():
            non_zero = [v for v in values if v > 0]
            if not non_zero:
                continue
            n = len(non_zero)
            avg = sum(non_zero) / n
            # API가 pre-aggregated 평균만 제공하므로 도메인 지식 기반 std 사용
            if n == 1:
                std = cls.METRIC_STDS.get(metric, 1.0)
            else:
                variance = sum((v - avg) ** 2 for v in non_zero) / n
                std = math.sqrt(variance) if variance > 0 else cls.METRIC_STDS.get(metric, 1.0)

            result[metric] = {'avg': round(avg, 3), 'std': round(std, 3), 'n': n}

        return result

    @staticmethod
    def _z_to_percentile(z: float) -> float:
        """Z-score → 백분위 (0~100)"""
        from math import erf, sqrt
        z = max(-4.0, min(4.0, z))
        percentile = 50.0 * (1.0 + erf(z / sqrt(2.0)))
        return round(percentile, 1)

    @staticmethod
    def _gap_level(z: float) -> str:
        if z >= 1.0:
            return 'ranker_level'
        elif z >= 0.0:
            return 'near_ranker'
        elif z >= -0.5:
            return 'slight_gap'
        elif z >= -1.0:
            return 'moderate_gap'
        elif z >= -2.0:
            return 'significant_gap'
        else:
            return 'large_gap'

    @classmethod
    def analyze_player_gap(
        cls,
        spid: int,
        player_name: str,
        position: int,
        appearances: int,
        performances: List[Dict],
        ranker_status_list: List[Dict],
    ) -> Dict[str, Any]:
        """
        단일 선수에 대한 Skill Gap 분석.

        Returns:
            {spid, player_name, appearances, metric_gaps, priority_improvements,
             overall_z_score, overall_level, ranker_proximity}
        """
        my_stats = cls._extract_my_stats(performances)
        ranker_stats = cls._extract_ranker_stats(ranker_status_list)

        if not my_stats or not ranker_stats:
            return {}

        gaps = {}
        priority_improvements = []

        for metric, config in cls.METRICS_CONFIG.items():
            if metric not in my_stats or metric not in ranker_stats:
                continue

            my_val = my_stats[metric]
            ranker_avg = ranker_stats[metric]['avg']
            ranker_std = ranker_stats[metric]['std']
            n_rankers = ranker_stats[metric].get('n', 0)

            z_score = (my_val - ranker_avg) / ranker_std if ranker_std > 0 else 0.0
            z_score = round(z_score, 2)

            gaps[metric] = {
                'label': config['label'],
                'description': config['description'],
                'my_value': round(my_val, 2),
                'ranker_avg': round(ranker_avg, 2),
                'ranker_std': round(ranker_std, 2),
                'n_rankers': n_rankers,
                'z_score': z_score,
                'percentile': cls._z_to_percentile(z_score),
                'gap_level': cls._gap_level(z_score),
                'gap_level_info': cls.GAP_LEVEL_LABELS.get(cls._gap_level(z_score), {}),
            }

            if z_score < -0.5:
                priority_improvements.append({
                    'metric': metric,
                    'label': config['label'],
                    'description': config['description'],
                    'gap': round(abs(z_score), 2),
                    'my_value': round(my_val, 2),
                    'ranker_avg': round(ranker_avg, 2),
                })

        priority_improvements.sort(key=lambda x: x['gap'], reverse=True)

        # Weighted overall Z-score
        total_weight = 0.0
        weighted_sum = 0.0
        for metric, config in cls.METRICS_CONFIG.items():
            if metric in gaps:
                weighted_sum += gaps[metric]['z_score'] * config['weight']
                total_weight += config['weight']

        overall_z = (weighted_sum / total_weight) if total_weight > 0 else 0.0

        # Generate Korean improvement guide
        guide = cls._generate_guide(gaps, player_name, priority_improvements)

        return {
            'spid': spid,
            'player_name': player_name,
            'position': position,
            'appearances': appearances,
            'metric_gaps': gaps,
            'priority_improvements': priority_improvements[:3],
            'overall_z_score': round(overall_z, 2),
            'overall_level': cls._gap_level(overall_z),
            'overall_level_info': cls.GAP_LEVEL_LABELS.get(cls._gap_level(overall_z), {}),
            'ranker_proximity': cls._z_to_percentile(overall_z),
            'improvement_guide': guide,
        }

    @staticmethod
    def _generate_guide(gaps: Dict, player_name: str, improvements: List[Dict]) -> List[str]:
        """랭커 수준 달성을 위한 한국어 가이드 생성"""
        guide = []
        if not improvements:
            guide.append(f"✅ {player_name} 활용도가 랭커 수준에 근접합니다!")
            return guide

        top = improvements[0]
        metric = top['metric']
        my_val = top['my_value']
        ranker_avg = top['ranker_avg']

        if metric == 'avg_rating':
            guide.append(f"🎯 {player_name}의 평균 평점을 {my_val:.1f} → {ranker_avg:.1f}으로 올리세요. "
                         f"더 적극적인 수비 가담과 킬패스가 평점을 높입니다.")
        elif metric == 'goals_per_game':
            guide.append(f"⚽ {player_name}의 경기당 득점을 {my_val:.2f} → {ranker_avg:.2f}으로 늘리세요. "
                         f"패널티박스 안에서 슈팅 기회를 더 만들어야 합니다.")
        elif metric == 'assists_per_game':
            guide.append(f"🅰️ {player_name}의 경기당 어시스트를 {my_val:.2f} → {ranker_avg:.2f}으로 늘리세요. "
                         f"스루패스 활용도를 높이고 빈 공간 침투를 유도하세요.")
        elif metric == 'shot_accuracy':
            guide.append(f"🎯 {player_name}의 슈팅 정확도를 {my_val:.1f}% → {ranker_avg:.1f}%로 높이세요. "
                         f"패널티박스 안에서의 유효슈팅 비율을 개선하세요.")
        elif metric == 'pass_accuracy':
            guide.append(f"↗️ {player_name}의 패스 성공률을 {my_val:.1f}% → {ranker_avg:.1f}%로 높이세요. "
                         f"압박 상황에서 무리한 장패스보다 짧은 패스를 활용하세요.")
        elif metric == 'dribble_success_rate':
            guide.append(f"🏃 {player_name}의 드리블 성공률을 {my_val:.1f}% → {ranker_avg:.1f}%로 높이세요. "
                         f"좁은 공간에서의 드리블보다 넓은 공간을 활용하세요.")

        if len(improvements) > 1:
            second = improvements[1]
            guide.append(f"다음 개선 포인트: {second['label']} "
                         f"(현재 {second['my_value']:.1f} vs 랭커 {second['ranker_avg']:.1f})")

        return guide

    @classmethod
    def generate_overall_insights(cls, player_gaps: List[Dict]) -> List[str]:
        """전체 선수 목록에 대한 종합 인사이트 생성"""
        insights = []
        if not player_gaps:
            return ['분석할 데이터가 부족합니다. 5경기 이상 플레이한 선수가 필요합니다.']

        valid = [p for p in player_gaps if p.get('overall_z_score') is not None]
        if not valid:
            return ['랭커 스탯 비교 데이터를 가져오지 못했습니다.']

        valid.sort(key=lambda x: x['overall_z_score'], reverse=True)
        best = valid[0]
        worst = valid[-1]

        if best['overall_z_score'] >= 0:
            insights.append(
                f"🏆 {best['player_name']}이(가) 가장 랭커에 근접한 활용도를 보이고 있습니다 "
                f"(상위 {100 - best['ranker_proximity']:.0f}% 수준)"
            )

        if worst['overall_z_score'] < -1.0 and worst['priority_improvements']:
            top_improve = worst['priority_improvements'][0]
            insights.append(
                f"⚠️ {worst['player_name']}의 {top_improve['label']} 개선이 가장 시급합니다 "
                f"(현재 {top_improve['my_value']:.1f} vs 랭커 {top_improve['ranker_avg']:.1f})"
            )

        near_ranker_count = sum(1 for p in valid if p['overall_z_score'] >= -0.5)
        insights.append(
            f"📊 분석 선수 {len(valid)}명 중 {near_ranker_count}명이 랭커 수준의 80% 이상에 도달했습니다."
        )

        # Trend check (if we have enough players)
        if len(valid) >= 3:
            avg_z = sum(p['overall_z_score'] for p in valid) / len(valid)
            if avg_z >= 0:
                insights.append("✅ 전반적으로 랭커와 비교해 준수한 선수 활용도를 보이고 있습니다!")
            elif avg_z >= -1.0:
                insights.append("📈 전반적인 선수 활용도가 랭커보다 약간 낮습니다. 개선 여지가 있습니다.")
            else:
                insights.append("🔴 전반적인 선수 활용도가 랭커보다 상당히 낮습니다. 집중 훈련이 필요합니다.")

        return insights
