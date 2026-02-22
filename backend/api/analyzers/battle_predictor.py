"""
나와의 승부 예측 — Battle Predictor (공식경기 전용)

방법론:
  1. 양 플레이어 최근 경기 원시 데이터에서 실제 성과 지표 추출
     (실제 득/실점, 승/무/패, 슈팅 정확도, 패스 성공률)
  2. Poisson 분포 기반 예상 득점(xG) → 승/무/패 확률 계산
     - my_xg  = (내 평균 득점) × (상대 평균 실점) / 리그 평균
     - opp_xg = (상대 평균 득점) × (내 평균 실점) / 리그 평균
  3. 전술 스타일 매치업 보정 (내 강점 vs 상대 약점 : ±최대 20%)
  4. 6개 전술 차원별 어드밴티지 비교
  5. 핵심 승부처 3개 추출 (점수 차이 기준)
  6. 예상 시나리오 서술
"""
import math
from typing import Dict, List, Any, Tuple


# 리그 평균 득점 (FC Online 공식경기 기준 — 실축구보다 득점 많음)
LEAGUE_AVG_GOALS = 2.8


class BattlePredictor:
    """나와의 승부 예측 분석기"""

    # ── Poisson 분포 ──────────────────────────────────────────────────────

    @staticmethod
    def _poisson_pmf(k: int, lam: float) -> float:
        """P(X = k) for Poisson(lambda)"""
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return math.exp(-lam) * (lam ** k) / math.factorial(k)

    @classmethod
    def _poisson_match_probs(
        cls, my_xg: float, opp_xg: float, max_goals: int = 8
    ) -> Tuple[float, float, float]:
        """
        독립 Poisson 분포 기반 승/무/패 확률 계산.
        my_xg: 내 예상 득점, opp_xg: 상대 예상 득점.
        """
        win = draw = lose = 0.0
        for i in range(max_goals + 1):
            p_i = cls._poisson_pmf(i, my_xg)
            for j in range(max_goals + 1):
                p_j = cls._poisson_pmf(j, opp_xg)
                prob = p_i * p_j
                if i > j:
                    win += prob
                elif i == j:
                    draw += prob
                else:
                    lose += prob
        total = win + draw + lose
        if total == 0:
            return 0.40, 0.20, 0.40
        return win / total, draw / total, lose / total

    # ── 실제 성과 지표 추출 ────────────────────────────────────────────────

    @classmethod
    def extract_performance(
        cls, matches_raw: List[Dict], player_ouid: str
    ) -> Dict[str, Any]:
        """
        매치 원시 데이터에서 핵심 성과 지표 추출.
        matchResult: '승'/'패'/'무' 또는 숫자(1/2/3).
        """
        wins = draws = losses = 0
        goals_for = goals_against = 0
        shots_total = shots_effective = 0
        passes_try = passes_success = 0
        tackles_total = blocks_total = 0

        for raw in matches_raw:
            match_info_list = raw.get('matchInfo', [])
            my_info = next(
                (m for m in match_info_list if m.get('ouid') == player_ouid), None
            )
            if not my_info:
                continue

            # 승/무/패
            match_detail = my_info.get('matchDetail') or {}
            result = match_detail.get('matchResult', '')
            if result in ('승', 1, '1'):
                wins += 1
            elif result in ('무', 2, '2'):
                draws += 1
            elif result in ('패', 3, '3'):
                losses += 1

            # 내 득점 / 슈팅
            my_shoot = my_info.get('shoot') or {}
            goals_for      += my_shoot.get('goalTotalDisplay', 0) or 0
            shots_total    += my_shoot.get('shootTotal', 0) or 0
            shots_effective += my_shoot.get('effectiveShootTotal', 0) or 0

            # 패스
            my_pass = my_info.get('pass') or {}
            passes_try     += my_pass.get('passTry', 0) or 0
            passes_success += my_pass.get('passSuccess', 0) or 0

            # 수비 지표
            my_defence = my_info.get('defence') or {}
            tackles_total += my_defence.get('tackleTry', 0) or 0
            blocks_total  += my_defence.get('blockTry', 0) or 0

            # 상대 득점 = 내 실점
            opp_info = next(
                (m for m in match_info_list if m.get('ouid') != player_ouid), None
            )
            if opp_info:
                opp_shoot = opp_info.get('shoot') or {}
                goals_against += opp_shoot.get('goalTotalDisplay', 0) or 0

        total = wins + draws + losses
        if total == 0:
            return {
                'win_rate': 0.50, 'draw_rate': 0.10, 'loss_rate': 0.40,
                'goals_for_avg': 1.5, 'goals_against_avg': 1.5,
                'shot_accuracy': 0.40, 'pass_accuracy': 0.80,
                'tackles_per_game': 0, 'blocks_per_game': 0,
                'matches': 0, 'wins': 0, 'draws': 0, 'losses': 0,
            }

        return {
            'win_rate':           round(wins   / total, 3),
            'draw_rate':          round(draws  / total, 3),
            'loss_rate':          round(losses / total, 3),
            'goals_for_avg':      round(goals_for      / total, 2),
            'goals_against_avg':  round(goals_against  / total, 2),
            'shot_accuracy':      round(shots_effective / shots_total, 3) if shots_total > 0 else 0.0,
            'pass_accuracy':      round(passes_success  / passes_try,  3) if passes_try  > 0 else 0.0,
            'tackles_per_game':   round(tackles_total  / total, 2),
            'blocks_per_game':    round(blocks_total   / total, 2),
            'matches': total,
            'wins': wins, 'draws': draws, 'losses': losses,
        }

    # ── 스타일 매치업 보정 ─────────────────────────────────────────────────

    @staticmethod
    def _compute_style_advantage(my_idx: Dict, opp_idx: Dict) -> float:
        """
        내 공격 스타일이 상대 수비 취약점을 얼마나 찌르는가.
        0.0 ~ 1.0 (0.5 = 중립)
        """
        advantage = 0.50

        # 내 측면 공격 vs 상대 전술 경직성 (경직 = 유연성 낮음 = 측면 대응 약)
        if my_idx.get('attack_width_index', 0) > 0.14 and \
           opp_idx.get('formation_rigidity', 0.5) < 0.45:
            advantage += 0.07

        # 내 점유 우위 + 상대 후반 취약
        if my_idx.get('avg_possession', 50) >= 52 and \
           opp_idx.get('late_collapse_rate', 0.2) >= 0.30:
            advantage += 0.08

        # 내 스루패스 창의성 vs 상대 고빌드업(높은 수비 라인)
        if my_idx.get('through_pass_ratio', 0) >= 0.08 and \
           opp_idx.get('buildup_index', 0) >= 0.44:
            advantage += 0.06

        # 내 슈팅 정확도 vs 상대 낮은 수비 안정성(높은 실점)
        if my_idx.get('shot_efficiency', 0) >= 0.50 and \
           opp_idx.get('formation_rigidity', 0.5) < 0.40:
            advantage += 0.05

        # 나는 후반 강 + 상대 후반 약
        if my_idx.get('late_collapse_rate', 0.2) < 0.15 and \
           opp_idx.get('late_collapse_rate', 0.2) >= 0.30:
            advantage += 0.07

        # 상대 슈팅 결정력 저하 → 내 수비 부담 경감
        if opp_idx.get('shot_efficiency', 0.4) <= 0.28:
            advantage += 0.04

        # 내 세트피스 + 상대 경직 수비
        if my_idx.get('setpiece_dependency', 0) >= 0.20 and \
           opp_idx.get('formation_rigidity', 0.5) < 0.45:
            advantage += 0.04

        return round(min(0.85, max(0.15, advantage)), 3)

    # ── 6개 차원 비교 ──────────────────────────────────────────────────────

    @staticmethod
    def _compute_dimensions(
        my_idx: Dict, opp_idx: Dict,
        my_perf: Dict, opp_perf: Dict,
    ) -> List[Dict]:
        """6개 전술 차원별 나 vs 상대 점수 비교 (0 ~ 100)"""

        def clamp(v):
            return max(0.0, min(100.0, v))

        dims = []

        # 1. 슈팅 위협 — 실제 득점력 + 유효슛 비율
        my_shot = clamp(
            my_perf.get('shot_accuracy', 0) * 50
            + my_idx.get('shot_efficiency', 0) * 30
            + min(my_perf.get('goals_for_avg', 1.5) * 13, 30)
        )
        opp_shot = clamp(
            opp_perf.get('shot_accuracy', 0) * 50
            + opp_idx.get('shot_efficiency', 0) * 30
            + min(opp_perf.get('goals_for_avg', 1.5) * 13, 30)
        )
        dims.append({
            'key': 'shooting',
            'label': '슈팅 위협',
            'icon': '🎯',
            'my_score':  round(my_shot, 1),
            'opp_score': round(opp_shot, 1),
            'my_detail':  f"경기당 {my_perf.get('goals_for_avg', 0):.2f}골 · 유효슛 {my_perf.get('shot_accuracy', 0)*100:.0f}%",
            'opp_detail': f"경기당 {opp_perf.get('goals_for_avg', 0):.2f}골 · 유효슛 {opp_perf.get('shot_accuracy', 0)*100:.0f}%",
        })

        # 2. 공격 전개력 — 스루패스·공격 폭·점유
        my_build = clamp(
            my_idx.get('through_pass_ratio', 0) * 300
            + my_idx.get('attack_width_index', 0) * 200
            + max(0, (my_idx.get('avg_possession', 50) - 40)) * 1.5
        )
        opp_build = clamp(
            opp_idx.get('through_pass_ratio', 0) * 300
            + opp_idx.get('attack_width_index', 0) * 200
            + max(0, (opp_idx.get('avg_possession', 50) - 40)) * 1.5
        )
        dims.append({
            'key': 'attack_build',
            'label': '공격 전개력',
            'icon': '⚡',
            'my_score':  round(my_build, 1),
            'opp_score': round(opp_build, 1),
            'my_detail':  f"점유 {my_idx.get('avg_possession', 50):.0f}% · 스루패스 {my_idx.get('through_pass_ratio', 0)*100:.1f}%",
            'opp_detail': f"점유 {opp_idx.get('avg_possession', 50):.0f}% · 스루패스 {opp_idx.get('through_pass_ratio', 0)*100:.1f}%",
        })

        # 3. 수비 안정성 — 실제 실점 + 후반 취약성 + 포메이션
        my_def = clamp(
            (1 - min(my_perf.get('goals_against_avg', 1.5) / 3.5, 1.0)) * 55
            + (1 - my_idx.get('late_collapse_rate', 0.2)) * 25
            + my_idx.get('formation_rigidity', 0.5) * 20
        )
        opp_def = clamp(
            (1 - min(opp_perf.get('goals_against_avg', 1.5) / 3.5, 1.0)) * 55
            + (1 - opp_idx.get('late_collapse_rate', 0.2)) * 25
            + opp_idx.get('formation_rigidity', 0.5) * 20
        )
        dims.append({
            'key': 'defense',
            'label': '수비 안정성',
            'icon': '🛡️',
            'my_score':  round(my_def, 1),
            'opp_score': round(opp_def, 1),
            'my_detail':  f"경기당 실점 {my_perf.get('goals_against_avg', 0):.2f} · 후반취약 {my_idx.get('late_collapse_rate', 0)*100:.0f}%",
            'opp_detail': f"경기당 실점 {opp_perf.get('goals_against_avg', 0):.2f} · 후반취약 {opp_idx.get('late_collapse_rate', 0)*100:.0f}%",
        })

        # 4. 후반 체력 — 후반 취약성 + 최근 승률
        my_stam = clamp(
            (1 - my_idx.get('late_collapse_rate', 0.2)) * 70
            + my_perf.get('win_rate', 0.5) * 30
        )
        opp_stam = clamp(
            (1 - opp_idx.get('late_collapse_rate', 0.2)) * 70
            + opp_perf.get('win_rate', 0.5) * 30
        )
        dims.append({
            'key': 'stamina',
            'label': '후반 체력',
            'icon': '💪',
            'my_score':  round(my_stam, 1),
            'opp_score': round(opp_stam, 1),
            'my_detail':  f"후반취약 {my_idx.get('late_collapse_rate', 0)*100:.0f}% · 최근 승률 {my_perf.get('win_rate', 0)*100:.0f}%",
            'opp_detail': f"후반취약 {opp_idx.get('late_collapse_rate', 0)*100:.0f}% · 최근 승률 {opp_perf.get('win_rate', 0)*100:.0f}%",
        })

        # 5. 세트피스 & 공중볼
        my_dead = clamp(
            my_idx.get('setpiece_dependency', 0) * 200
            + my_idx.get('heading_tendency', 0) * 150
        )
        opp_dead = clamp(
            opp_idx.get('setpiece_dependency', 0) * 200
            + opp_idx.get('heading_tendency', 0) * 150
        )
        dims.append({
            'key': 'deadball',
            'label': '세트피스 & 공중볼',
            'icon': '⚽',
            'my_score':  round(my_dead, 1),
            'opp_score': round(opp_dead, 1),
            'my_detail':  f"세트피스 득점 {my_idx.get('setpiece_dependency', 0)*100:.0f}% · 헤딩 {my_idx.get('heading_tendency', 0)*100:.0f}%",
            'opp_detail': f"세트피스 득점 {opp_idx.get('setpiece_dependency', 0)*100:.0f}% · 헤딩 {opp_idx.get('heading_tendency', 0)*100:.0f}%",
        })

        # 6. 패스 & 전술 다양성
        my_pass_score = clamp(
            my_perf.get('pass_accuracy', 0) * 60
            + my_idx.get('formation_rigidity', 0.5) * 25
            + my_idx.get('through_pass_ratio', 0) * 150
        )
        opp_pass_score = clamp(
            opp_perf.get('pass_accuracy', 0) * 60
            + opp_idx.get('formation_rigidity', 0.5) * 25
            + opp_idx.get('through_pass_ratio', 0) * 150
        )
        dims.append({
            'key': 'pass_variety',
            'label': '패스 & 전술 유연성',
            'icon': '🔀',
            'my_score':  round(my_pass_score, 1),
            'opp_score': round(opp_pass_score, 1),
            'my_detail':  f"패스 성공률 {my_perf.get('pass_accuracy', 0)*100:.0f}% · 전술유연성 {my_idx.get('formation_rigidity', 0)*100:.0f}%",
            'opp_detail': f"패스 성공률 {opp_perf.get('pass_accuracy', 0)*100:.0f}% · 전술유연성 {opp_idx.get('formation_rigidity', 0)*100:.0f}%",
        })

        return dims

    # ── 핵심 승부처 ────────────────────────────────────────────────────────

    @staticmethod
    def _key_battles(dimensions: List[Dict]) -> List[Dict]:
        """점수 차이가 큰 3개 차원 = 핵심 승부처"""
        sorted_dims = sorted(dimensions, key=lambda d: abs(d['my_score'] - d['opp_score']), reverse=True)
        result = []
        for d in sorted_dims[:3]:
            diff = d['my_score'] - d['opp_score']
            if diff > 10:
                verdict, color = '내 강점', 'green'
                desc = f"이 영역에서 {diff:.0f}점 우위 — 적극적으로 활용하라"
            elif diff < -10:
                verdict, color = '내 약점', 'red'
                desc = f"상대가 {-diff:.0f}점 우위 — 노출 최소화 필수"
            elif diff > 3:
                verdict, color = '약간 유리', 'blue'
                desc = f"소폭 {diff:.0f}점 우위 — 이 흐름을 유지하는 것이 관건"
            elif diff < -3:
                verdict, color = '약간 불리', 'amber'
                desc = f"소폭 {-diff:.0f}점 열세 — 상대가 이 루트를 노릴 것"
            else:
                verdict, color = '백중세', 'gray'
                desc = "양측 막상막하 — 집중력과 결정적 순간 포착이 관건"
            result.append({
                'label':     d['label'],
                'icon':      d['icon'],
                'verdict':   verdict,
                'color':     color,
                'desc':      desc,
                'my_score':  d['my_score'],
                'opp_score': d['opp_score'],
            })
        return result

    # ── 예상 시나리오 ──────────────────────────────────────────────────────

    @staticmethod
    def _generate_scenarios(
        win_p: float, draw_p: float, lose_p: float,
        my_perf: Dict, opp_perf: Dict,
        my_idx: Dict, opp_idx: Dict,
        my_xg: float, opp_xg: float,
    ) -> List[Dict]:
        scenarios = []

        opp_collapse  = opp_idx.get('late_collapse_rate', 0.2)
        my_collapse   = my_idx.get('late_collapse_rate', 0.2)
        my_poss       = my_idx.get('avg_possession', 50)
        opp_shot_eff  = opp_idx.get('shot_efficiency', 0.4)
        my_through    = my_idx.get('through_pass_ratio', 0)

        # 승리 시나리오
        if opp_collapse >= 0.30:
            win_detail = (
                f"상대의 후반 취약성({opp_collapse*100:.0f}%)이 뚜렷하다. "
                f"동점 또는 1점 차 상황을 유지하며 75분까지 버틴 뒤 집중 공세로 역전 또는 추가골을 노려라."
            )
        elif my_poss >= 52:
            win_detail = (
                f"점유율 {my_poss:.0f}%로 경기 주도권을 확보한 뒤 "
                f"스루패스({my_through*100:.1f}%)를 통해 상대 수비 틈을 공략하면 xG {my_xg:.1f}골 달성 가능."
            )
        elif my_perf.get('goals_for_avg', 0) > opp_perf.get('goals_against_avg', 2):
            win_detail = (
                f"내 평균 득점({my_perf.get('goals_for_avg',0):.2f})이 상대 평균 실점({opp_perf.get('goals_against_avg',0):.2f})을 상회. "
                f"초반 선제골로 상대 전술 붕괴를 유도하고 이후 수비 집중으로 마무리."
            )
        else:
            win_detail = (
                f"Poisson 모델 기준 예상 득점 {my_xg:.1f}골. "
                f"슈팅 찬스를 높은 정확도로 마무리하면 승리 가능."
            )
        scenarios.append({
            'type': 'win', 'color': 'green', 'icon': '✅',
            'label': f'승리 시나리오 ({win_p*100:.0f}%)',
            'detail': win_detail,
            'score_line': f"예상 득점 {my_xg:.1f}골 vs {opp_xg:.1f}골",
        })

        # 무승부 시나리오
        if draw_p >= 0.12:
            draw_detail = (
                "양팀의 수비 안정성이 공격력을 상쇄. "
                "결정적 실수나 세트피스 한 방이 없으면 스코어가 묶일 가능성 높음. "
                "연장 대비 체력 배분이 중요."
            )
            scenarios.append({
                'type': 'draw', 'color': 'yellow', 'icon': '⚖️',
                'label': f'무승부 시나리오 ({draw_p*100:.0f}%)',
                'detail': draw_detail,
                'score_line': f"예상 스코어: {min(round(my_xg,1), round(opp_xg,1))} - {min(round(my_xg,1), round(opp_xg,1))}",
            })

        # 패배 위험 시나리오
        if lose_p >= 0.25:
            if my_collapse >= 0.28:
                lose_detail = (
                    f"내 후반 취약성({my_collapse*100:.0f}%)이 가장 큰 위험 요소. "
                    f"75분 이후 집중력 저하 시 상대 역습에 무너질 수 있다. 후반 교체와 체력 관리가 핵심."
                )
            elif opp_shot_eff >= 0.50:
                lose_detail = (
                    f"상대의 슈팅 정확도({opp_shot_eff*100:.0f}%)가 매우 높다. "
                    f"찬스를 적게 주더라도 한두 번의 결정적 슛에 실점할 수 있음. "
                    f"수비 라인 관리와 슈팅 기회 원천 차단이 필수."
                )
            else:
                lose_detail = (
                    f"상대의 평균 득점({opp_perf.get('goals_for_avg',0):.2f}골)이 위협적. "
                    f"내 수비 집중력이 흔들리는 순간 연속 실점 위험 있음."
                )
            scenarios.append({
                'type': 'lose', 'color': 'red', 'icon': '⚠️',
                'label': f'패배 위험 시나리오 ({lose_p*100:.0f}%)',
                'detail': lose_detail,
                'score_line': f"상대 예상 득점 {opp_xg:.1f}골",
            })

        return scenarios

    # ── 메인 예측 ─────────────────────────────────────────────────────────

    @classmethod
    def predict(
        cls,
        my_indices: Dict,
        opp_indices: Dict,
        my_matches_raw: List[Dict],
        opp_matches_raw: List[Dict],
        my_ouid: str,
        opp_ouid: str,
        my_nickname: str = '',
        opp_nickname: str = '',
    ) -> Dict[str, Any]:
        """나와의 승부 예측 메인"""

        # 1. 실제 성과 지표 추출
        my_perf  = cls.extract_performance(my_matches_raw, my_ouid)
        opp_perf = cls.extract_performance(opp_matches_raw, opp_ouid)

        # 2. xG 계산 (Dixon-Coles 단순화 버전)
        #    내 공격력 × 상대 수비 취약성 / 리그 평균
        my_xg  = (my_perf['goals_for_avg']  * opp_perf['goals_against_avg']) / LEAGUE_AVG_GOALS
        opp_xg = (opp_perf['goals_for_avg'] * my_perf['goals_against_avg'])  / LEAGUE_AVG_GOALS

        # xG 범위 제한 (FC Online 현실적 득점 범위: 0.3 ~ 3.5)
        my_xg  = round(max(0.3, min(3.5, my_xg)),  2)
        opp_xg = round(max(0.3, min(3.5, opp_xg)), 2)

        # 3. Poisson 기반 기초 확률
        win_p, draw_p, lose_p = cls._poisson_match_probs(my_xg, opp_xg)

        # 4. 전술 스타일 보정 (±최대 20%)
        style_adv = cls._compute_style_advantage(my_indices, opp_indices)
        style_adj = (style_adv - 0.5) * 0.25
        win_p  = max(0.05, min(0.88, win_p  + style_adj))
        lose_p = max(0.05, min(0.88, lose_p - style_adj))
        draw_p = max(0.05, 1.0 - win_p - lose_p)

        # 5. 차원별 비교
        dimensions  = cls._compute_dimensions(my_indices, opp_indices, my_perf, opp_perf)

        # 6. 핵심 승부처
        key_battles = cls._key_battles(dimensions)

        # 7. 예상 시나리오
        scenarios   = cls._generate_scenarios(
            win_p, draw_p, lose_p, my_perf, opp_perf,
            my_indices, opp_indices, my_xg, opp_xg,
        )

        # 8. 종합 판정
        if win_p >= 0.56:
            verdict, verdict_icon = '승리 우세', '🟢'
            verdict_desc = f"승리 확률 {win_p*100:.0f}%로 전술·성적 모두 우위. 페이스 유지가 관건."
        elif win_p >= 0.46:
            verdict, verdict_icon = '약간 우세', '🔵'
            verdict_desc = f"승리 확률 {win_p*100:.0f}%. 핵심 승부처를 선점하면 격차 벌릴 수 있음."
        elif win_p >= 0.38:
            verdict, verdict_icon = '백중세', '🟡'
            verdict_desc = f"승/패 확률 차이 {abs(win_p-lose_p)*100:.0f}%p 이내의 박빙. 먼저 실수하는 쪽이 진다."
        else:
            verdict, verdict_icon = '상대 우세', '🔴'
            verdict_desc = f"상대 승률 우위({lose_p*100:.0f}%). 전술적 변화와 집중력 강화가 필수."

        # 데이터 신뢰도
        min_matches = min(my_perf['matches'], opp_perf['matches'])
        if min_matches >= 20:
            reliability = 'high'
            reliability_label = '높음 (20경기+)'
        elif min_matches >= 10:
            reliability = 'medium'
            reliability_label = '보통 (10경기+)'
        else:
            reliability = 'low'
            reliability_label = f'낮음 ({min_matches}경기 — 데이터 부족)'

        return {
            'my_nickname':   my_nickname,
            'opp_nickname':  opp_nickname,
            'my_performance':  my_perf,
            'opp_performance': opp_perf,
            'win_probability':  round(win_p  * 100, 1),
            'draw_probability': round(draw_p * 100, 1),
            'lose_probability': round(lose_p * 100, 1),
            'my_xg':   my_xg,
            'opp_xg':  opp_xg,
            'style_advantage': style_adv,
            'dimensions':   dimensions,
            'key_battles':  key_battles,
            'scenarios':    scenarios,
            'verdict':       verdict,
            'verdict_icon':  verdict_icon,
            'verdict_desc':  verdict_desc,
            'data_quality': {
                'my_matches':       my_perf['matches'],
                'opp_matches':      opp_perf['matches'],
                'reliability':      reliability,
                'reliability_label': reliability_label,
            },
        }
