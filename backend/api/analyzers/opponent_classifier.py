"""
Opponent Type Classifier & Win Rate Map — D2
내 매치 기록 안에 있는 상대팀 데이터를 K-means로 6개 유형으로 분류.
유형별 내 승률/성적/취약점 분석.
"""
import math
from typing import List, Dict, Any, Optional
from collections import defaultdict


class OpponentClassifier:
    """상대 유형 분류기"""

    # 6개 유형 정의 (K-means centroid 기반으로 사후 레이블링)
    ARCHETYPES = [
        {
            'id': 'possession',
            'label': '점유형',
            'emoji': '🎯',
            'description': '높은 점유율과 짧은 패스로 경기를 지배하는 팀',
            'typical_traits': '점유율 55%+, 단패 비율 높음, 세트피스 의존 낮음',
            'weakness': '고압박 시 빌드업 실패, 깊은 수비 시 득점 어려움',
        },
        {
            'id': 'direct_counter',
            'label': '직접형 카운터',
            'emoji': '⚡',
            'description': '빠른 전진 패스와 카운터 어택을 주로 사용하는 팀',
            'typical_traits': '점유율 낮음, 장패 비율 높음, 득점력은 강함',
            'weakness': '볼 점유 시 역습 기회 감소, 수비 라인 높이면 압박 가능',
        },
        {
            'id': 'wide_overload',
            'label': '측면 과부하형',
            'emoji': '↔️',
            'description': '측면 크로스와 윙어를 활용하는 팀',
            'typical_traits': '슛 x좌표 분산 높음, 공중볼 경합 많음',
            'weakness': '크로스 대응 수비 강화 시 효과 감소',
        },
        {
            'id': 'setpiece',
            'label': '세트피스 의존형',
            'emoji': '⚽',
            'description': '코너킥/프리킥으로 주로 득점하는 팀',
            'typical_traits': '세트피스 득점 비율 30%+, 헤딩 득점 많음',
            'weakness': '세트피스 수비 특화 시 득점 기회 크게 감소',
        },
        {
            'id': 'balanced',
            'label': '균형형',
            'emoji': '⚖️',
            'description': '다양한 공격 루트를 고르게 사용하는 팀',
            'typical_traits': '모든 지표가 평균 근처, 예측 어려움',
            'weakness': '특정 약점이 없어 분석이 어려움, 집중력 유지 필요',
        },
        {
            'id': 'high_press',
            'label': '고압박형',
            'emoji': '🔥',
            'description': '강한 압박으로 상대 실수를 유도하는 팀',
            'typical_traits': '수비 태클 많음, 점유율 50% 근처, 상대 패스 정확도 낮춤',
            'weakness': '체력 소모, 역습 공간 노출',
        },
    ]

    @staticmethod
    def _extract_opponent_features(raw_data: Dict, user_ouid: str) -> Optional[Dict[str, float]]:
        """
        매치 raw_data에서 상대방 특성 추출.
        상대방 matchInfo를 찾아 분석.
        """
        match_info_list = raw_data.get('matchInfo', [])
        opponent_info = None

        for info in match_info_list:
            if info.get('ouid') != user_ouid:
                opponent_info = info
                break

        if not opponent_info:
            return None

        # Possession
        match_detail = opponent_info.get('matchDetail') or {}
        possession = float(match_detail.get('possession', 50) or 50)

        # Pass data
        pass_data = opponent_info.get('pass') or {}
        if isinstance(pass_data, dict):
            pass_try = float(pass_data.get('passTry', 1) or 1)
            short_pass = float(pass_data.get('shortPassTry', 0) or 0)
            long_pass = float(pass_data.get('longPassTry', 0) or 0)
            through_pass = float(pass_data.get('throughPassTry', 0) or 0)
            pass_success = float(pass_data.get('passSuccess', 0) or 0)
        else:
            pass_try = 1
            short_pass = long_pass = through_pass = pass_success = 0

        short_ratio = short_pass / max(pass_try, 1)
        long_ratio = long_pass / max(pass_try, 1)
        through_ratio = through_pass / max(pass_try, 1)
        pass_accuracy = pass_success / max(pass_try, 1)

        # Shooting
        shoot_data = opponent_info.get('shoot') or {}
        total_shots = float(shoot_data.get('shootTotal', 0) or 0)

        # Get shot x-coord std (attack width) from shootDetail
        shoot_detail = raw_data.get('shootDetail') or []
        # Filter to opponent shots (heuristic: all shots in raw or filter by team)
        x_coords = [float(s.get('x', 0.5)) for s in shoot_detail if s.get('x') is not None]
        if len(x_coords) >= 3:
            mean_x = sum(x_coords) / len(x_coords)
            variance = sum((x - mean_x) ** 2 for x in x_coords) / len(x_coords)
            attack_width = math.sqrt(variance)
        else:
            attack_width = 0.15  # default

        # Defense data
        defence_data = opponent_info.get('defence') or {}
        if isinstance(defence_data, dict):
            tackle_try = float(defence_data.get('tackleTry', 0) or 0)
            block = float(defence_data.get('block', 0) or 0)
        else:
            tackle_try = block = 0

        defensive_actions = tackle_try + block

        return {
            'possession': possession / 100,          # 0-1
            'short_ratio': short_ratio,              # 0-1
            'long_ratio': long_ratio,                # 0-1
            'through_ratio': through_ratio,          # 0-1
            'pass_accuracy': pass_accuracy,          # 0-1
            'attack_width': attack_width,            # 0-0.3+
            'total_shots': min(total_shots / 20, 1), # normalized
            'defensive_actions': min(defensive_actions / 30, 1),  # normalized
        }

    @staticmethod
    def _euclidean_distance(a: Dict[str, float], b: Dict[str, float]) -> float:
        """두 특성 벡터 간의 유클리드 거리"""
        keys = set(a.keys()) & set(b.keys())
        return math.sqrt(sum((a[k] - b[k]) ** 2 for k in keys))

    @staticmethod
    def _get_archetype_centroids() -> List[Dict[str, float]]:
        """
        6개 유형의 중심점 (도메인 지식 기반 초기화).
        실제 K-means 대신 도메인 지식 기반 분류 사용 (scikit-learn 불필요).
        """
        return [
            # 0: 점유형
            {'possession': 0.60, 'short_ratio': 0.55, 'long_ratio': 0.20, 'through_ratio': 0.08,
             'pass_accuracy': 0.88, 'attack_width': 0.12, 'total_shots': 0.50, 'defensive_actions': 0.40},
            # 1: 직접형 카운터
            {'possession': 0.40, 'short_ratio': 0.35, 'long_ratio': 0.45, 'through_ratio': 0.06,
             'pass_accuracy': 0.75, 'attack_width': 0.13, 'total_shots': 0.65, 'defensive_actions': 0.35},
            # 2: 측면 과부하형
            {'possession': 0.50, 'short_ratio': 0.45, 'long_ratio': 0.30, 'through_ratio': 0.05,
             'pass_accuracy': 0.80, 'attack_width': 0.22, 'total_shots': 0.60, 'defensive_actions': 0.38},
            # 3: 세트피스 의존형
            {'possession': 0.48, 'short_ratio': 0.40, 'long_ratio': 0.35, 'through_ratio': 0.04,
             'pass_accuracy': 0.78, 'attack_width': 0.14, 'total_shots': 0.45, 'defensive_actions': 0.50},
            # 4: 균형형
            {'possession': 0.50, 'short_ratio': 0.45, 'long_ratio': 0.30, 'through_ratio': 0.08,
             'pass_accuracy': 0.82, 'attack_width': 0.15, 'total_shots': 0.55, 'defensive_actions': 0.45},
            # 5: 고압박형
            {'possession': 0.52, 'short_ratio': 0.48, 'long_ratio': 0.25, 'through_ratio': 0.10,
             'pass_accuracy': 0.83, 'attack_width': 0.15, 'total_shots': 0.58, 'defensive_actions': 0.70},
        ]

    @classmethod
    def _classify_opponent(cls, features: Dict[str, float]) -> int:
        """특성 벡터를 가장 가까운 유형 중심점으로 분류"""
        centroids = cls._get_archetype_centroids()
        distances = [cls._euclidean_distance(features, c) for c in centroids]
        return distances.index(min(distances))

    @classmethod
    def classify_opponents(
        cls,
        matches: List[Dict],  # Match objects with raw_data
        user_ouid: str,
    ) -> Dict[str, Any]:
        """
        상대 유형 분류 및 유형별 승률 분석.

        Args:
            matches: Match 딕셔너리 목록 (raw_data 포함)
            user_ouid: 사용자 OUID

        Returns:
            {archetype_summary, win_rate_map, nemesis_type, insights}
        """
        if len(matches) < 10:
            return {
                **cls._empty_result(),
                'insights': ['상대 유형 분류에는 최소 10경기 이상의 데이터가 필요합니다.'],
            }

        # Classify each match's opponent
        archetype_stats: Dict[int, Dict] = {i: {
            'wins': 0, 'losses': 0, 'draws': 0,
            'goals_for': 0, 'goals_against': 0, 'match_count': 0,
            'matches': []
        } for i in range(6)}

        classified_count = 0
        for match in matches:
            raw_data = match.get('raw_data') or {}
            if not raw_data:
                continue

            features = cls._extract_opponent_features(raw_data, user_ouid)
            if features is None:
                continue

            archetype_idx = cls._classify_opponent(features)
            result = match.get('result', 'lose')
            goals_for = match.get('goals_for', 0)
            goals_against = match.get('goals_against', 0)

            stats = archetype_stats[archetype_idx]
            stats['match_count'] += 1
            stats['goals_for'] += goals_for
            stats['goals_against'] += goals_against
            if result == 'win':
                stats['wins'] += 1
            elif result == 'lose':
                stats['losses'] += 1
            else:
                stats['draws'] += 1

            classified_count += 1

        # Build summary
        archetype_summary = []
        for idx, archetype_info in enumerate(cls.ARCHETYPES):
            stats = archetype_stats[idx]
            count = stats['match_count']
            if count == 0:
                continue

            win_rate = round(stats['wins'] / count * 100, 1)
            avg_gf = round(stats['goals_for'] / count, 2)
            avg_ga = round(stats['goals_against'] / count, 2)

            archetype_summary.append({
                'archetype_id': archetype_info['id'],
                'label': archetype_info['label'],
                'emoji': archetype_info['emoji'],
                'description': archetype_info['description'],
                'typical_traits': archetype_info['typical_traits'],
                'weakness': archetype_info['weakness'],
                'match_count': count,
                'win_rate': win_rate,
                'wins': stats['wins'],
                'losses': stats['losses'],
                'draws': stats['draws'],
                'avg_goals_for': avg_gf,
                'avg_goals_against': avg_ga,
                'avg_goal_diff': round(avg_gf - avg_ga, 2),
                'frequency_pct': round(count / classified_count * 100, 1) if classified_count > 0 else 0,
            })

        # Sort by frequency
        archetype_summary.sort(key=lambda x: x['match_count'], reverse=True)

        # Nemesis type (lowest win rate with enough matches)
        nemesis = None
        enough = [a for a in archetype_summary if a['match_count'] >= 3]
        if enough:
            nemesis = min(enough, key=lambda x: x['win_rate'])

        # Best matchup type (highest win rate)
        best_matchup = None
        if enough:
            best_matchup = max(enough, key=lambda x: x['win_rate'])

        insights = cls._generate_insights(archetype_summary, nemesis, best_matchup, classified_count)

        return {
            'total_classified': classified_count,
            'archetype_summary': archetype_summary,
            'nemesis_type': nemesis,
            'best_matchup': best_matchup,
            'insights': insights,
        }

    @staticmethod
    def _generate_insights(
        summary: List[Dict],
        nemesis: Optional[Dict],
        best: Optional[Dict],
        total: int,
    ) -> List[str]:
        insights = []

        if nemesis:
            insights.append(
                f"🚨 천적 유형 발견: {nemesis['label']} {nemesis['emoji']} — "
                f"{nemesis['match_count']}경기에서 승률 {nemesis['win_rate']}%. "
                f"약점: {nemesis['weakness']}"
            )

        if best and best != nemesis:
            insights.append(
                f"✅ 강점 유형: {best['label']} {best['emoji']} — "
                f"승률 {best['win_rate']}%로 가장 좋은 성적."
            )

        if summary:
            most_common = summary[0]
            insights.append(
                f"📊 가장 많이 만나는 상대: {most_common['label']} "
                f"({most_common['frequency_pct']}%, {most_common['match_count']}경기)"
            )

        return insights

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            'total_classified': 0,
            'archetype_summary': [],
            'nemesis_type': None,
            'best_matchup': None,
            'insights': [],
        }
