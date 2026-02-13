"""
Position-Specific Evaluation System
축구 전문가 관점의 포지션별 차별화 평가 시스템
"""
from typing import Dict, List, Any
from decimal import Decimal


class PositionEvaluationSystem:
    """
    20년 경력 축구 전문가 관점의 포지션별 평가 시스템

    각 포지션의 역할과 책임에 맞춘 차별화된 평가 기준:
    - GK: 안정성, 실점 방지
    - 수비수: 수비 지표, 공중볼 경합, 빌드업
    - 미드필더: 포지션별 공수 균형 (CDM, CM, CAM 차별화)
    - 공격수: 득점력, 슈팅 효율, 찬스 메이킹
    """

    # 포지션 그룹 정의 (Nexon API 기준)
    # 0: GK, 1: SW, 2: RWB, 3: RB, 4: RCB, 5: CB, 6: LCB, 7: LB, 8: LWB, 9: RDM,
    # 10: CDM, 11: LDM, 12: RM, 13: RCM, 14: CM, 15: LCM, 16: LM, 17: RAM,
    # 18: CAM, 19: LAM, 20: RF, 21: CF, 22: LF, 23: RW, 24: RS, 25: ST, 26: LS, 27: LW
    POSITION_GROUPS = {
        'GK': [0],  # Goalkeeper
        'CB': [1, 4, 5, 6],  # SW, RCB, CB, LCB
        'FB': [3, 7],  # RB, LB
        'WB': [2, 8],  # RWB, LWB
        'CDM': [9, 10, 11],  # RDM, CDM, LDM
        'CM': [13, 14, 15],  # RCM, CM, LCM
        'CAM': [17, 18, 19],  # RAM, CAM, LAM
        'WM': [12, 16],  # RM, LM
        'W': [20, 22, 23, 27],  # RF, LF, RW, LW
        'ST': [21, 24, 25, 26],  # CF, RS, ST, LS
    }

    # 포지션 그룹별 한글 이름
    POSITION_GROUP_NAMES = {
        'GK': '골키퍼',
        'CB': '센터백',
        'FB': '풀백',
        'WB': '윙백',
        'CDM': '수비형 미드필더',
        'CM': '중앙 미드필더',
        'CAM': '공격형 미드필더',
        'WM': '측면 미드필더',
        'W': '윙어',
        'ST': '스트라이커',
    }

    @classmethod
    def get_position_group(cls, position: int) -> str:
        """포지션 코드에서 포지션 그룹 반환"""
        for group, positions in cls.POSITION_GROUPS.items():
            if position in positions:
                return group
        return 'CM'  # 기본값

    @classmethod
    def get_position_group_name(cls, position: int) -> str:
        """포지션 그룹 한글 이름 반환"""
        group = cls.get_position_group(position)
        return cls.POSITION_GROUP_NAMES.get(group, '미드필더')

    @classmethod
    def evaluate_position_performance(cls,
                                     performances: List[Dict[str, Any]],
                                     position: int) -> Dict[str, Any]:
        """
        포지션별 차별화된 성능 평가

        Args:
            performances: 선수의 최근 경기 성능 데이터
            position: 선수 포지션 코드

        Returns:
            포지션별 평가 결과 (점수, 강점, 약점, 평가 기준)
        """
        position_group = cls.get_position_group(position)

        # 포지션 그룹별 평가 함수 호출
        evaluator = {
            'GK': cls._evaluate_goalkeeper,
            'CB': cls._evaluate_center_back,
            'FB': cls._evaluate_full_back,
            'WB': cls._evaluate_wing_back,
            'CDM': cls._evaluate_defensive_midfielder,
            'CM': cls._evaluate_center_midfielder,
            'CAM': cls._evaluate_attacking_midfielder,
            'WM': cls._evaluate_wide_midfielder,
            'W': cls._evaluate_winger,
            'ST': cls._evaluate_striker,
        }.get(position_group, cls._evaluate_center_midfielder)

        return evaluator(performances, position)

    @classmethod
    def _calculate_averages(cls, performances: List[Dict[str, Any]]) -> Dict[str, float]:
        """경기 평균 지표 계산"""
        if not performances:
            return {}

        total_matches = len(performances)

        # 누적 계산 (원시 데이터만)
        totals = {
            'rating': 0.0,
            'goals': 0,
            'assists': 0,
            'shots': 0,
            'shots_on_target': 0,
            'pass_attempts': 0,
            'pass_success': 0,
            'dribble_attempts': 0,
            'dribble_success': 0,
            'tackles': 0,
            'intercepts': 0,
            'blocks': 0,
            'aerial_attempts': 0,
            'aerial_success': 0,
        }

        for perf in performances:
            for key in totals.keys():
                value = perf.get(key, 0)
                # Decimal, int, float를 모두 float로 변환
                if value is not None and value != '':
                    try:
                        totals[key] += float(value)
                    except (ValueError, TypeError):
                        # 변환 불가능한 값은 무시
                        pass

        # 평균 계산
        averages = {k: v / total_matches for k, v in totals.items()}

        # 성공률 계산
        if totals['shots'] > 0:
            averages['shot_accuracy'] = (totals['shots_on_target'] / totals['shots']) * 100
            averages['shot_conversion'] = (totals['goals'] / totals['shots']) * 100
        else:
            averages['shot_accuracy'] = 0
            averages['shot_conversion'] = 0

        if totals['pass_attempts'] > 0:
            averages['pass_success_rate'] = (totals['pass_success'] / totals['pass_attempts']) * 100
        else:
            averages['pass_success_rate'] = 0

        if totals['dribble_attempts'] > 0:
            averages['dribble_success_rate'] = (totals['dribble_success'] / totals['dribble_attempts']) * 100
        else:
            averages['dribble_success_rate'] = 0

        if totals['aerial_attempts'] > 0:
            averages['aerial_success_rate'] = (totals['aerial_success'] / totals['aerial_attempts']) * 100
        else:
            averages['aerial_success_rate'] = 0

        return averages

    # ============ 포지션별 평가 함수 ============

    @classmethod
    def _evaluate_goalkeeper(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """골키퍼 평가 (GK)"""
        avg = cls._calculate_averages(performances)

        # GK는 rating이 가장 중요
        rating_score = min((avg.get('rating', 0) / 10.0) * 100, 100)

        # 안정성 (rating 분산도 - 낮을수록 좋음)
        ratings = [float(p.get('rating', 0)) for p in performances]
        rating_variance = sum((r - avg['rating']) ** 2 for r in ratings) / len(ratings) if ratings else 0
        consistency_score = max(0, 100 - (rating_variance * 20))  # 분산이 낮을수록 높은 점수

        # 최종 점수 (GK는 rating과 안정성 중심)
        position_score = (
            rating_score * 0.85 +  # Rating이 85% 차지
            consistency_score * 0.15  # 안정성 15%
        )

        # 강점/약점 분석
        strengths = []
        weaknesses = []

        if avg['rating'] >= 7.5:
            strengths.append("뛰어난 평점 유지")
        elif avg['rating'] < 6.5:
            weaknesses.append("평점 개선 필요")

        if rating_variance < 0.5:
            strengths.append("안정적인 퍼포먼스")
        elif rating_variance > 1.0:
            weaknesses.append("기복이 심한 편")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'GK',
            'position_group_name': '골키퍼',
            'key_metrics': {
                '평균 평점': round(avg['rating'], 2),
                '안정성': round(consistency_score, 1),
            },
            'strengths': strengths if strengths else ["평균적인 퍼포먼스"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '평점': '85%',
                '안정성': '15%',
            }
        }

    @classmethod
    def _evaluate_center_back(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """센터백 평가 (CB)"""
        avg = cls._calculate_averages(performances)

        # 수비 지표 점수 (50%)
        tackles_score = min((avg.get('tackles', 0) / 5.0) * 100, 100)
        intercepts_score = min((avg.get('intercepts', 0) / 4.0) * 100, 100)
        blocks_score = min((avg.get('blocks', 0) / 3.0) * 100, 100)
        defensive_score = (tackles_score * 0.4 + intercepts_score * 0.35 + blocks_score * 0.25)

        # 공중볼 경합 (25%)
        aerial_score = min(avg.get('aerial_success_rate', 0), 100)

        # 빌드업 능력 (15%)
        buildup_score = min(avg.get('pass_success_rate', 0), 100)

        # 안정성 (10%)
        rating_score = min((avg.get('rating', 0) / 10.0) * 100, 100)

        # 최종 점수
        position_score = (
            defensive_score * 0.50 +
            aerial_score * 0.25 +
            buildup_score * 0.15 +
            rating_score * 0.10
        )

        # 강점/약점
        strengths = []
        weaknesses = []

        if avg['tackles'] >= 4.0:
            strengths.append("적극적인 태클")
        if avg['intercepts'] >= 3.0:
            strengths.append("뛰어난 인터셉트")
        if avg.get('aerial_success_rate', 0) >= 70:
            strengths.append("강력한 공중볼 경합")
        if avg.get('pass_success_rate', 0) >= 85:
            strengths.append("안정적인 빌드업")

        if avg['tackles'] < 2.0:
            weaknesses.append("태클 빈도 부족")
        if avg.get('aerial_success_rate', 0) < 50:
            weaknesses.append("공중볼 경합 개선 필요")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'CB',
            'position_group_name': '센터백',
            'key_metrics': {
                '경기당 태클': round(avg['tackles'], 1),
                '경기당 인터셉트': round(avg['intercepts'], 1),
                '경기당 블록': round(avg['blocks'], 1),
                '공중볼 성공률': f"{round(avg.get('aerial_success_rate', 0), 1)}%",
                '패스 성공률': f"{round(avg.get('pass_success_rate', 0), 1)}%",
            },
            'strengths': strengths if strengths else ["평균적인 수비력"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '수비 지표': '50% (태클, 인터셉트, 블록)',
                '공중볼 경합': '25%',
                '빌드업': '15%',
                '안정성': '10%',
            }
        }

    @classmethod
    def _evaluate_full_back(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """풀백 평가 (FB - RB, LB)"""
        avg = cls._calculate_averages(performances)

        # 수비 지표 (40%)
        tackles_score = min((avg.get('tackles', 0) / 4.0) * 100, 100)
        intercepts_score = min((avg.get('intercepts', 0) / 3.0) * 100, 100)
        defensive_score = (tackles_score * 0.6 + intercepts_score * 0.4)

        # 공격 기여 (30%)
        assists_score = min((avg.get('assists', 0) / 0.3) * 100, 100)
        pass_score = min(avg.get('pass_success_rate', 0), 100)
        dribble_score = min(avg.get('dribble_success_rate', 0), 100)
        offensive_score = (assists_score * 0.4 + pass_score * 0.35 + dribble_score * 0.25)

        # 활동량 (20%)
        total_actions = avg.get('tackles', 0) + avg.get('dribble_attempts', 0) + avg.get('pass_attempts', 0) / 10.0
        activity_score = min((total_actions / 15.0) * 100, 100)

        # 안정성 (10%)
        rating_score = min((avg.get('rating', 0) / 10.0) * 100, 100)

        # 최종 점수
        position_score = (
            defensive_score * 0.40 +
            offensive_score * 0.30 +
            activity_score * 0.20 +
            rating_score * 0.10
        )

        strengths = []
        weaknesses = []

        if avg['tackles'] >= 3.5:
            strengths.append("강력한 수비력")
        if avg['assists'] >= 0.25:
            strengths.append("우수한 공격 지원")
        if avg.get('dribble_success_rate', 0) >= 70:
            strengths.append("효과적인 측면 돌파")

        if avg['tackles'] < 2.0:
            weaknesses.append("수비 기여도 부족")
        if avg['assists'] < 0.1:
            weaknesses.append("공격 가담 필요")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'FB',
            'position_group_name': '풀백',
            'key_metrics': {
                '경기당 태클': round(avg['tackles'], 1),
                '경기당 어시스트': round(avg['assists'], 2),
                '드리블 성공률': f"{round(avg.get('dribble_success_rate', 0), 1)}%",
                '패스 성공률': f"{round(avg.get('pass_success_rate', 0), 1)}%",
            },
            'strengths': strengths if strengths else ["균형잡힌 공수"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '수비 지표': '40%',
                '공격 기여': '30%',
                '활동량': '20%',
                '안정성': '10%',
            }
        }

    @classmethod
    def _evaluate_wing_back(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """윙백 평가 (WB - RWB, LWB)"""
        avg = cls._calculate_averages(performances)

        # 공격 기여 (45%) - 풀백보다 높음
        assists_score = min((avg.get('assists', 0) / 0.4) * 100, 100)
        dribble_score = min(avg.get('dribble_success_rate', 0), 100)
        shots_score = min((avg.get('shots', 0) / 2.0) * 100, 100)
        offensive_score = (assists_score * 0.5 + dribble_score * 0.3 + shots_score * 0.2)

        # 수비 지표 (30%)
        tackles_score = min((avg.get('tackles', 0) / 3.5) * 100, 100)
        intercepts_score = min((avg.get('intercepts', 0) / 2.5) * 100, 100)
        defensive_score = (tackles_score * 0.6 + intercepts_score * 0.4)

        # 활동량 (15%)
        total_actions = avg.get('dribble_attempts', 0) + avg.get('tackles', 0) * 1.5 + avg.get('pass_attempts', 0) / 10.0
        activity_score = min((total_actions / 18.0) * 100, 100)

        # 패스 정확도 (10%)
        pass_score = min(avg.get('pass_success_rate', 0), 100)

        position_score = (
            offensive_score * 0.45 +
            defensive_score * 0.30 +
            activity_score * 0.15 +
            pass_score * 0.10
        )

        strengths = []
        weaknesses = []

        if avg['assists'] >= 0.3:
            strengths.append("탁월한 공격 가담")
        if avg.get('dribble_success_rate', 0) >= 70:
            strengths.append("효과적인 측면 돌파")
        if avg['tackles'] >= 3.0:
            strengths.append("적극적인 수비 복귀")

        if avg['assists'] < 0.15:
            weaknesses.append("공격 기여도 향상 필요")
        if avg['tackles'] < 2.0:
            weaknesses.append("수비 기여도 부족")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'WB',
            'position_group_name': '윙백',
            'key_metrics': {
                '경기당 어시스트': round(avg['assists'], 2),
                '드리블 성공률': f"{round(avg.get('dribble_success_rate', 0), 1)}%",
                '경기당 태클': round(avg['tackles'], 1),
                '경기당 슈팅': round(avg['shots'], 1),
            },
            'strengths': strengths if strengths else ["공수 겸비"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '공격 기여': '45%',
                '수비 지표': '30%',
                '활동량': '15%',
                '패스 정확도': '10%',
            }
        }

    @classmethod
    def _evaluate_defensive_midfielder(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """수비형 미드필더 평가 (CDM)"""
        avg = cls._calculate_averages(performances)

        # 수비 지표 (45%)
        tackles_score = min((avg.get('tackles', 0) / 4.5) * 100, 100)
        intercepts_score = min((avg.get('intercepts', 0) / 3.5) * 100, 100)
        blocks_score = min((avg.get('blocks', 0) / 2.0) * 100, 100)
        defensive_score = (tackles_score * 0.45 + intercepts_score * 0.35 + blocks_score * 0.20)

        # 패스 정확도 (30%)
        pass_accuracy_score = min(avg.get('pass_success_rate', 0), 100)

        # 볼 순환 (15%)
        pass_volume_score = min((avg.get('pass_attempts', 0) / 50.0) * 100, 100)

        # 안정성 (10%)
        rating_score = min((avg.get('rating', 0) / 10.0) * 100, 100)

        position_score = (
            defensive_score * 0.45 +
            pass_accuracy_score * 0.30 +
            pass_volume_score * 0.15 +
            rating_score * 0.10
        )

        strengths = []
        weaknesses = []

        if avg['intercepts'] >= 3.0:
            strengths.append("탁월한 공격 차단")
        if avg.get('pass_success_rate', 0) >= 88:
            strengths.append("안정적인 볼 배급")
        if avg['tackles'] >= 4.0:
            strengths.append("적극적인 볼 탈취")

        if avg['tackles'] < 2.5:
            weaknesses.append("볼 탈취 빈도 향상 필요")
        if avg.get('pass_success_rate', 0) < 80:
            weaknesses.append("패스 정확도 개선 필요")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'CDM',
            'position_group_name': '수비형 미드필더',
            'key_metrics': {
                '경기당 태클': round(avg['tackles'], 1),
                '경기당 인터셉트': round(avg['intercepts'], 1),
                '패스 성공률': f"{round(avg.get('pass_success_rate', 0), 1)}%",
                '경기당 패스 시도': round(avg['pass_attempts'], 0),
            },
            'strengths': strengths if strengths else ["수비적 안정감"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '수비 지표': '45%',
                '패스 정확도': '30%',
                '볼 순환': '15%',
                '안정성': '10%',
            }
        }

    @classmethod
    def _evaluate_center_midfielder(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """중앙 미드필더 평가 (CM)"""
        avg = cls._calculate_averages(performances)

        # 패스 플레이 (35%)
        pass_accuracy_score = min(avg.get('pass_success_rate', 0), 100)
        pass_volume_score = min((avg.get('pass_attempts', 0) / 45.0) * 100, 100)
        passing_score = (pass_accuracy_score * 0.6 + pass_volume_score * 0.4)

        # 공격 기여 (30%)
        assists_score = min((avg.get('assists', 0) / 0.35) * 100, 100)
        goals_score = min((avg.get('goals', 0) / 0.25) * 100, 100)
        shots_score = min((avg.get('shots', 0) / 2.5) * 100, 100)
        offensive_score = (assists_score * 0.45 + goals_score * 0.35 + shots_score * 0.20)

        # 수비 기여 (20%)
        tackles_score = min((avg.get('tackles', 0) / 3.0) * 100, 100)
        intercepts_score = min((avg.get('intercepts', 0) / 2.0) * 100, 100)
        defensive_score = (tackles_score * 0.6 + intercepts_score * 0.4)

        # 드리블 (15%)
        dribble_score = min(avg.get('dribble_success_rate', 0), 100)

        position_score = (
            passing_score * 0.35 +
            offensive_score * 0.30 +
            defensive_score * 0.20 +
            dribble_score * 0.15
        )

        strengths = []
        weaknesses = []

        if avg.get('pass_success_rate', 0) >= 88:
            strengths.append("정확한 패스 플레이")
        if avg['assists'] >= 0.3:
            strengths.append("우수한 찬스 메이킹")
        if avg['goals'] >= 0.2:
            strengths.append("득점 가담 능력")
        if avg['tackles'] >= 2.5:
            strengths.append("균형잡힌 수비 기여")

        if avg.get('pass_success_rate', 0) < 80:
            weaknesses.append("패스 정확도 향상 필요")
        if avg['assists'] < 0.1:
            weaknesses.append("어시스트 기여도 부족")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'CM',
            'position_group_name': '중앙 미드필더',
            'key_metrics': {
                '패스 성공률': f"{round(avg.get('pass_success_rate', 0), 1)}%",
                '경기당 어시스트': round(avg['assists'], 2),
                '경기당 골': round(avg['goals'], 2),
                '경기당 태클': round(avg['tackles'], 1),
            },
            'strengths': strengths if strengths else ["균형잡힌 플레이"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '패스 플레이': '35%',
                '공격 기여': '30%',
                '수비 기여': '20%',
                '드리블': '15%',
            }
        }

    @classmethod
    def _evaluate_attacking_midfielder(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """공격형 미드필더 평가 (CAM)"""
        avg = cls._calculate_averages(performances)

        # 어시스트 (35%)
        assists_score = min((avg.get('assists', 0) / 0.5) * 100, 100)
        pass_accuracy_score = min(avg.get('pass_success_rate', 0), 100)
        assist_contribution = (assists_score * 0.7 + pass_accuracy_score * 0.3)

        # 득점 (30%)
        goals_score = min((avg.get('goals', 0) / 0.4) * 100, 100)
        shot_accuracy = min(avg.get('shot_accuracy', 0), 100)
        goal_contribution = (goals_score * 0.7 + shot_accuracy * 0.3)

        # 드리블 (20%)
        dribble_score = min(avg.get('dribble_success_rate', 0), 100)

        # 패스 정확도 (15%)
        pass_score = min(avg.get('pass_success_rate', 0), 100)

        position_score = (
            assist_contribution * 0.35 +
            goal_contribution * 0.30 +
            dribble_score * 0.20 +
            pass_score * 0.15
        )

        strengths = []
        weaknesses = []

        if avg['assists'] >= 0.4:
            strengths.append("탁월한 찬스 메이킹")
        if avg['goals'] >= 0.3:
            strengths.append("우수한 득점력")
        if avg.get('dribble_success_rate', 0) >= 75:
            strengths.append("효과적인 돌파")

        if avg['assists'] < 0.2:
            weaknesses.append("어시스트 향상 필요")
        if avg['goals'] < 0.15:
            weaknesses.append("득점 기여도 부족")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'CAM',
            'position_group_name': '공격형 미드필더',
            'key_metrics': {
                '경기당 어시스트': round(avg['assists'], 2),
                '경기당 골': round(avg['goals'], 2),
                '드리블 성공률': f"{round(avg.get('dribble_success_rate', 0), 1)}%",
                '슈팅 정확도': f"{round(avg.get('shot_accuracy', 0), 1)}%",
            },
            'strengths': strengths if strengths else ["창의적인 플레이"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '어시스트': '35%',
                '득점': '30%',
                '드리블': '20%',
                '패스 정확도': '15%',
            }
        }

    @classmethod
    def _evaluate_wide_midfielder(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """측면 미드필더 평가 (WM - RM, LM)"""
        avg = cls._calculate_averages(performances)

        # 공격 기여 (40%)
        assists_score = min((avg.get('assists', 0) / 0.4) * 100, 100)
        dribble_score = min(avg.get('dribble_success_rate', 0), 100)
        offensive_score = (assists_score * 0.55 + dribble_score * 0.45)

        # 활동량 (25%)
        total_actions = avg.get('dribble_attempts', 0) + avg.get('pass_attempts', 0) / 10.0 + avg.get('tackles', 0)
        activity_score = min((total_actions / 20.0) * 100, 100)

        # 패스/크로스 (20%)
        pass_score = min(avg.get('pass_success_rate', 0), 100)

        # 수비 기여 (15%)
        tackles_score = min((avg.get('tackles', 0) / 2.5) * 100, 100)

        position_score = (
            offensive_score * 0.40 +
            activity_score * 0.25 +
            pass_score * 0.20 +
            tackles_score * 0.15
        )

        strengths = []
        weaknesses = []

        if avg['assists'] >= 0.35:
            strengths.append("효과적인 크로스")
        if avg.get('dribble_success_rate', 0) >= 70:
            strengths.append("측면 돌파 능력")
        if avg['tackles'] >= 2.0:
            strengths.append("수비 가담")

        if avg['assists'] < 0.15:
            weaknesses.append("어시스트 향상 필요")
        if avg.get('dribble_success_rate', 0) < 55:
            weaknesses.append("드리블 성공률 개선 필요")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'WM',
            'position_group_name': '측면 미드필더',
            'key_metrics': {
                '경기당 어시스트': round(avg['assists'], 2),
                '드리블 성공률': f"{round(avg.get('dribble_success_rate', 0), 1)}%",
                '패스 성공률': f"{round(avg.get('pass_success_rate', 0), 1)}%",
                '경기당 태클': round(avg['tackles'], 1),
            },
            'strengths': strengths if strengths else ["측면 활동"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '공격 기여': '40%',
                '활동량': '25%',
                '패스/크로스': '20%',
                '수비 기여': '15%',
            }
        }

    @classmethod
    def _evaluate_winger(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """윙어 평가 (W - LW, RW)"""
        avg = cls._calculate_averages(performances)

        # 득점 (35%)
        goals_score = min((avg.get('goals', 0) / 0.5) * 100, 100)
        shot_conversion = min(avg.get('shot_conversion', 0) * 2, 100)
        shot_accuracy = min(avg.get('shot_accuracy', 0), 100)
        scoring_score = (goals_score * 0.5 + shot_conversion * 0.3 + shot_accuracy * 0.2)

        # 어시스트 (30%)
        assists_score = min((avg.get('assists', 0) / 0.45) * 100, 100)

        # 드리블 (25%)
        dribble_success_score = min(avg.get('dribble_success_rate', 0), 100)
        dribble_volume_score = min((avg.get('dribble_attempts', 0) / 5.0) * 100, 100)
        dribbling_score = (dribble_success_score * 0.6 + dribble_volume_score * 0.4)

        # 슈팅 효율 (10%)
        shot_efficiency = min(avg.get('shot_conversion', 0) * 2.5, 100)

        position_score = (
            scoring_score * 0.35 +
            assists_score * 0.30 +
            dribbling_score * 0.25 +
            shot_efficiency * 0.10
        )

        strengths = []
        weaknesses = []

        if avg['goals'] >= 0.4:
            strengths.append("일류 득점력")
        if avg['assists'] >= 0.35:
            strengths.append("우수한 찬스 메이킹")
        if avg.get('dribble_success_rate', 0) >= 75:
            strengths.append("탁월한 드리블")
        if avg.get('shot_conversion', 0) >= 20:
            strengths.append("효율적인 마무리")

        if avg['goals'] < 0.2:
            weaknesses.append("득점력 향상 필요")
        if avg.get('dribble_success_rate', 0) < 60:
            weaknesses.append("드리블 성공률 개선 필요")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'W',
            'position_group_name': '윙어',
            'key_metrics': {
                '경기당 골': round(avg['goals'], 2),
                '경기당 어시스트': round(avg['assists'], 2),
                '슈팅 전환율': f"{round(avg.get('shot_conversion', 0), 1)}%",
                '드리블 성공률': f"{round(avg.get('dribble_success_rate', 0), 1)}%",
            },
            'strengths': strengths if strengths else ["측면 위협"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '득점': '35%',
                '어시스트': '30%',
                '드리블': '25%',
                '슈팅 효율': '10%',
            }
        }

    @classmethod
    def _evaluate_striker(cls, performances: List[Dict[str, Any]], position: int) -> Dict[str, Any]:
        """스트라이커 평가 (ST - CF, RS, ST, LS)"""
        avg = cls._calculate_averages(performances)

        # 득점 (50%) - 가장 높은 비중
        goals_per_game_score = min((avg.get('goals', 0) / 0.7) * 100, 100)
        goals_score = goals_per_game_score

        # 슈팅 효율 (30%)
        shot_conversion = min(avg.get('shot_conversion', 0) * 2, 100)
        shot_accuracy = min(avg.get('shot_accuracy', 0), 100)
        efficiency_score = (shot_conversion * 0.65 + shot_accuracy * 0.35)

        # 어시스트 (10%)
        assists_score = min((avg.get('assists', 0) / 0.25) * 100, 100)

        # 헤딩 (10%)
        aerial_score = min(avg.get('aerial_success_rate', 0), 100)

        position_score = (
            goals_score * 0.50 +
            efficiency_score * 0.30 +
            assists_score * 0.10 +
            aerial_score * 0.10
        )

        strengths = []
        weaknesses = []

        if avg['goals'] >= 0.6:
            strengths.append("일류 득점 능력")
        elif avg['goals'] >= 0.4:
            strengths.append("우수한 득점력")

        if avg.get('shot_conversion', 0) >= 25:
            strengths.append("뛰어난 마무리")
        elif avg.get('shot_conversion', 0) >= 18:
            strengths.append("효율적인 슈팅")

        if avg.get('aerial_success_rate', 0) >= 70:
            strengths.append("강력한 헤딩")

        if avg['assists'] >= 0.2:
            strengths.append("찬스 메이킹 능력")

        if avg['goals'] < 0.25:
            weaknesses.append("득점력 대폭 향상 필요")
        if avg.get('shot_conversion', 0) < 15:
            weaknesses.append("마무리 정확도 개선 필요")
        if avg.get('shot_accuracy', 0) < 50:
            weaknesses.append("슈팅 정확도 부족")

        return {
            'position_score': round(position_score, 1),
            'position_group': 'ST',
            'position_group_name': '스트라이커',
            'key_metrics': {
                '경기당 골': round(avg['goals'], 2),
                '슈팅 전환율': f"{round(avg.get('shot_conversion', 0), 1)}%",
                '슈팅 정확도': f"{round(avg.get('shot_accuracy', 0), 1)}%",
                '헤딩 성공률': f"{round(avg.get('aerial_success_rate', 0), 1)}%",
            },
            'strengths': strengths if strengths else ["득점 지향적"],
            'weaknesses': weaknesses if weaknesses else [],
            'evaluation_criteria': {
                '득점': '50% (경기당 골이 가장 중요)',
                '슈팅 효율': '30% (전환율, 정확도)',
                '어시스트': '10%',
                '헤딩': '10%',
            }
        }
