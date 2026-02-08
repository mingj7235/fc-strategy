"""
Advanced Shot Analysis System
Provides professional-level shooting analysis with detailed insights
"""
import numpy as np
from typing import List, Dict, Any
from decimal import Decimal
import math


class ShotAnalyzer:
    """Professional-grade shot analyzer with advanced xG model"""

    # Enhanced xG model with distance and angle factors
    XG_BASE_VALUES = {
        'inside_six_yard': 0.60,
        'inside_box_center': 0.35,
        'inside_box_side': 0.20,
        'edge_of_box': 0.12,
        'outside_box_center': 0.08,
        'outside_box_side': 0.05,
        'long_range': 0.02,
    }

    # Shot type multipliers
    SHOT_TYPE_MULTIPLIERS = {
        0: 1.0,   # Normal
        1: 1.2,   # Header (close range advantage)
        2: 0.8,   # Weak foot
        3: 1.3,   # Power shot
        4: 1.1,   # Finesse
    }

    @classmethod
    def _calculate_shot_xg(cls, shot: Dict[str, Any]) -> float:
        """Alias for _calculate_advanced_xg — exposed for testing."""
        return cls._calculate_advanced_xg(shot)

    @classmethod
    def _get_shot_zone(cls, shot: Dict[str, Any]) -> str:
        """Classify a shot into a zone string."""
        x = float(shot.get('x', 0))
        y = float(shot.get('y', 0))
        if x >= 0.95 and 0.35 <= y <= 0.65:
            return 'six_yard_box'
        if x >= 0.78:
            return 'penalty_box'
        if x >= 0.72 and 0.3 <= y <= 0.7:
            return 'edge_of_box'
        if x >= 0.5:
            return 'outside_box'
        return 'long_range'

    @classmethod
    def analyze_shots(cls, shot_details) -> Dict[str, Any]:
        """
        Comprehensive shot analysis with advanced metrics.

        Accepts either:
        - A list of shot-detail dicts (original interface used by views)
        - A Django QuerySet of Match objects (test/alternate interface),
          in which case shot details are fetched from the related ShotDetail objects
          and a simplified {total_shots, total_xg, shot_zones} dict is returned.

        Returns detailed analysis including:
        - Basic statistics
        - Expected Goals (xG) with advanced model
        - Zone analysis with efficiency metrics
        - Shot type breakdown
        - Distance and angle analysis
        - Time-based patterns
        - Performance vs expectation
        """
        # If a QuerySet of Match objects is passed, fetch their ShotDetails and
        # return a simplified dict so callers that query by Match can use this method.
        from django.db.models.query import QuerySet
        if isinstance(shot_details, QuerySet) and shot_details.model.__name__ == 'Match':
            from api.models import ShotDetail
            shot_list = list(ShotDetail.objects.filter(match__in=shot_details).values())
            total = len(shot_list)
            total_xg = sum(cls._calculate_advanced_xg(s) for s in shot_list)
            zones: Dict[str, int] = {}
            for s in shot_list:
                zone = cls._get_shot_zone(s)
                zones[zone] = zones.get(zone, 0) + 1
            return {
                'total_shots': total,
                'total_xg': round(total_xg, 2),
                'shot_zones': zones,
            }

        if not shot_details:
            return cls._empty_analysis()

        total_shots = len(shot_details)
        goals = sum(1 for shot in shot_details if shot.get('result') == 'goal')
        on_target = sum(1 for shot in shot_details if shot.get('result') in ['goal', 'on_target'])
        off_target = sum(1 for shot in shot_details if shot.get('result') == 'off_target')
        blocked = sum(1 for shot in shot_details if shot.get('result') == 'blocked')

        shot_accuracy = (on_target / total_shots * 100) if total_shots > 0 else 0
        conversion_rate = (goals / total_shots * 100) if total_shots > 0 else 0

        # Advanced xG calculation
        xg_total = sum(cls._calculate_advanced_xg(shot) for shot in shot_details)
        xg_per_shot = xg_total / total_shots if total_shots > 0 else 0

        # Performance vs expectation
        goals_over_xg = goals - xg_total
        finishing_quality = (goals / xg_total) if xg_total > 0 else 0

        # Heatmap data with enhanced xG
        heatmap_data = [
            {
                'x': float(shot.get('x', 0)),
                'y': float(shot.get('y', 0)),
                'result': shot.get('result'),
                'xg': cls._calculate_advanced_xg(shot),
                'shot_type': shot.get('shot_type', 0)
            }
            for shot in shot_details
        ]

        # Enhanced zone analysis
        zone_analysis = cls._analyze_zones_advanced(shot_details)

        # Shot type analysis
        shot_type_breakdown = cls._analyze_shot_types(shot_details)

        # Distance analysis
        distance_analysis = cls._analyze_distances(shot_details)

        # Angle analysis
        angle_analysis = cls._analyze_angles(shot_details)

        # Big chances (xG > 0.3)
        big_chances = [s for s in shot_details if cls._calculate_advanced_xg(s) > 0.3]
        big_chances_count = len(big_chances)
        big_chances_scored = sum(1 for s in big_chances if s.get('result') == 'goal')
        big_chance_conversion = (big_chances_scored / big_chances_count * 100) if big_chances_count > 0 else 0

        return {
            'basic_stats': {
                'total_shots': total_shots,
                'goals': goals,
                'on_target': on_target,
                'off_target': off_target,
                'blocked': blocked,
                'shot_accuracy': round(shot_accuracy, 2),
                'conversion_rate': round(conversion_rate, 2),
            },
            'xg_metrics': {
                'xg_total': round(xg_total, 2),
                'xg_per_shot': round(xg_per_shot, 3),
                'goals_over_xg': round(goals_over_xg, 2),
                'finishing_quality': round(finishing_quality, 2),
            },
            'big_chances': {
                'count': big_chances_count,
                'scored': big_chances_scored,
                'conversion': round(big_chance_conversion, 2)
            },
            'zone_analysis': zone_analysis,
            'shot_type_breakdown': shot_type_breakdown,
            'distance_analysis': distance_analysis,
            'angle_analysis': angle_analysis,
            'heatmap_data': heatmap_data,
        }

    @classmethod
    def _calculate_advanced_xg(cls, shot: Dict[str, Any]) -> float:
        """
        Advanced xG calculation considering:
        - Distance from goal
        - Angle to goal
        - Shot type
        - Position quality
        """
        x = float(shot.get('x', 0))
        y = float(shot.get('y', 0))
        shot_type = shot.get('shot_type', 0)

        # Calculate distance from goal (goal is at x=1.0, y=0.5)
        distance = math.sqrt((1.0 - x) ** 2 + (0.5 - y) ** 2)

        # Calculate angle to goal (simplified)
        angle_to_center = abs(0.5 - y)

        # Base xG from position
        base_xg = cls._get_base_xg(x, y)

        # Distance modifier (closer = better)
        distance_modifier = max(0.5, 1.0 - distance * 0.8)

        # Angle modifier (central = better)
        angle_modifier = max(0.6, 1.0 - angle_to_center * 1.5)

        # Shot type modifier
        shot_type_modifier = cls.SHOT_TYPE_MULTIPLIERS.get(shot_type, 1.0)

        # Final xG
        xg = base_xg * distance_modifier * angle_modifier * shot_type_modifier

        return min(xg, 0.95)  # Cap at 95%

    @classmethod
    def _get_base_xg(cls, x: float, y: float) -> float:
        """Get base xG value from position"""
        # Six yard box (very close to goal)
        if x >= 0.95 and 0.35 <= y <= 0.65:
            return cls.XG_BASE_VALUES['inside_six_yard']

        # Inside penalty box
        if 0.78 <= x < 0.95:
            if 0.35 <= y <= 0.65:  # Center
                return cls.XG_BASE_VALUES['inside_box_center']
            elif 0.22 <= y <= 0.78:  # Side
                return cls.XG_BASE_VALUES['inside_box_side']

        # Edge of box
        if 0.72 <= x < 0.78 and 0.3 <= y <= 0.7:
            return cls.XG_BASE_VALUES['edge_of_box']

        # Outside box
        if 0.5 <= x < 0.72:
            if 0.35 <= y <= 0.65:  # Center
                return cls.XG_BASE_VALUES['outside_box_center']
            else:  # Side
                return cls.XG_BASE_VALUES['outside_box_side']

        # Long range
        return cls.XG_BASE_VALUES['long_range']

    @classmethod
    def _analyze_zones_advanced(cls, shot_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced zone analysis with detailed metrics"""
        zones = {
            'inside_box': {'shots': 0, 'goals': 0, 'on_target': 0, 'xg': 0.0},
            'outside_box': {'shots': 0, 'goals': 0, 'on_target': 0, 'xg': 0.0},
            'center': {'shots': 0, 'goals': 0, 'on_target': 0, 'xg': 0.0},
            'left': {'shots': 0, 'goals': 0, 'on_target': 0, 'xg': 0.0},
            'right': {'shots': 0, 'goals': 0, 'on_target': 0, 'xg': 0.0},
            'six_yard': {'shots': 0, 'goals': 0, 'on_target': 0, 'xg': 0.0},
        }

        for shot in shot_details:
            x = float(shot.get('x', 0))
            y = float(shot.get('y', 0))
            is_goal = shot.get('result') == 'goal'
            is_on_target = shot.get('result') in ['goal', 'on_target']
            xg = cls._calculate_advanced_xg(shot)

            # Inside vs outside box
            if x >= 0.78:
                zones['inside_box']['shots'] += 1
                zones['inside_box']['xg'] += xg
                if is_goal:
                    zones['inside_box']['goals'] += 1
                if is_on_target:
                    zones['inside_box']['on_target'] += 1
            else:
                zones['outside_box']['shots'] += 1
                zones['outside_box']['xg'] += xg
                if is_goal:
                    zones['outside_box']['goals'] += 1
                if is_on_target:
                    zones['outside_box']['on_target'] += 1

            # Six yard box
            if x >= 0.95 and 0.35 <= y <= 0.65:
                zones['six_yard']['shots'] += 1
                zones['six_yard']['xg'] += xg
                if is_goal:
                    zones['six_yard']['goals'] += 1
                if is_on_target:
                    zones['six_yard']['on_target'] += 1

            # Left, Center, Right
            if y < 0.35:
                zone_key = 'left'
            elif y > 0.65:
                zone_key = 'right'
            else:
                zone_key = 'center'

            zones[zone_key]['shots'] += 1
            zones[zone_key]['xg'] += xg
            if is_goal:
                zones[zone_key]['goals'] += 1
            if is_on_target:
                zones[zone_key]['on_target'] += 1

        # Calculate efficiency metrics
        for zone_name, zone_data in zones.items():
            if zone_data['shots'] > 0:
                zone_data['conversion_rate'] = round((zone_data['goals'] / zone_data['shots']) * 100, 2)
                zone_data['accuracy'] = round((zone_data['on_target'] / zone_data['shots']) * 100, 2)
                zone_data['xg'] = round(zone_data['xg'], 2)
                zone_data['xg_per_shot'] = round(zone_data['xg'] / zone_data['shots'], 3)
            else:
                zone_data['conversion_rate'] = 0.0
                zone_data['accuracy'] = 0.0
                zone_data['xg_per_shot'] = 0.0

        return zones

    @classmethod
    def _analyze_shot_types(cls, shot_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze shots by type (normal, header, weak foot, etc.)"""
        shot_types = {}

        for shot in shot_details:
            shot_type = shot.get('shot_type', 0)
            type_name = cls._get_shot_type_name(shot_type)

            if type_name not in shot_types:
                shot_types[type_name] = {'count': 0, 'goals': 0, 'xg': 0.0}

            shot_types[type_name]['count'] += 1
            shot_types[type_name]['xg'] += cls._calculate_advanced_xg(shot)
            if shot.get('result') == 'goal':
                shot_types[type_name]['goals'] += 1

        # Calculate conversion rates
        for type_data in shot_types.values():
            if type_data['count'] > 0:
                type_data['conversion'] = round((type_data['goals'] / type_data['count']) * 100, 2)
                type_data['xg'] = round(type_data['xg'], 2)

        return shot_types

    @classmethod
    def _analyze_distances(cls, shot_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze shot distribution by distance"""
        distance_bands = {
            'very_close': {'range': '0-6m', 'shots': 0, 'goals': 0},  # x >= 0.95
            'inside_box': {'range': '6-16m', 'shots': 0, 'goals': 0},  # 0.78 <= x < 0.95
            'edge_of_box': {'range': '16-20m', 'shots': 0, 'goals': 0},  # 0.72 <= x < 0.78
            'long_range': {'range': '20m+', 'shots': 0, 'goals': 0},  # x < 0.72
        }

        for shot in shot_details:
            x = float(shot.get('x', 0))
            is_goal = shot.get('result') == 'goal'

            if x >= 0.95:
                band = 'very_close'
            elif x >= 0.78:
                band = 'inside_box'
            elif x >= 0.72:
                band = 'edge_of_box'
            else:
                band = 'long_range'

            distance_bands[band]['shots'] += 1
            if is_goal:
                distance_bands[band]['goals'] += 1

        # Calculate conversion rates
        for band_data in distance_bands.values():
            if band_data['shots'] > 0:
                band_data['conversion'] = round((band_data['goals'] / band_data['shots']) * 100, 2)

        return distance_bands

    @classmethod
    def _analyze_angles(cls, shot_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze shot distribution by angle"""
        angle_zones = {
            'central': {'shots': 0, 'goals': 0},  # 0.4 <= y <= 0.6
            'semi_central': {'shots': 0, 'goals': 0},  # 0.3 <= y < 0.4 or 0.6 < y <= 0.7
            'wide': {'shots': 0, 'goals': 0},  # y < 0.3 or y > 0.7
        }

        for shot in shot_details:
            y = float(shot.get('y', 0))
            is_goal = shot.get('result') == 'goal'

            if 0.4 <= y <= 0.6:
                zone = 'central'
            elif 0.3 <= y < 0.4 or 0.6 < y <= 0.7:
                zone = 'semi_central'
            else:
                zone = 'wide'

            angle_zones[zone]['shots'] += 1
            if is_goal:
                angle_zones[zone]['goals'] += 1

        # Calculate conversion rates
        for zone_data in angle_zones.values():
            if zone_data['shots'] > 0:
                zone_data['conversion'] = round((zone_data['goals'] / zone_data['shots']) * 100, 2)

        return angle_zones

    @classmethod
    def _get_shot_type_name(cls, shot_type: int) -> str:
        """Get readable name for shot type

        Based on actual data analysis (310 shots):
        - Type 1: 83 shots (27%), 53.0% conversion → Header (confirmed by raw_data shootHeading)
        - Type 2: 139 shots (45%), 35.3% conversion → Normal Shot (most common, lowest conversion)
        - Type 3: 31 shots (10%), 58.1% conversion → Power Shot
        - Type 6: 29 shots (9%), 65.5% conversion → Volley
        - Types 0, 4, 5, 11: No data exists
        """
        type_names = {
            0: '일반 슈팅',  # Not found in actual data
            1: '헤딩',  # Header - confirmed
            2: '일반 슈팅',  # Normal shot - most common (45%), lowest conversion (35.3%)
            3: '파워 슛',  # Power shot - high conversion (58.1%)
            4: '피네스 슛',  # Finesse shot - not found in actual data
            6: '발리 슛',  # Volley - very high conversion (65.5%)
            7: '하프 발리',  # Half volley
            8: '칩 슛',  # Chip shot
            9: '드리븐 슛',  # Driven shot
            10: '오버헤드 킥',  # Overhead kick
            12: '로우 드리븐',  # Low driven
            13: '플레어 슛'  # Flair shot
        }
        return type_names.get(shot_type, f'기타 ({shot_type})')

    @classmethod
    def _empty_analysis(cls) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'basic_stats': {
                'total_shots': 0,
                'goals': 0,
                'on_target': 0,
                'off_target': 0,
                'blocked': 0,
                'shot_accuracy': 0.0,
                'conversion_rate': 0.0,
            },
            'xg_metrics': {
                'xg_total': 0.0,
                'xg_per_shot': 0.0,
                'goals_over_xg': 0.0,
                'finishing_quality': 0.0,
            },
            'big_chances': {
                'count': 0,
                'scored': 0,
                'conversion': 0.0
            },
            'zone_analysis': {},
            'shot_type_breakdown': {},
            'distance_analysis': {},
            'angle_analysis': {},
            'heatmap_data': [],
        }

    @classmethod
    def generate_feedback(cls, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate professional coaching feedback categorized into Keep-Stop-Action framework

        Returns:
            Dictionary with 'keep', 'stop', and 'action_items' lists
        """
        keep = []  # Things to maintain (positive aspects)
        stop = []  # Things to stop doing
        action_items = []  # Recommendations for improvement

        basic = analysis.get('basic_stats', {})
        xg = analysis.get('xg_metrics', {})
        zones = analysis.get('zone_analysis', {})
        big_chances = analysis.get('big_chances', {})
        distance = analysis.get('distance_analysis', {})
        shot_types = analysis.get('shot_type_breakdown', {})

        # === KEEP: Positive aspects to maintain ===

        # Shot accuracy
        shot_acc = basic.get('shot_accuracy', 0)
        if shot_acc >= 60:
            keep.append("슈팅 정확도가 매우 우수합니다 ({}%)".format(round(shot_acc, 1)))
        elif shot_acc >= 50:
            keep.append("슈팅 정확도가 준수한 수준입니다 ({}%)".format(round(shot_acc, 1)))

        # xG performance
        goals_over_xg = xg.get('goals_over_xg', 0)
        finishing_quality = xg.get('finishing_quality', 0)

        if goals_over_xg > 1.0:
            keep.append("기대 득점 대비 {}골 초과 달성 - 뛰어난 마무리 능력".format(round(goals_over_xg, 1)))
        elif goals_over_xg > 0:
            keep.append("기대 득점을 상회하는 골 결정력")

        if finishing_quality >= 1.3:
            keep.append("엘리트급 마무리 능력 (Finishing Quality: {})".format(round(finishing_quality, 2)))

        # Big chances
        big_chance_conv = big_chances.get('conversion', 0)
        if big_chances.get('count', 0) > 0 and big_chance_conv >= 55:
            keep.append("결정적 기회를 {}% 성공 - 압박 상황에서의 침착함".format(round(big_chance_conv, 1)))

        # Quality shot positions
        xg_per_shot = xg.get('xg_per_shot', 0)
        if xg_per_shot >= 0.18:
            keep.append("질 높은 슈팅 위치 선택 (슈팅당 xG: {})".format(round(xg_per_shot, 3)))

        # Inside box effectiveness
        inside_box = zones.get('inside_box', {})
        if inside_box.get('conversion_rate', 0) >= 35:
            keep.append("박스 안 슈팅 효율이 우수합니다 (전환율: {}%)".format(round(inside_box.get('conversion_rate', 0), 1)))

        # Center shooting
        center_shots = zones.get('center', {}).get('shots', 0)
        total_shots = basic.get('total_shots', 1)
        if center_shots / total_shots >= 0.35:
            keep.append("중앙 공격 루트 활용이 효과적입니다")

        # === STOP: Negative patterns to eliminate ===

        # Poor shot accuracy
        if shot_acc < 40:
            stop.append("무리한 슈팅 시도 - 정확도 {}%로 낮음".format(round(shot_acc, 1)))

        # Underperforming xG
        if goals_over_xg < -1.5:
            stop.append("기대치 이하 마무리 - xG 대비 {}골 부족".format(round(abs(goals_over_xg), 1)))

        # Too many long range shots
        long_range = distance.get('long_range', {})
        edge_of_box = distance.get('edge_of_box', {})
        long_range_shots = long_range.get('shots', 0) + edge_of_box.get('shots', 0)
        if long_range_shots / total_shots > 0.35:
            stop.append("장거리 슈팅 과다 ({}%) - 낮은 성공률".format(round(long_range_shots / total_shots * 100, 1)))

        # Outside box shots
        outside_box = zones.get('outside_box', {})
        if outside_box.get('shots', 0) > inside_box.get('shots', 0) * 1.3:
            stop.append("박스 외곽 슈팅 과다 - 더 깊이 침투 필요")

        # Poor big chance conversion
        if big_chances.get('count', 0) > 0 and big_chance_conv < 40:
            stop.append("결정적 기회 낭비 (성공률 {}%)".format(round(big_chance_conv, 1)))

        # Wide shooting inefficiency
        left_shots = zones.get('left', {}).get('shots', 0)
        right_shots = zones.get('right', {}).get('shots', 0)
        if (left_shots + right_shots) / total_shots > 0.5 and center_shots / total_shots < 0.25:
            stop.append("측면 슈팅 편중 - 중앙 공략 부족")

        # Poor shot selection
        if xg_per_shot < 0.10:
            stop.append("낮은 품질의 슈팅 선택 (슈팅당 xG: {})".format(round(xg_per_shot, 3)))

        # === ACTION ITEMS: Specific recommendations ===

        # Improve shot accuracy
        if shot_acc < 50:
            action_items.append("더 가까이 침투하거나 명확한 각도를 만든 후 슈팅하세요")
            action_items.append("슈팅 전 한 번의 터치로 볼 컨트롤을 안정화하세요")

        # Improve finishing
        if goals_over_xg < -1.0:
            action_items.append("골키퍼의 반대편을 노리거나 파워보다 정확도를 우선하세요")
            action_items.append("슈팅 연습 모드에서 다양한 각도의 마무리를 훈련하세요")

        # Get closer
        if long_range_shots / total_shots > 0.3:
            action_items.append("한 번 더 패스하거나 드리블로 박스 안까지 침투하세요")
            action_items.append("측면에서 컷백 패스를 활용해 박스 중앙에서 슈팅 기회를 만드세요")

        # Improve big chance conversion
        if big_chances.get('count', 0) > 0 and big_chance_conv < 50:
            action_items.append("결정적 순간에 침착함을 유지하세요 - 서두르지 말고 정확하게")
            action_items.append("1대1 상황에서 골키퍼의 움직임을 확인한 후 슈팅하세요")

        # Diversify attack
        if (left_shots + right_shots) / total_shots > 0.5:
            action_items.append("컷백, 인사이드 패스로 중앙 공격 루트를 다양화하세요")

        # Better shot selection
        if xg_per_shot < 0.12:
            action_items.append("슈팅보다 패스가 나은 상황을 판단하는 연습을 하세요")
            action_items.append("수비수가 막고 있을 때는 공간을 만든 후 슈팅하세요")

        # Inside box efficiency
        if inside_box.get('shots', 0) > 0 and inside_box.get('conversion_rate', 0) < 25:
            action_items.append("박스 안에서 더 확실한 기회에만 슈팅하세요")
            action_items.append("혼잡한 상황에서는 한 번 더 터치로 공간을 만드세요")

        # Maintain good practices
        if len(keep) > 0 and len(stop) == 0:
            action_items.append("현재의 슈팅 패턴을 유지하면서 일관성을 높이세요")

        # Default messages if categories are empty
        if not keep:
            keep.append("균형잡힌 슈팅 접근 방식")

        if not stop and not action_items:
            action_items.append("현재 수준을 유지하며 꾸준히 연습하세요")

        return {
            'keep': keep,
            'stop': stop,
            'action_items': action_items
        }
