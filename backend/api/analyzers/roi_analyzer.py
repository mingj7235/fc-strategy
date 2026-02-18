"""
Player Contribution Analyzer — C1 (v3)
포지션별 맞춤 기여도 분석.

가격 ROI 제거 이유:
  Nexon Open API /fconline/v1/user/trade는 유저별 구매 내역이 아닌
  글로벌 경매장 거래 로그를 반환함 (두 유저가 동일한 saleSn 반환으로 확인).
  신뢰할 수 없는 가격 데이터로 ROI를 계산하는 것은 무의미하므로,
  match-detail 데이터에서 직접 추출 가능한 기여도 점수를 핵심 지표로 사용.
"""
import math
from typing import List, Dict, Any, Optional


# ── 포지션 그룹 매핑 ──────────────────────────────────────────────────────────
POSITION_GROUP_MAP: Dict[int, str] = {
    0: 'GK', 28: 'GK',
    1: 'DEF', 2: 'DEF', 3: 'DEF', 4: 'DEF', 5: 'DEF', 6: 'DEF', 7: 'DEF', 8: 'DEF',
    9: 'CDM', 10: 'CDM',
    11: 'CM', 12: 'CM', 13: 'CM',
    14: 'CAM', 15: 'CAM', 16: 'CAM',
    17: 'WG', 18: 'WG', 19: 'WG', 20: 'WG', 21: 'WG', 22: 'WG',
    23: 'FWD', 24: 'FWD', 25: 'FWD', 26: 'FWD', 27: 'FWD',
}

# ── 포지션별 기여도 가중치 ───────────────────────────────────────────────────
POSITION_CONFIGS: Dict[str, Dict] = {
    'GK': {
        'label': '골키퍼',
        'rating_weight': 2.5,
        'goals': 0.0, 'assists': 0.0, 'defensive': 0.0,
        'pass_acc': 0.04, 'shots_on': 0.0, 'dribble_ok': 0.0,
        'role_desc': '안정적인 골킥 & 높은 평점',
        'primary_metrics': ['평균 평점', '패스 성공률'],
    },
    'DEF': {
        'label': '수비수',
        'rating_weight': 1.5,
        'goals': 5.0, 'assists': 3.5, 'defensive': 1.0,
        'pass_acc': 0.02, 'shots_on': 0.0, 'dribble_ok': 0.0,
        'role_desc': '태클·블록 & 평점 안정',
        'primary_metrics': ['태클+블록', '평균 평점', '골·어시스트(보너스)'],
    },
    'CDM': {
        'label': '수비형 MF',
        'rating_weight': 1.8,
        'goals': 3.5, 'assists': 3.5, 'defensive': 0.9,
        'pass_acc': 0.03, 'shots_on': 0.0, 'dribble_ok': 0.02,
        'role_desc': '볼 탈취 & 패스 안정',
        'primary_metrics': ['태클', '어시스트', '평균 평점'],
    },
    'CM': {
        'label': '중앙 MF',
        'rating_weight': 2.0,
        'goals': 3.0, 'assists': 4.0, 'defensive': 0.5,
        'pass_acc': 0.03, 'shots_on': 0.0, 'dribble_ok': 0.03,
        'role_desc': '어시스트 & 공수 균형',
        'primary_metrics': ['어시스트', '평균 평점', '골'],
    },
    'CAM': {
        'label': '공격형 MF',
        'rating_weight': 1.8,
        'goals': 3.5, 'assists': 4.5, 'defensive': 0.0,
        'pass_acc': 0.02, 'shots_on': 0.3, 'dribble_ok': 0.05,
        'role_desc': '키패스 & 득점 창출',
        'primary_metrics': ['어시스트', '골', '유효슛'],
    },
    'WG': {
        'label': '윙어',
        'rating_weight': 1.8,
        'goals': 3.5, 'assists': 3.5, 'defensive': 0.0,
        'pass_acc': 0.0, 'shots_on': 0.3, 'dribble_ok': 0.12,
        'role_desc': '드리블 돌파 & G+A',
        'primary_metrics': ['골', '어시스트', '드리블 성공'],
    },
    'FWD': {
        'label': '공격수',
        'rating_weight': 1.5,
        'goals': 5.5, 'assists': 2.5, 'defensive': 0.0,
        'pass_acc': 0.0, 'shots_on': 0.4, 'dribble_ok': 0.0,
        'role_desc': '골 결정력',
        'primary_metrics': ['골', '유효슛', '평균 평점'],
    },
}

