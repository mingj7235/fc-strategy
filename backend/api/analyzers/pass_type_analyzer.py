"""
Pass Type Analyzer
패스 타입별 상세 분석 및 스타일 분류
"""
from typing import Dict, Any, List
import math


class PassTypeAnalyzer:
    """
    패스 타입별 분석기
    - 6가지 패스 타입 분석
    - 패스 믹스 다양성 점수
    - 패스 스타일 분류 (땅볼 vs 공중볼)
    """

    @classmethod
    def analyze_pass_types(cls, pass_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        패스 타입별 상세 분석

        Args:
            pass_data: raw_data['matchInfo'][]['pass']

        Returns:
            패스 분석 결과
        """
        # 패스 타입별 성공률 계산
        pass_breakdown = cls._calculate_pass_breakdown(pass_data)

        # 패스 믹스 다양성 점수
        diversity_score = cls._calculate_diversity_score(pass_breakdown)

        # 패스 스타일 분류
        play_style = cls._classify_play_style(pass_data)

        # 인사이트 생성
        insights = cls._generate_insights(pass_breakdown, diversity_score, play_style)

        # 총 패스 통계
        total_stats = cls._calculate_total_stats(pass_data)

        return {
            'pass_breakdown': pass_breakdown,
            'diversity_score': diversity_score,
            'play_style': play_style,
            'total_stats': total_stats,
            'insights': insights
        }

    @classmethod
    def _calculate_pass_breakdown(cls, pass_data: Dict) -> List[Dict]:
        """패스 타입별 시도/성공/성공률 계산"""
        breakdown = []

        # 1. 짧은 패스
        short_try = pass_data.get('shortPassTry', 0)
        short_success = pass_data.get('shortPassSuccess', 0)
        if short_try > 0:
            breakdown.append({
                'type_name': '짧은 패스',
                'type_code': 'short',
                'attempts': short_try,
                'success': short_success,
                'success_rate': round((short_success / short_try) * 100, 1) if short_try > 0 else 0
            })

        # 2. 긴 패스
        long_try = pass_data.get('longPassTry', 0)
        long_success = pass_data.get('longPassSuccess', 0)
        if long_try > 0:
            breakdown.append({
                'type_name': '긴 패스',
                'type_code': 'long',
                'attempts': long_try,
                'success': long_success,
                'success_rate': round((long_success / long_try) * 100, 1) if long_try > 0 else 0
            })

        # 3. 스루 패스
        through_try = pass_data.get('throughPassTry', 0)
        through_success = pass_data.get('throughPassSuccess', 0)
        if through_try > 0:
            breakdown.append({
                'type_name': '스루 패스',
                'type_code': 'through',
                'attempts': through_try,
                'success': through_success,
                'success_rate': round((through_success / through_try) * 100, 1) if through_try > 0 else 0
            })

        # 4. 롭 스루 패스
        lobbed_try = pass_data.get('lobbedThroughPassTry', 0)
        lobbed_success = pass_data.get('lobbedThroughPassSuccess', 0)
        if lobbed_try > 0:
            breakdown.append({
                'type_name': '롱 스루 패스',
                'type_code': 'lobbed_through',
                'attempts': lobbed_try,
                'success': lobbed_success,
                'success_rate': round((lobbed_success / lobbed_try) * 100, 1) if lobbed_try > 0 else 0
            })

        # 5. 드리븐 그라운드 패스 (시도 횟수 정보 없음, 성공만)
        driven_ground = pass_data.get('drivenGroundPassSuccess', 0)
        if driven_ground > 0:
            breakdown.append({
                'type_name': '드리븐 패스',
                'type_code': 'driven_ground',
                'attempts': driven_ground,  # 성공만 기록됨
                'success': driven_ground,
                'success_rate': 100.0  # 성공만 기록되므로 100%
            })

        # 6. 바운싱 롭 패스 (시도 횟수 정보 없음, 성공만)
        bouncing_lob = pass_data.get('bouncingLobPassSuccess', 0)
        if bouncing_lob > 0:
            breakdown.append({
                'type_name': '바운싱 롭 패스',
                'type_code': 'bouncing_lob',
                'attempts': bouncing_lob,  # 성공만 기록됨
                'success': bouncing_lob,
                'success_rate': 100.0  # 성공만 기록되므로 100%
            })

        return breakdown

    @classmethod
    def _calculate_diversity_score(cls, pass_breakdown: List[Dict]) -> int:
        """
        패스 다양성 점수 계산 (0-100)

        섀넌 엔트로피를 사용하여 다양성 측정
        - 모든 패스 타입을 골고루 사용하면 100점
        - 한 가지만 사용하면 0점
        """
        if not pass_breakdown:
            return 0

        total_attempts = sum(p['attempts'] for p in pass_breakdown)
        if total_attempts == 0:
            return 0

        # 각 패스 타입의 비율 계산
        proportions = [p['attempts'] / total_attempts for p in pass_breakdown]

        # 섀넌 엔트로피 계산
        entropy = 0
        for p in proportions:
            if p > 0:
                entropy -= p * math.log2(p)

        # 최대 엔트로피 (모든 타입이 균등하게 사용될 때)
        max_entropy = math.log2(len(pass_breakdown))

        # 0-100 점수로 정규화
        diversity_score = int((entropy / max_entropy) * 100) if max_entropy > 0 else 0

        return diversity_score

    @classmethod
    def _classify_play_style(cls, pass_data: Dict) -> Dict[str, Any]:
        """
        패스 스타일 분류
        - "땅볼 플레이어" vs "공중볼 플레이어"
        - "빌드업형" vs "속공형"
        """
        # 땅볼 패스 (짧은 패스 + 드리븐 그라운드 패스)
        ground_passes = (
            pass_data.get('shortPassSuccess', 0) +
            pass_data.get('drivenGroundPassSuccess', 0)
        )

        # 공중볼 패스 (긴 패스 + 롭 스루 패스 + 바운싱 롭 패스)
        aerial_passes = (
            pass_data.get('longPassSuccess', 0) +
            pass_data.get('lobbedThroughPassSuccess', 0) +
            pass_data.get('bouncingLobPassSuccess', 0)
        )

        # 관통 패스 (스루 패스 + 롭 스루 패스)
        penetrative_passes = (
            pass_data.get('throughPassSuccess', 0) +
            pass_data.get('lobbedThroughPassSuccess', 0)
        )

        total_passes = ground_passes + aerial_passes

        # 땅볼 vs 공중볼 비율
        ground_ratio = (ground_passes / total_passes * 100) if total_passes > 0 else 50
        aerial_ratio = (aerial_passes / total_passes * 100) if total_passes > 0 else 50

        # 스타일 분류
        if ground_ratio >= 70:
            primary_style = "땅볼 플레이어"
            style_description = "짧은 패스로 안정적인 빌드업을 선호합니다"
        elif aerial_ratio >= 70:
            primary_style = "공중볼 플레이어"
            style_description = "긴 패스와 공중볼을 적극 활용합니다"
        else:
            primary_style = "균형형 플레이어"
            style_description = "땅볼과 공중볼을 적절히 혼합합니다"

        # 속공 vs 빌드업 분류
        short_passes = pass_data.get('shortPassSuccess', 0)
        if penetrative_passes > short_passes * 0.15:
            secondary_style = "속공형"
        elif short_passes > penetrative_passes * 5:
            secondary_style = "빌드업형"
        else:
            secondary_style = "혼합형"

        return {
            'primary_style': primary_style,
            'secondary_style': secondary_style,
            'description': style_description,
            'ground_ratio': round(ground_ratio, 1),
            'aerial_ratio': round(aerial_ratio, 1),
            'ground_passes': ground_passes,
            'aerial_passes': aerial_passes,
            'penetrative_passes': penetrative_passes
        }

    @classmethod
    def _calculate_total_stats(cls, pass_data: Dict) -> Dict[str, Any]:
        """전체 패스 통계"""
        total_try = pass_data.get('passTry', 0)
        total_success = pass_data.get('passSuccess', 0)

        return {
            'total_attempts': total_try,
            'total_success': total_success,
            'overall_success_rate': round((total_success / total_try) * 100, 1) if total_try > 0 else 0
        }

    @classmethod
    def _generate_insights(
        cls,
        pass_breakdown: List[Dict],
        diversity_score: int,
        play_style: Dict
    ) -> List[str]:
        """한국어 인사이트 생성"""
        insights = []

        # 1. 플레이 스타일 인사이트
        insights.append(
            f"🎯 {play_style['primary_style']} - {play_style['description']}"
        )

        # 2. 다양성 점수 인사이트
        if diversity_score >= 70:
            insights.append(
                f"✨ 패스 다양성 {diversity_score}점! 다양한 패스로 상대를 혼란시키고 있습니다"
            )
        elif diversity_score < 40:
            insights.append(
                f"⚠️ 패스 다양성 {diversity_score}점. 다양한 패스 타입을 시도해보세요"
            )

        # 3. 성공률 기반 인사이트
        if pass_breakdown:
            # 가장 성공률이 높은 패스 타입
            best_pass = max(pass_breakdown, key=lambda x: x['success_rate'])
            if best_pass['success_rate'] >= 80:
                insights.append(
                    f"🔥 {best_pass['type_name']} 성공률 {best_pass['success_rate']}%! 강점을 더 활용해보세요"
                )

            # 가장 성공률이 낮은 패스 타입
            worst_pass = min(pass_breakdown, key=lambda x: x['success_rate'])
            if worst_pass['success_rate'] < 60 and worst_pass['attempts'] >= 5:
                insights.append(
                    f"💡 {worst_pass['type_name']} 성공률이 {worst_pass['success_rate']}%로 낮습니다. 타이밍과 각도를 조절해보세요"
                )

        # 4. 스루 패스 인사이트
        through_pass = next((p for p in pass_breakdown if p['type_code'] == 'through'), None)
        if through_pass and through_pass['attempts'] >= 3:
            if through_pass['success_rate'] >= 60:
                insights.append(
                    "⚡ 스루 패스 활용이 좋습니다! 수비 뒷공간을 잘 노리고 있습니다"
                )
            else:
                insights.append(
                    "💭 스루 패스 성공률 개선이 필요합니다. 수비수 위치를 더 잘 확인하세요"
                )

        # 5. 플레이 스타일별 추천
        if play_style['primary_style'] == "땅볼 플레이어":
            if play_style['aerial_passes'] < 5:
                insights.append(
                    "📚 가끔 긴 패스를 섞으면 상대 수비를 더 흔들 수 있습니다"
                )
        elif play_style['primary_style'] == "공중볼 플레이어":
            if play_style['ground_passes'] < 10:
                insights.append(
                    "📚 짧은 패스로 템포를 조절하는 것도 좋은 전략입니다"
                )

        return insights
