"""
Form Index Calculator
Calculates player form based on recent performance (last 5-10 games)
Form Index: 0-100 scale where 100 = peak form, 0 = worst form
"""
from typing import List, Dict, Any
from decimal import Decimal


class FormIndexCalculator:
    """Calculate player form index based on recent performances"""

    # Weights for different metrics (total = 1.0)
    WEIGHTS = {
        'rating': 0.35,      # Player rating is most important
        'goals': 0.25,       # Goal contribution
        'assists': 0.15,     # Assist contribution
        'shot_accuracy': 0.10,  # Shooting efficiency
        'pass_accuracy': 0.10,  # Passing efficiency
        'win_contribution': 0.05  # Team result
    }

    # Rating thresholds for normalization
    RATING_SCALE = {
        'excellent': 8.5,
        'good': 7.5,
        'average': 6.5,
        'poor': 5.5
    }

    @classmethod
    def calculate_form_index(cls, recent_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate form index from recent performances

        Args:
            recent_performances: List of recent PlayerPerformance data (last 5-10 games)
                Each dict should contain: rating, goals, assists, shots, shots_on_target,
                pass_attempts, pass_success, match_result

        Returns:
            Dictionary with:
            - form_index: 0-100 score
            - trend: 'improving', 'declining', 'stable'
            - form_grade: 'excellent', 'good', 'average', 'poor'
            - breakdown: Detailed score breakdown
        """
        if not recent_performances:
            return {
                'form_index': 50.0,
                'trend': 'stable',
                'form_grade': 'average',
                'breakdown': {}
            }

        # Calculate weighted scores for each component
        rating_score = cls._calculate_rating_score(recent_performances)
        goal_score = cls._calculate_goal_score(recent_performances)
        assist_score = cls._calculate_assist_score(recent_performances)
        shot_accuracy_score = cls._calculate_shot_accuracy_score(recent_performances)
        pass_accuracy_score = cls._calculate_pass_accuracy_score(recent_performances)
        win_score = cls._calculate_win_contribution_score(recent_performances)

        # Calculate weighted form index
        form_index = (
            rating_score * cls.WEIGHTS['rating'] +
            goal_score * cls.WEIGHTS['goals'] +
            assist_score * cls.WEIGHTS['assists'] +
            shot_accuracy_score * cls.WEIGHTS['shot_accuracy'] +
            pass_accuracy_score * cls.WEIGHTS['pass_accuracy'] +
            win_score * cls.WEIGHTS['win_contribution']
        )

        # Determine trend by comparing first half vs second half
        trend = cls._calculate_trend(recent_performances)

        # Assign form grade
        form_grade = cls._assign_form_grade(form_index)

        return {
            'form_index': round(form_index, 1),
            'trend': trend,
            'form_grade': form_grade,
            'breakdown': {
                'rating_score': round(rating_score, 1),
                'goal_score': round(goal_score, 1),
                'assist_score': round(assist_score, 1),
                'shot_accuracy_score': round(shot_accuracy_score, 1),
                'pass_accuracy_score': round(pass_accuracy_score, 1),
                'win_score': round(win_score, 1)
            }
        }

    @classmethod
    def _calculate_rating_score(cls, performances: List[Dict[str, Any]]) -> float:
        """Convert average rating to 0-100 score"""
        ratings = [float(p.get('rating', 0)) for p in performances if p.get('rating')]
        if not ratings:
            return 50.0

        avg_rating = sum(ratings) / len(ratings)

        # Normalize to 0-100 scale
        # 10.0 rating = 100, 5.0 rating = 0
        score = ((avg_rating - 5.0) / 5.0) * 100
        return max(0, min(100, score))

    @classmethod
    def _calculate_goal_score(cls, performances: List[Dict[str, Any]]) -> float:
        """Calculate goal contribution score"""
        total_goals = sum(p.get('goals', 0) for p in performances)
        num_matches = len(performances)

        goals_per_game = total_goals / num_matches if num_matches > 0 else 0

        # Excellent: 1+ goals/game = 100
        # Good: 0.5 goals/game = 70
        # Average: 0.25 goals/game = 50
        # Poor: 0 goals/game = 0
        if goals_per_game >= 1.0:
            return 100.0
        elif goals_per_game >= 0.5:
            return 70 + (goals_per_game - 0.5) * 60  # 70-100
        elif goals_per_game >= 0.25:
            return 50 + (goals_per_game - 0.25) * 80  # 50-70
        else:
            return goals_per_game * 200  # 0-50

    @classmethod
    def _calculate_assist_score(cls, performances: List[Dict[str, Any]]) -> float:
        """Calculate assist contribution score"""
        total_assists = sum(p.get('assists', 0) for p in performances)
        num_matches = len(performances)

        assists_per_game = total_assists / num_matches if num_matches > 0 else 0

        # Similar scale to goals but slightly less weighted
        if assists_per_game >= 1.0:
            return 100.0
        elif assists_per_game >= 0.5:
            return 70 + (assists_per_game - 0.5) * 60
        elif assists_per_game >= 0.25:
            return 50 + (assists_per_game - 0.25) * 80
        else:
            return assists_per_game * 200

    @classmethod
    def _calculate_shot_accuracy_score(cls, performances: List[Dict[str, Any]]) -> float:
        """Calculate shooting accuracy score"""
        total_shots = sum(p.get('shots', 0) for p in performances)
        total_on_target = sum(p.get('shots_on_target', 0) for p in performances)

        if total_shots == 0:
            return 50.0  # Neutral if no shots

        accuracy = (total_on_target / total_shots) * 100

        # 80%+ accuracy = 100
        # 60% accuracy = 75
        # 40% accuracy = 50
        # 20% accuracy = 25
        return min(100, accuracy * 1.25)

    @classmethod
    def _calculate_pass_accuracy_score(cls, performances: List[Dict[str, Any]]) -> float:
        """Calculate passing accuracy score"""
        total_attempts = sum(p.get('pass_attempts', 0) for p in performances)
        total_success = sum(p.get('pass_success', 0) for p in performances)

        if total_attempts == 0:
            return 50.0  # Neutral if no passes

        accuracy = (total_success / total_attempts) * 100

        # 90%+ accuracy = 100
        # 80% accuracy = 80
        # 70% accuracy = 60
        # 60% accuracy = 40
        if accuracy >= 90:
            return 100
        elif accuracy >= 70:
            return 40 + (accuracy - 70) * 3  # 40-100
        else:
            return accuracy * 0.57  # 0-40

    @classmethod
    def _calculate_win_contribution_score(cls, performances: List[Dict[str, Any]]) -> float:
        """Calculate score based on team results"""
        results = [p.get('match_result') for p in performances]
        wins = results.count('win')
        total = len(results)

        if total == 0:
            return 50.0

        win_rate = (wins / total) * 100
        return win_rate

    @classmethod
    def _calculate_trend(cls, performances: List[Dict[str, Any]]) -> str:
        """
        Determine if form is improving, declining, or stable
        Compare first half vs second half of recent performances
        """
        if len(performances) < 4:
            return 'stable'

        mid_point = len(performances) // 2
        first_half = performances[:mid_point]
        second_half = performances[mid_point:]

        # Calculate average ratings for each half
        first_avg = sum(float(p.get('rating', 0)) for p in first_half) / len(first_half)
        second_avg = sum(float(p.get('rating', 0)) for p in second_half) / len(second_half)

        difference = second_avg - first_avg

        if difference > 0.5:
            return 'improving'
        elif difference < -0.5:
            return 'declining'
        else:
            return 'stable'

    @classmethod
    def _assign_form_grade(cls, form_index: float) -> str:
        """Assign letter grade based on form index"""
        if form_index >= 85:
            return 'excellent'
        elif form_index >= 70:
            return 'good'
        elif form_index >= 50:
            return 'average'
        else:
            return 'poor'