# ── 기여도 등급 기준 ──────────────────────────────────────────────────────────
# 포지션 보정 후 기여도: 평균 ~4점, 우수 ~8점, 에이스 12+
CONTRIBUTION_TIERS = [
    {'min': 15.0, 'label': '압도적 에이스', 'color': 'gold',    'emoji': '👑'},
    {'min': 10.0, 'label': '팀의 핵심',     'color': 'amber',   'emoji': '⭐'},
    {'min': 7.0,  'label': '주전급',        'color': 'green',   'emoji': '✅'},
    {'min': 4.5,  'label': '안정적 활용',   'color': 'blue',    'emoji': '📊'},
    {'min': 2.5,  'label': '보통 수준',     'color': 'yellow',  'emoji': '⚠️'},
    {'min': 0.0,  'label': '기여도 낮음',   'color': 'red',     'emoji': '🔻'},
]


class ROIAnalyzer:
    """선수 기여도 분석기 — 포지션 맞춤 기여도 점수 산출"""

    @staticmethod
    def _get_position_group(position: int) -> str:
        return POSITION_GROUP_MAP.get(position, 'CM')

    @staticmethod
    def _get_contribution_tier(score: float) -> Dict:
        for tier in CONTRIBUTION_TIERS:
            if score >= tier['min']:
                return tier
        return CONTRIBUTION_TIERS[-1]

    @classmethod
    def _calculate_contribution(
        cls,
        performances: List[Dict],
        position_group: str,
    ) -> Dict[str, Any]:
        """포지션 맞춤 기여도 계산"""
        if not performances:
            cfg = POSITION_CONFIGS.get(position_group, POSITION_CONFIGS['CM'])
            return {
                'score': 0.0, 'goals_per_game': 0.0, 'assists_per_game': 0.0,
                'avg_rating': 0.0, 'defensive_per_game': 0.0,
                'shots_on_per_game': 0.0, 'dribble_ok_per_game': 0.0,
                'pass_success_rate': 0.0, 'appearances': 0,
                'position_group': position_group,
                'position_label': cfg['label'],
                'primary_metrics': cfg['primary_metrics'],
                'role_desc': cfg['role_desc'],
            }

        cfg = POSITION_CONFIGS.get(position_group, POSITION_CONFIGS['CM'])
        total = len(performances)

        total_goals      = sum(int(p.get('goals', 0))          for p in performances)
        total_assists    = sum(int(p.get('assists', 0))         for p in performances)
        total_rating     = sum(float(p.get('rating', 5.0))     for p in performances)
        total_tackles    = sum(int(p.get('tackle_success', 0))  for p in performances)
        total_blocks     = sum(int(p.get('blocks', 0))          for p in performances)
        total_shots_on   = sum(int(p.get('shots_on_target', 0)) for p in performances)
        total_dribble_ok = sum(int(p.get('dribble_success', 0)) for p in performances)
        total_pass_try   = sum(int(p.get('pass_attempts', 0))   for p in performances)
        total_pass_ok    = sum(int(p.get('pass_success', 0))    for p in performances)

        goals_pg      = total_goals / total
        assists_pg    = total_assists / total
        avg_rating    = total_rating / total
        defensive_pg  = (total_tackles + total_blocks) / total
        shots_on_pg   = total_shots_on / total
        dribble_ok_pg = total_dribble_ok / total
        pass_acc      = (total_pass_ok / total_pass_try * 100) if total_pass_try > 0 else 0.0

        score = (
            max(0.0, avg_rating - 4.0) * cfg['rating_weight']
            + goals_pg      * cfg['goals']
            + assists_pg    * cfg['assists']
            + defensive_pg  * cfg['defensive']
            + pass_acc      * cfg['pass_acc']
            + shots_on_pg   * cfg['shots_on']
            + dribble_ok_pg * cfg['dribble_ok']
        )

        return {
            'score':               round(score, 2),
            'goals_per_game':      round(goals_pg, 2),
            'assists_per_game':    round(assists_pg, 2),
            'avg_rating':          round(avg_rating, 1),
            'defensive_per_game':  round(defensive_pg, 2),
            'shots_on_per_game':   round(shots_on_pg, 2),
            'dribble_ok_per_game': round(dribble_ok_pg, 2),
            'pass_success_rate':   round(pass_acc, 1),
            'appearances':         total,
            'position_group':      position_group,
            'position_label':      cfg['label'],
            'primary_metrics':     cfg['primary_metrics'],
            'role_desc':           cfg['role_desc'],
        }

    @classmethod
    def calculate_squad_roi(
        cls,
        trade_history: List[Dict],       # 더 이상 사용하지 않음 (API 신뢰 불가)
        player_performances_by_spid: Dict[int, List[Dict]],
        metadata_loader=None,
    ) -> Dict[str, Any]:
        """스쿼드 전체 기여도 분석"""

        squad_roi = []

        for spid, performances in player_performances_by_spid.items():
            if len(performances) < 3:
                continue

            position     = performances[0].get('position', 11)
            pos_group    = cls._get_position_group(position)
            contribution = cls._calculate_contribution(performances, pos_group)
            player_name  = performances[0].get('player_name', f'Unknown({spid})')

            tier = cls._get_contribution_tier(contribution['score'])

            squad_roi.append({
                'spid':           spid,
                'player_name':    player_name,
                'image_url':      f"https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png",
                'appearances':    contribution['appearances'],
                'contribution':   contribution,
                'roi_score':      contribution['score'],   # 기여도 점수를 메인 지표로
                'roi_tier':       tier,
                'has_price':      False,
                'position_group': pos_group,
                'position_label': contribution['position_label'],
            })

        # 기여도 내림차순 정렬
        squad_roi.sort(key=lambda x: x['contribution']['score'], reverse=True)

        # 포지션 그룹별 요약
        pos_group_summary: Dict[str, Dict] = {}
        for p in squad_roi:
            pg = p['position_group']
            if pg not in pos_group_summary:
                pos_group_summary[pg] = {
                    'label': p['position_label'],
                    'scores': [],
                }
            pos_group_summary[pg]['scores'].append(p['contribution']['score'])

        for pg, data in pos_group_summary.items():
            scores = data['scores']
            data['avg_contribution'] = round(sum(scores) / len(scores), 2)
            data['max_contribution'] = round(max(scores), 2)
            data['count'] = len(scores)
            del data['scores']

        # 에이스 & 약점 포지션 찾기
        ace = squad_roi[0] if squad_roi else None
        weakest_pg = min(pos_group_summary.items(),
                         key=lambda x: x[1]['avg_contribution'],
                         default=(None, {}))[0] if pos_group_summary else None

        summary = {
            'total_players_analyzed': len(squad_roi),
            'players_with_price':     0,
            'avg_roi':                round(
                sum(p['contribution']['score'] for p in squad_roi) / len(squad_roi), 2
            ) if squad_roi else 0.0,
            'best_value_player':      ace['player_name'] if ace else None,
            'worst_value_player':     squad_roi[-1]['player_name'] if squad_roi else None,
            'position_group_summary': pos_group_summary,
            'trade_data_reliable':    False,
            'estimated_price_count':  0,
        }

        insights = cls._generate_insights(squad_roi, pos_group_summary, weakest_pg)

        return {
            'squad_roi': squad_roi,
            'summary':   summary,
            'insights':  insights,
        }

    @staticmethod
    def _generate_insights(
        squad_roi: List[Dict],
        pos_group_summary: Dict,
        weakest_pg: Optional[str],
    ) -> List[str]:
        insights = []

        if not squad_roi:
            return ['분석할 경기 데이터가 부족합니다.']

        # 에이스 선수
        ace = squad_roi[0]
        insights.append(
            f"⭐ {ace['player_name']}({ace['position_label']})이(가) 팀 최고 기여도를 기록 중입니다 "
            f"(기여도 {ace['contribution']['score']:.1f}점 · "
            f"{ace['appearances']}경기)"
        )

        # 약점 포지션
        if weakest_pg and pos_group_summary.get(weakest_pg, {}).get('avg_contribution', 99) < 4.0:
            info = pos_group_summary[weakest_pg]
            insights.append(
                f"⚠️ {info['label']} 라인 평균 기여도가 {info['avg_contribution']:.1f}점으로 낮습니다. "
                f"해당 포지션 활용법 점검이 필요합니다."
            )

        # 에이스급(10점+) 선수 수
        aces = [p for p in squad_roi if p['contribution']['score'] >= 10.0]
        if aces:
            ace_names = ', '.join(p['player_name'] for p in aces[:3])
            insights.append(f"👑 핵심 선수 ({len(aces)}명): {ace_names}")

        # 하위 기여도 선수 경고
        low = [p for p in squad_roi if p['contribution']['score'] < 2.5 and p['appearances'] >= 5]
        if low:
            low_names = ', '.join(p['player_name'] for p in low[:2])
            insights.append(
                f"🔻 {low_names} — 출전 경기 대비 기여도가 낮습니다. "
                f"포지션 변경 또는 전술 조정을 고려하세요."
            )

        return insights
