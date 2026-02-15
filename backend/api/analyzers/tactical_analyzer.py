"""
Tactical Insights Analyzer
Provides professional-level tactical analysis and coaching feedback in Korean
"""
from typing import Dict, List
from api.models import Match


class TacticalInsightsAnalyzer:
    """Analyze tactical approach and generate professional insights"""

    @classmethod
    def analyze_tactical_approach(cls, match: Match, shot_details: List[Dict], timeline: Dict) -> Dict:
        """
        Comprehensive tactical analysis

        Args:
            match: Match instance
            shot_details: List of shot detail dictionaries
            timeline: Timeline analysis data

        Returns:
            Dict with tactical insights
        """
        # 1. Attack pattern detection (returns dict for internal use; expose string type)
        attack_pattern_data = cls._detect_attack_pattern(shot_details)
        attack_pattern = attack_pattern_data.get('type', 'balanced')

        # 2. Possession style analysis
        possession_style = cls._analyze_possession_style(match.possession, match.pass_success_rate)

        # 3. Defensive approach
        defensive_approach = cls._analyze_defensive_approach(match)

        # 4. Generate insights (internal methods still receive the full dict)
        insights = cls._generate_insights(match, timeline, attack_pattern_data, possession_style)

        # 5. Tactical recommendations
        recommendations = cls._generate_recommendations(match, attack_pattern_data, possession_style)

        return {
            'attack_pattern': attack_pattern,  # String for external consumers
            'possession_style': possession_style,
            'defensive_approach': defensive_approach,
            'insights': insights,
            'recommendations': recommendations
        }

    @classmethod
    def _detect_attack_pattern(cls, shot_details: List[Dict]) -> Dict:
        """
        Detect attack pattern: wing play vs central penetration

        Returns:
            Dict with pattern type and statistics
        """
        if not shot_details:
            return {
                'type': 'balanced',
                'wing_shots': 0,
                'central_shots': 0,
                'description': '공격 패턴 분석 불가'
            }

        # Classify shots by position (y coordinate)
        # y < 0.25 or y > 0.75: wing
        # 0.35 <= y <= 0.65: central
        wing_shots = sum(1 for s in shot_details if s.get('y', 0.5) < 0.25 or s.get('y', 0.5) > 0.75)
        central_shots = sum(1 for s in shot_details if 0.35 <= s.get('y', 0.5) <= 0.65)
        total_shots = len(shot_details)

        # Determine pattern
        if wing_shots > central_shots * 1.5:
            pattern_type = 'wing_play'
            description = '측면 공격 중심'
        elif central_shots > wing_shots * 1.5:
            pattern_type = 'central_penetration'
            description = '중앙 돌파 중심'
        else:
            pattern_type = 'balanced'
            description = '균형잡힌 공격'

        return {
            'type': pattern_type,
            'wing_shots': wing_shots,
            'central_shots': central_shots,
            'total_shots': total_shots,
            'description': description
        }

    @classmethod
    def _analyze_possession_style(cls, possession: float, pass_success_rate) -> Dict:
        """
        Analyze possession style

        Returns:
            Dict with style type and description
        """
        psr = float(pass_success_rate) if pass_success_rate is not None else 0.0
        if possession >= 60:
            if psr >= 85:
                style_type = 'tiki_taka'
                description = '티키타카 (압도적 점유율 + 높은 패스 정확도)'
            else:
                style_type = 'possession_based'
                description = '점유율 중심 플레이'
        elif possession >= 45:
            style_type = 'balanced'
            description = '균형잡힌 플레이'
        else:
            if psr >= 75:
                style_type = 'counter_attack'
                description = '역습 중심 (낮은 점유율 + 효율적 패스)'
            else:
                style_type = 'direct_play'
                description = '직접적인 플레이'

        return {
            'type': style_type,
            'possession': possession,
            'pass_success_rate': pass_success_rate,
            'description': description
        }

    @classmethod
    def _analyze_defensive_approach(cls, match: Match) -> Dict:
        """
        Analyze defensive approach based on match data

        Returns:
            Dict with defensive style
        """
        # Simple defensive analysis based on possession
        if match.possession >= 55:
            defensive_type = 'high_press'
            description = '높은 압박 수비'
        elif match.possession >= 45:
            defensive_type = 'balanced'
            description = '균형잡힌 수비'
        else:
            defensive_type = 'deep_defense'
            description = '깊은 수비 라인'

        return {
            'type': defensive_type,
            'description': description
        }

    @classmethod
    def _generate_insights(cls, match: Match, timeline: Dict, attack_pattern: Dict, possession_style: Dict) -> List[str]:
        """
        Generate natural language insights in Korean

        Returns:
            List of insight strings
        """
        insights = []

        # Result-based opening
        if match.result == 'win':
            insights.append(f"✅ {match.goals_for}-{match.goals_against} 승리를 거두었습니다!")
        elif match.result == 'draw':
            insights.append(f"⚖️ {match.goals_for}-{match.goals_against} 무승부로 마무리되었습니다.")
        else:
            insights.append(f"❌ {match.goals_for}-{match.goals_against} 패배했습니다.")

        # Possession analysis
        if match.possession >= 65:
            insights.append("🎯 압도적인 점유율로 경기를 지배했습니다")
            if match.result != 'win':
                insights.append("⚠️ 높은 점유율에 비해 골 결정력이 부족했습니다. 슈팅 정확도 개선이 필요합니다")
        elif match.possession >= 55:
            insights.append("✨ 점유율 우위로 경기를 주도했습니다")
        elif match.possession <= 35:
            insights.append("⚡ 낮은 점유율에도 효율적인 플레이를 보여주었습니다")
            if match.result == 'win':
                insights.append("🎯 역습 축구의 교과서를 보여주었습니다!")

        # Shot efficiency
        shot_accuracy = (match.shots_on_target / match.shots * 100) if match.shots > 0 else 0
        if shot_accuracy >= 70:
            insights.append("🎯 슈팅 정확도가 매우 우수합니다! 좋은 위치에서 슈팅을 선택하고 있습니다")
        elif shot_accuracy >= 50:
            insights.append("👍 슈팅 정확도가 준수한 편입니다")
        elif shot_accuracy < 40 and match.shots >= 5:
            insights.append("⚠️ 슈팅 정확도가 낮습니다. 더 가까이 침투하거나 각도를 만든 후 슈팅하세요")

        # Pass success rate
        psr = float(match.pass_success_rate) if match.pass_success_rate is not None else 0.0
        if psr >= 85:
            insights.append("✅ 안정적인 빌드업 플레이를 보여줍니다")
        elif 0 < psr < 70:
            insights.append("⚠️ 패스 정확도 개선이 필요합니다. 짧은 패스로 안전하게 연결하세요")

        # Attack pattern feedback
        if attack_pattern['type'] == 'wing_play':
            insights.append("📊 측면 공격을 적극 활용했습니다. 크로스 대신 컷백 패스도 시도해보세요")
        elif attack_pattern['type'] == 'central_penetration':
            insights.append("📊 중앙 돌파를 선호합니다. 수비가 밀집되면 측면을 활용하는 것도 좋습니다")

        # Timeline-based insights
        if timeline and 'xg_by_period' in timeline:
            first_half_xg = timeline['xg_by_period'].get('first_half', 0)
            second_half_xg = timeline['xg_by_period'].get('second_half', 0)

            if second_half_xg < first_half_xg * 0.6 and first_half_xg > 0.5:
                insights.append("⚠️ 후반전 체력 저하로 공격력이 감소했습니다. 선수 교체 타이밍을 고려하세요")
            elif second_half_xg > first_half_xg * 1.5:
                insights.append("💪 후반전에 더 좋은 기회를 만들어냈습니다. 집중력이 향상되었습니다")

        return insights

    @classmethod
    def _generate_recommendations(cls, match: Match, attack_pattern: Dict, possession_style: Dict) -> List[str]:
        """
        Generate tactical recommendations

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Based on result and performance
        if match.result == 'lose':
            if match.possession < 40:
                recommendations.append("💡 점유율이 낮습니다. 미드필더 숫자를 늘려 경기를 통제하세요")
            if match.shots < 8:
                recommendations.append("💡 슈팅 횟수가 부족합니다. 더 과감하게 슈팅을 시도하세요")

        # Attack pattern recommendations
        if attack_pattern['type'] == 'wing_play' and attack_pattern['central_shots'] < 3:
            recommendations.append("💡 측면 공격만 의존하고 있습니다. 중앙 침투로 수비에 변화를 주세요")
        elif attack_pattern['type'] == 'central_penetration' and attack_pattern['wing_shots'] < 3:
            recommendations.append("💡 중앙만 공략하고 있습니다. 측면 공간을 활용하여 수비를 분산시키세요")

        # Possession style recommendations
        if possession_style['type'] == 'tiki_taka':
            recommendations.append("💡 점유율이 높습니다. 가끔 롱볼이나 스루패스로 리듬 변화를 주세요")
        elif possession_style['type'] == 'direct_play':
            recommendations.append("💡 패스 연결이 부족합니다. 중원에서 짧은 패스로 안정성을 높이세요")

        # Shot efficiency recommendations
        shot_accuracy = (match.shots_on_target / match.shots * 100) if match.shots > 0 else 0
        if shot_accuracy < 40:
            recommendations.append("💡 슈팅 정확도가 낮습니다. 페널티 박스 안으로 더 침투한 후 슈팅하세요")

        # Goals vs xG (if we had xG data)
        if match.shots >= 10 and match.goals_for < 2:
            recommendations.append("💡 슈팅은 많지만 골이 부족합니다. 슈팅 파워와 코스를 개선하세요")

        return recommendations if recommendations else ["👍 전반적으로 좋은 경기를 펼쳤습니다. 현재 전술을 유지하세요"]
