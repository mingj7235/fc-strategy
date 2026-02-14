"""
Shooting Quality Analysis System
Analyzes shooting efficiency by location and type
"""
from typing import Dict, Any, List


class ShootingQualityAnalyzer:
    """
    Analyzes shooting quality including:
    - Inside vs outside box efficiency
    - Heading efficiency
    - Shot type distribution
    - Clinical finishing rating
    """

    @classmethod
    def analyze_shooting_quality(cls, matches_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive shooting quality analysis across multiple matches

        Args:
            matches_data: List of match raw_data dictionaries

        Returns:
            Dictionary with shooting quality analysis
        """
        # Aggregate shooting stats
        total_shots_in_box = 0
        total_goals_in_box = 0
        total_shots_out_box = 0
        total_goals_out_box = 0
        total_heading_shots = 0
        total_heading_goals = 0
        total_shots = 0
        total_goals = 0
        total_effective_shots = 0
        total_matches = len(matches_data)

        for match_data in matches_data:
            if not match_data or 'matchInfo' not in match_data:
                continue

            # Get user's match info
            match_info = match_data['matchInfo'][0]
            shoot_data = match_info.get('shoot') or {}  # Handle None case

            # Inside box (handle None values)
            total_shots_in_box += shoot_data.get('shootInPenalty') or 0
            total_goals_in_box += shoot_data.get('goalInPenalty') or 0

            # Outside box
            total_shots_out_box += shoot_data.get('shootOutPenalty') or 0
            total_goals_out_box += shoot_data.get('goalOutPenalty') or 0

            # Heading
            total_heading_shots += shoot_data.get('shootHeading') or 0
            total_heading_goals += shoot_data.get('goalHeading') or 0

            # Total
            total_shots += shoot_data.get('shootTotal') or 0
            total_goals += shoot_data.get('goalTotalDisplay') or 0
            total_effective_shots += shoot_data.get('effectiveShootTotal') or 0

        # Calculate conversion rates
        inside_box_conversion = (total_goals_in_box / total_shots_in_box * 100) if total_shots_in_box > 0 else 0
        outside_box_conversion = (total_goals_out_box / total_shots_out_box * 100) if total_shots_out_box > 0 else 0
        heading_conversion = (total_heading_goals / total_heading_shots * 100) if total_heading_shots > 0 else 0
        overall_conversion = (total_goals / total_shots * 100) if total_shots > 0 else 0
        shot_on_target_rate = (total_effective_shots / total_shots * 100) if total_shots > 0 else 0

        # Calculate shot distribution
        inside_box_ratio = (total_shots_in_box / total_shots * 100) if total_shots > 0 else 0
        outside_box_ratio = (total_shots_out_box / total_shots * 100) if total_shots > 0 else 0
        heading_ratio = (total_heading_shots / total_shots * 100) if total_shots > 0 else 0

        # Clinical finishing rating (0-100)
        clinical_rating = cls._calculate_clinical_rating(
            inside_box_conversion,
            shot_on_target_rate,
            inside_box_ratio
        )

        # Determine shooting style
        shooting_style = cls._determine_shooting_style(
            inside_box_ratio,
            outside_box_ratio,
            inside_box_conversion,
            outside_box_conversion
        )

        # Generate insights
        insights = cls._generate_shooting_insights(
            inside_box_conversion,
            outside_box_conversion,
            heading_conversion,
            shot_on_target_rate,
            inside_box_ratio,
            outside_box_ratio,
            shooting_style,
            clinical_rating
        )

        return {
            'location_analysis': {
                'inside_box': {
                    'shots': total_shots_in_box,
                    'goals': total_goals_in_box,
                    'conversion_rate': round(inside_box_conversion, 1),
                    'ratio': round(inside_box_ratio, 1)
                },
                'outside_box': {
                    'shots': total_shots_out_box,
                    'goals': total_goals_out_box,
                    'conversion_rate': round(outside_box_conversion, 1),
                    'ratio': round(outside_box_ratio, 1)
                }
            },
            'shot_type_analysis': {
                'heading': {
                    'shots': total_heading_shots,
                    'goals': total_heading_goals,
                    'conversion_rate': round(heading_conversion, 1),
                    'ratio': round(heading_ratio, 1)
                },
                'total_shots': total_shots,
                'effective_shots': total_effective_shots,
                'shot_on_target_rate': round(shot_on_target_rate, 1)
            },
            'overall': {
                'conversion_rate': round(overall_conversion, 1),
                'clinical_rating': round(clinical_rating, 1),
                'shooting_style': shooting_style,
                'shots_per_game': round(total_shots / total_matches, 1),
                'goals_per_game': round(total_goals / total_matches, 2),
                'matches_analyzed': total_matches
            },
            'insights': insights
        }

    @classmethod
    def _calculate_clinical_rating(cls,
                                   inside_conv: float,
                                   shot_on_target: float,
                                   inside_ratio: float) -> float:
        """
        Calculate clinical finishing rating (0-100)

        Factors:
        - Inside box conversion (most important)
        - Shot on target rate
        - Shot selection (inside box ratio)
        """
        # Inside box conversion score (weight: 50%)
        conversion_score = min(100, (inside_conv / 40) * 100)

        # Shot on target score (weight: 30%)
        accuracy_score = min(100, (shot_on_target / 70) * 100)

        # Shot selection score (weight: 20%)
        # Prefer 60-80% inside box (good balance)
        if 60 <= inside_ratio <= 80:
            selection_score = 100
        elif inside_ratio < 60:
            selection_score = (inside_ratio / 60) * 100
        else:
            selection_score = max(0, 100 - (inside_ratio - 80) * 2)

        # Weighted rating
        clinical_rating = (
            conversion_score * 0.5 +
            accuracy_score * 0.3 +
            selection_score * 0.2
        )

        return clinical_rating

    @classmethod
    def _determine_shooting_style(cls,
                                  inside_ratio: float,
                                  outside_ratio: float,
                                  inside_conv: float,
                                  outside_conv: float) -> str:
        """Determine shooting style"""
        # Clinical finisher
        if inside_ratio > 70 and inside_conv > 25:
            return 'clinical_finisher'

        # Long shot specialist
        elif outside_ratio > 40 and outside_conv > 12:
            return 'long_shot_specialist'

        # Volume shooter
        elif inside_ratio < 50:
            return 'volume_shooter'

        # Efficient
        elif inside_ratio > 65 and inside_conv > 20:
            return 'efficient'

        # Needs improvement
        elif inside_conv < 15:
            return 'needs_improvement'

        else:
            return 'balanced'

    @classmethod
    def _generate_shooting_insights(cls,
                                    inside_conv: float,
                                    outside_conv: float,
                                    heading_conv: float,
                                    shot_on_target: float,
                                    inside_ratio: float,
                                    outside_ratio: float,
                                    shooting_style: str,
                                    clinical_rating: float) -> Dict[str, List[str]]:
        """Generate Keep-Stop-Action insights for shooting"""
        keep = []
        stop = []
        action_items = []

        # Inside box conversion
        if inside_conv > 28:
            keep.append(f"박스 안 슈팅 전환율 우수 ({inside_conv:.1f}%)")
        elif inside_conv < 15:
            stop.append(f"박스 안 슈팅 전환율이 낮습니다 ({inside_conv:.1f}%)")
            action_items.append("더 좋은 위치에서 슈팅하거나 마무리 정확도를 높이세요")

        # Shot on target
        if shot_on_target > 65:
            keep.append(f"슈팅 정확도 우수 ({shot_on_target:.1f}%가 유효슈팅)")
        elif shot_on_target < 45:
            stop.append(f"유효슈팅 비율이 낮습니다 ({shot_on_target:.1f}%)")
            action_items.append("무리한 슈팅을 줄이고 더 확실한 찬스에만 슈팅하세요")

        # Shot selection
        if inside_ratio < 50:
            stop.append(f"박스 밖 슈팅 비중이 너무 높습니다 ({outside_ratio:.1f}%)")
            action_items.append("박스 안으로 더 침투하여 슈팅 기회를 만드세요")
        elif inside_ratio > 75:
            keep.append("박스 안에서의 슈팅 비중이 높습니다")

        # Outside box
        if outside_conv > 15:
            keep.append(f"중거리 슈팅 효율 우수 ({outside_conv:.1f}%)")
        elif outside_conv < 5 and outside_ratio > 30:
            stop.append("중거리 슈팅 성공률이 매우 낮습니다")
            action_items.append("중거리 슈팅을 줄이고 박스 안으로 침투하세요")

        # Heading
        if heading_conv > 30:
            keep.append(f"헤딩 마무리 능력 우수 ({heading_conv:.1f}%)")
            action_items.append("크로스와 코너킥을 더 적극 활용하세요")

        # Style feedback
        if shooting_style == 'clinical_finisher':
            keep.append("훌륭한 마무리 능력을 보유하고 있습니다")

        elif shooting_style == 'long_shot_specialist':
            keep.append("중거리 슈팅이 강점입니다")
            action_items.append("박스 안 침투도 병행하여 득점 다양성을 높이세요")

        elif shooting_style == 'volume_shooter':
            stop.append("슈팅 선택이 비효율적입니다")
            action_items.append("질 좋은 찬스를 만들고 더 확실한 순간에 슈팅하세요")

        elif shooting_style == 'needs_improvement':
            action_items.append("마무리 연습에 더 많은 시간을 투자하세요")
            action_items.append("슈팅 타이밍과 파워 조절을 개선하세요")

        # Clinical rating feedback
        if clinical_rating > 75:
            keep.append("뛰어난 골 결정력")
        elif clinical_rating < 45:
            action_items.append("전반적인 슈팅 품질 개선이 필요합니다")

        return {
            'keep': keep,
            'stop': stop,
            'action_items': action_items
        }
