"""
Assist Network Analyzer

어시스트 네트워크 분석 - 선수 간 연결성, 찬스 메이킹 패턴 분석
"""

from typing import List, Dict, Any, Tuple
from decimal import Decimal
import math
from collections import defaultdict


class AssistNetworkAnalyzer:
    """어시스트 네트워크 분석기"""

    @classmethod
    def analyze_assists(cls, shot_details: List[Dict]) -> Dict[str, Any]:
        """
        어시스트 네트워크 종합 분석

        Args:
            shot_details: ShotDetail 쿼리셋 값 리스트

        Returns:
            Dict containing:
            - assist_heatmap: 어시스트 발생 위치 히트맵
            - player_network: 선수 간 어시스트 네트워크
            - assist_types: 어시스트 타입 분석
            - assist_distance_stats: 어시스트 거리 통계
            - top_playmakers: 찬스 메이커 TOP 선수
        """
        # 골로 연결된 샷만 필터링 (어시스트가 의미 있는 경우)
        goals = [shot for shot in shot_details if shot.get('result') == 'goal']

        if not goals:
            return cls._empty_analysis()

        # 1. 어시스트 히트맵 데이터
        assist_heatmap = cls._build_assist_heatmap(goals)

        # 2. 선수 간 네트워크 (A선수 → B선수)
        player_network = cls._build_player_network(goals)

        # 3. 어시스트 타입 분석 (측면 vs 중앙)
        assist_types = cls._analyze_assist_types(goals)

        # 4. 어시스트 거리 통계
        distance_stats = cls._calculate_assist_distances(goals)

        # 5. 찬스 메이커 랭킹
        top_playmakers = cls._rank_playmakers(player_network)

        return {
            'assist_heatmap': assist_heatmap,
            'player_network': player_network,
            'assist_types': assist_types,
            'assist_distance_stats': distance_stats,
            'top_playmakers': top_playmakers,
            'total_goals': len(goals),
            'goals_with_assist': len([g for g in goals if g.get('assist_spid')]),
        }

    @classmethod
    def _build_assist_heatmap(cls, goals: List[Dict]) -> List[Dict]:
        """
        어시스트 발생 위치 히트맵 데이터 생성

        Returns:
            List of {x, y, count} for heatmap visualization
        """
        heatmap_data = []

        for goal in goals:
            assist_x = goal.get('assist_x')
            assist_y = goal.get('assist_y')
            assist_spid = goal.get('assist_spid')

            # assist_spid가 None이면 어시스트 없음 (예: 개인 플레이, 자책골 등)
            if assist_spid is None:
                continue

            if assist_x is not None and assist_y is not None:
                heatmap_data.append({
                    'x': float(assist_x),
                    'y': float(assist_y),
                    'shooter_spid': goal.get('shooter_spid'),
                    'assist_spid': assist_spid,
                    'goal_time': goal.get('goal_time', 0),
                })

        return heatmap_data

    @classmethod
    def _build_player_network(cls, goals: List[Dict]) -> List[Dict]:
        """
        선수 간 어시스트 네트워크 구축

        Returns:
            List of {from_spid, to_spid, count} - A선수가 B선수에게 몇 번 어시스트
        """
        # {(assist_spid, shooter_spid): count}
        network = defaultdict(int)

        for goal in goals:
            assist_spid = goal.get('assist_spid')
            shooter_spid = goal.get('shooter_spid')

            if assist_spid and shooter_spid:
                network[(assist_spid, shooter_spid)] += 1

        # Convert to list format
        network_list = [
            {
                'from_spid': from_spid,
                'to_spid': to_spid,
                'assists': count,
            }
            for (from_spid, to_spid), count in network.items()
        ]

        # Sort by assists count (descending)
        network_list.sort(key=lambda x: x['assists'], reverse=True)

        return network_list

    @classmethod
    def _analyze_assist_types(cls, goals: List[Dict]) -> Dict[str, Any]:
        """
        어시스트 타입 분석: 측면 vs 중앙 vs 후방 지원

        Returns:
            Dict with:
            - wing_assists: 측면 어시스트 (y < 0.3 or y > 0.7)
            - central_assists: 중앙 어시스트 (0.3 <= y <= 0.7)
            - deep_assists: 후방 지원 (x < 0.5)
            - forward_assists: 전방 지원 (x >= 0.5)
        """
        wing_count = 0
        central_count = 0
        deep_count = 0
        forward_count = 0
        total_with_assist = 0

        for goal in goals:
            assist_x = goal.get('assist_x')
            assist_y = goal.get('assist_y')
            assist_spid = goal.get('assist_spid')

            if assist_spid is None or assist_x is None or assist_y is None:
                continue

            total_with_assist += 1

            # Convert to float for comparison
            ax = float(assist_x)
            ay = float(assist_y)

            # 측면 vs 중앙
            if ay < 0.3 or ay > 0.7:
                wing_count += 1
            else:
                central_count += 1

            # 후방 vs 전방
            if ax < 0.5:
                deep_count += 1
            else:
                forward_count += 1

        return {
            'wing_assists': wing_count,
            'central_assists': central_count,
            'deep_assists': deep_count,
            'forward_assists': forward_count,
            'total_assists': total_with_assist,
            'wing_percentage': round((wing_count / total_with_assist * 100) if total_with_assist > 0 else 0, 1),
            'central_percentage': round((central_count / total_with_assist * 100) if total_with_assist > 0 else 0, 1),
        }

    @classmethod
    def _calculate_assist_distances(cls, goals: List[Dict]) -> Dict[str, Any]:
        """
        어시스트 거리 계산 (어시스트 위치 → 슈팅 위치)

        Returns:
            Dict with:
            - avg_distance: 평균 어시스트 거리
            - max_distance: 최대 거리 (롱패스)
            - min_distance: 최소 거리 (숏패스)
            - short_passes: 짧은 패스 (<0.2 거리)
            - long_passes: 긴 패스 (>0.4 거리)
        """
        distances = []

        for goal in goals:
            assist_x = goal.get('assist_x')
            assist_y = goal.get('assist_y')
            shot_x = goal.get('x')
            shot_y = goal.get('y')
            assist_spid = goal.get('assist_spid')

            if assist_spid is None or None in [assist_x, assist_y, shot_x, shot_y]:
                continue

            # Euclidean distance
            distance = math.sqrt(
                (float(shot_x) - float(assist_x))**2 +
                (float(shot_y) - float(assist_y))**2
            )
            distances.append(distance)

        if not distances:
            return {
                'avg_distance': 0.0,
                'max_distance': 0.0,
                'min_distance': 0.0,
                'short_passes': 0,
                'long_passes': 0,
            }

        short_passes = sum(1 for d in distances if d < 0.2)
        long_passes = sum(1 for d in distances if d > 0.4)

        return {
            'avg_distance': round(sum(distances) / len(distances), 3),
            'max_distance': round(max(distances), 3),
            'min_distance': round(min(distances), 3),
            'short_passes': short_passes,
            'long_passes': long_passes,
            'total_measured': len(distances),
        }

    @classmethod
    def _rank_playmakers(cls, player_network: List[Dict]) -> List[Dict]:
        """
        찬스 메이커 랭킹 (어시스트를 가장 많이 한 선수)

        Returns:
            List of {spid, total_assists} sorted by assists
        """
        # Aggregate assists by spid
        playmaker_stats = defaultdict(int)

        for connection in player_network:
            from_spid = connection['from_spid']
            assists = connection['assists']
            playmaker_stats[from_spid] += assists

        # Convert to list and sort
        playmakers = [
            {'spid': spid, 'total_assists': assists}
            for spid, assists in playmaker_stats.items()
        ]
        playmakers.sort(key=lambda x: x['total_assists'], reverse=True)

        # Return top 5
        return playmakers[:5]

    @classmethod
    def _empty_analysis(cls) -> Dict[str, Any]:
        """빈 분석 결과 반환 (골이 없는 경우)"""
        return {
            'assist_heatmap': [],
            'player_network': [],
            'assist_types': {
                'wing_assists': 0,
                'central_assists': 0,
                'deep_assists': 0,
                'forward_assists': 0,
                'total_assists': 0,
                'wing_percentage': 0,
                'central_percentage': 0,
            },
            'assist_distance_stats': {
                'avg_distance': 0.0,
                'max_distance': 0.0,
                'min_distance': 0.0,
                'short_passes': 0,
                'long_passes': 0,
                'total_measured': 0,
            },
            'top_playmakers': [],
            'total_goals': 0,
            'goals_with_assist': 0,
        }
