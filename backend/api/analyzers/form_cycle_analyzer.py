"""
Form Cycle Analyzer — B4
전체 매치 이력에서 핫 스트릭/슬럼프의 주기를 탐지하고,
무엇이 촉발하는지 분석.
"""
import math
from typing import List, Dict, Any, Optional
from datetime import datetime


class FormCycleAnalyzer:
    """폼 사이클 분석기 — 핫/콜드 스트릭 탐지"""

    # 폼 지수 가중치 (결과에 따른 점수)
    RESULT_SCORES = {
        'win': 3,
        'draw': 1,
        'lose': 0,
    }

    # 퍼포먼스 지수 (xG 근사치 포함)
    @staticmethod
    def _match_performance_score(match: Dict) -> float:
        """단일 경기 퍼포먼스 점수 (0-10 스케일)"""
        result = match.get('result', 'lose')
        goals_for = float(match.get('goals_for', 0))
        goals_against = float(match.get('goals_against', 0))
        possession = float(match.get('possession', 50))
        shots_on_target = float(match.get('shots_on_target', 0))
        shots = max(float(match.get('shots', 1)), 1)
        pass_rate = float(match.get('pass_success_rate', 70))

        # Base score from result
        base = {'win': 6.0, 'draw': 4.0, 'lose': 2.0}.get(result, 2.0)

        # Goal difference bonus (max ±2)
        gd_bonus = min(2.0, max(-2.0, (goals_for - goals_against) * 0.5))

        # Shot quality bonus (max 1.0)
        shot_quality = min(1.0, (shots_on_target / shots) * 1.5)

        # Possession bonus (max 0.5)
        poss_bonus = (possession - 50) * 0.01

        # Pass accuracy bonus (max 0.5)
        pass_bonus = (pass_rate - 70) * 0.01

        score = base + gd_bonus + shot_quality + poss_bonus + pass_bonus
        return max(0.0, min(10.0, score))

    @classmethod
    def _compute_rolling_form(cls, matches: List[Dict], window: int) -> List[Dict]:
        """롤링 폼 지수 계산 (오래된 순 정렬된 matches 필요)"""
        rolling = []
        for i in range(len(matches)):
            if i < window - 1:
                rolling.append(None)
                continue

            window_matches = matches[i - window + 1: i + 1]
            perf_scores = [cls._match_performance_score(m) for m in window_matches]
            win_count = sum(1 for m in window_matches if m.get('result') == 'win')
            draw_count = sum(1 for m in window_matches if m.get('result') == 'draw')
            loss_count = sum(1 for m in window_matches if m.get('result') == 'lose')

            avg_score = sum(perf_scores) / len(perf_scores)
            # Win rate weighted form (0-100)
            form_index = (avg_score / 10.0) * 100

            rolling.append({
                'form_index': round(form_index, 1),
                'avg_score': round(avg_score, 2),
                'wins': win_count,
                'draws': draw_count,
                'losses': loss_count,
                'win_rate': round(win_count / window * 100, 1),
            })
        return rolling

    @staticmethod
    def _detect_streaks(matches: List[Dict], rolling_5: List[Optional[Dict]]) -> List[Dict]:
        """
        핫/콜드 스트릭 탐지.
        Rolling 5-game form index가 임계값 초과/미달인 구간을 감지.
        """
        streaks = []
        HOT_THRESHOLD = 70.0
        COLD_THRESHOLD = 40.0
        MIN_STREAK_LEN = 3

        current_type = None
        streak_start = None

        for i, rolling in enumerate(rolling_5):
            if rolling is None:
                continue

            fi = rolling['form_index']

            if fi >= HOT_THRESHOLD:
                phase = 'hot'
            elif fi <= COLD_THRESHOLD:
                phase = 'cold'
            else:
                phase = 'neutral'

            if phase != current_type:
                # End previous streak
                if current_type in ('hot', 'cold') and streak_start is not None:
                    streak_len = i - streak_start
                    if streak_len >= MIN_STREAK_LEN:
                        streaks.append({
                            'type': current_type,
                            'start_idx': streak_start,
                            'end_idx': i - 1,
                            'length': streak_len,
                            'match_date': matches[streak_start].get('match_date', ''),
                        })

                current_type = phase if phase in ('hot', 'cold') else None
                streak_start = i if current_type else None

        # Close last streak
        if current_type in ('hot', 'cold') and streak_start is not None:
            streak_len = len(rolling_5) - streak_start
            if streak_len >= MIN_STREAK_LEN:
                streaks.append({
                    'type': current_type,
                    'start_idx': streak_start,
                    'end_idx': len(rolling_5) - 1,
                    'length': streak_len,
                    'match_date': matches[streak_start].get('match_date', ''),
                })

        return streaks

    @staticmethod
    def _session_length_analysis(matches: List[Dict]) -> Dict[str, Any]:
        """
        하루 내 경기 번호별 성적 분석.
        match_date로 같은 날 몇 번째 경기인지 판단.
        """
        session_stats: Dict[int, Dict] = {}

        # Group by date
        date_groups: Dict[str, List[Dict]] = {}
        for m in matches:
            date_str = m.get('match_date', '')
            if isinstance(date_str, str):
                date_key = date_str[:10]  # YYYY-MM-DD
            else:
                date_key = str(date_str)[:10]

            if date_key not in date_groups:
                date_groups[date_key] = []
            date_groups[date_key].append(m)

        for date_key, day_matches in date_groups.items():
            # Sort by time within same day
            for idx, match in enumerate(day_matches):
                session_num = idx + 1
                if session_num not in session_stats:
                    session_stats[session_num] = {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0}

                session_stats[session_num]['total'] += 1
                result = match.get('result', 'lose')
                if result == 'win':
                    session_stats[session_num]['wins'] += 1
                elif result == 'lose':
                    session_stats[session_num]['losses'] += 1
                else:
                    session_stats[session_num]['draws'] += 1

        # Compute win rates per session
        session_winrates = []
        for session_num in sorted(session_stats.keys()):
            stats = session_stats[session_num]
            total = stats['total']
            if total >= 3:  # Only include if enough sample
                win_rate = round(stats['wins'] / total * 100, 1)
                session_winrates.append({
                    'session': session_num,
                    'label': f'{session_num}번째 경기',
                    'win_rate': win_rate,
                    'total': total,
                    'wins': stats['wins'],
                })

        # Find optimal session (highest win rate)
        optimal_session = None
        if session_winrates:
            optimal_session = max(session_winrates, key=lambda x: x['win_rate'])

        return {
            'by_session': session_winrates,
            'optimal_session': optimal_session,
            'insight': (
                f"하루 {optimal_session['session']}번째 경기에서 승률 {optimal_session['win_rate']}%로 "
                f"최고 성적을 보입니다."
                if optimal_session else
                "세션 분석에 충분한 데이터가 없습니다."
            ),
        }

    @classmethod
    def analyze_form_cycle(cls, matches: List[Dict]) -> Dict[str, Any]:
        """
        전체 폼 사이클 분석.

        Args:
            matches: Match 객체 목록 (딕셔너리 형태, 오래된 순 정렬)
                각 항목: {match_date, result, goals_for, goals_against,
                          possession, shots, shots_on_target, pass_success_rate}

        Returns:
            {form_timeline, streaks, session_analysis, current_form, insights}
        """
        if not matches:
            return cls._empty_result()

        # Ensure chronological order (oldest first)
        def parse_date(m):
            d = m.get('match_date', '')
            if isinstance(d, str):
                return d
            return str(d)

        sorted_matches = sorted(matches, key=parse_date)

        # Compute performance scores for each match
        match_scores = [cls._match_performance_score(m) for m in sorted_matches]

        # Rolling 5-game and 10-game form indices
        rolling_5 = cls._compute_rolling_form(sorted_matches, 5)
        rolling_10 = cls._compute_rolling_form(sorted_matches, 10)

        # Build timeline data (for visualization)
        timeline = []
        for i, m in enumerate(sorted_matches):
            entry = {
                'match_index': i + 1,
                'match_date': m.get('match_date', ''),
                'result': m.get('result', 'lose'),
                'goals_for': m.get('goals_for', 0),
                'goals_against': m.get('goals_against', 0),
                'perf_score': round(match_scores[i], 2),
                'form_5': rolling_5[i]['form_index'] if rolling_5[i] else None,
                'form_10': rolling_10[i]['form_index'] if rolling_10[i] else None,
            }
            timeline.append(entry)

        # Detect streaks
        streaks = cls._detect_streaks(sorted_matches, rolling_5)

        # Current form (last 5 and 10 games)
        last_5_results = [m.get('result') for m in sorted_matches[-5:]]
        last_10_results = [m.get('result') for m in sorted_matches[-10:]]

        current_form_5 = rolling_5[-1] if rolling_5 else None
        current_form_10 = rolling_10[-1] if rolling_10 else None

        # Session analysis
        session_analysis = cls._session_length_analysis(sorted_matches)

        # Overall stats
        total = len(sorted_matches)
        wins = sum(1 for m in sorted_matches if m.get('result') == 'win')
        avg_form_5 = None
        valid_5 = [r for r in rolling_5 if r is not None]
        if valid_5:
            avg_form_5 = round(sum(r['form_index'] for r in valid_5) / len(valid_5), 1)

        # Generate insights
        insights = cls._generate_insights(
            sorted_matches, streaks, current_form_5, session_analysis
        )

        hot_streaks = [s for s in streaks if s['type'] == 'hot']
        cold_streaks = [s for s in streaks if s['type'] == 'cold']

        return {
            'total_matches': total,
            'win_rate': round(wins / total * 100, 1) if total > 0 else 0,
            'form_timeline': timeline,
            'rolling_5': [r for r in rolling_5 if r is not None],
            'rolling_10': [r for r in rolling_10 if r is not None],
            'streaks': {
                'all': streaks,
                'hot': hot_streaks,
                'cold': cold_streaks,
                'longest_hot': max((s['length'] for s in hot_streaks), default=0),
                'longest_cold': max((s['length'] for s in cold_streaks), default=0),
            },
            'current_form': {
                'last_5_results': last_5_results,
                'form_5': current_form_5,
                'form_10': current_form_10,
                'status': cls._form_status(current_form_5),
            },
            'avg_form_index': avg_form_5,
            'session_analysis': session_analysis,
            'insights': insights,
        }

    @staticmethod
    def _form_status(rolling: Optional[Dict]) -> str:
        if not rolling:
            return 'unknown'
        fi = rolling['form_index']
        if fi >= 70:
            return 'hot'
        elif fi >= 55:
            return 'good'
        elif fi >= 45:
            return 'neutral'
        elif fi >= 30:
            return 'poor'
        else:
            return 'cold'

    @staticmethod
    def _generate_insights(
        matches: List[Dict],
        streaks: List[Dict],
        current_form: Optional[Dict],
        session_analysis: Dict,
    ) -> List[str]:
        insights = []

        total = len(matches)
        if total < 5:
            insights.append('⚠️ 폼 사이클 분석에는 최소 5경기 이상이 필요합니다.')
            return insights

        # Current form insight
        if current_form:
            fi = current_form['form_index']
            if fi >= 70:
                insights.append(
                    f"🔥 현재 핫 스트릭! 최근 5경기 폼 지수 {fi}로 최상의 컨디션입니다. 이 흐름을 유지하세요!"
                )
            elif fi >= 55:
                insights.append(f"✅ 현재 폼이 좋습니다. 최근 5경기 폼 지수 {fi}.")
            elif fi <= 30:
                insights.append(
                    f"❄️ 슬럼프 구간 감지. 최근 5경기 폼 지수 {fi}. "
                    f"전술을 점검하고 간단한 플레이에 집중하세요."
                )
            elif fi <= 45:
                insights.append(f"📉 최근 폼이 저조합니다. 폼 지수 {fi}. 회복이 필요합니다.")

        # Streak insights
        hot_streaks = [s for s in streaks if s['type'] == 'hot']
        cold_streaks = [s for s in streaks if s['type'] == 'cold']

        if hot_streaks:
            longest_hot = max(hot_streaks, key=lambda s: s['length'])
            insights.append(
                f"🏆 전체 기록 중 최장 {longest_hot['length']}경기 연속 핫 스트릭 달성 기록이 있습니다."
            )

        if cold_streaks:
            longest_cold = max(cold_streaks, key=lambda s: s['length'])
            insights.append(
                f"⚠️ 슬럼프 위험: 최장 {longest_cold['length']}경기 연속 부진 구간이 있었습니다."
            )

        # Session analysis insight
        optimal = session_analysis.get('optimal_session')
        if optimal and optimal.get('total', 0) >= 5:
            insights.append(
                f"⏰ 하루 {optimal['session']}번째 경기에서 승률 {optimal['win_rate']}%로 "
                f"최고 성적. 컨디션 관리를 고려하세요."
            )

        return insights

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            'total_matches': 0,
            'win_rate': 0,
            'form_timeline': [],
            'rolling_5': [],
            'rolling_10': [],
            'streaks': {'all': [], 'hot': [], 'cold': [], 'longest_hot': 0, 'longest_cold': 0},
            'current_form': {'last_5_results': [], 'form_5': None, 'form_10': None, 'status': 'unknown'},
            'avg_form_index': None,
            'session_analysis': {'by_session': [], 'optimal_session': None, 'insight': ''},
            'insights': ['경기 데이터가 없습니다.'],
        }
