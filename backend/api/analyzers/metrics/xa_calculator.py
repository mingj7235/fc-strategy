"""
xA (Expected Assists) Calculator
Calculates the quality of passes based on the likelihood of resulting in a goal
"""
from typing import Dict, Any
import math


class XACalculator:
    """
    Calculate xA (Expected Assists) for passes

    xA measures the quality of a pass based on:
    - Pass ending location (closer to goal = higher xA)
    - Pass type (through ball, cross, key pass)
    - Defensive pressure
    - Angle to goal
    """

    # Base xA values by zone (similar to xG zones)
    XA_BASE_VALUES = {
        'inside_six_yard': 0.65,
        'inside_box_center': 0.40,
        'inside_box_side': 0.28,
        'edge_of_box': 0.15,
        'outside_box_center': 0.08,
        'outside_box_side': 0.05,
        'midfield': 0.02,
    }

    # Pass type multipliers
    PASS_TYPE_MULTIPLIERS = {
        'through_ball': 1.8,      # Splitting defense
        'cross': 1.3,             # Aerial threat
        'key_pass': 1.5,          # Pass leading to shot
        'progressive': 1.2,       # Forward pass 10m+
        'normal': 1.0,
    }

    @classmethod
    def calculate_xa(cls, pass_data: Dict[str, Any]) -> float:
        """
        Calculate xA for a single pass

        Args:
            pass_data: Dictionary containing:
                - target_x: End location x (0-1, where 1 is opponent goal)
                - target_y: End location y (0-1, where 0.5 is center)
                - pass_type: Type of pass (optional)
                - is_key_pass: Whether pass led to shot (optional)
                - distance: Pass distance in meters (optional)

        Returns:
            xA value (0-1 scale)
        """
        target_x = float(pass_data.get('target_x', 0.5))
        target_y = float(pass_data.get('target_y', 0.5))
        is_key_pass = pass_data.get('is_key_pass', False)
        pass_type = pass_data.get('pass_type', 'normal')

        # Get base xA from target location
        base_xa = cls._get_base_xa(target_x, target_y)

        # Calculate distance from goal
        distance_modifier = cls._calculate_distance_modifier(target_x, target_y)

        # Calculate angle modifier
        angle_modifier = cls._calculate_angle_modifier(target_y)

        # Pass type multiplier
        type_multiplier = cls.PASS_TYPE_MULTIPLIERS.get(pass_type, 1.0)

        # Key pass bonus
        if is_key_pass:
            type_multiplier *= 1.3

        # Calculate final xA
        xa = base_xa * distance_modifier * angle_modifier * type_multiplier

        # Cap at 0.85 (perfect pass still needs finishing)
        return min(xa, 0.85)

    @classmethod
    def _get_base_xa(cls, x: float, y: float) -> float:
        """Get base xA value from target position"""
        # Six yard box (very close to goal)
        if x >= 0.95 and 0.35 <= y <= 0.65:
            return cls.XA_BASE_VALUES['inside_six_yard']

        # Inside penalty box - center
        if 0.78 <= x < 0.95:
            if 0.35 <= y <= 0.65:
                return cls.XA_BASE_VALUES['inside_box_center']
            elif 0.22 <= y <= 0.78:
                return cls.XA_BASE_VALUES['inside_box_side']

        # Edge of box
        if 0.72 <= x < 0.78:
            return cls.XA_BASE_VALUES['edge_of_box']

        # Outside box - attacking third
        if 0.60 <= x < 0.72:
            if 0.30 <= y <= 0.70:
                return cls.XA_BASE_VALUES['outside_box_center']
            else:
                return cls.XA_BASE_VALUES['outside_box_side']

        # Midfield
        return cls.XA_BASE_VALUES['midfield']

    @classmethod
    def _calculate_distance_modifier(cls, x: float, y: float) -> float:
        """
        Modifier based on distance from goal
        Closer = better
        """
        # Distance to goal (goal at x=1.0, y=0.5)
        distance = math.sqrt((1.0 - x) ** 2 + (0.5 - y) ** 2)

        # Convert to modifier (closer = higher)
        # 0 distance = 1.0 modifier
        # 0.5 distance = 0.5 modifier
        modifier = max(0.3, 1.0 - distance * 0.9)
        return modifier

    @classmethod
    def _calculate_angle_modifier(cls, y: float) -> float:
        """
        Modifier based on angle to goal
        Central = better
        """
        # Distance from center line (y=0.5)
        angle_distance = abs(0.5 - y)

        # Central positions are better
        # 0 distance (center) = 1.0 modifier
        # 0.5 distance (touchline) = 0.4 modifier
        modifier = max(0.4, 1.0 - angle_distance * 1.2)
        return modifier

    @classmethod
    def calculate_pass_quality_score(cls, pass_data: Dict[str, Any]) -> str:
        """
        Categorize pass quality based on xA

        Returns:
            Quality grade: 'excellent', 'good', 'average', 'poor'
        """
        xa = cls.calculate_xa(pass_data)

        if xa >= 0.4:
            return 'excellent'
        elif xa >= 0.2:
            return 'good'
        elif xa >= 0.1:
            return 'average'
        else:
            return 'poor'

    @classmethod
    def identify_key_passes(cls, passes: list, shots: list) -> list:
        """
        Identify which passes led to shots (key passes)

        Args:
            passes: List of pass data
            shots: List of shot data

        Returns:
            List of pass indices that are key passes
        """
        key_passes = []

        # For each shot, find if there was a pass nearby in time/location
        for shot in shots:
            shot_x = shot.get('x', 0)
            shot_y = shot.get('y', 0)
            shot_time = shot.get('goal_time', 0)

            # Find passes that ended near this shot location and time
            for i, pass_data in enumerate(passes):
                target_x = pass_data.get('target_x', 0)
                target_y = pass_data.get('target_y', 0)
                pass_time = pass_data.get('time', 0)

                # Check if pass ended near shot location (within 0.1 units)
                distance = math.sqrt((shot_x - target_x) ** 2 + (shot_y - target_y) ** 2)

                # Check if pass happened within 5 seconds before shot
                time_diff = shot_time - pass_time

                if distance < 0.15 and 0 < time_diff < 10:  # 10 seconds window
                    key_passes.append(i)
                    break  # Only count once per shot

        return key_passes
