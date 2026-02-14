"""
Pass Variety Analysis System
Analyzes different types of passes and attacking build-up style
"""
from typing import Dict, Any, List


class PassVarietyAnalyzer:
    """
    Analyzes pass variety and build-up style including:
    - Short vs Long pass ratio
    - Through pass usage
    - Pass type diversity
    - Build-up style classification
    """

    @classmethod
    def analyze_pass_variety(cls, matches_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive pass variety analysis across multiple matches

        Args:
            matches_data: List of match raw_data dictionaries

        Returns:
            Dictionary with pass variety analysis
        """
        # Aggregate pass stats
        total_short_pass_try = 0
        total_short_pass_success = 0
        total_long_pass_try = 0
        total_long_pass_success = 0
        total_through_pass_try = 0
        total_through_pass_success = 0
        total_lobbed_through_try = 0
        total_lobbed_through_success = 0
        total_driven_ground_try = 0
        total_driven_ground_success = 0
        total_pass_try = 0
        total_pass_success = 0
        total_matches = len(matches_data)

        for match_data in matches_data:
            if not match_data or 'matchInfo' not in match_data:
                continue

            # Get user's match info
            match_info = match_data['matchInfo'][0]
            pass_data = match_info.get('pass') or {}  # Handle None case

            # Short passes (handle None values)
            total_short_pass_try += pass_data.get('shortPassTry') or 0
            total_short_pass_success += pass_data.get('shortPassSuccess') or 0

            # Long passes
            total_long_pass_try += pass_data.get('longPassTry') or 0
            total_long_pass_success += pass_data.get('longPassSuccess') or 0

            # Through passes
            total_through_pass_try += pass_data.get('throughPassTry') or 0
            total_through_pass_success += pass_data.get('throughPassSuccess') or 0

            # Lobbed through passes
            total_lobbed_through_try += pass_data.get('lobbedThroughPassTry') or 0
            total_lobbed_through_success += pass_data.get('lobbedThroughPassSuccess') or 0

            # Driven ground passes
            total_driven_ground_try += pass_data.get('drivenGroundPassTry') or 0
            total_driven_ground_success += pass_data.get('drivenGroundPassSuccess') or 0

            # Total
            total_pass_try += pass_data.get('passTry') or 0
            total_pass_success += pass_data.get('passSuccess') or 0

        # Calculate success rates
        short_pass_rate = (total_short_pass_success / total_short_pass_try * 100) if total_short_pass_try > 0 else 0
        long_pass_rate = (total_long_pass_success / total_long_pass_try * 100) if total_long_pass_try > 0 else 0
        through_pass_rate = (total_through_pass_success / total_through_pass_try * 100) if total_through_pass_try > 0 else 0

        # Calculate proportions
        short_pass_ratio = (total_short_pass_try / total_pass_try * 100) if total_pass_try > 0 else 0
        long_pass_ratio = (total_long_pass_try / total_pass_try * 100) if total_pass_try > 0 else 0
        through_pass_ratio = (total_through_pass_try / total_pass_try * 100) if total_pass_try > 0 else 0

        # Calculate diversity index (0-100)
        diversity_index = cls._calculate_diversity_index(
            short_pass_ratio,
            long_pass_ratio,
            through_pass_ratio
        )

        # Determine build-up style
        buildup_style = cls._determine_buildup_style(
            short_pass_ratio,
            long_pass_ratio,
            through_pass_ratio,
            short_pass_rate
        )

        # Generate insights
        insights = cls._generate_pass_insights(
            short_pass_rate,
            long_pass_rate,
            through_pass_rate,
            short_pass_ratio,
            long_pass_ratio,
            buildup_style,
            diversity_index
        )

        return {
            'pass_distribution': {
                'short_passes': {
                    'attempts': total_short_pass_try,
                    'success': total_short_pass_success,
                    'success_rate': round(short_pass_rate, 1),
                    'ratio': round(short_pass_ratio, 1)
                },
                'long_passes': {
                    'attempts': total_long_pass_try,
                    'success': total_long_pass_success,
                    'success_rate': round(long_pass_rate, 1),
                    'ratio': round(long_pass_ratio, 1)
                },
                'through_passes': {
                    'attempts': total_through_pass_try,
                    'success': total_through_pass_success,
                    'success_rate': round(through_pass_rate, 1),
                    'ratio': round(through_pass_ratio, 1)
                }
            },
            'special_passes': {
                'lobbed_through': {
                    'attempts': total_lobbed_through_try,
                    'success': total_lobbed_through_success,
                    'success_rate': round((total_lobbed_through_success / total_lobbed_through_try * 100) if total_lobbed_through_try > 0 else 0, 1)
                },
                'driven_ground': {
                    'attempts': total_driven_ground_try,
                    'success': total_driven_ground_success,
                    'success_rate': round((total_driven_ground_success / total_driven_ground_try * 100) if total_driven_ground_try > 0 else 0, 1)
                }
            },
            'overall': {
                'diversity_index': round(diversity_index, 1),
                'buildup_style': buildup_style,
                'total_passes': total_pass_try,
                'overall_accuracy': round((total_pass_success / total_pass_try * 100) if total_pass_try > 0 else 0, 1),
                'matches_analyzed': total_matches
            },
            'insights': insights
        }

    @classmethod
    def _calculate_diversity_index(cls,
                                   short_ratio: float,
                                   long_ratio: float,
                                   through_ratio: float) -> float:
        """
        Calculate pass diversity index (0-100)
        Higher score = more varied passing game
        """
        # Convert to proportions
        proportions = [short_ratio / 100, long_ratio / 100, through_ratio / 100]

        # Calculate Shannon entropy (normalized to 0-100)
        import math
        entropy = 0
        for p in proportions:
            if p > 0:
                entropy -= p * math.log(p)

        # Normalize to 0-100 (max entropy for 3 categories = log(3) ≈ 1.099)
        max_entropy = math.log(3)
        diversity = (entropy / max_entropy) * 100

        return diversity

    @classmethod
    def _determine_buildup_style(cls,
                                 short_ratio: float,
                                 long_ratio: float,
                                 through_ratio: float,
                                 short_pass_rate: float) -> str:
        """Determine build-up playing style"""
        # Possession-based (high short passes)
        if short_ratio > 70 and short_pass_rate > 85:
            return 'possession_based'

        # Direct play (high long passes)
        elif long_ratio > 30:
            return 'direct_play'

        # Through ball focused
        elif through_ratio > 12:
            return 'penetrative'

        # Balanced
        elif 60 <= short_ratio <= 70 and long_ratio > 15:
            return 'balanced'

        # Conservative
        elif short_ratio > 75 and short_pass_rate < 80:
            return 'conservative'

        else:
            return 'varied'

    @classmethod
    def _generate_pass_insights(cls,
                                short_pass_rate: float,
                                long_pass_rate: float,
                                through_pass_rate: float,
                                short_ratio: float,
                                long_ratio: float,
                                buildup_style: str,
                                diversity_index: float) -> Dict[str, List[str]]:
        """Generate Keep-Stop-Action insights for passing"""
        keep = []
        stop = []
        action_items = []

        # Short pass accuracy
        if short_pass_rate > 88:
            keep.append(f"숏패스 정확도 우수 ({short_pass_rate:.1f}%)")
        elif short_pass_rate < 75:
            action_items.append("숏패스 정확도를 개선하여 안정적인 빌드업을 구축하세요")

        # Long pass accuracy
        if long_pass_rate > 60:
            keep.append(f"롱패스 정확도 양호 ({long_pass_rate:.1f}%)")
        elif long_pass_rate < 40 and long_ratio > 20:
            stop.append(f"롱패스 정확도가 낮습니다 ({long_pass_rate:.1f}%)")
            action_items.append("롱패스 사용을 줄이거나 정확도를 높이는 연습이 필요합니다")

        # Through pass
        if through_pass_rate > 50:
            keep.append(f"스루패스 성공률 우수 ({through_pass_rate:.1f}%)")
            action_items.append("효과적인 스루패스를 더 자주 시도하세요")

        # Build-up style feedback
        if buildup_style == 'possession_based':
            keep.append("안정적인 점유율 기반 플레이")
            action_items.append("가끔 롱패스로 템포를 바꿔 수비를 흔들어보세요")

        elif buildup_style == 'direct_play':
            keep.append("직선적이고 빠른 공격 전개")
            if long_pass_rate < 50:
                stop.append("롱패스 정확도가 전술에 비해 부족합니다")

        elif buildup_style == 'penetrative':
            keep.append("스루패스를 활용한 침투적인 플레이")
            action_items.append("스루패스 실패 시 후속 조치를 준비하세요")

        elif buildup_style == 'conservative':
            stop.append("너무 보수적인 패스 플레이")
            action_items.append("더 과감한 패스로 상대 수비를 무너뜨리세요")

        # Diversity feedback
        if diversity_index < 40:
            stop.append("패스 패턴이 단조롭습니다")
            action_items.append("다양한 패스 타입을 활용하여 예측 불가능한 플레이를 만드세요")
        elif diversity_index > 70:
            keep.append("다양한 패스 타입 활용")

        return {
            'keep': keep,
            'stop': stop,
            'action_items': action_items
        }
