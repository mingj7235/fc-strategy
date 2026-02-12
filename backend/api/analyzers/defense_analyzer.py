"""
Defense and Pressing Analysis System
Analyzes defensive performance, tackling, blocking, and pressing intensity
"""
from typing import Dict, Any, List


class DefenseAnalyzer:
    """
    Analyzes defensive performance including:
    - Tackle success rate
    - Block success rate
    - Defensive intensity
    - Defensive style classification
    """

    @classmethod
    def analyze_defense(cls, matches_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive defensive analysis across multiple matches

        Args:
            matches_data: List of match raw_data dictionaries

        Returns:
            Dictionary with defensive analysis
        """
        # Aggregate defensive stats
        total_tackle_try = 0
        total_tackle_success = 0
        total_block_try = 0
        total_block_success = 0
        total_matches = len(matches_data)

        for match_data in matches_data:
            if not match_data or 'matchInfo' not in match_data:
                continue

            # Get user's match info
            match_info = match_data['matchInfo'][0]
            defence_data = match_info.get('defence') or {}  # Handle None case

            total_tackle_try += defence_data.get('tackleTry') or 0
            total_tackle_success += defence_data.get('tackleSuccess') or 0
            total_block_try += defence_data.get('blockTry') or 0
            total_block_success += defence_data.get('blockSuccess') or 0

        # Calculate rates
        tackle_success_rate = (total_tackle_success / total_tackle_try * 100) if total_tackle_try > 0 else 0
        block_success_rate = (total_block_success / total_block_try * 100) if total_block_try > 0 else 0

        # Per game averages
        tackles_per_game = total_tackle_try / total_matches if total_matches > 0 else 0
        blocks_per_game = total_block_try / total_matches if total_matches > 0 else 0

        # Calculate defensive intensity (0-100)
        defensive_intensity = cls._calculate_defensive_intensity(
            tackles_per_game,
            blocks_per_game,
            tackle_success_rate
        )

        # Determine defensive style
        defensive_style = cls._determine_defensive_style(
            tackles_per_game,
            tackle_success_rate,
            blocks_per_game
        )

        # Generate insights
        insights = cls._generate_defense_insights(
            tackle_success_rate,
            block_success_rate,
            defensive_intensity,
            defensive_style,
            tackles_per_game
        )

        return {
            'tackle_stats': {
                'total_attempts': total_tackle_try,
                'total_success': total_tackle_success,
                'success_rate': round(tackle_success_rate, 1),
                'per_game': round(tackles_per_game, 1)
            },
            'block_stats': {
                'total_attempts': total_block_try,
                'total_success': total_block_success,
                'success_rate': round(block_success_rate, 1),
                'per_game': round(blocks_per_game, 1)
            },
            'overall': {
                'defensive_intensity': round(defensive_intensity, 1),
                'defensive_style': defensive_style,
                'matches_analyzed': total_matches
            },
            'insights': insights
        }

    @classmethod
    def _calculate_defensive_intensity(cls,
                                       tackles_per_game: float,
                                       blocks_per_game: float,
                                       tackle_success_rate: float) -> float:
        """
        Calculate defensive intensity score (0-100)

        High tackles + high success = aggressive pressing
        High blocks = organized defensive structure
        """
        # Normalize tackles (typical range: 5-25 per game)
        tackle_score = min(100, (tackles_per_game / 20) * 100)

        # Normalize blocks (typical range: 3-15 per game)
        block_score = min(100, (blocks_per_game / 12) * 100)

        # Success rate factor
        efficiency_factor = tackle_success_rate / 100

        # Weighted intensity
        intensity = (tackle_score * 0.5 + block_score * 0.3) * (0.7 + efficiency_factor * 0.3)

        return min(100, intensity)

    @classmethod
    def _determine_defensive_style(cls,
                                   tackles_per_game: float,
                                   tackle_success_rate: float,
                                   blocks_per_game: float) -> str:
        """Determine defensive playing style"""
        # High pressing
        if tackles_per_game > 18:
            if tackle_success_rate > 65:
                return 'aggressive_pressing'
            else:
                return 'risky_pressing'

        # Low pressing, high blocking
        elif tackles_per_game < 12 and blocks_per_game > 8:
            return 'organized_defense'

        # Balanced
        elif 12 <= tackles_per_game <= 18:
            if tackle_success_rate > 60:
                return 'balanced_defense'
            else:
                return 'passive_defense'

        # Very passive
        else:
            return 'passive_defense'

    @classmethod
    def _generate_defense_insights(cls,
                                   tackle_success_rate: float,
                                   block_success_rate: float,
                                   defensive_intensity: float,
                                   defensive_style: str,
                                   tackles_per_game: float) -> Dict[str, List[str]]:
        """Generate Keep-Stop-Action insights for defense"""
        keep = []
        stop = []
        action_items = []

        # Tackle success rate
        if tackle_success_rate > 70:
            keep.append(f"태클 성공률 우수 ({tackle_success_rate:.1f}%)")
        elif tackle_success_rate < 50:
            stop.append(f"태클 성공률이 낮습니다 ({tackle_success_rate:.1f}%)")
            action_items.append("타이밍을 잘 맞춰 태클하세요. 무리한 태클은 파울을 유발합니다")

        # Block success rate
        if block_success_rate > 60:
            keep.append(f"블록 성공률 안정적 ({block_success_rate:.1f}%)")

        # Defensive style feedback
        if defensive_style == 'aggressive_pressing':
            keep.append("공격적인 압박 수비가 효과적입니다")
            action_items.append("높은 수비 라인을 유지하면서 공간을 커버하세요")

        elif defensive_style == 'risky_pressing':
            stop.append("무리한 압박으로 인한 파울과 공간 노출 위험")
            action_items.append("압박 타이밍을 개선하고, 조직적인 수비를 구축하세요")

        elif defensive_style == 'organized_defense':
            keep.append("조직적인 수비 라인 유지")
            action_items.append("역습 전환 속도를 높여 공격 효율을 개선하세요")

        elif defensive_style == 'passive_defense':
            stop.append("너무 소극적인 수비")
            action_items.append("더 적극적으로 볼을 소유하려는 시도가 필요합니다")

        # Intensity feedback
        if defensive_intensity > 75:
            keep.append("높은 수비 강도 유지")
        elif defensive_intensity < 40:
            action_items.append("수비 강도를 높이고 볼 탈취를 더 적극적으로 시도하세요")

        # General recommendations
        if tackles_per_game < 10:
            action_items.append("상대의 공격을 끊기 위한 태클 시도를 늘리세요")

        return {
            'keep': keep,
            'stop': stop,
            'action_items': action_items
        }
