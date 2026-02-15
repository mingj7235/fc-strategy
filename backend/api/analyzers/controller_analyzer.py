"""
Controller Analysis
키보드 vs 패드 플레이 스타일 분석 및 비교
"""
from typing import Dict, Any, List
from collections import defaultdict


class ControllerAnalyzer:
    """
    컨트롤러 분석기
    - 키보드 vs 패드 승률 비교
    - 컨트롤러별 플레이 스타일 차이
    - 컨트롤러 변경 추천
    """

    @classmethod
    def analyze_controller_performance(cls, matches: List[Dict[str, Any]], ouid: str = None) -> Dict[str, Any]:
        """
        컨트롤러별 성적 및 플레이 스타일 분석

        Args:
            matches: List of match data with raw_data
            ouid: 유저 ouid (matchInfo에서 유저 정보 찾기 위해 필요)

        Returns:
            컨트롤러 분석 결과
        """
        if not matches:
            return cls._empty_analysis()

        # 컨트롤러별 데이터 수집
        controller_stats = cls._collect_controller_stats(matches, ouid)

        # 컨트롤러별 승률 계산
        performance_comparison = cls._calculate_performance(controller_stats)

        # 컨트롤러별 플레이 스타일 분석
        playstyle_comparison = cls._analyze_playstyle(controller_stats)

        # 추천 생성
        recommendation = cls._generate_recommendation(
            performance_comparison,
            playstyle_comparison
        )

        # 인사이트 생성
        insights = cls._generate_insights(
            performance_comparison,
            playstyle_comparison,
            recommendation
        )

        return {
            'controller_stats': {
                'keyboard': controller_stats.get('keyboard', {}),
                'gamepad': controller_stats.get('gamepad', {})
            },
            'performance_comparison': performance_comparison,
            'playstyle_comparison': playstyle_comparison,
            'recommendation': recommendation,
            'insights': insights
        }

    @classmethod
    def _collect_controller_stats(cls, matches: List[Dict], ouid: str = None) -> Dict[str, Dict]:
        """컨트롤러별 통계 수집"""
        stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0,
            'possession': [],
            'shots': [],
            'shots_on_target': [],
            'pass_success_rate': [],
        })

        for match in matches:
            # Get controller from raw_data
            if not match.get('raw_data'):
                continue

            match_info = match['raw_data'].get('matchInfo', [])
            if not match_info:
                continue

            # Find user's matchInfo entry using ouid — fallback to first entry
            user_info = None
            if ouid:
                for entry in match_info:
                    if entry.get('ouid') == ouid:
                        user_info = entry
                        break
            if user_info is None:
                user_info = match_info[0]

            match_detail = user_info.get('matchDetail', {})
            controller = match_detail.get('controller')

            if not controller:
                continue

            # Normalize controller name
            controller = controller.lower()
            if controller not in ['keyboard', 'gamepad']:
                continue

            # Collect stats
            stats[controller]['matches'] += 1

            result = match.get('result')
            if result == 'win':
                stats[controller]['wins'] += 1
            elif result == 'draw':
                stats[controller]['draws'] += 1
            elif result == 'lose':
                stats[controller]['losses'] += 1

            stats[controller]['goals_for'] += match.get('goals_for', 0)
            stats[controller]['goals_against'] += match.get('goals_against', 0)
            stats[controller]['possession'].append(match.get('possession', 0))

            if match.get('shots') is not None:
                stats[controller]['shots'].append(match.get('shots'))
            if match.get('shots_on_target') is not None:
                stats[controller]['shots_on_target'].append(match.get('shots_on_target'))
            if match.get('pass_success_rate') is not None:
                try:
                    # Handle both float and string (Decimal serialized as string)
                    psr = float(match.get('pass_success_rate'))
                    stats[controller]['pass_success_rate'].append(psr)
                except (ValueError, TypeError):
                    pass

        return dict(stats)

    @classmethod
    def _calculate_performance(cls, controller_stats: Dict) -> Dict[str, Any]:
        """컨트롤러별 승률 및 성적 계산"""
        comparison = {}

        for controller, stats in controller_stats.items():
            matches = stats['matches']
            if matches == 0:
                continue

            wins = stats['wins']
            draws = stats['draws']
            losses = stats['losses']

            win_rate = round((wins / matches) * 100, 1) if matches > 0 else 0
            draw_rate = round((draws / matches) * 100, 1) if matches > 0 else 0
            loss_rate = round((losses / matches) * 100, 1) if matches > 0 else 0

            avg_goals_for = round(stats['goals_for'] / matches, 2) if matches > 0 else 0
            avg_goals_against = round(stats['goals_against'] / matches, 2) if matches > 0 else 0
            goal_difference = round(avg_goals_for - avg_goals_against, 2)

            comparison[controller] = {
                'matches': matches,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'win_rate': win_rate,
                'draw_rate': draw_rate,
                'loss_rate': loss_rate,
                'avg_goals_for': avg_goals_for,
                'avg_goals_against': avg_goals_against,
                'goal_difference': goal_difference
            }

        return comparison

    @classmethod
    def _analyze_playstyle(cls, controller_stats: Dict) -> Dict[str, Any]:
        """컨트롤러별 플레이 스타일 분석"""
        comparison = {}

        for controller, stats in controller_stats.items():
            matches = stats['matches']
            if matches == 0:
                continue

            # Calculate averages
            avg_possession = round(
                sum(stats['possession']) / len(stats['possession']), 1
            ) if stats['possession'] else 0

            avg_shots = round(
                sum(stats['shots']) / len(stats['shots']), 1
            ) if stats['shots'] else 0

            avg_shots_on_target = round(
                sum(stats['shots_on_target']) / len(stats['shots_on_target']), 1
            ) if stats['shots_on_target'] else 0

            avg_pass_success_rate = round(
                sum(stats['pass_success_rate']) / len(stats['pass_success_rate']), 1
            ) if stats['pass_success_rate'] else 0

            # Classify playstyle
            style_tags = []
            if avg_possession >= 55:
                style_tags.append('점유율 중시')
            elif avg_possession <= 45:
                style_tags.append('역습형')

            if avg_shots >= 15:
                style_tags.append('공격적')
            elif avg_shots <= 10:
                style_tags.append('수비적')

            if avg_pass_success_rate >= 85:
                style_tags.append('안정적 패스')

            comparison[controller] = {
                'avg_possession': avg_possession,
                'avg_shots': avg_shots,
                'avg_shots_on_target': avg_shots_on_target,
                'avg_pass_success_rate': avg_pass_success_rate,
                'style_tags': style_tags
            }

        return comparison

    @classmethod
    def _generate_recommendation(
        cls,
        performance: Dict,
        playstyle: Dict
    ) -> Dict[str, Any]:
        """컨트롤러 변경 추천"""
        if len(performance) < 2:
            return {
                'recommended_controller': None,
                'reason': '두 가지 컨트롤러 데이터가 모두 필요합니다',
                'confidence': 0
            }

        keyboard_perf = performance.get('keyboard', {})
        gamepad_perf = performance.get('gamepad', {})

        keyboard_wr = keyboard_perf.get('win_rate', 0)
        gamepad_wr = gamepad_perf.get('win_rate', 0)

        keyboard_matches = keyboard_perf.get('matches', 0)
        gamepad_matches = gamepad_perf.get('matches', 0)

        # Need at least 5 matches with each controller for reliable recommendation
        if keyboard_matches < 5 or gamepad_matches < 5:
            return {
                'recommended_controller': None,
                'reason': '각 컨트롤러로 최소 5경기 이상 플레이해야 정확한 추천이 가능합니다',
                'confidence': 0
            }

        # Calculate win rate difference
        wr_diff = abs(keyboard_wr - gamepad_wr)

        if wr_diff < 5:
            return {
                'recommended_controller': 'either',
                'reason': '두 컨트롤러 간 성적 차이가 크지 않습니다. 편한 것을 사용하세요.',
                'confidence': 50
            }

        # Determine better controller
        if keyboard_wr > gamepad_wr:
            recommended = 'keyboard'
            korean_name = '키보드'
            better_wr = keyboard_wr
            worse_wr = gamepad_wr
        else:
            recommended = 'gamepad'
            korean_name = '패드'
            better_wr = gamepad_wr
            worse_wr = keyboard_wr

        # Calculate confidence (based on sample size and win rate difference)
        min_matches = min(keyboard_matches, gamepad_matches)
        confidence = min(100, int(wr_diff * 2 + (min_matches / 20) * 100))

        reason = f"{korean_name}로 플레이할 때 승률이 {wr_diff}%p 더 높습니다 ({better_wr}% vs {worse_wr}%)"

        return {
            'recommended_controller': recommended,
            'reason': reason,
            'confidence': confidence
        }

    @classmethod
    def _generate_insights(
        cls,
        performance: Dict,
        playstyle: Dict,
        recommendation: Dict
    ) -> List[str]:
        """한국어 인사이트 생성"""
        insights = []

        # 1. 승률 비교 인사이트
        if len(performance) == 2:
            keyboard_perf = performance.get('keyboard', {})
            gamepad_perf = performance.get('gamepad', {})

            keyboard_wr = keyboard_perf.get('win_rate', 0)
            gamepad_wr = gamepad_perf.get('win_rate', 0)

            if keyboard_wr > gamepad_wr + 10:
                insights.append(
                    f"🎮 키보드 승률이 {keyboard_wr}%로 패드({gamepad_wr}%)보다 {keyboard_wr - gamepad_wr}%p 높습니다!"
                )
            elif gamepad_wr > keyboard_wr + 10:
                insights.append(
                    f"🎮 패드 승률이 {gamepad_wr}%로 키보드({keyboard_wr}%)보다 {gamepad_wr - keyboard_wr}%p 높습니다!"
                )
            else:
                insights.append(
                    "⚖️ 두 컨트롤러 간 승률 차이가 크지 않습니다. 편한 것을 사용하세요."
                )

        # 2. 플레이 스타일 비교
        if len(playstyle) == 2:
            keyboard_style = playstyle.get('keyboard', {})
            gamepad_style = playstyle.get('gamepad', {})

            keyboard_poss = keyboard_style.get('avg_possession', 0)
            gamepad_poss = gamepad_style.get('avg_possession', 0)

            if abs(keyboard_poss - gamepad_poss) >= 5:
                if keyboard_poss > gamepad_poss:
                    insights.append(
                        f"📊 키보드로 플레이할 때 점유율이 {keyboard_poss - gamepad_poss}%p 더 높습니다 (키보드 {keyboard_poss}% vs 패드 {gamepad_poss}%)"
                    )
                else:
                    insights.append(
                        f"📊 패드로 플레이할 때 점유율이 {gamepad_poss - keyboard_poss}%p 더 높습니다 (패드 {gamepad_poss}% vs 키보드 {keyboard_poss}%)"
                    )

            keyboard_shots = keyboard_style.get('avg_shots', 0)
            gamepad_shots = gamepad_style.get('avg_shots', 0)

            if abs(keyboard_shots - gamepad_shots) >= 3:
                if keyboard_shots > gamepad_shots:
                    insights.append(
                        f"⚽ 키보드로 플레이할 때 슈팅이 {keyboard_shots - gamepad_shots}회 더 많습니다"
                    )
                else:
                    insights.append(
                        f"⚽ 패드로 플레이할 때 슈팅이 {gamepad_shots - keyboard_shots}회 더 많습니다"
                    )

        # 3. 추천 인사이트
        if recommendation.get('recommended_controller') and recommendation['confidence'] >= 70:
            insights.append(
                f"💡 {recommendation['reason']}"
            )

        # 4. 스타일 태그 인사이트
        for controller, style in playstyle.items():
            tags = style.get('style_tags', [])
            if tags:
                controller_kr = '키보드' if controller == 'keyboard' else '패드'
                insights.append(
                    f"🎯 {controller_kr} 스타일: {', '.join(tags)}"
                )

        return insights

    @classmethod
    def _empty_analysis(cls) -> Dict[str, Any]:
        """빈 분석 결과"""
        return {
            'controller_stats': {
                'keyboard': {},
                'gamepad': {}
            },
            'performance_comparison': {},
            'playstyle_comparison': {},
            'recommendation': {
                'recommended_controller': None,
                'reason': '경기 데이터가 없습니다',
                'confidence': 0
            },
            'insights': []
        }
