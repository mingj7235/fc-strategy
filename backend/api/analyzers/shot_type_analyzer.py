"""
Shot Type Analyzer

슈팅 타입별 상세 분석 - 타입, 골대 맞춤, 박스 위치 등
"""

from typing import List, Dict, Any
from collections import defaultdict


class ShotTypeAnalyzer:
    """슈팅 타입별 상세 분석기"""

    # 슈팅 타입 매핑 (Nexon API type 코드 → 한국어 이름)
    SHOT_TYPE_NAMES = {
        1: '일반 슛',
        2: '일반 슛',
        3: '헤딩',
        4: '발리',
        6: '발리',
        7: '프리킥',
        8: '페널티킥',
        9: '로빙 슛',
        10: '칩 슛',
        12: '땅볼 슛',
        13: '파워 슛',
    }

    @classmethod
    def analyze_shot_types(cls, shot_details: List[Dict]) -> Dict[str, Any]:
        """
        슈팅 타입별 종합 분석

        Args:
            shot_details: ShotDetail 쿼리셋 값 리스트

        Returns:
            Dict containing:
            - type_breakdown: 타입별 성공률
            - location_analysis: 박스 내/외 분석
            - post_hits: 골대 맞춤 분석
            - insights: 인사이트
        """
        if not shot_details:
            return cls._empty_analysis()

        # 1. 타입별 분석
        type_breakdown = cls._analyze_by_type(shot_details)

        # 2. 박스 위치 분석
        location_analysis = cls._analyze_by_location(shot_details)

        # 3. 골대 맞춤 분석
        post_hits = cls._analyze_post_hits(shot_details)

        # 4. 인사이트 생성
        insights = cls._generate_insights(
            shot_details, type_breakdown, location_analysis, post_hits
        )

        return {
            'type_breakdown': type_breakdown,
            'location_analysis': location_analysis,
            'post_hits': post_hits,
            'total_shots': len(shot_details),
            'insights': insights,
        }

    @classmethod
    def _analyze_by_type(cls, shot_details: List[Dict]) -> List[Dict]:
        """
        슈팅 타입별 성공률 분석

        Returns:
            List of {type_name, shots, goals, on_target, success_rate, conversion_rate}
        """
        type_stats = defaultdict(lambda: {
            'shots': 0,
            'goals': 0,
            'on_target': 0,
        })

        for shot in shot_details:
            shot_type = shot.get('shot_type', 1)
            type_name = cls.SHOT_TYPE_NAMES.get(shot_type, f'타입 {shot_type}')
            result = shot.get('result')

            type_stats[type_name]['shots'] += 1

            if result == 'goal':
                type_stats[type_name]['goals'] += 1
                type_stats[type_name]['on_target'] += 1
            elif result == 'on_target':
                type_stats[type_name]['on_target'] += 1

        # Convert to list and calculate rates
        breakdown = []
        for type_name, stats in type_stats.items():
            shots = stats['shots']
            goals = stats['goals']
            on_target = stats['on_target']

            success_rate = (on_target / shots * 100) if shots > 0 else 0
            conversion_rate = (goals / shots * 100) if shots > 0 else 0

            breakdown.append({
                'type_name': type_name,
                'shots': shots,
                'goals': goals,
                'on_target': on_target,
                'success_rate': round(success_rate, 1),
                'conversion_rate': round(conversion_rate, 1),
            })

        # Sort by shots count (descending)
        breakdown.sort(key=lambda x: x['shots'], reverse=True)

        return breakdown

    @classmethod
    def _analyze_by_location(cls, shot_details: List[Dict]) -> Dict[str, Any]:
        """
        박스 내/외 슈팅 효율 비교

        Returns:
            Dict with inside_box and outside_box stats
        """
        inside_stats = {'shots': 0, 'goals': 0, 'on_target': 0}
        outside_stats = {'shots': 0, 'goals': 0, 'on_target': 0}

        for shot in shot_details:
            in_penalty = shot.get('in_penalty', False)
            result = shot.get('result')

            target_stats = inside_stats if in_penalty else outside_stats
            target_stats['shots'] += 1

            if result == 'goal':
                target_stats['goals'] += 1
                target_stats['on_target'] += 1
            elif result == 'on_target':
                target_stats['on_target'] += 1

        # Calculate rates
        def calc_rates(stats):
            shots = stats['shots']
            return {
                **stats,
                'success_rate': round((stats['on_target'] / shots * 100) if shots > 0 else 0, 1),
                'conversion_rate': round((stats['goals'] / shots * 100) if shots > 0 else 0, 1),
            }

        return {
            'inside_box': calc_rates(inside_stats),
            'outside_box': calc_rates(outside_stats),
        }

    @classmethod
    def _analyze_post_hits(cls, shot_details: List[Dict]) -> Dict[str, Any]:
        """
        골대 맞춤 분석

        Returns:
            Dict with post_hit_count, post_hit_shots, unlucky_factor
        """
        post_hits = [shot for shot in shot_details if shot.get('hit_post', False)]
        post_hit_count = len(post_hits)

        # Unlucky factor: 골대 맞춘 것 중 골로 연결되지 않은 비율
        post_hit_no_goal = sum(1 for shot in post_hits if shot.get('result') != 'goal')
        unlucky_factor = (post_hit_no_goal / post_hit_count) if post_hit_count > 0 else 0

        return {
            'post_hit_count': post_hit_count,
            'post_hit_shots': post_hits,
            'unlucky_factor': round(unlucky_factor * 100, 1),
        }

    @classmethod
    def _generate_insights(
        cls,
        shot_details: List[Dict],
        type_breakdown: List[Dict],
        location_analysis: Dict,
        post_hits: Dict
    ) -> List[str]:
        """인사이트 생성 (한국어)"""
        insights = []
        total_shots = len(shot_details)

        # 1. 골대 맞춤 인사이트
        post_count = post_hits['post_hit_count']
        if post_count >= 3:
            insights.append(f"⚠️ 골대를 {post_count}번 맞췄습니다. 오늘 운이 안 좋네요!")
        elif post_count >= 2:
            insights.append(f"골대를 {post_count}번 맞췄습니다. 조금만 더 정확하게!")

        # 2. 헤딩 분석
        heading_stats = next((t for t in type_breakdown if t['type_name'] == '헤딩'), None)
        if heading_stats and heading_stats['shots'] >= 3:
            if heading_stats['conversion_rate'] >= 30:
                insights.append(f"🎯 헤딩 성공률이 높습니다 ({heading_stats['conversion_rate']:.1f}%). 공중볼 전술이 효과적이에요!")
            elif heading_stats['conversion_rate'] < 15:
                insights.append(f"헤딩 슈팅 {heading_stats['shots']}회 중 {heading_stats['goals']}골. 크로스 타이밍을 개선해보세요.")

        # 3. 박스 위치 분석
        inside = location_analysis['inside_box']
        outside = location_analysis['outside_box']

        inside_percentage = (inside['shots'] / total_shots * 100) if total_shots > 0 else 0

        if inside_percentage < 40:
            insights.append(f"⚡ 박스 내 슈팅이 {inside_percentage:.0f}%밖에 안 됩니다. 더 깊숙이 침투해보세요!")
        elif inside_percentage >= 70:
            insights.append(f"✅ 박스 내 슈팅 비율이 높습니다 ({inside_percentage:.0f}%). 좋은 위치 선정이에요!")

        # 박스 외곽 비효율성
        if outside['shots'] >= 5 and outside['conversion_rate'] < 10:
            insights.append(f"박스 외곽 슈팅 {outside['shots']}회 중 {outside['goals']}골만 성공. 박스 안으로 들어가는 것이 더 효율적입니다.")

        # 4. 타입별 인사이트
        if len(type_breakdown) >= 3:
            best_type = max(type_breakdown, key=lambda x: x['conversion_rate'] if x['shots'] >= 3 else 0)
            if best_type['shots'] >= 3:
                insights.append(f"💪 {best_type['type_name']}의 골 전환율이 가장 높습니다 ({best_type['conversion_rate']:.1f}%).")

        # 5. 전반적인 슈팅 품질
        total_goals = sum(1 for shot in shot_details if shot.get('result') == 'goal')
        overall_conversion = (total_goals / total_shots * 100) if total_shots > 0 else 0

        if overall_conversion >= 25:
            insights.append(f"🔥 골 전환율 {overall_conversion:.1f}%! 매우 효율적인 슈팅입니다!")
        elif overall_conversion < 15:
            insights.append(f"골 전환율이 {overall_conversion:.1f}%로 낮습니다. 더 확실한 기회를 만들어보세요.")

        return insights

    @classmethod
    def _empty_analysis(cls) -> Dict[str, Any]:
        """빈 분석 결과 반환"""
        return {
            'type_breakdown': [],
            'location_analysis': {
                'inside_box': {'shots': 0, 'goals': 0, 'on_target': 0, 'success_rate': 0, 'conversion_rate': 0},
                'outside_box': {'shots': 0, 'goals': 0, 'on_target': 0, 'success_rate': 0, 'conversion_rate': 0},
            },
            'post_hits': {
                'post_hit_count': 0,
                'post_hit_shots': [],
                'unlucky_factor': 0,
            },
            'total_shots': 0,
            'insights': ['슈팅 데이터가 없습니다.'],
        }
