"""
Impact Score Calculator
Measures player's impact on match outcome through goals, assists, and key contributions
"""
from typing import List, Dict, Any
from decimal import Decimal


class ImpactScoreCalculator:
    """Calculate player impact score based on match contributions"""

    # Base weights for different contributions
    CONTRIBUTION_WEIGHTS = {
        'goal': 10.0,           # Each goal
        'assist': 7.0,          # Each assist
        'big_chance': 4.0,      # Big chance created (xG > 0.3)
        'shot_on_target': 1.5,  # Each shot on target
        'key_pass': 3.0,        # Pass leading to shot
        'win': 5.0,             # Bonus for winning
        'draw_save': 3.0,       # Bonus for draw in losing position
    }

    # Multipliers for match importance/context
    CONTEXT_MULTIPLIERS = {
        'clutch_goal': 1.5,      # Goal when score is tied or 1 goal behind
        'winning_goal': 1.3,     # Goal that puts team ahead
        'late_goal': 1.2,        # Goal after 75th minute
        'comeback': 1.4,         # Performance when team is losing
    }

    @classmethod
    def calculate_impact_score(cls,
                               performance: Dict[str, Any],
                               match_context: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate comprehensive impact score

        Args:
            performance: Player performance data (goals, assists, shots, etc.)
            match_context: Match context (result, score progression, timing)

        Returns:
            Dictionary with:
            - total_impact: Overall impact score
            - offensive_impact: Attacking contribution
            - creative_impact: Chance creation
            - clutch_impact: Performance in critical moments
            - breakdown: Detailed score components
        """
        # Base contributions
        goals = performance.get('goals', 0)
        assists = performance.get('assists', 0)
        shots_on_target = performance.get('shots_on_target', 0)

        # Calculate base scores
        goal_impact = goals * cls.CONTRIBUTION_WEIGHTS['goal']
        assist_impact = assists * cls.CONTRIBUTION_WEIGHTS['assist']
        shot_impact = shots_on_target * cls.CONTRIBUTION_WEIGHTS['shot_on_target']

        # Apply context multipliers
        goal_impact = cls._apply_context_multipliers(
            goal_impact,
            goals,
            match_context
        )

        # Calculate creative impact (assists + key passes)
        creative_impact = assist_impact
        if 'key_passes' in performance:
            creative_impact += performance['key_passes'] * cls.CONTRIBUTION_WEIGHTS['key_pass']

        # Calculate clutch impact (performance in critical moments)
        clutch_impact = cls._calculate_clutch_impact(performance, match_context)

        # Match result bonus
        result_bonus = cls._calculate_result_bonus(match_context)

        # Total impact score
        total_impact = (
            goal_impact +
            assist_impact +
            shot_impact +
            creative_impact +
            clutch_impact +
            result_bonus
        )

        return {
            'total_impact': round(total_impact, 1),
            'offensive_impact': round(goal_impact + shot_impact, 1),
            'creative_impact': round(creative_impact, 1),
            'clutch_impact': round(clutch_impact, 1),
            'breakdown': {
                'goals': round(goal_impact, 1),
                'assists': round(assist_impact, 1),
                'shots': round(shot_impact, 1),
                'result_bonus': round(result_bonus, 1)
            }
        }

    @classmethod
    def _apply_context_multipliers(cls,
                                   base_score: float,
                                   goals: int,
                                   context: Dict[str, Any]) -> float:
        """Apply context-based multipliers to goal impact"""
        if goals == 0:
            return base_score

        multiplier = 1.0

        # Check for clutch goals (scoring when tied or 1 goal behind)
        if context.get('is_clutch_situation'):
            multiplier *= cls.CONTEXT_MULTIPLIERS['clutch_goal']

        # Check for winning goal (goal that puts team ahead)
        if context.get('is_winning_goal'):
            multiplier *= cls.CONTEXT_MULTIPLIERS['winning_goal']

        # Check for late goal (75+ minute)
        if context.get('has_late_goal'):
            multiplier *= cls.CONTEXT_MULTIPLIERS['late_goal']

        # Check for comeback situation
        if context.get('is_comeback'):
            multiplier *= cls.CONTEXT_MULTIPLIERS['comeback']

        return base_score * multiplier

    @classmethod
    def _calculate_clutch_impact(cls,
                                performance: Dict[str, Any],
                                context: Dict[str, Any]) -> float:
        """Calculate impact in clutch situations (close games, critical moments)"""
        # If match was close (1 goal difference or less at end)
        if context.get('final_goal_difference', 999) <= 1:
            goals = performance.get('goals', 0)
            assists = performance.get('assists', 0)

            # Extra points for contributing in close games
            return (goals + assists) * 2.0

        return 0.0

    @classmethod
    def _calculate_result_bonus(cls, context: Dict[str, Any]) -> float:
        """Calculate bonus based on match result"""
        result = context.get('result', '')

        if result == 'win':
            return cls.CONTRIBUTION_WEIGHTS['win']
        elif result == 'draw' and context.get('was_losing'):
            # Bonus for salvaging a draw from losing position
            return cls.CONTRIBUTION_WEIGHTS['draw_save']

        return 0.0

    @classmethod
    def calculate_average_impact(cls,
                                 performances: List[Dict[str, Any]],
                                 contexts: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate average impact score across multiple matches

        Args:
            performances: List of performance dicts
            contexts: List of match context dicts

        Returns:
            Average impact metrics
        """
        if not performances or len(performances) != len(contexts):
            return {
                'avg_total_impact': 0.0,
                'avg_offensive_impact': 0.0,
                'avg_creative_impact': 0.0,
                'avg_clutch_impact': 0.0
            }

        total_impacts = []
        offensive_impacts = []
        creative_impacts = []
        clutch_impacts = []

        for perf, ctx in zip(performances, contexts):
            impact = cls.calculate_impact_score(perf, ctx)
            total_impacts.append(impact['total_impact'])
            offensive_impacts.append(impact['offensive_impact'])
            creative_impacts.append(impact['creative_impact'])
            clutch_impacts.append(impact['clutch_impact'])

        num_matches = len(performances)

        return {
            'avg_total_impact': round(sum(total_impacts) / num_matches, 1),
            'avg_offensive_impact': round(sum(offensive_impacts) / num_matches, 1),
            'avg_creative_impact': round(sum(creative_impacts) / num_matches, 1),
            'avg_clutch_impact': round(sum(clutch_impacts) / num_matches, 1),
            'consistency': cls._calculate_consistency(total_impacts)
        }

    @classmethod
    def _calculate_consistency(cls, impact_scores: List[float]) -> str:
        """Calculate consistency grade based on variance"""
        if len(impact_scores) < 3:
            return 'insufficient_data'

        avg = sum(impact_scores) / len(impact_scores)
        variance = sum((x - avg) ** 2 for x in impact_scores) / len(impact_scores)
        std_dev = variance ** 0.5

        # Low variance = high consistency
        coefficient_of_variation = (std_dev / avg) if avg > 0 else 999

        if coefficient_of_variation < 0.3:
            return 'very_consistent'
        elif coefficient_of_variation < 0.5:
            return 'consistent'
        elif coefficient_of_variation < 0.7:
            return 'moderate'
        else:
            return 'inconsistent'
