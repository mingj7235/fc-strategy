"""
Heading Analysis
헤딩 전문 분석 - 공중볼 전술 및 타겟맨 활용도
"""
from typing import Dict, Any, List
from collections import defaultdict


class HeadingAnalyzer:
    """
    헤딩 분석기
    - 헤딩 슈팅/골 분석
    - 헤딩 발생 위치 분석
    - 크로스 출발 위치 분석
    - 타겟맨 선수 식별
    - 공중볼 전술 효율성 측정
    """

    # Heading shot type
    HEADING_TYPE = 3

    @classmethod
    def analyze_heading(cls, shot_details: List[Dict[str, Any]], player_data: List[Dict] = None) -> Dict[str, Any]:
        """
        헤딩 전문 분석

        Args:
            shot_details: List of shot detail data
            player_data: Optional player performance data for target man identification

        Returns:
            헤딩 분석 결과
        """
        # Filter heading shots
        heading_shots = [shot for shot in shot_details if shot.get('shot_type') == cls.HEADING_TYPE]

        if not heading_shots:
            return cls._empty_analysis()

        # Basic heading stats
        heading_stats = cls._calculate_heading_stats(heading_shots)

        # Heading positions (where headers occurred)
        heading_positions = cls._analyze_heading_positions(heading_shots)

        # Cross origins (where assists came from)
        cross_origins = cls._analyze_cross_origins(heading_shots)

        # Target man identification
        target_man = cls._identify_target_man(heading_shots, player_data)

        # Aerial efficiency score
        efficiency_score = cls._calculate_efficiency_score(heading_stats, heading_positions)

        # Insights
        insights = cls._generate_insights(
            heading_stats,
            heading_positions,
            cross_origins,
            target_man,
            efficiency_score
        )

        return {
            'heading_stats': heading_stats,
            'heading_positions': heading_positions,
            'cross_origins': cross_origins,
            'target_man': target_man,
            'efficiency_score': efficiency_score,
            'insights': insights
        }

    @classmethod
    def _calculate_heading_stats(cls, heading_shots: List[Dict]) -> Dict[str, Any]:
        """헤딩 기본 통계"""
        total_headers = len(heading_shots)
        goals = sum(1 for shot in heading_shots if shot.get('result') == 'goal')
        on_target = sum(1 for shot in heading_shots if shot.get('result') in ['goal', 'on_target'])

        success_rate = round((on_target / total_headers) * 100, 1) if total_headers > 0 else 0
        conversion_rate = round((goals / total_headers) * 100, 1) if total_headers > 0 else 0

        # Headers with assists (crosses)
        headers_with_assist = sum(1 for shot in heading_shots if shot.get('assist_spid') is not None)
        cross_percentage = round((headers_with_assist / total_headers) * 100, 1) if total_headers > 0 else 0

        # Penalty box headers
        inside_box = sum(1 for shot in heading_shots if shot.get('in_penalty', False))
        box_percentage = round((inside_box / total_headers) * 100, 1) if total_headers > 0 else 0

        return {
            'total_headers': total_headers,
            'goals': goals,
            'on_target': on_target,
            'success_rate': success_rate,
            'conversion_rate': conversion_rate,
            'headers_with_assist': headers_with_assist,
            'cross_percentage': cross_percentage,
            'inside_box': inside_box,
            'box_percentage': box_percentage
        }

    @classmethod
    def _analyze_heading_positions(cls, heading_shots: List[Dict]) -> Dict[str, Any]:
        """헤딩 발생 위치 분석"""
        positions = {
            'central': 0,  # 중앙 (y: 0.3-0.7)
            'left': 0,     # 좌측 (y: 0-0.3)
            'right': 0,    # 우측 (y: 0.7-1.0)
            'box': 0,      # 박스 내
            'edge': 0      # 박스 외곽
        }

        position_goals = defaultdict(int)

        for shot in heading_shots:
            x = shot.get('x', 0)
            y = shot.get('y', 0.5)
            in_penalty = shot.get('in_penalty', False)
            is_goal = shot.get('result') == 'goal'

            # Lateral position
            if y < 0.3:
                positions['left'] += 1
                if is_goal:
                    position_goals['left'] += 1
            elif y > 0.7:
                positions['right'] += 1
                if is_goal:
                    position_goals['right'] += 1
            else:
                positions['central'] += 1
                if is_goal:
                    position_goals['central'] += 1

            # Depth position
            if in_penalty:
                positions['box'] += 1
                if is_goal:
                    position_goals['box'] += 1
            else:
                positions['edge'] += 1
                if is_goal:
                    position_goals['edge'] += 1

        # Calculate conversion rates by position
        total = len(heading_shots)
        position_percentages = {
            pos: round((count / total) * 100, 1) if total > 0 else 0
            for pos, count in positions.items()
        }

        return {
            'positions': positions,
            'position_percentages': position_percentages,
            'position_goals': dict(position_goals)
        }

    @classmethod
    def _analyze_cross_origins(cls, heading_shots: List[Dict]) -> Dict[str, Any]:
        """크로스 출발 위치 분석"""
        cross_origins = {
            'left_wing': 0,   # 좌측 측면 (assist_y < 0.3)
            'right_wing': 0,  # 우측 측면 (assist_y > 0.7)
            'central': 0,     # 중앙 (0.3 <= assist_y <= 0.7)
            'no_assist': 0    # 어시스트 없음
        }

        origin_goals = defaultdict(int)

        for shot in heading_shots:
            assist_y = shot.get('assist_y')
            is_goal = shot.get('result') == 'goal'

            if assist_y is None:
                cross_origins['no_assist'] += 1
                if is_goal:
                    origin_goals['no_assist'] += 1
            elif assist_y < 0.3:
                cross_origins['left_wing'] += 1
                if is_goal:
                    origin_goals['left_wing'] += 1
            elif assist_y > 0.7:
                cross_origins['right_wing'] += 1
                if is_goal:
                    origin_goals['right_wing'] += 1
            else:
                cross_origins['central'] += 1
                if is_goal:
                    origin_goals['central'] += 1

        # Calculate percentages
        total_with_assist = sum(v for k, v in cross_origins.items() if k != 'no_assist')
        origin_percentages = {}
        for origin, count in cross_origins.items():
            if origin == 'no_assist':
                continue
            origin_percentages[origin] = round((count / total_with_assist) * 100, 1) if total_with_assist > 0 else 0

        return {
            'cross_origins': cross_origins,
            'origin_percentages': origin_percentages,
            'origin_goals': dict(origin_goals)
        }

    @classmethod
    def _identify_target_man(cls, heading_shots: List[Dict], player_data: List[Dict] = None) -> Dict[str, Any]:
        """타겟맨 선수 식별 (가장 헤딩을 많이 한 선수)"""
        # Note: ShotDetail doesn't have shooter SPID, so we can't identify individual players
        # This would require player_data from PlayerPerformance or match raw_data

        # For now, return aggregate data
        # TODO: Enhance when player shooting data is available

        total_headers = len(heading_shots)
        total_goals = sum(1 for shot in heading_shots if shot.get('result') == 'goal')

        return {
            'player_identified': False,
            'total_headers': total_headers,
            'total_goals': total_goals,
            'message': '개별 선수 헤딩 데이터를 수집하려면 PlayerPerformance 확장이 필요합니다'
        }

    @classmethod
    def _calculate_efficiency_score(cls, heading_stats: Dict, heading_positions: Dict) -> Dict[str, Any]:
        """공중볼 전술 효율성 점수 (0-100)"""
        score = 0
        max_score = 100

        # 1. Conversion rate (40 points max)
        conversion_rate = heading_stats['conversion_rate']
        score += min(conversion_rate * 2, 40)  # 20% conversion = 40 points

        # 2. Success rate (30 points max)
        success_rate = heading_stats['success_rate']
        score += min(success_rate * 0.5, 30)  # 60% success = 30 points

        # 3. Cross utilization (15 points max)
        cross_percentage = heading_stats['cross_percentage']
        score += min(cross_percentage * 0.15, 15)  # 100% crosses = 15 points

        # 4. Box positioning (15 points max)
        box_percentage = heading_stats['box_percentage']
        score += min(box_percentage * 0.15, 15)  # 100% in box = 15 points

        score = min(int(score), max_score)

        # Grade
        if score >= 80:
            grade = 'S'
            grade_text = '우수'
        elif score >= 60:
            grade = 'A'
            grade_text = '좋음'
        elif score >= 40:
            grade = 'B'
            grade_text = '보통'
        elif score >= 20:
            grade = 'C'
            grade_text = '개선 필요'
        else:
            grade = 'D'
            grade_text = '많은 개선 필요'

        return {
            'score': score,
            'grade': grade,
            'grade_text': grade_text
        }

    @classmethod
    def _generate_insights(
        cls,
        heading_stats: Dict,
        heading_positions: Dict,
        cross_origins: Dict,
        target_man: Dict,
        efficiency_score: Dict
    ) -> List[str]:
        """한국어 인사이트 생성"""
        insights = []

        # 1. Overall efficiency
        score = efficiency_score['score']
        grade = efficiency_score['grade_text']
        insights.append(
            f"🎯 공중볼 전술 효율성: {score}점 ({grade})"
        )

        # 2. Heading stats
        total = heading_stats['total_headers']
        goals = heading_stats['goals']
        conversion = heading_stats['conversion_rate']

        if total == 0:
            insights.append("헤딩 슈팅이 없었습니다")
            return insights

        insights.append(
            f"⚽ 헤딩 슈팅 {total}회 중 {goals}골 (전환율 {conversion}%)"
        )

        # 3. Conversion rate insights
        if conversion >= 30:
            insights.append(
                "🔥 헤딩 골 전환율이 매우 높습니다! 공중볼 전술이 효과적입니다"
            )
        elif conversion < 10 and total >= 5:
            insights.append(
                "💡 헤딩 전환율이 낮습니다. 크로스 타이밍과 선수 위치 선정을 개선하세요"
            )

        # 4. Cross utilization
        cross_pct = heading_stats['cross_percentage']
        if cross_pct >= 80:
            insights.append(
                f"📊 헤딩의 {cross_pct}%가 크로스에서 나왔습니다. 측면 공격이 활발합니다"
            )
        elif cross_pct < 40 and total >= 3:
            insights.append(
                "⚠️ 크로스를 통한 헤딩이 적습니다. 측면 공격을 더 활용해보세요"
            )

        # 5. Position insights
        positions = heading_positions['positions']
        if positions['central'] > positions['left'] + positions['right']:
            insights.append(
                "🎯 중앙에서의 헤딩이 많습니다. 타겟맨을 중앙에 배치하는 전술이 효과적입니다"
            )

        # 6. Cross origin insights
        origins = cross_origins['cross_origins']
        if origins['left_wing'] > origins['right_wing'] * 2:
            insights.append(
                "📍 좌측 측면에서 크로스가 주로 발생합니다. 우측 공격도 균형있게 활용하세요"
            )
        elif origins['right_wing'] > origins['left_wing'] * 2:
            insights.append(
                "📍 우측 측면에서 크로스가 주로 발생합니다. 좌측 공격도 균형있게 활용하세요"
            )

        # 7. Box positioning
        box_pct = heading_stats['box_percentage']
        if box_pct >= 80:
            insights.append(
                "✓ 대부분의 헤딩이 박스 안에서 발생했습니다. 좋은 위치 선정입니다"
            )
        elif box_pct < 50:
            insights.append(
                "💡 박스 밖에서의 헤딩이 많습니다. 박스 안으로 더 침투하세요"
            )

        return insights

    @classmethod
    def _empty_analysis(cls) -> Dict[str, Any]:
        """빈 분석 결과"""
        return {
            'heading_stats': {
                'total_headers': 0,
                'goals': 0,
                'on_target': 0,
                'success_rate': 0,
                'conversion_rate': 0,
                'headers_with_assist': 0,
                'cross_percentage': 0,
                'inside_box': 0,
                'box_percentage': 0
            },
            'heading_positions': {
                'positions': {},
                'position_percentages': {},
                'position_goals': {}
            },
            'cross_origins': {
                'cross_origins': {},
                'origin_percentages': {},
                'origin_goals': {}
            },
            'target_man': {
                'player_identified': False,
                'total_headers': 0,
                'total_goals': 0,
                'message': '헤딩 데이터가 없습니다'
            },
            'efficiency_score': {
                'score': 0,
                'grade': 'N/A',
                'grade_text': '데이터 없음'
            },
            'insights': ['헤딩 슈팅이 없습니다']
        }
