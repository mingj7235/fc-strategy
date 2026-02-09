from typing import List, Dict, Any
from decimal import Decimal


class StatisticsCalculator:
    """Calculate various statistics from match data"""

    @classmethod
    def calculate_basic_stats(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic statistics from matches"""
        if not matches:
            return {
                'total_matches': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'win_rate': 0.0,
                'avg_goals_for': 0.0,
                'avg_goals_against': 0.0,
                'avg_possession': 0.0,
                'avg_shots': 0.0,
                'avg_shots_on_target': 0.0,
                'avg_pass_success_rate': 0.0,
            }

        total_matches = len(matches)
        wins = sum(1 for m in matches if m.get('result') == 'win')
        losses = sum(1 for m in matches if m.get('result') == 'lose')
        draws = total_matches - wins - losses

        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

        avg_goals_for = sum(m.get('goals_for', 0) for m in matches) / total_matches
        avg_goals_against = sum(m.get('goals_against', 0) for m in matches) / total_matches
        avg_possession = sum(m.get('possession', 0) for m in matches) / total_matches
        avg_shots = sum(m.get('shots', 0) for m in matches) / total_matches
        avg_shots_on_target = sum(m.get('shots_on_target', 0) for m in matches) / total_matches
        avg_pass_success_rate = sum(float(m.get('pass_success_rate', 0)) for m in matches) / total_matches

        return {
            'total_matches': total_matches,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': round(win_rate, 2),
            'avg_goals_for': round(avg_goals_for, 2),
            'avg_goals_against': round(avg_goals_against, 2),
            'avg_possession': round(avg_possession, 2),
            'avg_shots': round(avg_shots, 2),
            'avg_shots_on_target': round(avg_shots_on_target, 2),
            'avg_pass_success_rate': round(avg_pass_success_rate, 2),
        }

    @classmethod
    def calculate_trends(cls, matches: List[Dict[str, Any]], window: int = 5) -> Dict[str, Any]:
        """Calculate recent trends using a rolling window"""
        if len(matches) < window:
            return {}

        recent_matches = matches[:window]
        older_matches = matches[window:window*2] if len(matches) >= window*2 else []

        recent_stats = cls.calculate_basic_stats(recent_matches)
        older_stats = cls.calculate_basic_stats(older_matches) if older_matches else {}

        trends = {}
        if older_stats:
            trends['win_rate_change'] = round(recent_stats['win_rate'] - older_stats['win_rate'], 2)
            trends['goals_change'] = round(recent_stats['avg_goals_for'] - older_stats['avg_goals_for'], 2)
            trends['possession_change'] = round(recent_stats['avg_possession'] - older_stats['avg_possession'], 2)

        return {
            'recent_stats': recent_stats,
            'trends': trends,
        }

    @classmethod
    def calculate_form(cls, matches: List[Dict[str, Any]], num_matches: int = 5) -> str:
        """Calculate recent form string (e.g., 'WWLWD')"""
        if not matches:
            return ''

        recent = matches[:num_matches]
        form = ''

        for match in recent:
            result = match.get('result', '')
            if result == 'win':
                form += 'W'
            elif result == 'lose':
                form += 'L'
            elif result == 'draw':
                form += 'D'

        return form

    @classmethod
    def calculate_form_trend(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate trend by comparing recent half vs older half (newest-first input).
        Returns dict with 'trend', 'recent_win_rate', 'older_win_rate'.
        """
        if not matches or len(matches) < 2:
            return {'trend': 'stable', 'recent_win_rate': 0.0, 'older_win_rate': 0.0}

        split = len(matches) // 2
        recent = matches[:split]
        older = matches[split:]

        recent_wr = sum(1 for m in recent if m.get('result') == 'win') / len(recent) * 100
        older_wr = sum(1 for m in older if m.get('result') == 'win') / len(older) * 100

        if recent_wr > older_wr:
            trend = 'improving'
        elif recent_wr < older_wr:
            trend = 'declining'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'recent_win_rate': round(recent_wr, 1),
            'older_win_rate': round(older_wr, 1),
        }

    @classmethod
    def calculate_statistics(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics combining basic stats, form string, and trend.
        Returns data matching StatisticsSerializer fields.
        """
        basic = cls.calculate_basic_stats(matches)
        form_str = cls.calculate_form(matches)
        trend = cls.calculate_form_trend(matches)

        return {
            'total_matches': basic['total_matches'],
            'win_rate': basic['win_rate'],
            'avg_goals_for': basic['avg_goals_for'],
            'avg_goals_against': basic['avg_goals_against'],
            'avg_possession': basic['avg_possession'],
            'avg_shots': basic['avg_shots'],
            'avg_shots_on_target': basic['avg_shots_on_target'],
            'avg_pass_success_rate': basic['avg_pass_success_rate'],
            'recent_form': list(form_str),
            'trends': trend,
        }

    @classmethod
    def calculate_shot_efficiency(cls, matches: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate shooting efficiency metrics"""
        if not matches:
            return {
                'total_shots': 0,
                'total_shots_on_target': 0,
                'total_goals': 0,
                'shot_accuracy': 0.0,
                'conversion_rate': 0.0,
            }

        total_shots = sum(m.get('shots', 0) for m in matches)
        total_shots_on_target = sum(m.get('shots_on_target', 0) for m in matches)
        total_goals = sum(m.get('goals_for', 0) for m in matches)

        shot_accuracy = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0
        conversion_rate = (total_goals / total_shots * 100) if total_shots > 0 else 0

        return {
            'total_shots': total_shots,
            'total_shots_on_target': total_shots_on_target,
            'total_goals': total_goals,
            'shot_accuracy': round(shot_accuracy, 2),
            'conversion_rate': round(conversion_rate, 2),
        }


class StatisticsAnalyzer:
    """
    Alternative statistics interface that works directly with Django QuerySets
    (Match model instances) and returns a format compatible with test expectations.
    Complements StatisticsCalculator which works with plain dicts.
    """

    @classmethod
    def calculate_statistics(cls, matches) -> Dict[str, Any]:
        """
        Calculate overall statistics from a Match QuerySet or iterable.

        Returns dict with: total_matches, wins, losses, draws, win_rate,
        avg_possession, avg_shots, avg_goals (combined for/against average).
        """
        match_list = list(matches)
        if not match_list:
            return {
                'total_matches': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'win_rate': 0.0,
                'avg_possession': 0.0,
                'avg_shots': 0.0,
                'avg_goals': 0.0,
            }

        total = len(match_list)
        wins = sum(1 for m in match_list if m.result == 'win')
        losses = sum(1 for m in match_list if m.result == 'lose')
        draws = total - wins - losses

        avg_possession = sum(m.possession for m in match_list) / total
        avg_shots = sum(m.shots for m in match_list) / total
        avg_goals = sum(m.goals_for for m in match_list) / total

        return {
            'total_matches': total,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': round(wins / total * 100, 2),
            'avg_possession': round(avg_possession, 2),
            'avg_shots': round(avg_shots, 2),
            'avg_goals': round(avg_goals, 2),
        }

    @classmethod
    def calculate_recent_form(cls, matches, limit: int = 5) -> List[str]:
        """
        Return a list of recent form strings ('W', 'L', 'D') for the last
        `limit` matches (assumes matches are ordered newest-first).
        """
        result_map = {'win': 'W', 'lose': 'L', 'draw': 'D'}
        form = []
        for match in matches:
            if len(form) >= limit:
                break
            form.append(result_map.get(match.result, 'D'))
        return form
