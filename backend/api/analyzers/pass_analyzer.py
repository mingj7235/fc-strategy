"""
Pass Analyzer
Advanced pass analysis system including xA, key passes, progressive passing, and pass networks
"""
from typing import List, Dict, Any, Tuple
import math
from collections import defaultdict

from api.analyzers.metrics.xa_calculator import XACalculator
from nexon_api.metadata import MetadataLoader


class PassAnalyzer:
    """
    Comprehensive pass analysis system

    Analyzes:
    - Pass completion by zone
    - Key passes and xA (Expected Assists)
    - Progressive passing
    - Pass network (who passes to whom)
    - Pass under pressure
    - Build-up contribution
    """

    # Field zones for analysis
    ZONES = {
        'defensive_third': (0.0, 0.33),
        'middle_third': (0.33, 0.67),
        'attacking_third': (0.67, 1.0),
    }

    @classmethod
    def analyze_passes(cls,
                      match_data: Dict[str, Any],
                      player_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main pass analysis function

        Args:
            match_data: Match raw_data containing pass information
            player_performances: List of PlayerPerformance data

        Returns:
            Comprehensive pass analysis dictionary
        """
        # Extract pass data from match (if available)
        # Note: Nexon API may not provide detailed pass locations
        # We'll work with aggregate data for now

        total_attempts = sum(p.get('pass_attempts', 0) for p in player_performances)
        total_success = sum(p.get('pass_success', 0) for p in player_performances)

        if total_attempts == 0:
            return cls._empty_analysis()

        overall_accuracy = (total_success / total_attempts) * 100

        # Calculate metrics from PlayerPerformance data
        key_pass_analysis = cls._analyze_key_passes(player_performances, match_data)
        progressive_analysis = cls._estimate_progressive_passes(player_performances)
        pass_network = cls._build_pass_network(player_performances)
        efficiency_analysis = cls._analyze_pass_efficiency(player_performances)

        # Generate insights
        insights = cls._generate_pass_insights(
            overall_accuracy,
            key_pass_analysis,
            progressive_analysis,
            efficiency_analysis
        )

        return {
            'overall_stats': {
                'total_attempts': total_attempts,
                'total_success': total_success,
                'accuracy': round(overall_accuracy, 1),
            },
            'key_pass_analysis': key_pass_analysis,
            'progressive_passing': progressive_analysis,
            'pass_network': pass_network,
            'efficiency': efficiency_analysis,
            'insights': insights
        }

    @classmethod
    def _analyze_key_passes(cls,
                           player_performances: List[Dict[str, Any]],
                           match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze key passes (passes leading to shots)
        Estimate xA based on assists and shot data
        """
        total_assists = sum(p.get('assists', 0) for p in player_performances)
        total_shots = match_data.get('shots', 0)

        # Estimate key passes (rough approximation)
        # Typically 20-30% of shots come from key passes
        estimated_key_passes = int(total_shots * 0.25)

        # Estimate xA based on assists and shots
        # Each assist typically has xA of 0.3-0.5
        # Additional key passes have lower xA
        estimated_xa = total_assists * 0.4 + (estimated_key_passes - total_assists) * 0.15

        return {
            'total_assists': total_assists,
            'estimated_key_passes': estimated_key_passes,
            'estimated_xa': round(estimated_xa, 2),
            'xa_per_key_pass': round(estimated_xa / estimated_key_passes, 2) if estimated_key_passes > 0 else 0,
            'conversion_rate': round((total_assists / estimated_key_passes * 100), 1) if estimated_key_passes > 0 else 0
        }

    @classmethod
    def _estimate_progressive_passes(cls, player_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Estimate progressive passes (passes moving ball forward significantly)
        Based on pass success rate and player positions
        """
        # Estimate based on pass volume and position
        midfielders = [p for p in player_performances if 14 <= p.get('position', 0) <= 19]
        attackers = [p for p in player_performances if 21 <= p.get('position', 0) <= 27]

        midfielder_passes = sum(p.get('pass_attempts', 0) for p in midfielders)
        attacker_passes = sum(p.get('pass_attempts', 0) for p in attackers)

        # Estimate 15-25% of midfielder passes are progressive
        # Estimate 10-15% of attacker passes are progressive
        estimated_progressive = int(midfielder_passes * 0.20 + attacker_passes * 0.12)

        total_passes = sum(p.get('pass_attempts', 0) for p in player_performances)
        progressive_rate = (estimated_progressive / total_passes * 100) if total_passes > 0 else 0

        return {
            'estimated_progressive_passes': estimated_progressive,
            'progressive_rate': round(progressive_rate, 1),
            'midfielder_contribution': round((midfielder_passes * 0.20 / estimated_progressive * 100), 1) if estimated_progressive > 0 else 0
        }

    @classmethod
    def _build_pass_network(cls, player_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build pass network showing connections between players
        """
        # Aggregate by base player_id (spid % 1000000) to merge all season cards
        # of the same real-world player (e.g. TOTY Zidane + Icon Zidane → one entry)
        aggregated: Dict[int, Dict[str, Any]] = {}
        for p in player_performances:
            spid = p.get('spid')
            player_id = spid % 1000000 if spid else spid
            if player_id not in aggregated:
                season_id = p.get('season_id')
                season_info = MetadataLoader.get_season_info(season_id) if season_id else {'name': '', 'img': ''}
                aggregated[player_id] = {
                    'spid': spid,  # keep representative spid for image URL
                    'player_name': p.get('player_name', 'Unknown'),
                    'season_id': season_id,
                    'season_name': season_info['name'] or p.get('season_name'),
                    'season_img': season_info['img'],
                    'image_url': f"https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png" if spid else None,
                    'pass_attempts': 0,
                    'pass_success': 0,
                }
            aggregated[player_id]['pass_attempts'] += p.get('pass_attempts', 0)
            aggregated[player_id]['pass_success'] += p.get('pass_success', 0)

        aggregated_list = list(aggregated.values())

        # Sort by total pass attempts to find main passers
        sorted_players = sorted(
            aggregated_list,
            key=lambda p: p.get('pass_attempts', 0),
            reverse=True
        )

        top_passers = sorted_players[:3] if len(sorted_players) >= 3 else sorted_players

        network = {
            'top_passers': [
                {
                    'spid': p['spid'],
                    'player_name': p['player_name'],
                    'season_id': p['season_id'],
                    'season_name': p['season_name'],
                    'season_img': p.get('season_img', ''),
                    'image_url': p['image_url'],
                    'pass_attempts': p['pass_attempts'],
                    'pass_success': p['pass_success'],
                    'pass_success_rate': round(
                        (p['pass_success'] / p['pass_attempts'] * 100), 1
                    ) if p['pass_attempts'] > 0 else 0
                }
                for p in top_passers
            ],
            'total_connections': len(aggregated_list),
            'avg_passes_per_player': round(
                sum(p['pass_attempts'] for p in aggregated_list) / len(aggregated_list), 1
            ) if aggregated_list else 0
        }

        return network

    @classmethod
    def _analyze_pass_efficiency(cls, player_performances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze overall passing efficiency
        """
        total_attempts = sum(p.get('pass_attempts', 0) for p in player_performances)
        total_success = sum(p.get('pass_success', 0) for p in player_performances)
        total_assists = sum(p.get('assists', 0) for p in player_performances)

        # Passes per assist (lower is better)
        passes_per_assist = total_attempts / total_assists if total_assists > 0 else 999

        # Risk/Reward ratio
        # High accuracy with assists = good balance
        # Low accuracy with assists = risky but effective
        # High accuracy without assists = safe but ineffective
        if total_attempts > 0:
            accuracy = (total_success / total_attempts) * 100
            if total_assists > 0:
                assist_rate = (total_assists / total_attempts) * 100
                risk_reward = 'balanced' if accuracy >= 80 else 'aggressive'
            else:
                risk_reward = 'conservative'
        else:
            accuracy = 0
            assist_rate = 0
            risk_reward = 'unknown'

        return {
            'passes_per_assist': round(passes_per_assist, 1),
            'assist_rate': round((total_assists / total_attempts * 100), 2) if total_attempts > 0 else 0,
            'risk_reward_profile': risk_reward,
            'efficiency_score': cls._calculate_efficiency_score(accuracy, total_assists, total_attempts)
        }

    @classmethod
    def _calculate_efficiency_score(cls, accuracy: float, assists: int, attempts: int) -> float:
        """
        Calculate overall pass efficiency score (0-100)
        """
        # Weight accuracy and productivity
        accuracy_score = min(100, accuracy * 1.1)  # 90% accuracy = 99
        productivity_score = min(100, (assists / attempts * 1000)) if attempts > 0 else 0

        # Weighted average (accuracy 70%, productivity 30%)
        efficiency = accuracy_score * 0.7 + productivity_score * 0.3
        return round(efficiency, 1)

    @classmethod
    def _generate_pass_insights(cls,
                                accuracy: float,
                                key_passes: Dict[str, Any],
                                progressive: Dict[str, Any],
                                efficiency: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate insights using Keep-Stop-Action framework
        """
        keep = []
        stop = []
        action_items = []

        # Accuracy analysis
        if accuracy >= 88:
            keep.append(f"뛰어난 패스 정확도 ({accuracy:.1f}%)")
        elif accuracy >= 80:
            keep.append(f"안정적인 패스 정확도 ({accuracy:.1f}%)")
        elif accuracy < 75:
            stop.append(f"낮은 패스 정확도 ({accuracy:.1f}%) - 무리한 패스 줄이기")

        # Key pass analysis
        xa = key_passes.get('estimated_xa', 0)
        if xa >= 1.0:
            keep.append(f"우수한 찬스 창출 능력 (xA: {xa:.2f})")
        elif xa < 0.5:
            action_items.append("킬패스 빈도를 높이세요 - 최종 3분의 1 지역에서 위험한 패스 시도")

        # Assist conversion
        conversion = key_passes.get('conversion_rate', 0)
        if conversion >= 30:
            keep.append(f"높은 어시스트 전환율 ({conversion:.1f}%)")
        elif conversion < 15:
            action_items.append("마무리가 좋은 선수에게 패스하거나, 더 좋은 위치에서 패스하세요")

        # Progressive passing
        prog_rate = progressive.get('progressive_rate', 0)
        if prog_rate >= 20:
            keep.append("적극적인 전진 패스")
        elif prog_rate < 12:
            stop.append("너무 보수적인 패스 플레이")
            action_items.append("더 많은 전진 패스로 빠른 공격 전개를 시도하세요")

        # Efficiency
        if efficiency['risk_reward_profile'] == 'conservative':
            action_items.append("패스 정확도는 좋지만 창조성이 부족합니다. 리스크를 감수한 패스를 더 시도하세요")
        elif efficiency['risk_reward_profile'] == 'aggressive':
            keep.append("공격적인 패스 스타일로 찬스를 많이 만듭니다")

        # Default recommendations
        if not action_items:
            action_items.append("현재 패스 플레이를 유지하면서 일관성을 높이세요")

        return {
            'keep': keep,
            'stop': stop,
            'action_items': action_items
        }

    @classmethod
    def _empty_analysis(cls) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'overall_stats': {
                'total_attempts': 0,
                'total_success': 0,
                'accuracy': 0,
            },
            'key_pass_analysis': {
                'total_assists': 0,
                'estimated_key_passes': 0,
                'estimated_xa': 0,
                'xa_per_key_pass': 0,
                'conversion_rate': 0
            },
            'progressive_passing': {
                'estimated_progressive_passes': 0,
                'progressive_rate': 0,
                'midfielder_contribution': 0
            },
            'pass_network': {
                'top_passers': [],
                'total_connections': 0,
                'avg_passes_per_player': 0
            },
            'efficiency': {
                'passes_per_assist': 0,
                'assist_rate': 0,
                'risk_reward_profile': 'unknown',
                'efficiency_score': 0
            },
            'insights': {
                'keep': [],
                'stop': [],
                'action_items': ['패스 데이터가 충분하지 않습니다']
            }
        }
