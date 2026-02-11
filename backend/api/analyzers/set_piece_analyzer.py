"""
Set Piece Analysis System
Analyzes free kick, penalty kick, and corner kick efficiency
"""
from typing import Dict, Any, List
from decimal import Decimal


class SetPieceAnalyzer:
    """
    Analyzes set piece performance including:
    - Free kick efficiency
    - Penalty kick conversion rate
    - Set piece dependency
    - Scoring patterns from set pieces
    """

    @classmethod
    def analyze_set_pieces(cls, matches_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive set piece analysis across multiple matches

        Args:
            matches_data: List of match raw_data dictionaries

        Returns:
            Dictionary with set piece analysis
        """
        # Aggregate set piece stats
        total_freekick_shots = 0
        total_freekick_goals = 0
        total_penalty_shots = 0
        total_penalty_goals = 0
        total_heading_shots = 0
        total_heading_goals = 0
        total_goals = 0
        total_shots = 0

        for match_data in matches_data:
            if not match_data or 'matchInfo' not in match_data:
                continue

            # Get user's match info (first item)
            match_info = match_data['matchInfo'][0]
            shoot_data = match_info.get('shoot') or {}  # Handle None case

            # Free kicks (handle None values)
            total_freekick_shots += shoot_data.get('shootFreekick') or 0
            total_freekick_goals += shoot_data.get('goalFreekick') or 0

            # Penalties
            total_penalty_shots += shoot_data.get('shootPenaltyKick') or 0
            total_penalty_goals += shoot_data.get('goalPenaltyKick') or 0

            # Heading (often from corners/crosses)
            total_heading_shots += shoot_data.get('shootHeading') or 0
            total_heading_goals += shoot_data.get('goalHeading') or 0

            # Total
            total_shots += shoot_data.get('shootTotal') or 0
            total_goals += shoot_data.get('goalTotalDisplay') or 0

        # Calculate metrics
        freekick_conversion = (total_freekick_goals / total_freekick_shots * 100) if total_freekick_shots > 0 else 0
        penalty_conversion = (total_penalty_goals / total_penalty_shots * 100) if total_penalty_shots > 0 else 0
        heading_conversion = (total_heading_goals / total_heading_shots * 100) if total_heading_shots > 0 else 0

        # Set piece goals percentage
        set_piece_goals = total_freekick_goals + total_penalty_goals + total_heading_goals
        set_piece_dependency = (set_piece_goals / total_goals * 100) if total_goals > 0 else 0

        # Determine style
        style = cls._determine_set_piece_style(
            freekick_conversion,
            penalty_conversion,
            set_piece_dependency
        )

        # Generate insights
        insights = cls._generate_set_piece_insights(
            freekick_conversion,
            penalty_conversion,
            heading_conversion,
            set_piece_dependency,
            total_freekick_shots,
            total_penalty_shots
        )

        return {
            'freekick_analysis': {
                'shots': total_freekick_shots,
                'goals': total_freekick_goals,
                'conversion_rate': round(freekick_conversion, 1)
            },
            'penalty_analysis': {
                'shots': total_penalty_shots,
                'goals': total_penalty_goals,
                'conversion_rate': round(penalty_conversion, 1)
            },
            'heading_analysis': {
                'shots': total_heading_shots,
                'goals': total_heading_goals,
                'conversion_rate': round(heading_conversion, 1)
            },
            'overall': {
                'set_piece_goals': set_piece_goals,
                'total_goals': total_goals,
                'set_piece_dependency': round(set_piece_dependency, 1),
                'style': style
            },
            'insights': insights
        }

    @classmethod
    def _determine_set_piece_style(cls,
                                   freekick_conv: float,
                                   penalty_conv: float,
                                   dependency: float) -> str:
        """Determine set piece playing style"""
        if dependency > 40:
            return 'set_piece_specialist'
        elif freekick_conv > 20 or penalty_conv > 85:
            return 'efficient_set_pieces'
        elif dependency < 15:
            return 'open_play_focused'
        else:
            return 'balanced'

    @classmethod
    def _generate_set_piece_insights(cls,
                                     freekick_conv: float,
                                     penalty_conv: float,
                                     heading_conv: float,
                                     dependency: float,
                                     freekick_attempts: int,
                                     penalty_attempts: int) -> Dict[str, List[str]]:
        """Generate Keep-Stop-Action insights for set pieces"""
        keep = []
        stop = []
        action_items = []

        # Free kick analysis
        if freekick_conv > 15:
            keep.append(f"프리킥 전환율 우수 ({freekick_conv:.1f}%)")
        elif freekick_conv < 5 and freekick_attempts > 5:
            stop.append("프리킥 성공률이 매우 낮습니다")
            action_items.append("프리킥 연습을 통해 정확도를 높이세요")

        # Penalty analysis
        if penalty_conv >= 80:
            keep.append(f"페널티킥 성공률 안정적 ({penalty_conv:.1f}%)")
        elif penalty_conv < 70 and penalty_attempts > 3:
            stop.append("페널티킥 성공률이 낮습니다")
            action_items.append("페널티킥 주자를 변경하거나 연습하세요")

        # Heading analysis
        if heading_conv > 25:
            keep.append(f"헤딩 슈팅 효율 우수 ({heading_conv:.1f}%)")
            action_items.append("코너킥과 크로스를 더 적극적으로 활용하세요")

        # Set piece dependency
        if dependency > 50:
            stop.append(f"세트피스 의존도가 너무 높습니다 ({dependency:.1f}%)")
            action_items.append("오픈 플레이에서의 득점 능력을 향상시키세요")
        elif dependency < 10:
            action_items.append("세트피스 상황에서 더 많은 기회를 만들어보세요")

        # General recommendations
        if not keep:
            action_items.append("세트피스 훈련에 더 많은 시간을 투자하세요")

        return {
            'keep': keep,
            'stop': stop,
            'action_items': action_items
        }
