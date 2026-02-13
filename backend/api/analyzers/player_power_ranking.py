"""
Player Power Ranking System
Comprehensive data-driven player evaluation system
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
import math

from api.analyzers.metrics.form_index import FormIndexCalculator
from api.analyzers.metrics.impact_score import ImpactScoreCalculator
from api.analyzers.position_evaluation_system import PositionEvaluationSystem
from api.analyzers.metrics.position_specific_evaluator import PositionSpecificEvaluator


class PlayerPowerRanking:
    """
    Advanced player evaluation system combining multiple metrics:
    - Form Index: Recent performance trend
    - Impact Score: Match-winning contributions
    - Efficiency Metrics: Goals/assists per action
    - Consistency Rating: Performance variance
    - Position-Specific Ratings: Role-tailored evaluation
    """

    # Position groups for specialized evaluation (Nexon API 기준)
    # 0: GK, 1: SW, 2: RWB, 3: RB, 4: RCB, 5: CB, 6: LCB, 7: LB, 8: LWB, 9: RDM,
    # 10: CDM, 11: LDM, 12: RM, 13: RCM, 14: CM, 15: LCM, 16: LM, 17: RAM,
    # 18: CAM, 19: LAM, 20: RF, 21: CF, 22: LF, 23: RW, 24: RS, 25: ST, 26: LS, 27: LW
    POSITION_GROUPS = {
        'striker': [21, 24, 25, 26],  # CF, RS, ST, LS
        'winger': [20, 22, 23, 27],   # RF, LF, RW, LW
        'midfielder': [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],  # CDM, CM, CAM, WM variants
        'defender': [1, 2, 3, 4, 5, 6, 7, 8],  # SW, WB, FB, CB variants
        'goalkeeper': [0]
    }

    # ---------------------------------------------------------------------------
    # Position group lookup
    # ---------------------------------------------------------------------------
    @classmethod
    def _get_position_group(cls, position: int) -> str:
        """포지션 코드를 그룹 이름으로 변환"""
        for group, positions in cls.POSITION_GROUPS.items():
            if position in positions:
                return group
        return 'midfielder'

    # ---------------------------------------------------------------------------
    # Main entry point
    # ---------------------------------------------------------------------------
    @classmethod
    def calculate_power_ranking(cls,
                                player_performances: List[Dict[str, Any]],
                                match_contexts: Optional[List[Dict[str, Any]]] = None,
                                position: Optional[int] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive power ranking for a player

        Args:
            player_performances: List of recent PlayerPerformance data (last 10 games)
            match_contexts: Optional list of match context data for impact calculation
            position: Player position code for position-specific ratings

        Returns:
            Dictionary with complete power ranking analysis
        """
        if not player_performances:
            return cls._empty_ranking()

        # Determine position group early — drives all downstream weighting
        position_group = cls._get_position_group(position) if position is not None else 'midfielder'

        # Standard form analysis (displayed in API response)
        form_analysis = FormIndexCalculator.calculate_form_index(player_performances)

        # Calculate Impact Score (if context available)
        impact_analysis = None
        if match_contexts and len(match_contexts) == len(player_performances):
            impact_analysis = ImpactScoreCalculator.calculate_average_impact(
                player_performances,
                match_contexts
            )

        # Full efficiency breakdown (for API response)
        efficiency = cls._calculate_efficiency_metrics(player_performances)

        # Calculate Consistency Rating
        consistency = cls._calculate_consistency_rating(player_performances)

        # Position-Specific Rating (via world-class evaluator)
        position_rating = None
        if position is not None:
            position_rating = cls._calculate_position_specific_rating(
                player_performances,
                position
            )

        # ── Position-aware internal scores (used ONLY for power_score calc) ──
        pos_form_score = cls._calculate_position_form_score(player_performances, position_group)
        pos_efficiency_score = cls._calculate_position_efficiency_score(player_performances, position_group)

        # Calculate Overall Power Score with position-aware weighting
        power_score = cls._calculate_overall_power_score(
            pos_form_score,
            pos_efficiency_score,
            consistency,
            impact_analysis,
            position_rating,
            position_group
        )

        # Determine player tier
        tier = cls._assign_tier(power_score)

        # Position-specific radar chart data
        radar_data = cls._generate_radar_data(
            form_analysis,
            efficiency,
            consistency,
            impact_analysis,
            player_performances,
            position_group
        )

        return {
            'power_score': power_score,
            'tier': tier,
            'form_analysis': form_analysis,
            'efficiency_metrics': efficiency,
            'consistency_rating': consistency,
            'impact_analysis': impact_analysis,
            'position_rating': position_rating,
            'radar_data': radar_data,
            'percentile_rank': cls._calculate_percentile_rank(power_score)
        }

    # ---------------------------------------------------------------------------
    # Position-aware form score (used internally for power calculation only)
    # ---------------------------------------------------------------------------
    @classmethod
    def _calculate_position_form_score(cls, performances: List[Dict[str, Any]], position_group: str) -> float:
        """
        포지션별 폼 점수 계산 (0–100)
        골키퍼/수비수는 득점 지표 대신 포지션에 맞는 지표 사용
        """
        num = len(performances)
        if num == 0:
            return 50.0

        # ── 공통 지표 ──
        ratings = [float(p.get('rating', 0)) for p in performances if p.get('rating')]
        avg_rating = sum(ratings) / len(ratings) if ratings else 6.5
        rating_score = max(0.0, min(100.0, (avg_rating - 5.0) / 5.0 * 100))

        total_pass_att = sum(p.get('pass_attempts', 0) for p in performances)
        total_pass_ok = sum(p.get('pass_success', 0) for p in performances)
        pass_accuracy = (total_pass_ok / total_pass_att * 100) if total_pass_att > 0 else 70.0
        pass_score = min(100.0, pass_accuracy * 1.1)

        results = [p.get('match_result') for p in performances]
        win_rate = (results.count('win') / len(results) * 100) if results else 50.0

        if position_group == 'goalkeeper':
            # GK 폼: 평점(60%) + 선방률(20%) + 패스(10%) + 승률(10%)
            saves = sum(p.get('saves') or 0 for p in performances)
            opp_shots = sum(p.get('opponent_shots') or 0 for p in performances)
            save_rate = (saves / opp_shots * 100) if opp_shots > 0 else 70.0
            save_score = min(100.0, save_rate * 1.1)
            return (rating_score * 0.60 + save_score * 0.20
                    + pass_score * 0.10 + win_rate * 0.10)

        elif position_group == 'defender':
            # DEF 폼: 평점(40%) + 태클 성공률(25%) + 패스(20%) + 승률(15%)
            total_tk_att = sum(p.get('tackle_attempts', 0) for p in performances)
            total_tk_ok = sum(p.get('tackle_success', 0) for p in performances)
            tk_rate = (total_tk_ok / total_tk_att * 100) if total_tk_att > 0 else 50.0
            tk_score = min(100.0, tk_rate * 1.1)
            return (rating_score * 0.40 + tk_score * 0.25
                    + pass_score * 0.20 + win_rate * 0.15)

        elif position_group == 'midfielder':
            # CDM/CM 계열은 position_groups에서 'midfielder'로 묶임
            # 평점(35%) + 태클 성공률(15%) + 패스(25%) + G+A(15%) + 승률(10%)
            total_goals = sum(p.get('goals', 0) for p in performances)
            total_assists = sum(p.get('assists', 0) for p in performances)
            ga_per_game = (total_goals + total_assists) / num
            ga_score = min(100.0, ga_per_game * 75)

            total_tk_att = sum(p.get('tackle_attempts', 0) for p in performances)
            total_tk_ok = sum(p.get('tackle_success', 0) for p in performances)
            tk_rate = (total_tk_ok / total_tk_att * 100) if total_tk_att > 0 else 50.0
            tk_score = min(100.0, tk_rate * 1.1)

            return (rating_score * 0.35 + tk_score * 0.15
                    + pass_score * 0.25 + ga_score * 0.15 + win_rate * 0.10)

        elif position_group == 'winger':
            # 윙어: 평점(25%) + 어시스트(25%) + 득점(20%) + 드리블(15%) + 승률(10%) + 패스(5%)
            total_goals = sum(p.get('goals', 0) for p in performances)
            total_assists = sum(p.get('assists', 0) for p in performances)
            goal_score = min(100.0, (total_goals / num) * 80)
            assist_score = min(100.0, (total_assists / num) * 100)
            total_drb_att = sum(p.get('dribble_attempts', 0) for p in performances)
            total_drb_ok = sum(p.get('dribble_success', 0) for p in performances)
            drb_rate = (total_drb_ok / total_drb_att * 100) if total_drb_att > 0 else 50.0
            drb_score = min(100.0, drb_rate * 1.2)
            return (rating_score * 0.25 + assist_score * 0.25 + goal_score * 0.20
                    + drb_score * 0.15 + win_rate * 0.10 + pass_score * 0.05)

        else:  # striker
            # ST: 평점(25%) + 득점(40%) + 어시스트(10%) + 슈팅 정확도(15%) + 승률(10%)
            total_goals = sum(p.get('goals', 0) for p in performances)
            total_assists = sum(p.get('assists', 0) for p in performances)
            total_shots = sum(p.get('shots', 0) for p in performances)
            total_on_target = sum(p.get('shots_on_target', 0) for p in performances)
            goal_score = min(100.0, (total_goals / num) * 70)
            assist_score = min(100.0, (total_assists / num) * 100)
            shot_acc = (total_on_target / total_shots * 100) if total_shots > 0 else 50.0
            shot_acc_score = min(100.0, shot_acc * 1.25)
            return (rating_score * 0.25 + goal_score * 0.40 + assist_score * 0.10
                    + shot_acc_score * 0.15 + win_rate * 0.10)

    # ---------------------------------------------------------------------------
    # Position-aware efficiency score (used internally for power calculation only)
    # ---------------------------------------------------------------------------
    @classmethod
    def _calculate_position_efficiency_score(cls, performances: List[Dict[str, Any]], position_group: str) -> float:
        """
        포지션별 효율성 점수 계산 (0–100)
        GK/수비수는 수비 지표 기반, 공격수는 득점 지표 기반
        """
        num = len(performances)
        if num == 0:
            return 50.0

        if position_group == 'goalkeeper':
            # 선방률(50%) + 클린시트(30%) + 빌드업 패스(20%)
            saves = sum(p.get('saves') or 0 for p in performances)
            opp_shots = sum(p.get('opponent_shots') or 0 for p in performances)
            save_rate = (saves / opp_shots * 100) if opp_shots > 0 else 0.0
            save_score = min(100.0, save_rate * 1.1)

            clean_sheets = sum(1 for p in performances if (p.get('goals_conceded') or 0) == 0)
            cs_rate = clean_sheets / num * 100
            cs_score = min(100.0, cs_rate * 1.5)  # 67% 클린시트 = 100

            total_pa = sum(p.get('pass_attempts', 0) for p in performances)
            total_ps = sum(p.get('pass_success', 0) for p in performances)
            pass_acc = (total_ps / total_pa * 100) if total_pa > 0 else 70.0
            buildup_score = min(100.0, pass_acc * 1.1)

            return save_score * 0.50 + cs_score * 0.30 + buildup_score * 0.20

        elif position_group == 'defender':
            # 수비 액션(50%) + 태클 성공률(30%) + 공중볼(20%)
            def_actions_pg = sum(
                p.get('tackle_success', 0) + p.get('interceptions', 0) + p.get('blocks', 0)
                for p in performances
            ) / num
            def_score = min(100.0, def_actions_pg * 15)  # 6.7/경기 = 100

            total_tk_att = sum(p.get('tackle_attempts', 0) for p in performances)
            total_tk_ok = sum(p.get('tackle_success', 0) for p in performances)
            tk_rate = (total_tk_ok / total_tk_att * 100) if total_tk_att > 0 else 50.0
            tk_score = min(100.0, tk_rate * 1.1)

            aerial_pg = sum(p.get('aerial_success', 0) for p in performances) / num
            aerial_score = min(100.0, aerial_pg * 20)  # 5/경기 = 100

            return def_score * 0.50 + tk_score * 0.30 + aerial_score * 0.20

        elif position_group == 'midfielder':
            # CDM/CM: 태클 성공률(40%) + 패스 정확도(40%) + 키패스(20%)
            total_tk_att = sum(p.get('tackle_attempts', 0) for p in performances)
            total_tk_ok = sum(p.get('tackle_success', 0) for p in performances)
            tk_rate = (total_tk_ok / total_tk_att * 100) if total_tk_att > 0 else 50.0
            tk_score = min(100.0, tk_rate * 1.1)

            total_pa = sum(p.get('pass_attempts', 0) for p in performances)
            total_ps = sum(p.get('pass_success', 0) for p in performances)
            pass_acc = (total_ps / total_pa * 100) if total_pa > 0 else 70.0
            pass_score = min(100.0, pass_acc * 1.1)

            key_passes_pg = sum(p.get('key_passes', 0) for p in performances) / num
            kp_score = min(100.0, key_passes_pg * 33)  # 3/경기 = 100

            return tk_score * 0.40 + pass_score * 0.40 + kp_score * 0.20

        else:
            # Winger / Striker: 기존 공격 지표 기반 효율성
            total_shots = sum(p.get('shots', 0) for p in performances)
            total_goals = sum(p.get('goals', 0) for p in performances)
            total_assists = sum(p.get('assists', 0) for p in performances)
            total_pa = sum(p.get('pass_attempts', 0) for p in performances)
            total_ps = sum(p.get('pass_success', 0) for p in performances)
            total_drb = sum(p.get('dribble_attempts', 0) for p in performances)
            total_drb_ok = sum(p.get('dribble_success', 0) for p in performances)

            goal_conv = (total_goals / total_shots * 100) if total_shots > 0 else 0.0
            pass_acc = (total_ps / total_pa * 100) if total_pa > 0 else 70.0
            drb_rate = (total_drb_ok / total_drb * 100) if total_drb > 0 else 50.0

            conv_score = min(100.0, goal_conv * 2)
            pass_score = min(100.0, pass_acc * 1.1)
            drb_score = min(100.0, drb_rate * 1.25)
            output_score = min(100.0, ((total_goals + total_assists) / num) * 50)

            return (conv_score * 0.25 + pass_score * 0.25
                    + drb_score * 0.15 + output_score * 0.35)

    @classmethod
    def _calculate_efficiency_metrics(cls, performances: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate various efficiency metrics"""
        total_shots = sum(p.get('shots', 0) for p in performances)
        total_goals = sum(p.get('goals', 0) for p in performances)
        total_assists = sum(p.get('assists', 0) for p in performances)
        total_pass_attempts = sum(p.get('pass_attempts', 0) for p in performances)
        total_pass_success = sum(p.get('pass_success', 0) for p in performances)
        total_dribbles = sum(p.get('dribble_attempts', 0) for p in performances)
        total_dribble_success = sum(p.get('dribble_success', 0) for p in performances)

        num_matches = len(performances)

        # Calculate per-game averages
        goals_per_game = total_goals / num_matches if num_matches > 0 else 0
        assists_per_game = total_assists / num_matches if num_matches > 0 else 0

        # Calculate conversion rates
        goal_conversion = (total_goals / total_shots * 100) if total_shots > 0 else 0
        assist_rate = (total_assists / total_pass_attempts * 100) if total_pass_attempts > 0 else 0
        pass_accuracy = (total_pass_success / total_pass_attempts * 100) if total_pass_attempts > 0 else 0
        dribble_success_rate = (total_dribble_success / total_dribbles * 100) if total_dribbles > 0 else 0

        # Calculate efficiency score (0-100)
        efficiency_score = cls._normalize_efficiency(
            goal_conversion,
            pass_accuracy,
            dribble_success_rate,
            goals_per_game,
            assists_per_game
        )

        return {
            'efficiency_score': round(efficiency_score, 1),
            'goals_per_game': round(goals_per_game, 2),
            'assists_per_game': round(assists_per_game, 2),
            'goal_conversion_rate': round(goal_conversion, 1),
            'assist_rate': round(assist_rate, 2),
            'pass_accuracy': round(pass_accuracy, 1),
            'dribble_success_rate': round(dribble_success_rate, 1)
        }

    @classmethod
    def _normalize_efficiency(cls,
                             goal_conversion: float,
                             pass_accuracy: float,
                             dribble_rate: float,
                             goals_pg: float,
                             assists_pg: float) -> float:
        """Normalize efficiency metrics to 0-100 scale"""
        # Weight different components
        conversion_score = min(100, goal_conversion * 2)  # 50% conversion = 100
        passing_score = min(100, pass_accuracy * 1.1)    # 90% accuracy = 99
        dribble_score = min(100, dribble_rate * 1.25)    # 80% success = 100
        output_score = min(100, (goals_pg + assists_pg) * 50)  # 2 G+A/game = 100

        # Weighted average
        return (
            conversion_score * 0.25 +
            passing_score * 0.25 +
            dribble_score * 0.15 +
            output_score * 0.35
        )

    @classmethod
    def _calculate_consistency_rating(cls, performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate consistency metrics"""
        ratings = [float(p.get('rating', 0)) for p in performances if p.get('rating')]

        if len(ratings) < 3:
            return {
                'consistency_score': 50.0,
                'rating_variance': 0.0,
                'grade': 'insufficient_data'
            }

        # Calculate variance and standard deviation
        avg_rating = sum(ratings) / len(ratings)
        variance = sum((r - avg_rating) ** 2 for r in ratings) / len(ratings)
        std_dev = math.sqrt(variance)

        # Lower std_dev = higher consistency
        # Convert to 0-100 scale (inverted)
        consistency_score = max(0, 100 - (std_dev * 40))

        # Assign grade
        if consistency_score >= 85:
            grade = 'very_consistent'
        elif consistency_score >= 70:
            grade = 'consistent'
        elif consistency_score >= 50:
            grade = 'moderate'
        else:
            grade = 'inconsistent'

        return {
            'consistency_score': round(consistency_score, 1),
            'rating_variance': round(variance, 2),
            'standard_deviation': round(std_dev, 2),
            'grade': grade
        }

    @classmethod
    def _calculate_position_specific_rating(cls,
                                           performances: List[Dict[str, Any]],
                                           position: int) -> Dict[str, Any]:
        """
        Calculate position-specific ratings using world-class evaluation system
        세계적인 감독(무리뉴, 클롭, 과르디올라) 수준의 포지션별 전문 평가

        Returns detailed evaluation with:
        - position_score: 0-100 overall position rating
        - breakdown: 모든 핵심 지표별 상세 점수
        - key_strengths: 강점 목록
        - areas_for_improvement: 개선 필요 부분
        """
        return PositionSpecificEvaluator.evaluate_player(performances, position)

    @classmethod
    def _get_position_group(cls, position: int) -> str:
        """Determine position group from position code"""
        for group, positions in cls.POSITION_GROUPS.items():
            if position in positions:
                return group
        return 'unknown'

    @classmethod
    def _rate_striker(cls, performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rate striker-specific attributes"""
        total_goals = sum(p.get('goals', 0) for p in performances)
        total_shots = sum(p.get('shots', 0) for p in performances)
        total_shots_on_target = sum(p.get('shots_on_target', 0) for p in performances)

        num_matches = len(performances)
        goals_per_game = total_goals / num_matches if num_matches > 0 else 0
        shot_accuracy = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0
        conversion = (total_goals / total_shots * 100) if total_shots > 0 else 0

        # Striker rating components
        goal_threat = min(100, goals_per_game * 70)  # 1.4 goals/game = 98
        finishing = min(100, conversion * 2.5)       # 40% conversion = 100
        shot_quality = min(100, shot_accuracy * 1.2) # 83% accuracy = 100

        position_score = (goal_threat * 0.5 + finishing * 0.3 + shot_quality * 0.2)

        strengths = []
        weaknesses = []

        if goals_per_game >= 1.0:
            strengths.append('일류 득점 능력')
        elif goals_per_game < 0.3:
            weaknesses.append('득점력 부족')

        if conversion >= 40:
            strengths.append('뛰어난 마무리')
        elif conversion < 20:
            weaknesses.append('마무리 개선 필요')

        return {
            'position_score': round(position_score, 1),
            'goals_per_game': round(goals_per_game, 2),
            'finishing_ability': round(finishing, 1),
            'shot_quality': round(shot_quality, 1),
            'strengths': strengths,
            'weaknesses': weaknesses
        }

    @classmethod
    def _rate_winger(cls, performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rate winger-specific attributes"""
        total_goals = sum(p.get('goals', 0) for p in performances)
        total_assists = sum(p.get('assists', 0) for p in performances)
        total_dribbles = sum(p.get('dribble_attempts', 0) for p in performances)
        total_dribble_success = sum(p.get('dribble_success', 0) for p in performances)

        num_matches = len(performances)
        goal_contrib = (total_goals + total_assists) / num_matches if num_matches > 0 else 0
        dribble_success = (total_dribble_success / total_dribbles * 100) if total_dribbles > 0 else 0

        # Winger rating
        creativity = min(100, goal_contrib * 50)     # 2 G+A/game = 100
        dribbling = min(100, dribble_success * 1.2)  # 83% success = 100

        position_score = (creativity * 0.6 + dribbling * 0.4)

        strengths = []
        weaknesses = []

        if goal_contrib >= 1.5:
            strengths.append('공격 가담 우수')
        if dribble_success >= 75:
            strengths.append('돌파 능력 탁월')
        elif dribble_success < 50:
            weaknesses.append('돌파력 향상 필요')

        return {
            'position_score': round(position_score, 1),
            'goal_contributions_per_game': round(goal_contrib, 2),
            'dribbling_ability': round(dribbling, 1),
            'strengths': strengths,
            'weaknesses': weaknesses
        }

    @classmethod
    def _rate_midfielder(cls, performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rate midfielder-specific attributes"""
        total_assists = sum(p.get('assists', 0) for p in performances)
        total_pass_attempts = sum(p.get('pass_attempts', 0) for p in performances)
        total_pass_success = sum(p.get('pass_success', 0) for p in performances)
        total_tackles = sum(p.get('tackles', 0) for p in performances)
        total_intercepts = sum(p.get('intercepts', 0) for p in performances)

        num_matches = len(performances)
        assists_per_game = total_assists / num_matches if num_matches > 0 else 0
        pass_accuracy = (total_pass_success / total_pass_attempts * 100) if total_pass_attempts > 0 else 0
        defensive_actions = (total_tackles + total_intercepts) / num_matches if num_matches > 0 else 0

        # Midfielder rating
        playmaking = min(100, assists_per_game * 100)  # 1 assist/game = 100
        passing = min(100, pass_accuracy * 1.1)        # 90% accuracy = 99
        defense = min(100, defensive_actions * 20)     # 5 actions/game = 100

        position_score = (playmaking * 0.4 + passing * 0.4 + defense * 0.2)

        strengths = []
        weaknesses = []

        if pass_accuracy >= 88:
            strengths.append('패스 정확도 우수')
        if assists_per_game >= 0.7:
            strengths.append('창조력 뛰어남')

        return {
            'position_score': round(position_score, 1),
            'playmaking_ability': round(playmaking, 1),
            'passing_ability': round(passing, 1),
            'defensive_contribution': round(defense, 1),
            'strengths': strengths,
            'weaknesses': weaknesses
        }

    @classmethod
    def _rate_defender(cls, performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rate defender-specific attributes"""
        total_tackles = sum(p.get('tackles', 0) for p in performances)
        total_intercepts = sum(p.get('intercepts', 0) for p in performances)
        total_blocks = sum(p.get('blocks', 0) for p in performances)
        total_aerial_attempts = sum(p.get('aerial_attempts', 0) for p in performances)
        total_aerial_success = sum(p.get('aerial_success', 0) for p in performances)

        num_matches = len(performances)
        defensive_actions = (total_tackles + total_intercepts + total_blocks) / num_matches if num_matches > 0 else 0
        aerial_success = (total_aerial_success / total_aerial_attempts * 100) if total_aerial_attempts > 0 else 50

        # Defender rating
        defending = min(100, defensive_actions * 15)   # 6.7 actions/game = 100
        aerial_ability = aerial_success

        position_score = (defending * 0.7 + aerial_ability * 0.3)

        strengths = []
        if defensive_actions >= 6:
            strengths.append('수비 가담 적극적')
        if aerial_success >= 70:
            strengths.append('공중볼 강함')

        return {
            'position_score': round(position_score, 1),
            'defending_ability': round(defending, 1),
            'aerial_ability': round(aerial_ability, 1),
            'strengths': strengths,
            'weaknesses': []
        }

    @classmethod
    def _rate_goalkeeper(cls, performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rate goalkeeper (limited data available)"""
        # Goalkeeper ratings would need saves data from raw_data
        return {
            'position_score': 50.0,
            'strengths': [],
            'weaknesses': []
        }

    @classmethod
    def _calculate_overall_power_score(cls,
                                      pos_form_score: float,
                                      pos_efficiency_score: float,
                                      consistency: Dict[str, Any],
                                      impact: Optional[Dict[str, Any]],
                                      position_rating: Optional[Dict[str, Any]] = None,
                                      position_group: str = 'midfielder') -> float:
        """
        포지션별 가중치가 다른 종합 파워 스코어 (0-100)

        GK/수비: 포지션 평가 비중 극대화 (득점/어시스트 패널티 제거)
        공격형: 공격 효율성 중심
        """
        consistency_score = consistency.get('consistency_score', 50)
        position_score = position_rating.get('position_score', 50) if position_rating else 50

        if position_group == 'goalkeeper':
            # GK: 포지션 평가(65%) + 폼(15%) + 효율성(10%) + 일관성(10%)
            power_score = (
                position_score * 0.65 +
                pos_form_score * 0.15 +
                pos_efficiency_score * 0.10 +
                consistency_score * 0.10
            )

        elif position_group == 'defender':
            # DEF: 포지션 평가(55%) + 폼(25%) + 효율성(10%) + 일관성(10%)
            power_score = (
                position_score * 0.55 +
                pos_form_score * 0.25 +
                pos_efficiency_score * 0.10 +
                consistency_score * 0.10
            )

        elif position_group == 'midfielder':
            # CDM/CM: 포지션 평가(50%) + 폼(25%) + 효율성(15%) + 일관성(10%)
            power_score = (
                position_score * 0.50 +
                pos_form_score * 0.25 +
                pos_efficiency_score * 0.15 +
                consistency_score * 0.10
            )

        else:
            # Winger / Striker — impact 포함 시 더 세밀한 평가
            if impact:
                avg_impact = impact.get('avg_total_impact', 0)
                impact_score = min(100, avg_impact * 3)
                power_score = (
                    position_score * 0.35 +
                    pos_form_score * 0.25 +
                    pos_efficiency_score * 0.20 +
                    impact_score * 0.15 +
                    consistency_score * 0.05
                )
            else:
                power_score = (
                    position_score * 0.40 +
                    pos_form_score * 0.30 +
                    pos_efficiency_score * 0.20 +
                    consistency_score * 0.10
                )

        return round(power_score, 1)

    @classmethod
    def _assign_tier(cls, power_score: float) -> str:
        """
        Assign tier based on power score

        Tier System:
        - SSS (80+): 최고급 - 리그를 지배하는 초일류 선수
        - SS (70-79): 최상급 - 팀의 핵심이자 게임체인저
        - S (60-69): 상급 - 매우 우수하고 안정적인 주전급
        - A (50-59): 우수 - 믿을 수 있는 주전 또는 로테이션 핵심
        - B (40-49): 양호 - 준수한 로테이션 또는 백업 선수
        - C (30-39): 보통 - 기본 이상의 역할 수행
        - D (30 미만): 미흡 - 개선이 필요한 선수
        """
        if power_score >= 80:
            return 'SSS'
        elif power_score >= 70:
            return 'SS'
        elif power_score >= 60:
            return 'S'
        elif power_score >= 50:
            return 'A'
        elif power_score >= 40:
            return 'B'
        elif power_score >= 30:
            return 'C'
        else:
            return 'D'

    @classmethod
    def _generate_radar_data(cls,
                            form: Dict[str, Any],
                            efficiency: Dict[str, Any],
                            consistency: Dict[str, Any],
                            impact: Optional[Dict[str, Any]],
                            performances: Optional[List[Dict[str, Any]]] = None,
                            position_group: str = 'midfielder') -> Dict[str, Any]:
        """
        포지션별 레이더 차트 데이터 생성 (6축)

        values: 각 축의 0-100 점수
        labels: 포지션에 맞는 축 이름 (프론트엔드 표시용)
        """
        form_score = form.get('form_index', 50)
        consistency_score = consistency.get('consistency_score', 50)
        impact_score = min(100, impact.get('avg_total_impact', 0) * 3) if impact else 50

        perf = performances or []
        num = len(perf) if perf else 1

        if position_group == 'goalkeeper':
            saves = sum(p.get('saves') or 0 for p in perf)
            opp_shots = sum(p.get('opponent_shots') or 0 for p in perf)
            save_rate = (saves / opp_shots * 100) if opp_shots > 0 else 0
            save_score = min(100.0, save_rate * 1.1)

            clean_sheets = sum(1 for p in perf if (p.get('goals_conceded') or 0) == 0)
            cs_score = min(100.0, (clean_sheets / num * 100) * 1.5)

            total_pa = sum(p.get('pass_attempts', 0) for p in perf)
            total_ps = sum(p.get('pass_success', 0) for p in perf)
            dist_score = min(100.0, ((total_ps / total_pa * 100) if total_pa > 0 else 70.0) * 1.1)

            aerial_pg = sum(p.get('aerial_success', 0) for p in perf) / num
            aerial_score = min(100.0, aerial_pg * 20)

            return {
                'values': {
                    'save_ability': round(save_score, 1),
                    'clean_sheet': round(cs_score, 1),
                    'distribution': round(dist_score, 1),
                    'aerial': round(aerial_score, 1),
                    'consistency': round(consistency_score, 1),
                    'form': round(form_score, 1),
                },
                'labels': {
                    'save_ability': '선방 능력',
                    'clean_sheet': '클린시트',
                    'distribution': '배급력',
                    'aerial': '공중볼',
                    'consistency': '안정성',
                    'form': '폼',
                }
            }

        elif position_group == 'defender':
            def_actions_pg = sum(
                p.get('tackle_success', 0) + p.get('interceptions', 0) + p.get('blocks', 0)
                for p in perf
            ) / num
            def_score = min(100.0, def_actions_pg * 15)

            total_tk_att = sum(p.get('tackle_attempts', 0) for p in perf)
            total_tk_ok = sum(p.get('tackle_success', 0) for p in perf)
            tk_score = min(100.0, ((total_tk_ok / total_tk_att * 100) if total_tk_att > 0 else 50.0) * 1.1)

            aerial_pg = sum(p.get('aerial_success', 0) for p in perf) / num
            aerial_score = min(100.0, aerial_pg * 20)

            total_pa = sum(p.get('pass_attempts', 0) for p in perf)
            total_ps = sum(p.get('pass_success', 0) for p in perf)
            pass_score = min(100.0, ((total_ps / total_pa * 100) if total_pa > 0 else 70.0) * 1.1)

            fouls_pg = sum(p.get('fouls', 0) for p in perf) / num
            discipline_score = max(0.0, 100.0 - fouls_pg * 15)

            return {
                'values': {
                    'defending': round(def_score, 1),
                    'tackle_rate': round(tk_score, 1),
                    'aerial': round(aerial_score, 1),
                    'passing': round(pass_score, 1),
                    'discipline': round(discipline_score, 1),
                    'consistency': round(consistency_score, 1),
                },
                'labels': {
                    'defending': '수비 액션',
                    'tackle_rate': '태클 성공률',
                    'aerial': '공중볼',
                    'passing': '패스',
                    'discipline': '규율',
                    'consistency': '안정성',
                }
            }

        elif position_group == 'midfielder':
            total_tk_att = sum(p.get('tackle_attempts', 0) for p in perf)
            total_tk_ok = sum(p.get('tackle_success', 0) for p in perf)
            tk_score = min(100.0, ((total_tk_ok / total_tk_att * 100) if total_tk_att > 0 else 50.0) * 1.1)

            total_pa = sum(p.get('pass_attempts', 0) for p in perf)
            total_ps = sum(p.get('pass_success', 0) for p in perf)
            pass_score = min(100.0, ((total_ps / total_pa * 100) if total_pa > 0 else 70.0) * 1.1)

            key_pg = sum(p.get('key_passes', 0) for p in perf) / num
            key_score = min(100.0, key_pg * 33)

            total_goals = sum(p.get('goals', 0) for p in perf)
            total_assists = sum(p.get('assists', 0) for p in perf)
            creativity = min(100.0, ((total_goals + total_assists) / num) * 75)

            return {
                'values': {
                    'ball_winning': round(tk_score, 1),
                    'passing': round(pass_score, 1),
                    'key_passes': round(key_score, 1),
                    'creativity': round(creativity, 1),
                    'consistency': round(consistency_score, 1),
                    'form': round(form_score, 1),
                },
                'labels': {
                    'ball_winning': '볼 탈취',
                    'passing': '패스',
                    'key_passes': '키 패스',
                    'creativity': '창조력',
                    'consistency': '안정성',
                    'form': '폼',
                }
            }

        elif position_group == 'winger':
            total_goals = sum(p.get('goals', 0) for p in perf)
            total_assists = sum(p.get('assists', 0) for p in perf)
            goal_threat = min(100.0, (total_goals / num) * 80)
            creativity = min(100.0, (total_assists / num) * 100)

            total_drb = sum(p.get('dribble_attempts', 0) for p in perf)
            total_drb_ok = sum(p.get('dribble_success', 0) for p in perf)
            drb_score = min(100.0, ((total_drb_ok / total_drb * 100) if total_drb > 0 else 50.0) * 1.2)

            total_pa = sum(p.get('pass_attempts', 0) for p in perf)
            total_ps = sum(p.get('pass_success', 0) for p in perf)
            pass_score = min(100.0, ((total_ps / total_pa * 100) if total_pa > 0 else 70.0) * 1.1)

            return {
                'values': {
                    'goal_threat': round(goal_threat, 1),
                    'creativity': round(creativity, 1),
                    'dribbling': round(drb_score, 1),
                    'passing': round(pass_score, 1),
                    'consistency': round(consistency_score, 1),
                    'form': round(form_score, 1),
                },
                'labels': {
                    'goal_threat': '득점력',
                    'creativity': '창조력',
                    'dribbling': '드리블',
                    'passing': '패스',
                    'consistency': '안정성',
                    'form': '폼',
                }
            }

        else:  # striker
            total_goals = sum(p.get('goals', 0) for p in perf)
            total_shots = sum(p.get('shots', 0) for p in perf)
            total_on_target = sum(p.get('shots_on_target', 0) for p in perf)
            total_assists = sum(p.get('assists', 0) for p in perf)

            goal_threat = min(100.0, (total_goals / num) * 70)
            finishing = min(100.0, ((total_goals / total_shots * 100) if total_shots > 0 else 0) * 2.5)
            shot_quality = min(100.0, ((total_on_target / total_shots * 100) if total_shots > 0 else 50.0) * 1.25)
            link_play = min(100.0, (total_assists / num) * 100)

            return {
                'values': {
                    'goal_threat': round(goal_threat, 1),
                    'finishing': round(finishing, 1),
                    'shot_quality': round(shot_quality, 1),
                    'link_play': round(link_play, 1),
                    'consistency': round(consistency_score, 1),
                    'form': round(form_score, 1),
                },
                'labels': {
                    'goal_threat': '득점력',
                    'finishing': '결정력',
                    'shot_quality': '슈팅 정확도',
                    'link_play': '연계 플레이',
                    'consistency': '안정성',
                    'form': '폼',
                }
            }

    @classmethod
    def _calculate_percentile_rank(cls, power_score: float) -> int:
        """
        Estimate percentile rank (assumes normal distribution)
        This is a simplified estimation; ideally compare against all users
        """
        # Assume mean=65, std_dev=15
        z_score = (power_score - 65) / 15

        # Convert z-score to percentile (simplified)
        if z_score >= 2.0:
            return 98
        elif z_score >= 1.5:
            return 93
        elif z_score >= 1.0:
            return 84
        elif z_score >= 0.5:
            return 69
        elif z_score >= 0.0:
            return 50
        elif z_score >= -0.5:
            return 31
        elif z_score >= -1.0:
            return 16
        else:
            return 5

    @classmethod
    def _empty_ranking(cls) -> Dict[str, Any]:
        """Return empty ranking structure"""
        return {
            'power_score': 0.0,
            'tier': 'N/A',
            'form_analysis': {},
            'efficiency_metrics': {},
            'consistency_rating': {},
            'impact_analysis': None,
            'position_rating': None,
            'radar_data': {},
            'percentile_rank': 0
        }

    @classmethod
    def get_tier_information(cls) -> List[Dict[str, Any]]:
        """
        Get tier system information for display

        Returns:
            List of tier information dictionaries
        """
        return [
            {
                'tier': 'SSS',
                'name': '최고급',
                'score_range': '80+',
                'description': '리그를 지배하는 초일류 선수',
                'characteristics': [
                    '모든 지표에서 최상위권',
                    '경기를 홀로 결정지을 수 있는 능력',
                    '지속적으로 압도적인 퍼포먼스'
                ],
                'color': 'rainbow'  # Special rainbow gradient
            },
            {
                'tier': 'SS',
                'name': '최상급',
                'score_range': '70-79',
                'description': '팀의 핵심이자 게임체인저',
                'characteristics': [
                    '대부분의 지표에서 우수한 성적',
                    '중요한 순간에 경기를 바꿀 수 있음',
                    '팀의 전술적 중심축'
                ],
                'color': 'gold'
            },
            {
                'tier': 'S',
                'name': '상급',
                'score_range': '60-69',
                'description': '매우 우수하고 안정적인 주전급',
                'characteristics': [
                    '높은 수준의 일관성',
                    '주전으로서 믿을 수 있는 성능',
                    '팀 전력의 중요한 부분'
                ],
                'color': 'purple'
            },
            {
                'tier': 'A',
                'name': '우수',
                'score_range': '50-59',
                'description': '믿을 수 있는 주전 또는 로테이션 핵심',
                'characteristics': [
                    '안정적인 플레이',
                    '주전 또는 로테이션 선수로 활용 가능',
                    '특정 영역에서 두각을 나타냄'
                ],
                'color': 'blue'
            },
            {
                'tier': 'B',
                'name': '양호',
                'score_range': '40-49',
                'description': '준수한 로테이션 또는 백업 선수',
                'characteristics': [
                    '기본 이상의 능력',
                    '로테이션이나 특정 상황에서 유용',
                    '발전 가능성 있음'
                ],
                'color': 'green'
            },
            {
                'tier': 'C',
                'name': '보통',
                'score_range': '30-39',
                'description': '기본 이상의 역할 수행',
                'characteristics': [
                    '평균 수준의 퍼포먼스',
                    '백업 또는 후보 선수',
                    '개선이 필요한 부분이 있음'
                ],
                'color': 'yellow'
            },
            {
                'tier': 'D',
                'name': '미흡',
                'score_range': '30 미만',
                'description': '개선이 필요한 선수',
                'characteristics': [
                    '여러 지표에서 낮은 성적',
                    '출전 시간이나 역할 조정 필요',
                    '집중적인 훈련과 개선 필요'
                ],
                'color': 'gray'
            }
        ]
