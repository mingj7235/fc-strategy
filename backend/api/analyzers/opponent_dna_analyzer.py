"""
Opponent DNA Profile — A1 (Fixed + Enhanced)
상대 닉네임을 입력하면 최근 30경기를 분석해 전술 성향을 수치화.

버그 수정:
- shootDetail은 matchInfo[x] 안에 있음 (raw 최상위가 아님)
- setpiece_dependency: shoot summary의 goalFreekick+goalPenalty 사용
- late_collapse_rate: goalTime 비트 인코딩 디코딩 + 올바른 위치에서 데이터 읽기
- 신규 지표 추가: long_pass_ratio, through_pass_ratio, shot_efficiency, heading_tendency
"""
import math
from typing import List, Dict, Any, Optional
from collections import Counter


class OpponentDNAAnalyzer:
    """상대 전술 DNA 프로파일 분석기 (개선판)"""

    @staticmethod
    def _decode_goal_time(raw_goal_time: int) -> int:
        """
        Nexon FC Online goalTime 비트 인코딩 디코딩.
        period = goalTime >> 24  (0=전반, 1=후반, 2=ET전반, 3=ET후반)
        offset = goalTime & 0xFFFFFF  (해당 하프 내 초)
        실제_초 = period * 2700 + offset
        """
        if not raw_goal_time or raw_goal_time <= 0:
            return 0
        period = raw_goal_time >> 24
        offset = raw_goal_time & 0xFFFFFF
        decoded = period * 2700 + offset
        return decoded if decoded <= 10800 else 0  # 180분 상한

    @staticmethod
    def _compute_buildup_index(match_info: Dict) -> Optional[float]:
        """빌드업 지수 = (단패*1.0 + 장패*0.4 + 스루패스*1.5) / 총패스"""
        pass_data = match_info.get('pass') or {}
        if not isinstance(pass_data, dict):
            return None
        pass_try = pass_data.get('passTry', 0) or 0
        short_pass = pass_data.get('shortPassTry', 0) or 0
        long_pass = pass_data.get('longPassTry', 0) or 0
        through_pass = pass_data.get('throughPassTry', 0) or 0
        if pass_try == 0:
            return None
        return round((short_pass * 1.0 + long_pass * 0.4 + through_pass * 1.5) / pass_try, 3)

    @staticmethod
    def _compute_long_pass_ratio(match_info: Dict) -> Optional[float]:
        """장패 비율 — 직진성/카운터 성향"""
        pass_data = match_info.get('pass') or {}
        if not isinstance(pass_data, dict):
            return None
        pass_try = pass_data.get('passTry', 0) or 0
        long_pass = pass_data.get('longPassTry', 0) or 0
        if pass_try == 0:
            return None
        return round(long_pass / pass_try, 3)

    @staticmethod
    def _compute_through_pass_ratio(match_info: Dict) -> Optional[float]:
        """스루패스 비율 — 창의성"""
        pass_data = match_info.get('pass') or {}
        if not isinstance(pass_data, dict):
            return None
        pass_try = pass_data.get('passTry', 0) or 0
        through_pass = pass_data.get('throughPassTry', 0) or 0
        if pass_try == 0:
            return None
        return round(through_pass / pass_try, 3)

    @staticmethod
    def _compute_attack_width(shoot_detail: List[Dict]) -> Optional[float]:
        """
        공격 폭 지수 = 슛 x좌표의 표준편차.
        반드시 opponent_match_info.get('shootDetail', []) 를 전달해야 함.
        """
        x_coords = []
        for s in shoot_detail:
            x = s.get('x')
            if x is not None:
                try:
                    x_coords.append(float(x))
                except (TypeError, ValueError):
                    pass
        if len(x_coords) < 3:
            return None
        mean_x = sum(x_coords) / len(x_coords)
        variance = sum((x - mean_x) ** 2 for x in x_coords) / len(x_coords)
        return round(math.sqrt(variance), 3)

    @staticmethod
    def _compute_setpiece_dependency(match_info: Dict) -> float:
        """
        세트피스 의존도 = (프리킥 골 + 페널티 골) / 총득점.
        shoot summary의 goalFreekick + goalPenalty 사용 (버그 수정).
        """
        shoot_data = match_info.get('shoot') or {}
        if not isinstance(shoot_data, dict):
            return 0.0
        total_goals = shoot_data.get('goalTotalDisplay', 0) or 0
        if total_goals == 0:
            return 0.0
        freekick_goals = shoot_data.get('goalFreekick', 0) or 0
        penalty_goals = shoot_data.get('goalPenalty', 0) or 0
        return round((freekick_goals + penalty_goals) / total_goals, 3)

    @staticmethod
    def _compute_shot_efficiency(match_info: Dict) -> Optional[float]:
        """슈팅 정확도 = 유효슛 / 총슛"""
        shoot_data = match_info.get('shoot') or {}
        if not isinstance(shoot_data, dict):
            return None
        total = shoot_data.get('shootTotal', 0) or 0
        effective = shoot_data.get('effectiveShootTotal', 0) or 0
        if total == 0:
            return None
        return round(effective / total, 3)

    @staticmethod
    def _compute_heading_tendency(match_info: Dict) -> Optional[float]:
        """헤딩 슈팅 비율 — 공중볼/크로스 선호도"""
        shoot_data = match_info.get('shoot') or {}
        if not isinstance(shoot_data, dict):
            return None
        total = shoot_data.get('shootTotal', 0) or 0
        heading = shoot_data.get('shootHeading', 0) or 0
        if total == 0:
            return None
        return round(heading / total, 3)

    @staticmethod
    def _compute_formation_rigidity(players: List[Dict]) -> Optional[float]:
        """포진 고착도 = 선수 포지션 코드 분포의 엔트로피 (낮을수록 고착)"""
        if not players:
            return None
        positions = [p.get('spPosition', 0) for p in players if p.get('spPosition') is not None]
        if not positions:
            return None
        groups = []
        for pos in positions:
            if pos == 0:
                groups.append('GK')
            elif 1 <= pos <= 8:
                groups.append('DEF')
            elif 9 <= pos <= 19:
                groups.append('MID')
            elif 20 <= pos <= 27:
                groups.append('FWD')
        if not groups:
            return None
        counts = Counter(groups)
        total = len(groups)
        entropy = -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)
        return round(entropy / 2.0, 3)  # max entropy = log2(4) = 2.0

    @classmethod
    def _compute_late_collapse_rate(
        cls,
        all_matches_raw: List[Dict],
        opponent_ouid: str,
    ) -> float:
        """
        후반 붕괴율 = 75분 이후 실점 비중.
        상대방의 상대(other player) shootDetail에서 골 시간을 분석.
        goalTime 비트 인코딩 디코딩 적용.
        """
        total_goals_conceded = 0
        late_goals = 0

        for raw in all_matches_raw:
            match_info_list = raw.get('matchInfo', [])
            # opponent가 아닌 다른 선수의 matchInfo = opponent 상대방
            other_info = None
            for info in match_info_list:
                if info.get('ouid') != opponent_ouid:
                    other_info = info
                    break
            if not other_info:
                continue

            # 상대방의 상대가 넣은 골 = opponent가 실점한 골
            shoot_detail = other_info.get('shootDetail') or []
            shoot_summary = other_info.get('shoot') or {}
            other_goals_summary = shoot_summary.get('goalTotalDisplay', 0) or 0

            timed_goals = 0
            for shot in shoot_detail:
                result_code = shot.get('result')
                # result: 1=goal (numeric), 또는 문자열 다양성 대응
                is_goal = (
                    result_code == 1
                    or result_code == '1'
                    or result_code == '골'
                )
                if not is_goal:
                    continue

                raw_goal_time = shot.get('goalTime', 0) or 0
                decoded = cls._decode_goal_time(raw_goal_time)
                if decoded > 0:
                    timed_goals += 1
                    total_goals_conceded += 1
                    if decoded >= 4500:  # 75분 = 4500초
                        late_goals += 1

            # goalTime 데이터가 없을 경우 summary 카운트로 폴백
            if timed_goals == 0 and other_goals_summary > 0:
                total_goals_conceded += other_goals_summary

        if total_goals_conceded == 0:
            return 0.0
        return round(late_goals / total_goals_conceded, 3)

    @classmethod
    def analyze_opponent_dna(
        cls,
        opponent_matches_raw: List[Dict],
        opponent_ouid: str,
    ) -> Dict[str, Any]:
        """상대 DNA 프로파일 분석 메인."""
        if not opponent_matches_raw:
            return cls._empty_result()

        buildup_indices = []
        long_pass_ratios = []
        through_pass_ratios = []
        attack_widths = []
        setpiece_deps = []
        shot_efficiencies = []
        heading_tendencies = []
        formation_rigidities = []
        possession_list = []

        for raw in opponent_matches_raw:
            match_info_list = raw.get('matchInfo', [])
            opponent_match_info = None
            for info in match_info_list:
                if info.get('ouid') == opponent_ouid:
                    opponent_match_info = info
                    break
            if not opponent_match_info:
                continue

            # 1. 빌드업 지수
            bi = cls._compute_buildup_index(opponent_match_info)
            if bi is not None:
                buildup_indices.append(bi)

            # 2. 장패 비율
            lp = cls._compute_long_pass_ratio(opponent_match_info)
            if lp is not None:
                long_pass_ratios.append(lp)

            # 3. 스루패스 비율
            tp = cls._compute_through_pass_ratio(opponent_match_info)
            if tp is not None:
                through_pass_ratios.append(tp)

            # 4. 공격 폭 지수 (FIXED: opponent_match_info.shootDetail 사용)
            shoot_detail = opponent_match_info.get('shootDetail') or []
            aw = cls._compute_attack_width(shoot_detail)
            if aw is not None:
                attack_widths.append(aw)

            # 5. 세트피스 의존도 (FIXED: shoot summary 사용)
            sp_dep = cls._compute_setpiece_dependency(opponent_match_info)
            setpiece_deps.append(sp_dep)

            # 6. 슈팅 정확도
            se = cls._compute_shot_efficiency(opponent_match_info)
            if se is not None:
                shot_efficiencies.append(se)

            # 7. 헤딩 성향
            ht = cls._compute_heading_tendency(opponent_match_info)
            if ht is not None:
                heading_tendencies.append(ht)

            # 8. 포진 고착도
            players = opponent_match_info.get('player') or []
            fr = cls._compute_formation_rigidity(players)
            if fr is not None:
                formation_rigidities.append(fr)

            # 9. 점유율
            match_detail = opponent_match_info.get('matchDetail') or {}
            poss = match_detail.get('possession')
            if poss is not None:
                try:
                    possession_list.append(float(poss))
                except (TypeError, ValueError):
                    pass

        def safe_avg(lst: list) -> float:
            return round(sum(lst) / len(lst), 3) if lst else 0.0

        avg_buildup = safe_avg(buildup_indices)
        avg_long_pass = safe_avg(long_pass_ratios)
        avg_through_pass = safe_avg(through_pass_ratios)
        avg_attack_width = safe_avg(attack_widths)
        avg_setpiece = safe_avg(setpiece_deps)
        avg_shot_efficiency = safe_avg(shot_efficiencies)
        avg_heading = safe_avg(heading_tendencies)
        avg_formation = safe_avg(formation_rigidities)
        avg_possession = safe_avg(possession_list)

        # 후반 붕괴율 (FIXED)
        late_collapse = cls._compute_late_collapse_rate(opponent_matches_raw, opponent_ouid)

        # 전술 분류
        play_style = cls._classify_play_style(
            avg_buildup, avg_long_pass, avg_through_pass,
            avg_attack_width, avg_setpiece, avg_heading, avg_possession
        )

        # 7축 레이더 데이터
        radar_data = cls._normalize_radar(
            avg_buildup, avg_attack_width, avg_setpiece,
            avg_formation, late_collapse, avg_through_pass, avg_shot_efficiency
        )

        # 스카우팅 리포트
        scouting_report = cls._generate_scouting_report(
            play_style, avg_buildup, avg_long_pass, avg_attack_width,
            avg_setpiece, avg_heading, late_collapse, avg_possession,
            avg_shot_efficiency, len(opponent_matches_raw)
        )

        # 즉각 활용 전략 카드
        strategy_card = cls._generate_strategy_card(
            play_style, avg_buildup, avg_long_pass, avg_attack_width,
            avg_setpiece, avg_heading, late_collapse, avg_possession,
            avg_shot_efficiency, avg_through_pass,
        )

        return {
            'matches_analyzed': len(opponent_matches_raw),
            'indices': {
                'buildup_index': avg_buildup,
                'attack_width_index': avg_attack_width,
                'setpiece_dependency': avg_setpiece,
                'formation_rigidity': avg_formation,
                'late_collapse_rate': late_collapse,
                'through_pass_ratio': avg_through_pass,
                'shot_efficiency': avg_shot_efficiency,
                'heading_tendency': avg_heading,
                'long_pass_ratio': avg_long_pass,
                'avg_possession': avg_possession,
            },
            'radar_data': radar_data,
            'play_style': play_style,
            'scouting_report': scouting_report,
            'strategy_card': strategy_card,
        }

    @staticmethod
    def _generate_strategy_card(
        play_style: Dict,
        buildup: float,
        long_pass: float,
        attack_width: float,
        setpiece: float,
        heading: float,
        late_collapse: float,
        possession: float,
        shot_efficiency: float,
        through_pass: float,
    ) -> Dict:
        """
        경기 시작 10초 전에도 파악할 수 있는 즉각 활용 전략 카드.
        약점 / 해야 할 것 / 피해야 할 것을 한눈에 제공.
        """
        style = play_style['style']

        # ── 1. 상대 약점 (빨간 카드) ──────────────────────────────────
        weaknesses = []

        if possession <= 46:
            weaknesses.append({
                'icon': '⚡',
                'title': '점유력 부족',
                'desc': f'평균 점유율 {possession:.0f}% — 압박하면 실수 유도 가능',
                'level': 'high',
            })
        if late_collapse >= 0.30:
            weaknesses.append({
                'icon': '⏰',
                'title': '후반 집중력 저하',
                'desc': f'75분+ 실점 비중 {late_collapse*100:.0f}% — 끝까지 포기 금지',
                'level': 'high',
            })
        if shot_efficiency > 0 and shot_efficiency <= 0.33:
            weaknesses.append({
                'icon': '🎯',
                'title': '낮은 슛 결정력',
                'desc': f'유효슛 비율 {shot_efficiency*100:.0f}% — 슛 많이 줘도 실점 위험 낮음',
                'level': 'medium',
            })
        if long_pass >= 0.38:
            weaknesses.append({
                'icon': '🚀',
                'title': '단순 전진 패스 의존',
                'desc': f'장패 비율 {long_pass*100:.0f}% — 제2구역 장악 시 공격 차단',
                'level': 'medium',
            })
        if setpiece <= 0.08 and style not in ('setpiece',):
            weaknesses.append({
                'icon': '⚽',
                'title': '세트피스 위협 낮음',
                'desc': '세트피스 득점 의존도 낮아 수비 집중력 분산 가능',
                'level': 'low',
            })

        # ── 2. 내가 해야 할 것 (초록 카드) ───────────────────────────
        do_list = []

        # 공격 전략
        if possession <= 48:
            do_list.append({
                'category': '공격',
                'icon': '🔥',
                'action': '전방 압박 → 볼 탈취',
                'reason': f'점유율 {possession:.0f}%로 약해 압박 효과 극대화',
            })
        else:
            do_list.append({
                'category': '공격',
                'icon': '🎨',
                'action': '볼 점유 유지 후 찬스 노리기',
                'reason': '상대도 점유율이 높아 빠른 전환보다 지공 우위',
            })

        if late_collapse >= 0.30:
            do_list.append({
                'category': '공격',
                'icon': '💪',
                'action': '75분 이후 적극 공세',
                'reason': f'후반 실점 비중 {late_collapse*100:.0f}% — 체력 저하 구간 집중 공략',
            })

        if style == 'wide_counter' or attack_width >= 0.14:
            do_list.append({
                'category': '수비',
                'icon': '🛡️',
                'action': '윙백 적극 수비 참여',
                'reason': '측면 공간 허용 시 크로스→헤딩 득점 위험',
            })
        elif style == 'possession':
            do_list.append({
                'category': '수비',
                'icon': '⚔️',
                'action': '전방 압박으로 빌드업 방해',
                'reason': '짧은 패스 빌드업 차단 시 공격 루트 소멸',
            })
        elif style in ('direct',):
            do_list.append({
                'category': '수비',
                'icon': '🧱',
                'action': '수비 라인 낮게 유지',
                'reason': '롱볼 침투 공간을 줄여 배후를 차단',
            })
        elif style == 'setpiece':
            do_list.append({
                'category': '수비',
                'icon': '🧱',
                'action': '세트피스 존 수비 강화',
                'reason': f'세트피스 득점 의존 {setpiece*100:.0f}% — 반칙·코너킥 철저 대비',
            })
        elif style == 'aerial':
            do_list.append({
                'category': '수비',
                'icon': '🦅',
                'action': '크로스 원천 차단',
                'reason': f'헤딩 슈팅 비율 {heading*100:.0f}% — 측면 봉쇄가 핵심',
            })
        elif style == 'creative':
            do_list.append({
                'category': '수비',
                'icon': '🔒',
                'action': '스루패스 공간 미리 차단',
                'reason': f'스루패스 비율 {through_pass*100:.0f}% — 수비 라인 깊게 유지',
            })
        else:
            do_list.append({
                'category': '수비',
                'icon': '⚖️',
                'action': '상황별 유연한 수비 전환',
                'reason': '다양한 공격 패턴에 고정 전략 대신 유연하게 대응',
            })

        if shot_efficiency > 0 and shot_efficiency <= 0.33:
            do_list.append({
                'category': '수비',
                'icon': '😎',
                'action': '슛 허용해도 과감하게 역습',
                'reason': f'유효슛 {shot_efficiency*100:.0f}%로 실점 위험 낮아 역습 기회 손해 안 봐도 됨',
            })

        # ── 3. 피해야 할 것 (주황 카드) ──────────────────────────────
        dont_list = []

        if style in ('wide_counter', 'direct') or long_pass >= 0.35:
            dont_list.append({
                'icon': '🚫',
                'action': '공격 후 배후 공간 남기기',
                'reason': '빠른 역습으로 배후를 파고들어 한 방에 결정',
            })
        if style == 'possession' or possession >= 53:
            dont_list.append({
                'icon': '🚫',
                'action': '무리한 전진 압박',
                'reason': '압박이 뚫리면 넓어진 공간을 이용해 빠르게 전개',
            })
        if setpiece >= 0.25:
            dont_list.append({
                'icon': '🚫',
                'action': '위험 지역 불필요한 반칙',
                'reason': f'세트피스 득점 비율 {setpiece*100:.0f}% — 프리킥 기회 주면 위험',
            })
        if heading >= 0.25:
            dont_list.append({
                'icon': '🚫',
                'action': '측면에서 크로스 허용',
                'reason': f'헤딩 슈팅 {heading*100:.0f}% — 크로스가 득점으로 직결될 수 있음',
            })
        if late_collapse < 0.15:
            dont_list.append({
                'icon': '🚫',
                'action': '후반 초반 집중력 저하',
                'reason': '후반 실점이 적어 꾸준한 집중력이 핵심',
            })
        # 항상 1개 이상
        if not dont_list:
            dont_list.append({
                'icon': '🚫',
                'action': '방심하고 느슨한 수비',
                'reason': '균형잡힌 상대라 어느 순간에도 득점 가능',
            })

        # ── 헤드라인 한 줄 요약 ────────────────────────────────────────
        headline_parts = [f"{play_style['emoji']} {play_style['label']}"]
        if weaknesses:
            headline_parts.append(f"약점: {weaknesses[0]['title']}")
        if do_list:
            headline_parts.append(f"핵심: {do_list[0]['action']}")
        headline = ' · '.join(headline_parts)

        return {
            'headline': headline,
            'weaknesses': weaknesses[:3],
            'do_list': do_list[:3],
            'dont_list': dont_list[:3],
        }

    @staticmethod
    def _classify_play_style(
        buildup: float, long_pass: float, through_pass: float,
        attack_width: float, setpiece: float, heading: float, possession: float
    ) -> Dict[str, str]:
        """다차원 전술 유형 분류 (개선판)"""

        # 점유형: 점유율 높고, 빌드업 지수 높고, 장패 비율 낮음
        if possession >= 53 and buildup >= 0.38 and long_pass <= 0.28:
            style, label = 'possession', '점유형'
            desc = '볼 점유를 통해 경기를 지배하는 스타일'
            counter = '고압박으로 빌드업을 방해하고, 볼 탈취 후 빠른 역습'

        # 측면 역습형: 장패 높고 점유율 낮고 공격 폭 넓음
        elif long_pass >= 0.35 and possession <= 48 and attack_width >= 0.13:
            style, label = 'wide_counter', '측면 역습형'
            desc = '빠른 측면 전환과 크로스를 활용하는 역습 스타일'
            counter = '측면 공간을 차단하고 윙백 수비를 강화해 크로스 원천 차단'

        # 직접형: 장패 높고 점유율 낮고 중앙 집중
        elif long_pass >= 0.35 and possession <= 48:
            style, label = 'direct', '직접형'
            desc = '빠른 전진 패스로 직접 공격하는 스타일'
            counter = '제2구역을 확보하고 롱볼 대응 수비 조직 강화'

        # 세트피스 의존형
        elif setpiece >= 0.25:
            style, label = 'setpiece', '세트피스 의존형'
            desc = '코너킥/프리킥을 통한 득점에 크게 의존하는 스타일'
            counter = '세트피스 존 수비 강화, 헤딩 경합 적극 대응'

        # 공중볼 의존형: 헤딩 슈팅 비율 높음
        elif heading >= 0.28:
            style, label = 'aerial', '공중볼 의존형'
            desc = '헤딩과 공중볼 경합으로 득점을 노리는 스타일'
            counter = '키 큰 수비수 배치, 크로스 원천 차단이 핵심'

        # 창의형: 스루패스 비율 높음
        elif through_pass >= 0.10:
            style, label = 'creative', '창의형'
            desc = '스루패스와 개인기로 공간을 파고드는 창의적 스타일'
            counter = '수비 라인을 낮추고 스루패스 공간을 미리 차단'

        # 균형형
        else:
            style, label = 'balanced', '균형형'
            desc = '다양한 공격 패턴을 고르게 사용하는 스타일'
            counter = '상황별 유연한 대응이 핵심, 고정 약점이 적음'

        emoji_map = {
            'possession': '🎯', 'wide_counter': '⚡', 'direct': '🚀',
            'setpiece': '⚽', 'aerial': '🦅', 'creative': '🎨', 'balanced': '⚖️',
        }
        return {
            'style': style,
            'label': label,
            'description': desc,
            'counter_strategy': counter,
            'emoji': emoji_map.get(style, '📊'),
        }

    @staticmethod
    def _normalize_radar(
        buildup, attack_width, setpiece, formation, late_collapse,
        through_pass, shot_efficiency,
    ) -> List[Dict]:
        """7축 레이더차트 데이터 (0-100 정규화)"""
        return [
            {
                'axis': '빌드업 지수',
                'value': round(min(100, buildup * 200), 1),
                'raw': buildup,
                'description': '점유형 vs 직접형 (높을수록 점유형)',
            },
            {
                'axis': '공격 폭',
                'value': round(min(100, attack_width * 500), 1),
                'raw': attack_width,
                'description': '중앙형 vs 측면형 (높을수록 측면 선호)',
            },
            {
                'axis': '세트피스',
                'value': round(min(100, setpiece * 300), 1),
                'raw': setpiece,
                'description': '세트피스 득점 의존도',
            },
            {
                'axis': '전술 유연성',
                'value': round(formation * 100, 1),
                'raw': formation,
                'description': '포메이션 다양성 (높을수록 유연)',
            },
            {
                'axis': '후반 취약성',
                'value': round(min(100, late_collapse * 400), 1),
                'raw': late_collapse,
                'description': '75분 이후 실점 집중도',
            },
            {
                'axis': '창의성',
                'value': round(min(100, through_pass * 800), 1),
                'raw': through_pass,
                'description': '스루패스 활용도',
            },
            {
                'axis': '슈팅 정확도',
                'value': round(min(100, shot_efficiency * 200), 1),
                'raw': shot_efficiency,
                'description': '유효슛 비율',
            },
        ]

    @staticmethod
    def _generate_scouting_report(
        play_style, buildup, long_pass, attack_width, setpiece, heading,
        late_collapse, possession, shot_efficiency, matches_analyzed,
    ) -> List[str]:
        report = [
            f"📋 {matches_analyzed}경기 분석 기반 스카우팅 리포트",
            f"🎯 전술 성향: {play_style['label']} — {play_style['description']}",
        ]

        if possession >= 53:
            report.append(f"⚽ 평균 점유율 {possession:.1f}%로 볼을 지배. 압박 시 빌드업 실수 유도 가능.")
        elif possession <= 47:
            report.append(f"⚡ 평균 점유율 {possession:.1f}%로 역습 중심. 볼 탈취 즉시 역습 공간 주의.")

        if long_pass >= 0.35:
            report.append(f"🚀 장패 비율 {long_pass*100:.0f}%. 전진 패스 위주. 제2구역 수비 필수.")
        elif long_pass <= 0.18:
            report.append(f"🔗 단패 중심 플레이 ({long_pass*100:.0f}% 장패). 촘촘한 압박이 효과적.")

        if attack_width >= 0.14:
            report.append(f"📍 측면 공간 적극 활용. 윙백 수비 강화 및 크로스 차단 필요.")
        elif 0 < attack_width < 0.10:
            report.append(f"🎯 중앙 집중 공격 성향. 페널티박스 앞 밀집 수비가 효과적.")

        if setpiece >= 0.25:
            report.append(f"⚽ 세트피스 득점 의존도 {setpiece*100:.0f}%. 세트피스 수비 집중 필요.")

        if heading >= 0.25:
            report.append(f"🦅 헤딩 슈팅 비율 {heading*100:.0f}%. 공중볼 수비 강화 필요.")

        if shot_efficiency >= 0.55:
            report.append(f"🎯 유효슛 비율 {shot_efficiency*100:.0f}%. 슛 정확도가 높은 위험한 공격수.")
        elif 0 < shot_efficiency <= 0.30:
            report.append(f"📉 유효슛 비율 {shot_efficiency*100:.0f}%. 슛 결정력이 낮아 골문 위협 낮음.")

        if late_collapse >= 0.35:
            report.append(f"⏰ 75분+ 실점 비중 {late_collapse*100:.0f}%. 끈질기게 버티면 후반에 기회.")
        elif late_collapse <= 0.10 and late_collapse > 0:
            report.append(f"🛡️ 후반 집중력이 뛰어남. 역전이나 추가득점이 어려울 수 있음.")

        report.append(f"🛡️ 대응 전략: {play_style['counter_strategy']}")
        return report

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            'matches_analyzed': 0,
            'indices': {},
            'radar_data': [],
            'play_style': {
                'style': 'unknown', 'label': '분석 불가',
                'description': '', 'counter_strategy': '', 'emoji': '❓',
            },
            'scouting_report': ['분석할 경기 데이터가 없습니다.'],
            'strategy_card': {
                'headline': '데이터 부족',
                'weaknesses': [],
                'do_list': [],
                'dont_list': [],
            },
        }
