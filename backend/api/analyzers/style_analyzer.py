from typing import List, Dict, Any


class StyleAnalyzer:
    """Enhanced playing style analyzer with sophisticated pattern detection"""

    @classmethod
    def analyze_style(cls, matches) -> Dict[str, Any]:
        """
        Simplified style analysis for a QuerySet of Match objects (or list of dicts).
        Returns possession_style, attack_style, and avg_possession.
        """
        from django.db.models.query import QuerySet
        if isinstance(matches, QuerySet):
            match_list = list(matches.values('possession', 'shots', 'pass_success_rate', 'result'))
        else:
            match_list = list(matches)

        if not match_list:
            return {'possession_style': 'unknown', 'attack_style': 'unknown', 'avg_possession': 0.0}

        total = len(match_list)
        avg_possession = sum(m.get('possession', 0) or 0 for m in match_list) / total
        avg_shots = sum(m.get('shots', 0) or 0 for m in match_list) / total

        if avg_possession >= 55:
            possession_style = 'high_possession'
        elif avg_possession <= 45:
            possession_style = 'counter_attack'
        else:
            possession_style = 'balanced'

        attack_style = 'aggressive' if avg_shots >= 15 else 'patient'

        return {
            'possession_style': possession_style,
            'attack_style': attack_style,
            'avg_possession': round(avg_possession, 2),
        }

    @classmethod
    def analyze_play_style(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive play style analysis from multiple matches

        Args:
            matches: List of match data dictionaries

        Returns:
            Dictionary containing detailed play style analysis
        """
        if not matches:
            return cls._empty_analysis()

        total_matches = len(matches)
        wins = [m for m in matches if m.get('result') == 'win']
        losses = [m for m in matches if m.get('result') == 'lose']
        draws = [m for m in matches if m.get('result') == 'draw']

        analysis = {
            'total_matches': total_matches,
            'wins': len(wins),
            'losses': len(losses),
            'draws': len(draws),
            'win_rate': round(len(wins) / total_matches * 100, 1) if total_matches > 0 else 0,

            # Tactical patterns
            'attack_pattern': cls._analyze_attack_pattern(matches),
            'possession_style': cls._analyze_possession_style(matches),
            'defensive_approach': cls._analyze_defensive_approach(matches),
            'tempo': cls._analyze_tempo(matches),

            # Performance by situation
            'win_patterns': cls._analyze_patterns(wins) if wins else {},
            'loss_patterns': cls._analyze_patterns(losses) if losses else {},

            # Time-based analysis
            'time_analysis': cls._analyze_time_patterns(matches),

            # Efficiency metrics
            'efficiency': cls._analyze_efficiency(matches),

            # Consistency
            'consistency': cls._analyze_consistency(matches),

            # Comeback potential
            'comeback_stats': cls._analyze_comeback_potential(matches),
        }

        return analysis

    @classmethod
    def _empty_analysis(cls) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'total_matches': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'win_rate': 0,
            'attack_pattern': 'unknown',
            'possession_style': 'unknown',
            'defensive_approach': 'unknown',
            'tempo': 'unknown',
            'win_patterns': {},
            'loss_patterns': {},
            'time_analysis': {},
            'efficiency': {},
            'consistency': {},
            'comeback_stats': {},
        }

    @classmethod
    def _analyze_attack_pattern(cls, matches: List[Dict[str, Any]]) -> str:
        """
        Sophisticated attack pattern detection

        Returns: 'possession_based', 'counter_attack', 'direct_play', 'balanced'
        """
        if not matches:
            return 'unknown'

        avg_possession = sum(m.get('possession', 0) for m in matches) / len(matches)
        avg_shots = sum(m.get('shots', 0) for m in matches) / len(matches)
        avg_pass_success = sum(m.get('pass_success_rate', 0) for m in matches) / len(matches)

        # Possession-based: High possession + high pass success
        if avg_possession > 58 and avg_pass_success > 82:
            return 'possession_based'

        # Counter-attack: Low possession but efficient shots
        elif avg_possession < 45 and avg_shots >= 10:
            return 'counter_attack'

        # Direct play: Moderate possession + many shots + lower pass success
        elif 45 <= avg_possession <= 55 and avg_shots > 14 and avg_pass_success < 78:
            return 'direct_play'

        # Balanced
        else:
            return 'balanced'

    @classmethod
    def _analyze_possession_style(cls, matches: List[Dict[str, Any]]) -> str:
        """
        Detailed possession style classification

        Returns: 'tiki_taka', 'high_possession', 'balanced', 'counter_based', 'direct'
        """
        if not matches:
            return 'unknown'

        avg_possession = sum(m.get('possession', 0) for m in matches) / len(matches)
        avg_pass_success = sum(m.get('pass_success_rate', 0) for m in matches) / len(matches)

        # Tiki-taka: Very high possession + very high pass success
        if avg_possession > 60 and avg_pass_success > 85:
            return 'tiki_taka'

        # High possession
        elif avg_possession > 55:
            return 'high_possession'

        # Balanced
        elif 45 <= avg_possession <= 55:
            return 'balanced'

        # Counter-based
        elif avg_possession < 45:
            return 'counter_based'

        # Direct
        else:
            return 'direct'

    @classmethod
    def _analyze_defensive_approach(cls, matches: List[Dict[str, Any]]) -> str:
        """
        Analyze defensive playing style

        Returns: 'solid', 'aggressive', 'vulnerable', 'balanced'
        """
        if not matches:
            return 'unknown'

        avg_goals_against = sum(m.get('goals_against', 0) for m in matches) / len(matches)
        avg_possession = sum(m.get('possession', 0) for m in matches) / len(matches)

        # Solid: Low goals conceded
        if avg_goals_against < 1.2:
            return 'solid'

        # Aggressive: High possession + moderate conceding (high line)
        elif avg_possession > 55 and 1.2 <= avg_goals_against <= 1.8:
            return 'aggressive'

        # Vulnerable: Many goals conceded
        elif avg_goals_against > 2.0:
            return 'vulnerable'

        # Balanced
        else:
            return 'balanced'

    @classmethod
    def _analyze_tempo(cls, matches: List[Dict[str, Any]]) -> str:
        """
        Analyze game tempo

        Returns: 'fast', 'moderate', 'slow'
        """
        if not matches:
            return 'unknown'

        avg_shots = sum(m.get('shots', 0) for m in matches) / len(matches)
        avg_pass_success = sum(m.get('pass_success_rate', 0) for m in matches) / len(matches)

        # Fast: Many shots + lower pass success (risk-taking)
        if avg_shots > 15 and avg_pass_success < 78:
            return 'fast'

        # Slow: High pass success + fewer shots (patient build-up)
        elif avg_pass_success > 82 and avg_shots < 12:
            return 'slow'

        # Moderate
        else:
            return 'moderate'

    @classmethod
    def _analyze_patterns(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive statistical pattern analysis"""
        if not matches:
            return {}

        n = len(matches)

        return {
            'possession': round(sum(m.get('possession', 0) for m in matches) / n, 1),
            'shots': round(sum(m.get('shots', 0) for m in matches) / n, 1),
            'shots_on_target': round(sum(m.get('shots_on_target', 0) for m in matches) / n, 1),
            'pass_success_rate': round(sum(m.get('pass_success_rate', 0) for m in matches) / n, 1),
            'goals': round(sum(m.get('goals_for', 0) for m in matches) / n, 1),
            'goals_against': round(sum(m.get('goals_against', 0) for m in matches) / n, 1),
        }

    @classmethod
    def _analyze_time_patterns(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance across match time periods"""
        # Note: This requires first_half/second_half data which may not be in current models
        # Placeholder for future enhancement when detailed time data is available
        return {
            'early_game_performance': 'unknown',
            'late_game_performance': 'unknown',
        }

    @classmethod
    def _analyze_efficiency(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate various efficiency metrics"""
        if not matches:
            return {}

        total_shots = sum(m.get('shots', 0) for m in matches)
        total_shots_on_target = sum(m.get('shots_on_target', 0) for m in matches)
        total_goals = sum(m.get('goals_for', 0) for m in matches)
        total_possession = sum(m.get('possession', 0) for m in matches)

        shot_accuracy = (total_shots_on_target / total_shots * 100) if total_shots > 0 else 0
        conversion_rate = (total_goals / total_shots * 100) if total_shots > 0 else 0
        goals_per_possession = (total_goals / total_possession * 100) if total_possession > 0 else 0

        return {
            'shot_accuracy': round(shot_accuracy, 1),
            'conversion_rate': round(conversion_rate, 1),
            'goals_per_possession': round(goals_per_possession, 2),
            'possession_efficiency': 'high' if goals_per_possession > 3.5 else 'moderate' if goals_per_possession > 2.5 else 'low',
        }

    @classmethod
    def _analyze_consistency(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance consistency"""
        if not matches:
            return {}

        goals_list = [m.get('goals_for', 0) for m in matches]
        possession_list = [m.get('possession', 0) for m in matches]

        # Calculate standard deviation (measure of consistency)
        import statistics

        goal_variance = statistics.stdev(goals_list) if len(goals_list) > 1 else 0
        poss_variance = statistics.stdev(possession_list) if len(possession_list) > 1 else 0

        # Low variance = high consistency
        goal_consistency = 'high' if goal_variance < 1.2 else 'moderate' if goal_variance < 1.8 else 'low'
        poss_consistency = 'high' if poss_variance < 8 else 'moderate' if poss_variance < 15 else 'low'

        return {
            'goal_scoring_consistency': goal_consistency,
            'possession_consistency': poss_consistency,
            'goal_variance': round(goal_variance, 2),
            'possession_variance': round(poss_variance, 1),
        }

    @classmethod
    def _analyze_comeback_potential(cls, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze ability to come from behind"""
        if not matches:
            return {}

        # Count games where goals_for > goals_against (wins)
        wins = [m for m in matches if m.get('result') == 'win']
        losses = [m for m in matches if m.get('result') == 'lose']

        # Calculate goal difference in wins vs losses
        avg_win_margin = sum(m.get('goals_for', 0) - m.get('goals_against', 0) for m in wins) / len(wins) if wins else 0
        avg_loss_margin = sum(m.get('goals_against', 0) - m.get('goals_for', 0) for m in losses) / len(losses) if losses else 0

        # Close games (1 goal difference)
        close_wins = sum(1 for m in wins if abs(m.get('goals_for', 0) - m.get('goals_against', 0)) == 1)
        close_losses = sum(1 for m in losses if abs(m.get('goals_for', 0) - m.get('goals_against', 0)) == 1)

        return {
            'avg_win_margin': round(avg_win_margin, 1),
            'avg_loss_margin': round(avg_loss_margin, 1),
            'close_game_wins': close_wins,
            'close_game_losses': close_losses,
            'mental_strength': 'strong' if close_wins > close_losses else 'needs_improvement',
        }

    @classmethod
    def generate_insights(cls, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate professional insights using Keep-Stop-Action framework

        Returns:
            Dictionary with 'keep', 'stop', and 'action_items' lists
        """
        keep = []  # Positive aspects to maintain
        stop = []  # Negative patterns to eliminate
        action_items = []  # Specific recommendations

        win_rate = analysis.get('win_rate', 0)
        attack_pattern = analysis.get('attack_pattern', '')
        possession_style = analysis.get('possession_style', '')
        defensive = analysis.get('defensive_approach', '')
        tempo = analysis.get('tempo', '')
        win_patterns = analysis.get('win_patterns', {})
        loss_patterns = analysis.get('loss_patterns', {})
        efficiency = analysis.get('efficiency', {})
        consistency = analysis.get('consistency', {})
        comeback = analysis.get('comeback_stats', {})

        # === KEEP: Positive aspects ===

        # Good win rate
        if win_rate >= 55:
            keep.append(f"뛰어난 승률 {win_rate}% 유지")
        elif win_rate >= 45:
            keep.append(f"안정적인 승률 {win_rate}%")

        # Solid defense
        if defensive == 'solid':
            keep.append("견고한 수비 운영 - 실점 최소화")

        # Strong mental game
        if comeback.get('mental_strength') == 'strong':
            close_wins = comeback.get('close_game_wins', 0)
            close_losses = comeback.get('close_game_losses', 0)
            keep.append(f"접전에서의 강한 멘탈 (1골 차: {close_wins}승 {close_losses}패)")

        # Good efficiency
        conversion = efficiency.get('conversion_rate', 0)
        shot_acc = efficiency.get('shot_accuracy', 0)

        if conversion >= 14:
            keep.append(f"우수한 슈팅 전환율 ({conversion:.1f}%)")

        if shot_acc >= 55:
            keep.append(f"높은 슈팅 정확도 ({shot_acc:.1f}%)")

        # Consistent goal scoring
        if consistency.get('goal_scoring_consistency') == 'high':
            keep.append("일관된 득점 패턴")

        # Effective attack pattern
        if attack_pattern == 'possession_based':
            win_poss = win_patterns.get('possession', 0)
            if win_poss > 55:
                keep.append(f"점유율 기반 공격 ({win_poss:.1f}% 평균)")
        elif attack_pattern == 'counter_attack':
            keep.append("효과적인 역습 전술")

        # Winning pattern identification
        if win_patterns and loss_patterns:
            win_poss = win_patterns.get('possession', 0)
            loss_poss = loss_patterns.get('possession', 0)
            win_shots = win_patterns.get('shots', 0)

            if win_poss > loss_poss + 5:
                keep.append(f"점유율 우위 시 승률 상승 패턴")

            if win_shots >= 12:
                keep.append(f"충분한 슈팅 창출 능력 (승리 시 평균 {win_shots:.1f})")

        # === STOP: Negative patterns ===

        # Poor win rate
        if win_rate < 40:
            stop.append(f"낮은 승률 {win_rate}% - 현재 전술 고수")

        # Vulnerable defense
        if defensive == 'vulnerable':
            avg_goals_against = loss_patterns.get('goals_against', 0)
            stop.append(f"취약한 수비 (평균 실점 {avg_goals_against:.1f})")

        # Poor efficiency
        if conversion < 9:
            stop.append(f"낮은 슈팅 전환율 ({conversion:.1f}%)")

        if shot_acc < 45:
            stop.append(f"부정확한 슈팅 ({shot_acc:.1f}%)")

        # Inconsistent performance
        if consistency.get('goal_scoring_consistency') == 'low':
            stop.append("불안정한 득점 패턴")

        # Poor close game performance
        if comeback.get('mental_strength') == 'needs_improvement':
            close_wins = comeback.get('close_game_wins', 0)
            close_losses = comeback.get('close_game_losses', 0)
            if close_losses > close_wins:
                stop.append(f"접전 경기 약세 ({close_wins}승 {close_losses}패)")

        # Ineffective possession
        poss_eff = efficiency.get('possession_efficiency', '')
        if poss_eff == 'low':
            avg_poss = win_patterns.get('possession', 50) if win_patterns else 50
            if avg_poss > 50:
                stop.append("비효율적인 점유율 활용")

        # Poor shot selection in losses
        if loss_patterns:
            loss_shots = loss_patterns.get('shots', 0)
            loss_shot_acc = loss_patterns.get('shots_on_target', 0) / loss_shots * 100 if loss_shots > 0 else 0
            if loss_shot_acc < 40:
                stop.append("패배 시 무리한 슈팅 시도")

        # === ACTION ITEMS: Recommendations ===

        # Improve win rate
        if win_rate < 45:
            action_items.append("전술 분석: 패배 경기의 공통 패턴을 파악하고 개선하세요")

        # Defensive improvements
        if defensive == 'vulnerable':
            action_items.append("수비 라인을 낮추거나 중앙 수비를 강화하세요")
            action_items.append("상대 공격 시 빠르게 수비 대형을 갖추세요")

        # Attack improvements
        if conversion < 10:
            action_items.append("박스 안 침투를 늘리고 더 확실한 기회에 슈팅하세요")
            action_items.append("측면 돌파 후 컷백 패스로 중앙 슈팅 기회를 만드세요")

        # Possession efficiency
        if poss_eff == 'low' and win_patterns.get('possession', 0) > 50:
            action_items.append("점유율보다 슈팅 기회 창출에 집중하세요")
            action_items.append("무의미한 백패스를 줄이고 전방 패스 비율을 높이세요")

        # Shot accuracy
        if shot_acc < 50:
            action_items.append("슈팅 전 볼 컨트롤을 안정화하세요")
            action_items.append("각도가 좁거나 수비가 밀집한 상황에서는 패스를 선택하세요")

        # Consistency
        if consistency.get('goal_scoring_consistency') == 'low':
            action_items.append("핵심 전술을 정하고 매 경기 일관되게 적용하세요")
            action_items.append("주력 선수 조합을 고정하여 팀 케미스트리를 높이세요")

        # Mental strength
        if comeback.get('mental_strength') == 'needs_improvement':
            action_items.append("접전 상황에서 침착함을 유지하세요")
            action_items.append("동점이나 1골 차 상황에서는 안정적인 플레이를 우선하세요")

        # Tempo optimization
        if tempo == 'slow' and efficiency.get('conversion_rate', 0) < 10:
            action_items.append("템포를 높여 더 많은 공격 기회를 만드세요")
        elif tempo == 'fast' and shot_acc < 45:
            action_items.append("서두르지 말고 확실한 기회를 만든 후 마무리하세요")

        # Pattern-based recommendations
        if win_patterns and loss_patterns:
            win_poss = win_patterns.get('possession', 0)
            loss_poss = loss_patterns.get('possession', 0)

            if win_poss > loss_poss + 8:
                action_items.append(f"점유율을 높게 유지하세요 (승리 시 {win_poss:.1f}% vs 패배 시 {loss_poss:.1f}%)")
            elif loss_poss > win_poss + 8:
                action_items.append("역습 전술에 집중하고 불필요한 점유를 피하세요")

        # Default recommendations
        if not action_items:
            if win_rate >= 50:
                action_items.append("현재 플레이 스타일을 유지하며 세부 기술을 연마하세요")
            else:
                action_items.append("훈련 모드에서 다양한 전술을 실험해보세요")

        # Ensure all categories have content
        if not keep:
            keep.append("균형잡힌 전반적인 경기 운영")

        return {
            'keep': keep,
            'stop': stop,
            'action_items': action_items
        }
