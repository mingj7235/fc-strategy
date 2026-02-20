"""
Habit Loop Detector — B1
무의식적으로 반복하는 전술 습관 수치화.
마르코프 체인 기반 패스 시퀀스 분석 + 압박 반응 패턴.
"""
import math
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple


class HabitLoopAnalyzer:
    """습관 루프 탐지기"""

    PASS_TYPES = {
        'short': '단패',
        'long': '장패',
        'through': '스루패스',
        'lob': '로브패스',
    }

    @staticmethod
    def _extract_pass_type(match_info: Dict) -> Optional[str]:
        """매치에서 주요 패스 유형 추출 (압도적으로 많은 타입)"""
        pass_data = match_info.get('pass') or {}
        if not isinstance(pass_data, dict):
            return None

        short = pass_data.get('shortPassTry', 0) or 0
        long_ = pass_data.get('longPassTry', 0) or 0
        through = pass_data.get('throughPassTry', 0) or 0

        total = short + long_ + through
        if total == 0:
            return None

        ratios = {'short': short / total, 'long': long_ / total, 'through': through / total}
        return max(ratios, key=ratios.get)

    @staticmethod
    def _build_pass_sequence(matches_raw: List[Dict], user_ouid: str) -> List[str]:
        """
        경기별 주요 패스 유형 시퀀스 생성.
        각 경기를 하나의 심볼로 인코딩.
        """
        sequence = []
        for raw in matches_raw:
            match_info_list = raw.get('matchInfo', [])
            for info in match_info_list:
                if info.get('ouid') == user_ouid:
                    pass_type = HabitLoopAnalyzer._extract_pass_type(info)
                    if pass_type:
                        sequence.append(pass_type)
                    break
        return sequence

    @staticmethod
    def _compute_markov_transition_matrix(sequence: List[str]) -> Dict[str, Dict[str, float]]:
        """
        마르코프 체인 전이 행렬 계산.
        P(next_type | current_type) 계산.
        """
        if len(sequence) < 2:
            return {}

        # Count transitions
        transitions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for i in range(len(sequence) - 1):
            current = sequence[i]
            next_ = sequence[i + 1]
            transitions[current][next_] += 1

        # Convert to probabilities
        matrix = {}
        for from_type, to_counts in transitions.items():
            total = sum(to_counts.values())
            matrix[from_type] = {
                to_type: round(count / total, 3)
                for to_type, count in to_counts.items()
            }

        return matrix

    @staticmethod
    def _detect_dominant_chains(
        matrix: Dict[str, Dict[str, float]],
        threshold: float = 0.4,
    ) -> List[Dict]:
        """
        지배적 패스 시퀀스 탐지.
        전이 확률이 threshold 이상인 경우 습관으로 간주.
        """
        habits = []
        for from_type, to_probs in matrix.items():
            for to_type, prob in to_probs.items():
                if prob >= threshold:
                    habits.append({
                        'from': from_type,
                        'from_label': HabitLoopAnalyzer.PASS_TYPES.get(from_type, from_type),
                        'to': to_type,
                        'to_label': HabitLoopAnalyzer.PASS_TYPES.get(to_type, to_type),
                        'probability': round(prob * 100, 1),
                        'is_predictable': prob >= 0.6,
                        'habit_strength': 'strong' if prob >= 0.6 else 'moderate',
                    })

        habits.sort(key=lambda x: x['probability'], reverse=True)
        return habits

    @staticmethod
    def _compute_shot_zone_entropy(shot_details: List[Dict]) -> Optional[float]:
        """
        슛 존 고착화 스코어 = 슛 x,y 좌표의 엔트로피.
        낮을수록 예측 가능한 슈터 (항상 같은 위치에서 슛).
        """
        if len(shot_details) < 5:
            return None

        # Zone classification
        zones = []
        for shot in shot_details:
            x = float(shot.get('x', 0.5))
            y = float(shot.get('y', 0.5))

            # Grid 3x3 zone
            x_zone = 0 if x < 0.33 else (1 if x < 0.66 else 2)
            y_zone = 0 if y < 0.33 else (1 if y < 0.66 else 2)
            zones.append(f"{x_zone}_{y_zone}")

        if not zones:
            return None

        from collections import Counter
        counts = Counter(zones)
        total = len(zones)
        max_entropy = math.log2(9)  # 9 zones max

        entropy = -sum(
            (c / total) * math.log2(c / total)
            for c in counts.values() if c > 0
        )

        # Normalize 0-1 (0 = always same zone = predictable, 1 = perfectly spread)
        normalized = entropy / max_entropy if max_entropy > 0 else 0
        return round(normalized, 3)

    @staticmethod
    def _analyze_stress_response(matches: List[Dict]) -> Dict[str, Any]:
        """
        압박 반응 패턴 분석.
        점유율 40% 이하 시 장패 비율 급증 여부 탐지.
        """
        low_poss_matches = [m for m in matches if float(m.get('possession', 50)) <= 40]
        normal_matches = [m for m in matches if float(m.get('possession', 50)) > 40]

        def avg_long_pass_ratio(match_list):
            ratios = []
            for m in match_list:
                raw = m.get('raw_data') or {}
                match_info_list = raw.get('matchInfo', [])
                for info in match_info_list:
                    pass_data = info.get('pass') or {}
                    if isinstance(pass_data, dict):
                        short = pass_data.get('shortPassTry', 0) or 0
                        long_ = pass_data.get('longPassTry', 0) or 0
                        total = short + long_
                        if total > 0:
                            ratios.append(long_ / total)
                            break
            return sum(ratios) / len(ratios) if ratios else None

        low_poss_ratio = avg_long_pass_ratio(low_poss_matches)
        normal_ratio = avg_long_pass_ratio(normal_matches)

        stress_detected = False
        stress_level = 'none'
        delta = 0.0

        if low_poss_ratio is not None and normal_ratio is not None and normal_ratio > 0:
            delta = low_poss_ratio - normal_ratio
            if delta >= 0.15:
                stress_detected = True
                stress_level = 'high' if delta >= 0.25 else 'moderate'

        return {
            'stress_detected': stress_detected,
            'stress_level': stress_level,
            'low_possession_long_pass_rate': round(low_poss_ratio * 100, 1) if low_poss_ratio else None,
            'normal_long_pass_rate': round(normal_ratio * 100, 1) if normal_ratio else None,
            'delta': round(delta * 100, 1),
            'low_possession_matches': len(low_poss_matches),
        }

    @classmethod
    def analyze_habit_loops(
        cls,
        matches_raw: List[Dict],
        user_ouid: str,
        shot_details: List[Dict],
        matches: List[Dict],
    ) -> Dict[str, Any]:
        """
        습관 루프 분석 메인.

        Args:
            matches_raw: Match.raw_data 목록
            user_ouid: 사용자 OUID
            shot_details: ShotDetail 딕셔너리 목록
            matches: Match 딕셔너리 목록 (raw_data 포함)

        Returns:
            {pass_habits, shot_zone_habit, stress_response, good_habits, bad_habits, insights}
        """
        if len(matches_raw) < 10:
            return {
                **cls._empty_result(),
                'insights': ['습관 루프 탐지에는 최소 10경기 이상의 데이터가 필요합니다.'],
            }

        # 1. 패스 시퀀스 마르코프 체인
        pass_sequence = cls._build_pass_sequence(matches_raw, user_ouid)
        transition_matrix = cls._compute_markov_transition_matrix(pass_sequence)
        dominant_chains = cls._detect_dominant_chains(transition_matrix)

        # 분류: 좋은 습관 vs 나쁜 습관
        good_chains = [c for c in dominant_chains if not c['is_predictable']]
        bad_chains = [c for c in dominant_chains if c['is_predictable']]

        # 2. 슛 존 고착화
        shot_entropy = cls._compute_shot_zone_entropy(shot_details)
        shot_habit = cls._classify_shot_zone_habit(shot_entropy)

        # 3. 압박 반응 패턴
        stress_response = cls._analyze_stress_response(matches)

        # 4. 득점 후 패턴 분석
        post_goal_pattern = cls._analyze_post_goal_pattern(matches)

        # Generate insights
        insights = cls._generate_insights(dominant_chains, shot_habit, stress_response, post_goal_pattern)

        return {
            'matches_analyzed': len(matches_raw),
            'pass_sequence_length': len(pass_sequence),
            'transition_matrix': transition_matrix,
            'dominant_pass_chains': dominant_chains,
            'good_habits': good_chains[:3],
            'bad_habits': bad_chains[:3],
            'shot_zone_habit': shot_habit,
            'stress_response': stress_response,
            'post_goal_pattern': post_goal_pattern,
            'insights': insights,
        }

    @staticmethod
    def _classify_shot_zone_habit(entropy: Optional[float]) -> Dict[str, Any]:
        if entropy is None:
            return {'entropy': None, 'level': 'unknown', 'label': '데이터 부족', 'predictable': False}

        if entropy <= 0.4:
            level = 'highly_predictable'
            label = '매우 예측 가능'
            predictable = True
            desc = '항상 같은 위치에서 슛을 시도합니다. 상대가 읽기 쉽습니다.'
        elif entropy <= 0.65:
            level = 'somewhat_predictable'
            label = '다소 예측 가능'
            predictable = True
            desc = '슈팅 위치가 어느 정도 고착되어 있습니다.'
        elif entropy <= 0.8:
            level = 'diverse'
            label = '다양한 슈팅'
            predictable = False
            desc = '다양한 위치에서 슛을 시도하는 좋은 패턴입니다.'
        else:
            level = 'highly_diverse'
            label = '매우 다양한 슈팅'
            predictable = False
            desc = '슈팅 위치가 매우 다양합니다. 상대가 예측하기 어렵습니다.'

        return {
            'entropy': round(entropy, 3),
            'entropy_score': round(entropy * 100, 1),
            'level': level,
            'label': label,
            'predictable': predictable,
            'description': desc,
        }

    @staticmethod
    def _analyze_post_goal_pattern(matches: List[Dict]) -> Dict[str, Any]:
        """득점 후 수비/공격 패턴 변화"""
        scored_matches = [m for m in matches if m.get('goals_for', 0) > 0]
        if not scored_matches:
            return {'pattern': 'unknown', 'description': '데이터 부족'}

        # 득점 후 점유율 변화 (전체 vs 득점 경기)
        all_avg_poss = sum(float(m.get('possession', 50)) for m in matches) / len(matches)
        scored_avg_poss = sum(float(m.get('possession', 50)) for m in scored_matches) / len(scored_matches)

        delta_poss = scored_avg_poss - all_avg_poss

        if delta_poss >= 5:
            pattern = 'possession_increase'
            desc = '득점 후 점유율을 높여 경기를 지배하는 패턴'
        elif delta_poss <= -5:
            pattern = 'defensive_retreat'
            desc = '득점 후 수비적으로 전환하는 패턴 (역습 취약)'
        else:
            pattern = 'stable'
            desc = '득점 전후 패턴이 안정적'

        return {
            'pattern': pattern,
            'description': desc,
            'avg_possession_after_goal': round(scored_avg_poss, 1),
            'baseline_possession': round(all_avg_poss, 1),
            'delta': round(delta_poss, 1),
        }

    @staticmethod
    def _generate_insights(
        dominant_chains: List[Dict],
        shot_habit: Dict,
        stress_response: Dict,
        post_goal: Dict,
    ) -> List[str]:
        insights = []

        # Pass habits
        if dominant_chains:
            bad = [c for c in dominant_chains if c['is_predictable']]
            good = [c for c in dominant_chains if not c['is_predictable']]

            if bad:
                top_bad = bad[0]
                insights.append(
                    f"⚠️ 패스 습관 경고: {top_bad['from_label']} 이후 {top_bad['to_label']}을 "
                    f"{top_bad['probability']}% 확률로 반복합니다. 상대가 읽을 수 있습니다!"
                )
            if good:
                top_good = good[0]
                insights.append(
                    f"✅ 좋은 패스 루틴: {top_good['from_label']} 이후 {top_good['to_label']} "
                    f"전환이 자연스럽습니다."
                )

        # Shot zone
        if shot_habit.get('predictable'):
            insights.append(
                f"🎯 슛 위치 고착화 감지 (엔트로피 {shot_habit.get('entropy_score', 0):.0f}/100). "
                f"다양한 위치에서 슛을 시도하면 수비수가 읽기 어려워집니다."
            )
        elif shot_habit.get('entropy') is not None:
            insights.append(
                f"✅ 슛 위치가 다양합니다. 상대가 예측하기 어려운 좋은 슈팅 패턴입니다."
            )

        # Stress response
        if stress_response.get('stress_detected'):
            insights.append(
                f"😰 압박 반응 감지: 점유율 40% 이하 시 장패 사용이 "
                f"{stress_response.get('delta', 0):.0f}%p 증가합니다. "
                f"압박 상황에서도 짧은 패스로 안전하게 빠져나오는 연습이 필요합니다."
            )

        # Post goal pattern
        pattern = post_goal.get('pattern', 'stable')
        if pattern == 'defensive_retreat':
            insights.append(
                f"⚠️ 득점 후 수비로 물러나는 경향이 있습니다. "
                f"리드 상황에서 역습에 노출될 위험이 있습니다."
            )
        elif pattern == 'possession_increase':
            insights.append(
                f"✅ 득점 후 점유율을 높여 경기를 안전하게 가져가는 좋은 패턴입니다."
            )

        if not insights:
            insights.append('반복적인 습관 패턴이 감지되지 않았습니다. 다양한 플레이를 하고 있습니다!')

        return insights

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            'matches_analyzed': 0,
            'pass_sequence_length': 0,
            'transition_matrix': {},
            'dominant_pass_chains': [],
            'good_habits': [],
            'bad_habits': [],
            'shot_zone_habit': {'entropy': None, 'level': 'unknown', 'label': '데이터 부족'},
            'stress_response': {'stress_detected': False, 'stress_level': 'none'},
            'post_goal_pattern': {'pattern': 'unknown', 'description': '데이터 부족'},
            'insights': [],
        }
