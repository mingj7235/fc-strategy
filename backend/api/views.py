import time

import gevent
from gevent.pool import Pool as GeventPool

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from datetime import datetime
import datetime as dt
from .models import User, Match, ShotDetail, UserStats, PlayerPerformance, SiteVisit
from .serializers import (
    UserSerializer, MatchSerializer, MatchListSerializer,
    ShotDetailSerializer, UserStatsSerializer,
    ShotAnalysisSerializer, StyleAnalysisSerializer, StatisticsSerializer,
    PlayerPerformanceSerializer
)
from nexon_api.client import NexonAPIClient
from nexon_api.exceptions import NexonAPIException, UserNotFoundException
from nexon_api.metadata import MetadataLoader
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)
from .analyzers.shot_analyzer import ShotAnalyzer
from .analyzers.style_analyzer import StyleAnalyzer
from .analyzers.statistics import StatisticsCalculator
from .analyzers.timeline_analyzer import TimelineAnalyzer
from .analyzers.player_power_ranking import PlayerPowerRanking
from .analyzers.pass_analyzer import PassAnalyzer
from .analyzers.set_piece_analyzer import SetPieceAnalyzer
from .analyzers.defense_analyzer import DefenseAnalyzer
from .analyzers.pass_variety_analyzer import PassVarietyAnalyzer
from .analyzers.shooting_quality_analyzer import ShootingQualityAnalyzer
from .analyzers.aggregate_stats_analyzer import AggregateStatsAnalyzer


class UserViewSet(viewsets.ModelViewSet):
    """User API ViewSet"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'ouid'

    def _create_match_from_data(self, match_id, user, match_data):
        """Create a Match record from Nexon API match detail data."""
        user_match_info = None
        for info in match_data.get('matchInfo', []):
            if info.get('ouid') == user.ouid:
                user_match_info = info
                break

        if not user_match_info:
            return None

        # Determine result
        result_type = user_match_info.get('matchDetail', {}).get('matchResult')
        if result_type == '승':
            result = 'win'
        elif result_type == '패':
            result = 'lose'
        else:
            result = 'draw'

        # Get opponent's info
        opponent_match_info = None
        for info in match_data.get('matchInfo', []):
            if info.get('ouid') != user.ouid:
                opponent_match_info = info
                break

        opponent_nickname = opponent_match_info.get('nickname') if opponent_match_info else None

        # Calculate pass success rate
        pass_data = user_match_info.get('pass') or {}
        pass_try = pass_data.get('passTry') or 0
        pass_success = pass_data.get('passSuccess') or 0
        pass_success_rate = (pass_success / pass_try * 100) if pass_try > 0 else 0

        # Extract shooting data
        shoot_data = user_match_info.get('shoot') or {}
        opponent_shoot_data = opponent_match_info.get('shoot') or {} if opponent_match_info else {}
        match_detail = user_match_info.get('matchDetail') or {}

        # Calculate shots from player stats (more reliable than shootDetail)
        players = user_match_info.get('player') or []
        shots_count = sum(p.get('status', {}).get('shoot', 0) for p in players)
        shots_on_target_count = sum(p.get('status', {}).get('effectiveShoot', 0) for p in players)

        # Parse and make timezone-aware
        match_date_str = match_data.get('matchDate')
        if match_date_str:
            match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
            if timezone.is_naive(match_date):
                match_date = timezone.make_aware(match_date, dt.timezone.utc)
        else:
            match_date = None

        return Match.objects.create(
            match_id=match_id,
            ouid=user,
            match_date=match_date,
            match_type=match_data.get('matchType'),
            result=result,
            goals_for=shoot_data.get('goalTotalDisplay') or 0,
            goals_against=opponent_shoot_data.get('goalTotalDisplay') or 0,
            possession=match_detail.get('possession') or 0,
            shots=shots_count,
            shots_on_target=shots_on_target_count,
            pass_success_rate=round(pass_success_rate, 2),
            opponent_nickname=opponent_nickname,
            raw_data=match_data
        )

    def _invalidate_user_caches(self, ouid, matchtype, limit):
        """Invalidate all analysis caches for a user when new matches are found."""
        cache_keys = [
            f"user_overview:{ouid}:{matchtype}:{limit}",
            f"shot_analysis:{ouid}:{matchtype}:{limit}",
            f"style_analysis:{ouid}:{matchtype}:{limit}",
            f"statistics:{ouid}:{matchtype}:{limit}",
            f"power_rankings_{ouid}_{matchtype}_{limit}",
            f"pass_analysis_v2_{ouid}_{matchtype}_{limit}",
            f"set_piece_analysis_{ouid}_{matchtype}_{limit}",
            f"defense_analysis_{ouid}_{matchtype}_{limit}",
            f"pass_variety_analysis_{ouid}_{matchtype}_{limit}",
            f"shooting_quality_analysis_{ouid}_{matchtype}_{limit}",
            f"skill_gap_{ouid}_{matchtype}_{limit}",
            f"player_contribution_{ouid}_{matchtype}_{limit}",
            f"form_cycle_{ouid}_{matchtype}_{limit}",
            f"ranker_gap_{ouid}_{matchtype}_{limit}",
            f"habit_loop_{ouid}_{matchtype}_{limit}",
            f"opponent_types_{ouid}_{matchtype}_{limit}",
            f"controller_analysis_{ouid}_{matchtype}_{limit}",
            f"match_list:{ouid}:{matchtype}:0:{limit}",
            f"synced:{ouid}:{matchtype}",
        ]
        cache.delete_many(cache_keys)

    def _do_ensure_matches(self, user, matchtype, limit):
        """Core logic for fetching and storing matches from Nexon API."""
        existing_matches = Match.objects.filter(
            ouid=user,
            match_type=matchtype
        ).order_by('-match_date')

        try:
            client = NexonAPIClient()
            match_ids = client.get_user_matches(user.ouid, matchtype=matchtype, limit=limit)

            # Bulk check which match_ids already exist in DB (eliminates N+1)
            existing_ids = set(
                Match.objects.filter(match_id__in=match_ids, ouid=user)
                .values_list('match_id', flat=True)
            )
            new_ids = [mid for mid in match_ids if mid not in existing_ids]

            # Fetch new matches in parallel (gevent-compatible)
            if new_ids:
                def fetch_and_save(match_id):
                    try:
                        match_data = client.get_match_detail(match_id)
                        self._create_match_from_data(match_id, user, match_data)
                    except Exception:
                        pass  # Individual match failures are non-fatal

                pool = GeventPool(size=10)
                pool.map(fetch_and_save, new_ids)

                # Invalidate analysis caches so they recompute with new matches
                self._invalidate_user_caches(user.ouid, matchtype, limit)

            return list(
                Match.objects.filter(ouid=user, match_type=matchtype)
                .order_by('-match_date')[:limit]
            )

        except NexonAPIException:
            return list(existing_matches[:limit])

    def _ensure_matches(self, user, matchtype, limit):
        """
        Ensure we have at least 'limit' matches in the database.
        Uses Redis lock to prevent duplicate API calls for the same user.
        """
        lock_key = f"ensure_lock:{user.ouid}:{matchtype}"

        # Try to acquire lock; if another request is already fetching, wait
        for _ in range(60):  # Max 60s wait
            if cache.add(lock_key, "1", timeout=120):
                try:
                    return self._do_ensure_matches(user, matchtype, limit)
                finally:
                    cache.delete(lock_key)

            # While waiting, check if DB already has enough data
            count = Match.objects.filter(ouid=user, match_type=matchtype).count()
            if count >= limit:
                return list(
                    Match.objects.filter(ouid=user, match_type=matchtype)
                    .order_by('-match_date')[:limit]
                )
            time.sleep(1)

        # Timeout — return whatever is in DB
        return list(
            Match.objects.filter(ouid=user, match_type=matchtype)
            .order_by('-match_date')[:limit]
        )

    def _start_background_fetch(self, user, matchtype, limit):
        """
        Start fetching matches in the background if not already in progress.
        Returns True if a background fetch was started or is in progress.
        """
        lock_key = f"ensure_lock:{user.ouid}:{matchtype}"
        fetching_key = f"fetching:{user.ouid}:{matchtype}"
        synced_key = f"synced:{user.ouid}:{matchtype}"

        # Recently synced — no need to fetch again
        if cache.get(synced_key):
            return False

        # Check if already fetching
        if cache.get(fetching_key):
            return True

        # Try to acquire lock and fetch in background
        if cache.add(lock_key, "1", timeout=120):
            cache.set(fetching_key, "1", timeout=120)

            def bg_fetch():
                try:
                    self._do_ensure_matches(user, matchtype, limit)
                finally:
                    cache.delete(lock_key)
                    cache.delete(fetching_key)
                    cache.set(synced_key, "1", timeout=1800)  # 30 min

            gevent.spawn(bg_fetch)
            return True

        # Another request holds the lock — fetch is in progress
        return True

    def _is_fetching(self, user, matchtype):
        """Check if background fetch is in progress for this user."""
        return bool(cache.get(f"fetching:{user.ouid}:{matchtype}"))

    def retrieve(self, request, *args, **kwargs):
        """Return user with full division info for both matchtype 50 and 52"""
        from .utils.division_mapper import DivisionMapper
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = dict(serializer.data)

        try:
            cache_key = f'user_divisions:{instance.ouid}'
            divisions_raw = cache.get(cache_key)
            if divisions_raw is None:
                client = NexonAPIClient()
                divisions_raw = client.get_user_max_division(instance.ouid) or []
                cache.set(cache_key, divisions_raw, 1800)

            MATCHTYPE_LABELS = {50: '공식경기', 52: '감독모드'}
            divisions = []
            for d in (divisions_raw if isinstance(divisions_raw, list) else []):
                mt = d.get('matchType')
                div_id = d.get('division')
                if mt in MATCHTYPE_LABELS and div_id:
                    div_info = DivisionMapper.get_division_info(div_id)
                    divisions.append({
                        'matchtype': mt,
                        'matchtype_label': MATCHTYPE_LABELS[mt],
                        **div_info,
                    })
            data['divisions'] = sorted(divisions, key=lambda x: x['matchtype'])
        except Exception:
            data['divisions'] = []

        return Response(data)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """Search user by nickname"""
        nickname = request.query_params.get('nickname')

        if not nickname:
            return Response(
                {'error': 'Nickname parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"[USER_SEARCH] nickname='{nickname}'")

        try:
            # Try to find in database first
            user = User.objects.filter(nickname=nickname).first()

            if user:
                logger.info(f"[USER_SEARCH] nickname='{nickname}' found (DB hit, ouid={user.ouid})")
                serializer = self.get_serializer(user)
                return Response(serializer.data)

            # If not found, fetch from Nexon API
            client = NexonAPIClient()
            ouid = client.get_user_ouid(nickname)

            if not ouid:
                logger.info(f"[USER_SEARCH] nickname='{nickname}' not found")
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get max division and convert to meaningful tier name
            max_division_data = client.get_user_max_division(ouid)
            max_division = None
            if max_division_data and isinstance(max_division_data, list) and len(max_division_data) > 0:
                max_division = max_division_data[0].get('division')

            # Create user in database
            user, created = User.objects.get_or_create(
                ouid=ouid,
                defaults={
                    'nickname': nickname,
                    'max_division': max_division
                }
            )

            logger.info(f"[USER_SEARCH] nickname='{nickname}' found (API, ouid={ouid}, new={'yes' if created else 'no'})")
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        except UserNotFoundException as e:
            logger.info(f"[USER_SEARCH] nickname='{nickname}' not found (UserNotFoundException)")
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except NexonAPIException as e:
            logger.error(f"[USER_SEARCH] nickname='{nickname}' API error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='matches')
    def matches(self, request, ouid=None):
        """Get user's matches with progressive loading support.

        Returns immediately with DB data + is_fetching flag.
        Frontend polls until is_fetching=false.
        """
        user = get_object_or_404(User, ouid=ouid)
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = int(request.query_params.get('limit', 10))

        # Start background fetch if needed (non-blocking)
        is_fetching = self._start_background_fetch(user, matchtype, limit)

        # Return whatever is in DB right now
        db_matches = list(
            Match.objects.filter(ouid=user, match_type=matchtype)
            .order_by('-match_date')[:limit]
        )
        serializer = MatchListSerializer(db_matches, many=True)
        return Response({
            'matches': serializer.data,
            'is_fetching': is_fetching,
            'total': len(db_matches),
            'requested': limit,
        })

    @action(detail=True, methods=['get'], url_path='overview')
    def overview(self, request, ouid=None):
        """
        GET /api/users/{ouid}/overview/?matchtype=50&limit=20

        Returns comprehensive overview with statistics, trends, and insights
        """
        user = get_object_or_404(User, ouid=ouid)
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = int(request.query_params.get('limit', 20))

        # Check cache (15 minute TTL) — only use cache when not fetching
        cache_key = f"user_overview:{ouid}:{matchtype}:{limit}"
        is_fetching = self._is_fetching(user, matchtype)
        if not is_fetching:
            cached_data = cache.get(cache_key)
            if cached_data:
                cached_data['is_fetching'] = False
                return Response(cached_data)

        # Start background fetch if needed (non-blocking)
        if not is_fetching:
            is_fetching = self._start_background_fetch(user, matchtype, limit)

        # Use whatever matches are in DB right now
        matches = list(
            Match.objects.filter(ouid=user, match_type=matchtype)
            .order_by('-match_date')[:limit]
        )

        if not matches:
            return Response({
                'user': {
                    'ouid': user.ouid,
                    'nickname': user.nickname
                },
                'total_matches': 0,
                'record': {
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'win_rate': 0
                },
                'statistics': {
                    'avg_goals_for': 0,
                    'avg_goals_against': 0,
                    'goal_difference': 0,
                    'avg_possession': 0,
                    'avg_shots': 0,
                    'avg_shots_on_target': 0,
                    'shot_accuracy': 0,
                    'avg_pass_success': 0
                },
                'trends': {
                    'recent_form': [],
                    'recent_wins': 0,
                    'trend': 'stable',
                    'first_half_win_rate': 0,
                    'second_half_win_rate': 0
                },
                'insights': ['경기 데이터가 없습니다.'],
                'is_fetching': is_fetching,
            })

        # Calculate statistics
        total_matches = len(matches)
        wins = sum(1 for m in matches if m.result == 'win')
        losses = sum(1 for m in matches if m.result == 'lose')
        draws = sum(1 for m in matches if m.result == 'draw')
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

        # Average stats
        avg_goals_for = sum(m.goals_for for m in matches) / total_matches
        avg_goals_against = sum(m.goals_against for m in matches) / total_matches
        avg_possession = sum(m.possession for m in matches) / total_matches
        avg_shots = sum(m.shots for m in matches) / total_matches
        avg_shots_on_target = sum(m.shots_on_target for m in matches) / total_matches
        avg_pass_success = sum(float(m.pass_success_rate or 0) for m in matches) / total_matches

        shot_accuracy = (avg_shots_on_target / avg_shots * 100) if avg_shots > 0 else 0

        # Recent form (last 5 games)
        recent_5 = matches[:5]
        recent_form = [m.result for m in recent_5]
        recent_wins = sum(1 for r in recent_form if r == 'win')

        # Trends (recent half vs older half, matches ordered newest-first)
        match_dicts = [{'result': m.result} for m in matches]
        trend_data = StatisticsCalculator.calculate_form_trend(match_dicts)
        trend = trend_data['trend']
        recent_win_rate = trend_data['recent_win_rate']
        older_win_rate = trend_data['older_win_rate']

        # Generate insights
        insights = []

        # Win rate insights
        if win_rate >= 60:
            insights.append(f"✅ 승률 {win_rate:.1f}%로 매우 우수한 성적을 보이고 있습니다!")
        elif win_rate >= 50:
            insights.append(f"👍 승률 {win_rate:.1f}%로 준수한 성적입니다")
        else:
            insights.append(f"⚠️ 승률 {win_rate:.1f}%로 개선이 필요합니다")

        # Recent form insights
        if recent_wins >= 4:
            insights.append("🔥 최근 5경기에서 뛰어난 폼을 보이고 있습니다!")
        elif recent_wins <= 1:
            insights.append("📉 최근 폼이 좋지 않습니다. 전술 변화가 필요합니다")

        # Possession insights
        if avg_possession >= 55:
            insights.append(f"⚽ 평균 점유율 {avg_possession:.1f}%로 경기를 주도하고 있습니다")
            if avg_goals_for < 1.5:
                insights.append("⚠️ 높은 점유율에 비해 골 생산력이 부족합니다. 슈팅 결정력 개선이 필요합니다")
        elif avg_possession <= 45:
            insights.append(f"⚡ 평균 점유율 {avg_possession:.1f}%로 역습 축구를 구사하고 있습니다")
            if win_rate >= 50:
                insights.append("🎯 낮은 점유율에도 효율적인 플레이로 승리하고 있습니다")

        # Shot accuracy insights
        if shot_accuracy >= 50:
            insights.append(f"🎯 슈팅 정확도 {shot_accuracy:.1f}%로 매우 효율적입니다")
        elif shot_accuracy < 35:
            insights.append(f"⚠️ 슈팅 정확도 {shot_accuracy:.1f}%로 낮습니다. 더 좋은 위치에서 슈팅하세요")

        # Pass accuracy insights
        if avg_pass_success >= 85:
            insights.append(f"✅ 패스 성공률 {avg_pass_success:.1f}%로 안정적인 빌드업을 보입니다")
        elif avg_pass_success < 75:
            insights.append(f"⚠️ 패스 성공률 {avg_pass_success:.1f}%로 낮습니다. 짧은 패스로 안전하게 연결하세요")

        # Trend insights
        if trend == 'improving':
            insights.append("📈 최근 경기력이 향상되고 있습니다. 현재 전술을 유지하세요!")
        elif trend == 'declining':
            insights.append("📉 최근 경기력이 하락하고 있습니다. 전술 변화를 고려하세요")

        # Goal difference insights
        goal_diff = avg_goals_for - avg_goals_against
        if goal_diff >= 1:
            insights.append(f"⚽ 평균 득실 차 +{goal_diff:.1f}로 공격력이 우수합니다")
        elif goal_diff <= -0.5:
            insights.append(f"🛡️ 평균 득실 차 {goal_diff:.1f}로 수비 보강이 필요합니다")

        overview_data = {
            'user': {
                'ouid': user.ouid,
                'nickname': user.nickname
            },
            'total_matches': total_matches,
            'record': {
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'win_rate': round(win_rate, 1)
            },
            'statistics': {
                'avg_goals_for': round(avg_goals_for, 2),
                'avg_goals_against': round(avg_goals_against, 2),
                'goal_difference': round(avg_goals_for - avg_goals_against, 2),
                'avg_possession': round(avg_possession, 1),
                'avg_shots': round(avg_shots, 1),
                'avg_shots_on_target': round(avg_shots_on_target, 1),
                'shot_accuracy': round(shot_accuracy, 1),
                'avg_pass_success': round(avg_pass_success, 1)
            },
            'trends': {
                'recent_form': recent_form,
                'recent_wins': recent_wins,
                'trend': trend,
                'recent_win_rate': recent_win_rate,
                'older_win_rate': older_win_rate,
            },
            'insights': insights,
            'is_fetching': is_fetching,
        }

        # Only cache when fetch is complete (data is final)
        if not is_fetching:
            cache.set(cache_key, overview_data, 900)  # 15 minutes
        return Response(overview_data)

    @action(detail=True, methods=['get'], url_path='analysis/shots')
    def shot_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/shots/?matchtype=50&limit=10

        Returns comprehensive shot analysis across recent matches using ShotAnalyzer.
        """
        user = get_object_or_404(User, ouid=ouid)
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = int(request.query_params.get('limit', 10))

        # Check cache first (15 minute TTL)
        cache_key = f"shot_analysis:{ouid}:{matchtype}:{limit}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response(
                {'error': 'No matches found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Collect all shot details and player statistics
        all_shots = []
        player_shots = {}  # spid -> {shots, goals, xg_total}

        # Single query for all shots across all matches (fixes N+1)
        all_shot_objects = ShotDetail.objects.filter(match__in=matches)

        for shot in all_shot_objects:
                # Add to overall shot list for heatmap
                all_shots.append({
                    'x': float(shot.x),
                    'y': float(shot.y),
                    'result': shot.result,
                    'shot_type': shot.shot_type
                })

                # Aggregate by player
                if shot.shooter_spid:
                    spid = shot.shooter_spid

                    if spid not in player_shots:
                        player_shots[spid] = {
                            'spid': spid,
                            'shots': 0,
                            'goals': 0,
                            'on_target': 0,
                            'xg_total': 0.0
                        }

                    player_shots[spid]['shots'] += 1

                    # Count goals
                    if shot.result == 'goal':
                        player_shots[spid]['goals'] += 1

                    # Count on target (goal or on_target)
                    if shot.result in ['goal', 'on_target']:
                        player_shots[spid]['on_target'] += 1

                    # Calculate xG for this shot
                    shot_xg = ShotAnalyzer._calculate_advanced_xg({
                        'x': float(shot.x),
                        'y': float(shot.y),
                        'result': shot.result,
                        'shot_type': shot.shot_type
                    })
                    player_shots[spid]['xg_total'] += shot_xg

        if not all_shots:
            return Response(
                {
                    'total_shots': 0,
                    'goals': 0,
                    'on_target': 0,
                    'off_target': 0,
                    'blocked': 0,
                    'shot_accuracy': 0.0,
                    'conversion_rate': 0.0,
                    'xg': 0.0,
                    'heatmap_data': [],
                    'zone_analysis': {},
                    'top_scorers': [],
                    'feedback': ['아직 슈팅 데이터가 없습니다.']
                }
            )

        # Analyze using ShotAnalyzer
        analysis = ShotAnalyzer.analyze_shots(all_shots)

        # Prepare top scorers with player names and images
        top_scorers = []
        for spid, stats in player_shots.items():
            if stats['shots'] >= 3:  # Minimum 3 shots
                player_name = MetadataLoader.get_player_name(spid)
                conversion_rate = (stats['goals'] / stats['shots'] * 100) if stats['shots'] > 0 else 0
                shot_accuracy = (stats['on_target'] / stats['shots'] * 100) if stats['shots'] > 0 else 0
                goals_over_xg = stats['goals'] - stats['xg_total']

                top_scorers.append({
                    'spid': spid,
                    'player_name': player_name,
                    'image_url': f"https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png",
                    'shots': stats['shots'],
                    'goals': stats['goals'],
                    'on_target': stats['on_target'],
                    'conversion_rate': round(conversion_rate, 1),
                    'shot_accuracy': round(shot_accuracy, 1),
                    'xg_total': round(stats['xg_total'], 2),
                    'goals_over_xg': round(goals_over_xg, 2)
                })

        # Sort by goals, then by conversion rate
        top_scorers.sort(key=lambda x: (x['goals'], x['conversion_rate']), reverse=True)
        top_scorers = top_scorers[:10]  # Top 10 scorers

        # Generate feedback
        feedback = ShotAnalyzer.generate_feedback(analysis)

        # Flatten the nested structure for API response
        response_data = {
            # Flatten basic_stats
            **analysis.get('basic_stats', {}),
            # Add all other fields
            'xg_metrics': analysis.get('xg_metrics', {}),
            'big_chances': analysis.get('big_chances', {}),
            'zone_analysis': analysis.get('zone_analysis', {}),
            'shot_types': analysis.get('shot_type_breakdown', {}),
            'distance_analysis': analysis.get('distance_analysis', {}),
            'angle_analysis': analysis.get('angle_analysis', {}),
            'heatmap_data': analysis.get('heatmap_data', []),
            'top_scorers': top_scorers,  # NEW: Top scorers list
            'feedback': feedback
        }

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 900)

        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/style')
    def style_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/style/?matchtype=50&limit=20

        Returns play style analysis with tactical insights using StyleAnalyzer.
        """
        user = get_object_or_404(User, ouid=ouid)
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = int(request.query_params.get('limit', 20))

        # Check cache first (15 minute TTL)
        cache_key = f"style_analysis:{ouid}:{matchtype}:{limit}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            empty = StyleAnalyzer._empty_analysis()
            empty['insights'] = []
            return Response(empty)

        # Convert matches to dict format for analyzer
        match_data = [{
            'result': match.result,
            'possession': match.possession,
            'shots': match.shots,
            'shots_on_target': match.shots_on_target,
            'goals_for': match.goals_for,
            'goals_against': match.goals_against,
            'pass_success_rate': float(match.pass_success_rate or 0)
        } for match in matches]

        # Analyze using StyleAnalyzer
        analysis = StyleAnalyzer.analyze_play_style(match_data)

        # Generate insights
        insights = StyleAnalyzer.generate_insights(analysis)
        analysis['insights'] = insights

        # === Aggregate Statistics (NEW) ===
        # Collect all shot details in a single query (avoid N+1)
        all_shot_details = list(ShotDetail.objects.filter(match__in=matches).values(
            'x', 'y', 'result', 'shot_type', 'goal_time', 'in_penalty',
            'assist_spid', 'assist_x', 'assist_y', 'shooter_spid'
        ))

        # Collect all match raw_data for pass type distribution
        matches_raw_data = [match.raw_data for match in matches if match.raw_data]

        # Analyze aggregate statistics
        aggregate_stats = {}

        if all_shot_details:
            # Shooting efficiency trend (overall shooting stats)
            aggregate_stats['shooting_efficiency'] = AggregateStatsAnalyzer.analyze_shooting_efficiency_trend(all_shot_details)

            # Heading specialists (aerial ball usage)
            aggregate_stats['heading_specialists'] = AggregateStatsAnalyzer.analyze_heading_specialists(all_shot_details)

            # Time-based goal patterns (when goals are scored)
            aggregate_stats['goal_patterns'] = AggregateStatsAnalyzer.analyze_time_based_goal_patterns(all_shot_details)

            # Assist network aggregate
            aggregate_stats['assist_network'] = AggregateStatsAnalyzer.analyze_assist_network_aggregate(all_shot_details)

        if matches_raw_data:
            # Pass type distribution (average pass success rates)
            aggregate_stats['pass_distribution'] = AggregateStatsAnalyzer.analyze_pass_type_distribution(matches_raw_data)

        # Add aggregate stats to response
        analysis['aggregate_stats'] = aggregate_stats

        # Return data directly without serializer validation
        # Cache for 15 minutes
        cache.set(cache_key, analysis, 900)

        return Response(analysis)

    @action(detail=True, methods=['get'], url_path='statistics')
    def statistics(self, request, ouid=None):
        """
        GET /api/users/{ouid}/statistics/?matchtype=50&limit=10

        Returns statistical overview with trends using StatisticsCalculator.
        """
        user = get_object_or_404(User, ouid=ouid)
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = int(request.query_params.get('limit', 10))

        # Check cache first (10 minute TTL)
        cache_key = f"statistics:{ouid}:{matchtype}:{limit}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Get recent matches (auto-fetch from Nexon API if not in DB)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response(
                {'error': 'No matches found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Convert matches to dict format for analyzer
        match_data = [{
            'result': match.result,
            'goals_for': match.goals_for,
            'goals_against': match.goals_against,
            'possession': match.possession,
            'shots': match.shots,
            'shots_on_target': match.shots_on_target,
            'pass_success_rate': float(match.pass_success_rate or 0),
        } for match in matches]

        # Calculate statistics
        stats = StatisticsCalculator.calculate_statistics(match_data)

        # Validate and serialize
        serializer = StatisticsSerializer(data=stats)
        serializer.is_valid(raise_exception=True)

        # Cache for 10 minutes
        cache.set(cache_key, serializer.data, 600)

        return Response(serializer.data)

    def _clean_unavailable_fields(self, breakdown):
        """
        Remove fields that are always 0 because Nexon API doesn't provide them
        """
        # Fields that API doesn't provide
        unavailable_fields = {
            'key_passes', 'through_passes', 'through_pass_attempts', 'through_pass_success',
            'goals_vs_xg', 'xg', 'xg_against', 'xg_prevention',
            'long_passes', 'short_passes',
            'fouls', 'crosses', 'cross_accuracy', 'crosses_per_game',
            'crosses_success', 'long_pass_accuracy'
        }

        if not isinstance(breakdown, dict):
            return breakdown

        cleaned = {}
        for key, value in breakdown.items():
            if isinstance(value, dict):
                # Clean nested dict
                cleaned_nested = {}
                for sub_key, sub_value in value.items():
                    if sub_key not in unavailable_fields:
                        cleaned_nested[sub_key] = sub_value
                if cleaned_nested:  # Only include if not empty after cleaning
                    cleaned[key] = cleaned_nested
            elif key not in unavailable_fields:
                cleaned[key] = value

        return cleaned

    @action(detail=True, methods=['get'], url_path='analysis/power-rankings')
    def power_rankings(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/power-rankings/

        Returns player power rankings for recent matches
        - Power Score (0-100)
        - Tier (SSS, SS, S, A, B, C, D)
        - Form Index
        - Efficiency Metrics
        - Consistency Rating
        - Impact Analysis
        - Position-Specific Ratings
        - Radar Chart Data
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 20)), 100)

        # Check cache
        cache_key = f'power_rankings_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({
                'error': 'No matches found',
                'rankings': []
            })

        # Get ALL player performances in a single query (avoid N+1)
        player_rankings = {}

        all_performances = PlayerPerformance.objects.filter(
            match__in=matches,
            user_ouid=user
        ).exclude(position=28).select_related('match')



        for perf in all_performances:
            match = perf.match
            spid = perf.spid

            if spid not in player_rankings:
                season_info = MetadataLoader.get_season_info(perf.season_id)

                player_rankings[spid] = {
                    'spid': spid,
                    'player_name': perf.player_name,
                    'season_id': perf.season_id,
                    'season_name': season_info['name'],
                    'season_img': season_info['img'],
                    'position': perf.position,  # Will be updated to most common later
                    'grade': perf.grade,
                    'positions': [],  # Track all positions
                    'performances': [],
                    'match_contexts': []
                }

            # Track positions for each match
            player_rankings[spid]['positions'].append(perf.position)

            # Add performance data (updated field names)
            player_rankings[spid]['performances'].append({
                'rating': float(perf.rating),
                'goals': perf.goals,
                'assists': perf.assists,
                'shots': perf.shots,
                'shots_on_target': perf.shots_on_target,
                'shot_accuracy': float(perf.shot_accuracy) if perf.shot_accuracy else 0.0,
                'pass_attempts': perf.pass_attempts,
                'pass_success': perf.pass_success,
                'pass_success_rate': float(perf.pass_success_rate) if perf.pass_success_rate else 0.0,
                'short_pass_attempts': perf.short_pass_attempts,
                'short_pass_success': perf.short_pass_success,
                'long_pass_attempts': perf.long_pass_attempts,
                'long_pass_success': perf.long_pass_success,
                'through_pass_attempts': perf.through_pass_attempts,
                'through_pass_success': perf.through_pass_success,
                'dribble_attempts': perf.dribble_attempts,
                'dribble_success': perf.dribble_success,
                'dribble_success_rate': float(perf.dribble_success_rate) if perf.dribble_success_rate else 0.0,
                'tackle_attempts': perf.tackle_attempts,
                'tackle_success': perf.tackle_success,
                'interceptions': perf.interceptions or 0,
                'blocks': perf.blocks,
                'block_attempts': perf.block_attempts,
                'aerial_success': perf.aerial_success,
                'key_passes': perf.key_passes or 0,
                'fouls': perf.fouls or 0,
                'yellow_cards': perf.yellow_cards,
                'red_cards': perf.red_cards,
                # GK specific
                'saves': perf.saves if perf.position == 0 else None,
                'opponent_shots': perf.opponent_shots if perf.position == 0 else None,
                'goals_conceded': perf.goals_conceded if perf.position == 0 else None,
                'xg': float(perf.xg) if perf.xg else None,
                'xg_against': float(perf.xg_against) if perf.xg_against else None,
                'match_result': match.result
            })

            # Add match context
            player_rankings[spid]['match_contexts'].append({
                'result': match.result,
                'final_goal_difference': abs(match.goals_for - match.goals_against),
                'is_clutch_situation': abs(match.goals_for - match.goals_against) <= 1,
                'is_winning_goal': False,  # Would need shot details to determine
                'has_late_goal': False,     # Would need shot details to determine
                'is_comeback': match.result == 'win' and match.goals_against > 0,
                'was_losing': match.goals_against > match.goals_for
            })

        # Calculate power rankings for each player
        results = []
        for spid, data in player_rankings.items():
            # Only rank players with 3+ appearances
            if len(data['performances']) < 3:
                continue

            # Determine most common position (최빈값)
            from collections import Counter
            position_counter = Counter(data['positions'])
            most_common_position = position_counter.most_common(1)[0][0]

            ranking = PlayerPowerRanking.calculate_power_ranking(
                player_performances=data['performances'],
                match_contexts=data['match_contexts'],
                position=most_common_position
            )

            # Transform position_rating to match frontend expectations
            if ranking.get('position_rating'):
                pr = ranking['position_rating']

                # Add position_group and position_group_name
                # Must match PositionSpecificEvaluator.POSITION_CODES exactly
                position_groups = {
                    0: ('GK', '골키퍼'),
                    **{p: ('CB', '센터백') for p in [1, 4, 5, 6]},   # SW, RCB, CB, LCB
                    **{p: ('FB', '풀백/윙백') for p in [3, 7]},       # RB, LB
                    **{p: ('WB', '윙백') for p in [2, 8]},            # RWB, LWB
                    **{p: ('CDM', '수비형 미드필더') for p in [9, 10, 11]},  # RDM, CDM, LDM
                    **{p: ('CM', '중앙 미드필더') for p in [13, 14, 15]},    # RCM, CM, LCM
                    **{p: ('WM', '미드필더') for p in [12, 16]},       # RM, LM
                    **{p: ('CAM', '공격형 미드필더') for p in [17, 18, 19]},  # RAM, CAM, LAM
                    **{p: ('W', '윙어') for p in [20, 22, 23, 27]},   # RF, LF, RW, LW
                    **{p: ('ST', '스트라이커') for p in [21, 24, 25, 26]},  # CF, RS, ST, LS
                }
                position_group, position_group_name = position_groups.get(most_common_position, ('MID', '미드필더'))

                # Clean unavailable fields from breakdown
                cleaned_breakdown = self._clean_unavailable_fields(pr.get('breakdown', {}))

                ranking['position_rating'] = {
                    'position_score': pr.get('position_score', 0),
                    'position_group': position_group,
                    'position_group_name': position_group_name,
                    'key_metrics': cleaned_breakdown,
                    'strengths': pr.get('key_strengths', []),
                    'weaknesses': pr.get('areas_for_improvement', []),
                    'evaluation_criteria': {}
                }

            results.append({
                'spid': spid,
                'player_name': data['player_name'],
                'season_id': data['season_id'],
                'season_name': data['season_name'],
                'season_img': data.get('season_img', ''),
                'position': most_common_position,
                'grade': data['grade'],
                'matches_played': len(data['performances']),
                'image_url': f"https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png",
                **ranking
            })

        # Sort by power score
        results.sort(key=lambda x: x['power_score'], reverse=True)

        # === Aggregate Statistics (NEW) ===
        # Collect all shot details in a single query (avoid N+1)
        all_shot_details = list(ShotDetail.objects.filter(match__in=matches).values(
            'x', 'y', 'result', 'shot_type', 'goal_time', 'in_penalty',
            'assist_spid', 'assist_x', 'assist_y', 'shooter_spid'
        ))

        # Collect all match raw_data for pass type distribution
        matches_raw_data = [match.raw_data for match in matches if match.raw_data]

        # Analyze aggregate statistics
        aggregate_stats = {}

        if all_shot_details:
            # Assist network aggregate (top playmakers across all matches)
            aggregate_stats['assist_network'] = AggregateStatsAnalyzer.analyze_assist_network_aggregate(all_shot_details)

            # Heading specialists (heading stats across all matches)
            aggregate_stats['heading_specialists'] = AggregateStatsAnalyzer.analyze_heading_specialists(all_shot_details)

            # Shooting efficiency trend (overall shooting stats)
            aggregate_stats['shooting_efficiency'] = AggregateStatsAnalyzer.analyze_shooting_efficiency_trend(all_shot_details)

            # Time-based goal patterns (when goals are scored)
            aggregate_stats['goal_patterns'] = AggregateStatsAnalyzer.analyze_time_based_goal_patterns(all_shot_details)

        if matches_raw_data:
            # Pass type distribution (average pass success rates)
            aggregate_stats['pass_distribution'] = AggregateStatsAnalyzer.analyze_pass_type_distribution(matches_raw_data)

        response_data = {
            'total_players': len(results),
            'rankings': results,
            'aggregate_stats': aggregate_stats  # NEW: Aggregate statistics
        }

        # Cache for 30 minutes
        cache.set(cache_key, response_data, 1800)

        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/passes')
    def pass_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/passes/

        Returns comprehensive pass analysis:
        - Overall pass statistics
        - Key passes and xA (Expected Assists)
        - Progressive passing
        - Pass network (top passers)
        - Pass efficiency
        - Insights with Keep-Stop-Action framework
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 20)), 100)

        # Check cache
        cache_key = f'pass_analysis_v2_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({
                'error': 'No matches found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Aggregate match data
        total_shots = sum(m.shots for m in matches)
        match_data = {
            'shots': total_shots,
            'goals': sum(m.goals_for for m in matches),
        }

        # Get all player performances (single query instead of per-match)
        all_performances = list(
            PlayerPerformance.objects.filter(match__in=matches).values(
                'spid', 'player_name', 'season_id', 'season_name',
                'position', 'pass_attempts', 'pass_success',
                'assists', 'goals'
            )
        )

        # Analyze passes (PassAnalyzer handles empty performances gracefully)
        analysis = PassAnalyzer.analyze_passes(
            match_data=match_data,
            player_performances=all_performances
        )

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            **analysis
        }

        # Cache for 30 minutes
        cache.set(cache_key, response_data, 1800)

        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/set-pieces')
    def set_piece_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/set-pieces/

        Returns set piece analysis:
        - Free kick efficiency
        - Penalty kick conversion
        - Heading effectiveness
        - Set piece dependency
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 20)), 100)

        # Check cache
        cache_key = f'set_piece_analysis_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({
                'error': 'No matches found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Extract raw_data from matches
        matches_data = [match.raw_data for match in matches if match.raw_data]

        # Analyze set pieces
        analysis = SetPieceAnalyzer.analyze_set_pieces(matches_data)

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            **analysis
        }

        # Cache for 30 minutes
        cache.set(cache_key, response_data, 1800)

        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/defense')
    def defense_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/defense/

        Returns defensive analysis:
        - Tackle statistics
        - Block statistics
        - Defensive intensity
        - Defensive style
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 20)), 100)

        # Check cache
        cache_key = f'defense_analysis_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({
                'error': 'No matches found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Extract raw_data from matches
        matches_data = [match.raw_data for match in matches if match.raw_data]

        # Analyze defense
        analysis = DefenseAnalyzer.analyze_defense(matches_data)

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            **analysis
        }

        # Cache for 30 minutes
        cache.set(cache_key, response_data, 1800)

        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/pass-variety')
    def pass_variety_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/pass-variety/

        Returns pass variety analysis:
        - Pass type distribution
        - Build-up style
        - Pass diversity index
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 20)), 100)

        # Check cache
        cache_key = f'pass_variety_analysis_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({
                'error': 'No matches found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Extract raw_data from matches
        matches_data = [match.raw_data for match in matches if match.raw_data]

        # Analyze pass variety
        analysis = PassVarietyAnalyzer.analyze_pass_variety(matches_data)

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            **analysis
        }

        # Cache for 30 minutes
        cache.set(cache_key, response_data, 1800)

        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/shooting-quality')
    def shooting_quality_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/shooting-quality/

        Returns shooting quality analysis:
        - Inside vs outside box efficiency
        - Shot type analysis
        - Clinical finishing rating
        - Shooting style
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 20)), 100)

        # Check cache
        cache_key = f'shooting_quality_analysis_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({
                'error': 'No matches found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Extract raw_data from matches
        matches_data = [match.raw_data for match in matches if match.raw_data]

        # Analyze shooting quality
        analysis = ShootingQualityAnalyzer.analyze_shooting_quality(matches_data)

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            **analysis
        }

        # Cache for 30 minutes
        cache.set(cache_key, response_data, 1800)

        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/skill-gap')
    def skill_gap_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/skill-gap/?matchtype=50&limit=20

        B2. 실력 격차 인덱스 (Skill Gap Index)
        내가 쓰는 선수들로 랭커가 같은 선수로 내는 성적과 내 성적을 비교해 격차를 Z-score로 수치화.
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 20)), 100)

        cache_key = f'skill_gap_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({'error': 'No matches found'}, status=status.HTTP_404_NOT_FOUND)

        # Group PlayerPerformance by spid
        all_performances = PlayerPerformance.objects.filter(
            match__in=matches, user_ouid=user
        ).exclude(position=28).values(
            'spid', 'player_name', 'position', 'rating', 'goals', 'assists',
            'shots', 'shots_on_target', 'pass_attempts', 'pass_success',
            'dribble_attempts', 'dribble_success', 'tackle_success', 'blocks'
        )

        from collections import defaultdict
        perf_by_spid = defaultdict(list)
        for p in all_performances:
            perf_by_spid[p['spid']].append(p)

        # Filter players with 5+ appearances
        eligible = {spid: perfs for spid, perfs in perf_by_spid.items() if len(perfs) >= 5}

        if not eligible:
            return Response({
                'player_gaps': [],
                'insights': ['5경기 이상 플레이한 선수가 없습니다. 더 많은 경기를 분석하세요.'],
                'matches_analyzed': len(matches),
            })

        from .analyzers.skill_gap_analyzer import SkillGapAnalyzer
        client = NexonAPIClient()

        # Batch ranker API call (single request instead of up to 10)
        top_eligible = list(eligible.items())[:10]
        players_query = [{'id': spid, 'po': perfs[0]['position']} for spid, perfs in top_eligible]
        ranker_by_spid = {}
        try:
            ranker_data = client.get_ranker_stats(matchtype=matchtype, players=players_query)
            if ranker_data and isinstance(ranker_data, list):
                for entry in ranker_data:
                    entry_spid = entry.get('spId')
                    status = entry.get('status', {})
                    status_list = []
                    if isinstance(status, list):
                        status_list = status
                    elif isinstance(status, dict) and status:
                        status_list = [status]
                    if entry_spid:
                        ranker_by_spid[entry_spid] = status_list
        except Exception:
            pass

        player_gaps = []
        for spid, perfs in top_eligible:
            position = perfs[0]['position']
            player_name = perfs[0]['player_name']
            ranker_status_list = ranker_by_spid.get(spid, [])

            gap = SkillGapAnalyzer.analyze_player_gap(
                spid=spid,
                player_name=player_name,
                position=position,
                appearances=len(perfs),
                performances=perfs,
                ranker_status_list=ranker_status_list,
            )

            if gap:
                gap['image_url'] = f"https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png"
                player_gaps.append(gap)

        player_gaps.sort(key=lambda x: x.get('overall_z_score', -99), reverse=True)
        insights = SkillGapAnalyzer.generate_overall_insights(player_gaps)

        response_data = {
            'matches_analyzed': len(matches),
            'players_analyzed': len(player_gaps),
            'player_gaps': player_gaps,
            'insights': insights,
        }

        cache.set(cache_key, response_data, 1800)  # 30 min
        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/player-contribution')
    def player_contribution_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/player-contribution/?matchtype=50&limit=30

        C1. 선수 기여도 분석
        경기 기여도 → 포지션별 맞춤 기여도 점수 산출.
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 30)), 100)

        cache_key = f'player_contribution_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({'error': 'No matches found'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch trade history (buy trades only) — 전체 내역 페이지네이션
        try:
            client = NexonAPIClient()
            trade_history = []
            offset = 0
            page_size = 100
            max_pages = 20  # 최대 2000건 (과도한 API 호출 방지)
            for _ in range(max_pages):
                batch = client.get_user_trade(
                    user.ouid, tradetype='buy', offset=offset, limit=page_size
                )
                if not isinstance(batch, list) or not batch:
                    break
                trade_history.extend(batch)
                if len(batch) < page_size:
                    break  # 마지막 페이지
                offset += page_size
        except Exception:
            trade_history = []

        # Group performances by spid
        all_performances = PlayerPerformance.objects.filter(
            match__in=matches, user_ouid=user
        ).exclude(position=28).values(
            'spid', 'player_name', 'position', 'grade', 'rating', 'goals', 'assists',
            'shots', 'shots_on_target', 'pass_attempts', 'pass_success',
            'dribble_attempts', 'dribble_success', 'tackle_success', 'blocks'
        )

        from collections import defaultdict
        perf_by_spid = defaultdict(list)
        for p in all_performances:
            perf_by_spid[p['spid']].append(dict(p))

        from .analyzers.roi_analyzer import ROIAnalyzer
        result = ROIAnalyzer.calculate_squad_roi(
            trade_history=trade_history,
            player_performances_by_spid=perf_by_spid,
        )

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            'trade_history_count': len(trade_history),
            **result,
        }

        cache.set(cache_key, response_data, 1800)
        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/form-cycle')
    def form_cycle_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/form-cycle/?matchtype=50&limit=50

        B4. 폼 사이클 분석기
        핫 스트릭/슬럼프 주기 탐지 + 세션 최적화 분석.
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 50)), 200)

        cache_key = f'form_cycle_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({'error': 'No matches found'}, status=status.HTTP_404_NOT_FOUND)

        match_data = [{
            'match_date': str(m.match_date),
            'result': m.result,
            'goals_for': m.goals_for,
            'goals_against': m.goals_against,
            'possession': m.possession,
            'shots': m.shots,
            'shots_on_target': m.shots_on_target,
            'pass_success_rate': float(m.pass_success_rate or 70),
            'raw_data': m.raw_data,
        } for m in matches]

        from .analyzers.form_cycle_analyzer import FormCycleAnalyzer
        result = FormCycleAnalyzer.analyze_form_cycle(match_data)

        response_data = {
            'matchtype': matchtype,
            'matches_requested': limit,
            **result,
        }

        cache.set(cache_key, response_data, 900)  # 15 min
        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/ranker-gap')
    def ranker_gap_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/ranker-gap/?matchtype=50&limit=20

        D1. 랭커 격차 대시보드
        모든 차원을 랭커와 비교하는 단일 통합 대시보드.
        "랭커까지의 거리" 단일 점수 (0-100) 제공.
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 20)), 100)

        cache_key = f'ranker_gap_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({'error': 'No matches found'}, status=status.HTTP_404_NOT_FOUND)

        match_data = [{
            'result': m.result,
            'goals_for': m.goals_for,
            'goals_against': m.goals_against,
            'possession': m.possession,
            'shots': m.shots,
            'shots_on_target': m.shots_on_target,
            'pass_success_rate': float(m.pass_success_rate or 0),
        } for m in matches]

        # Single query for all fields (eliminates duplicate DB query)
        from collections import Counter
        all_perf_raw = list(PlayerPerformance.objects.filter(
            match__in=matches, user_ouid=user
        ).exclude(position=28).values(
            'spid', 'position', 'rating', 'goals', 'assists',
            'dribble_attempts', 'dribble_success'
        ))

        all_performances = [
            {k: p[k] for k in ('rating', 'goals', 'assists', 'dribble_attempts', 'dribble_success')}
            for p in all_perf_raw
        ]

        spid_counter = Counter(p['spid'] for p in all_perf_raw)
        top_spids = [(spid, count) for spid, count in spid_counter.most_common(3) if count >= 5]

        ranker_api_data = []
        if top_spids:
            try:
                client = NexonAPIClient()
                players_query = []
                spid_positions = {}
                for p in all_perf_raw:
                    if p['spid'] not in spid_positions:
                        spid_positions[p['spid']] = p['position']

                for spid, _ in top_spids:
                    players_query.append({'id': spid, 'po': spid_positions.get(spid, 18)})

                raw = client.get_ranker_stats(matchtype=matchtype, players=players_query)
                if isinstance(raw, list):
                    ranker_api_data = raw
            except Exception:
                pass

        # Get user's division
        division = user.max_division or 300

        from .analyzers.ranker_gap_analyzer import RankerGapAnalyzer
        result = RankerGapAnalyzer.calculate_ranker_gap(
            matches=match_data,
            player_performances=all_performances,
            division=division,
            ranker_api_data=ranker_api_data if ranker_api_data else None,
        )

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            **result,
        }

        cache.set(cache_key, response_data, 1800)
        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/habit-loop')
    def habit_loop_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/habit-loop/?matchtype=50&limit=30

        B1. 습관 루프 탐지기
        마르코프 체인 기반 패스 시퀀스 + 슛 존 고착화 + 압박 반응 패턴.
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 30)), 100)

        cache_key = f'habit_loop_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({'error': 'No matches found'}, status=status.HTTP_404_NOT_FOUND)

        matches_raw = [m.raw_data for m in matches if m.raw_data]
        match_dicts = [{
            'result': m.result,
            'goals_for': m.goals_for,
            'goals_against': m.goals_against,
            'possession': m.possession,
            'pass_success_rate': float(m.pass_success_rate or 0),
            'raw_data': m.raw_data,
        } for m in matches]

        shot_details = list(ShotDetail.objects.filter(match__in=matches).values('x', 'y', 'result'))

        from .analyzers.habit_loop_analyzer import HabitLoopAnalyzer
        result = HabitLoopAnalyzer.analyze_habit_loops(
            matches_raw=matches_raw,
            user_ouid=user.ouid,
            shot_details=shot_details,
            matches=match_dicts,
        )

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            **result,
        }

        cache.set(cache_key, response_data, 1800)
        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/opponent-types')
    def opponent_types_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/opponent-types/?matchtype=50&limit=50

        D2. 상대 유형 분류기 & 승률 맵
        내 매치 기록의 상대팀 데이터를 6개 유형으로 분류하고 유형별 승률 분석.
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 50)), 200)

        cache_key = f'opponent_types_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({'error': 'No matches found'}, status=status.HTTP_404_NOT_FOUND)

        match_dicts = [{
            'result': m.result,
            'goals_for': m.goals_for,
            'goals_against': m.goals_against,
            'raw_data': m.raw_data,
        } for m in matches if m.raw_data]

        from .analyzers.opponent_classifier import OpponentClassifier
        result = OpponentClassifier.classify_opponents(
            matches=match_dicts,
            user_ouid=user.ouid,
        )

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches),
            **result,
        }

        cache.set(cache_key, response_data, 3600)  # 1 hour
        return Response(response_data)

    @action(detail=True, methods=['get'], url_path='analysis/controller')
    def controller_analysis(self, request, ouid=None):
        """
        GET /api/users/{ouid}/analysis/controller/

        Returns controller performance analysis:
        - Keyboard vs gamepad win rate comparison
        - Controller-specific playstyle differences
        - Controller recommendation
        - Korean language insights
        """
        matchtype = int(request.query_params.get('matchtype', 50))
        limit = min(int(request.query_params.get('limit', 50)), 100)  # More matches for reliable comparison

        # Check cache
        cache_key = f'controller_analysis_{ouid}_{matchtype}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = get_object_or_404(User, ouid=ouid)

        # Ensure we have enough matches (fetch from API if needed)
        matches = self._ensure_matches(user, matchtype, limit)

        if not matches:
            return Response({
                'error': 'No matches found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Convert to serializable format with all needed fields
        matches_data = []
        for match in matches:
            if not match.raw_data:
                continue

            matches_data.append({
                'match_id': match.match_id,
                'result': match.result,
                'goals_for': match.goals_for,
                'goals_against': match.goals_against,
                'possession': match.possession,
                'shots': match.shots,
                'shots_on_target': match.shots_on_target,
                'pass_success_rate': match.pass_success_rate,
                'raw_data': match.raw_data
            })

        # Analyze controller performance
        from api.analyzers.controller_analyzer import ControllerAnalyzer
        analysis = ControllerAnalyzer.analyze_controller_performance(matches_data, ouid=ouid)

        response_data = {
            'matchtype': matchtype,
            'matches_analyzed': len(matches_data),
            **analysis
        }

        # Cache for 1 hour
        cache.set(cache_key, response_data, 3600)

        return Response(response_data)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """Match API ViewSet"""
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    lookup_field = 'match_id'

    def _get_match_safely(self, match_id, user_ouid=None):
        """Safely fetch a Match by match_id, avoiding MultipleObjectsReturned.

        Since match_id alone is not unique (the same match is stored once per
        user after migration 0009 changed the PK to an auto-increment id),
        we must always filter by ouid when it is available.  When no ouid is
        supplied we fall back to the first matching row so that API consumers
        that don't send an ouid query param still work.

        Raises Http404 when no matching record is found.
        """
        qs = Match.objects.filter(match_id=match_id)
        if user_ouid:
            qs = qs.filter(ouid__ouid=user_ouid)
        match = qs.first()
        if match is None:
            raise Http404(f'Match {match_id} not found')
        return match

    @action(detail=True, methods=['get'], url_path='detail')
    def get_detail(self, request, match_id=None):
        """Get match detail, filtered by ouid when provided."""
        user_ouid = request.query_params.get('ouid')
        try:
            match = self._get_match_safely(match_id, user_ouid)
            serializer = self.get_serializer(match)
            return Response(serializer.data)
        except Http404:
            # Not in DB — try Nexon API as fallback
            try:
                client = NexonAPIClient()
                match_data = client.get_match_detail(match_id)
                return Response(match_data)
            except NexonAPIException as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )

    @action(detail=True, methods=['get'], url_path='heatmap')
    def heatmap(self, request, match_id=None):
        """
        GET /api/matches/{match_id}/heatmap/?ouid=xxx

        Get shot heatmap data for the match.

        Query params:
        - ouid (optional): User's OUID to get their perspective of the match
        """
        user_ouid = request.query_params.get('ouid')

        match = self._get_match_safely(match_id, user_ouid)
        shot_details = ShotDetail.objects.filter(match=match)

        serializer = ShotDetailSerializer(shot_details, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='player-stats')
    def player_stats(self, request, match_id=None):
        """
        GET /api/matches/{match_id}/player-stats/?ouid=xxx

        Returns player performance statistics for the match.
        Includes top 3 performers and all player stats.

        Query params:
        - ouid (optional): User's OUID to get their perspective of the match
        """
        user_ouid = request.query_params.get('ouid')

        match = self._get_match_safely(match_id, user_ouid)

        # Get player performances ordered by rating (only participated players, user's team only)
        performances = PlayerPerformance.objects.filter(
            match=match,
            user_ouid=match.ouid,  # Only user's team
            rating__gt=0           # Exclude bench players (rating = 0)
        ).order_by('-rating')

        if not performances.exists():
            return Response({
                'top_performers': [],
                'all_players': [],
                'message': 'No player performance data available for this match'
            })

        # Top 3 performers
        top_performers = performances[:3]

        serializer = PlayerPerformanceSerializer(performances, many=True)
        top_serializer = PlayerPerformanceSerializer(top_performers, many=True)

        return Response({
            'top_performers': top_serializer.data,
            'all_players': serializer.data
        })

    @action(detail=True, methods=['get'], url_path='timeline')
    def timeline(self, request, match_id=None):
        """
        GET /api/matches/{match_id}/timeline/?ouid=xxx

        Returns timeline analysis including:
        - xG by period (first half vs second half)
        - Key moments (goals and big chances)
        - Timeline data for visualization
        - Insights in Korean

        Query params:
        - ouid (optional): User's OUID to get their perspective of the match
        """
        user_ouid = request.query_params.get('ouid')

        match = self._get_match_safely(match_id, user_ouid)

        # Get shot details with goal_time
        shot_details = ShotDetail.objects.filter(match=match).values(
            'x', 'y', 'result', 'shot_type', 'goal_time'
        )

        if not shot_details:
            return Response({
                'xg_by_period': {
                    'first_half': 0.0,
                    'second_half': 0.0
                },
                'key_moments': [],
                'timeline_data': [],
                'insights': ['아직 슈팅 데이터가 없습니다.']
            })

        # Convert to list of dicts
        shot_list = list(shot_details)

        # Analyze timeline
        analysis = TimelineAnalyzer.analyze_timeline(shot_list)

        # Generate insights
        insights = TimelineAnalyzer.generate_insights(analysis)
        analysis['insights'] = insights

        # Cache for 24 hours
        cache_key = f"timeline:{match_id}"
        cache.set(cache_key, analysis, 86400)

        return Response(analysis)

    @action(detail=True, methods=['get'], url_path='assist-network')
    def assist_network(self, request, match_id=None):
        """
        GET /api/matches/{match_id}/assist-network/?ouid=xxx

        Returns assist network analysis including:
        - Assist heatmap (where assists came from)
        - Player network (A → B connections)
        - Assist types (wing vs central)
        - Assist distance statistics
        - Top playmakers ranking

        Query params:
        - ouid (optional): User's OUID to get their perspective of the match
        """
        user_ouid = request.query_params.get('ouid')

        match = self._get_match_safely(match_id, user_ouid)

        # Check cache first (24 hours)
        cache_key = f"assist_network:{match_id}:{match.ouid.ouid}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Get shot details with assist information
        shot_details = ShotDetail.objects.filter(match=match).values(
            'x', 'y', 'result', 'shot_type', 'goal_time',
            'assist_x', 'assist_y', 'assist_spid', 'shooter_spid'
        )

        if not shot_details:
            from api.analyzers.assist_analyzer import AssistNetworkAnalyzer
            return Response(AssistNetworkAnalyzer._empty_analysis())

        # Convert to list
        shot_list = list(shot_details)

        # Analyze assists
        from api.analyzers.assist_analyzer import AssistNetworkAnalyzer
        analysis = AssistNetworkAnalyzer.analyze_assists(shot_list)

        # Enrich player network with player names
        from nexon_api.metadata import MetadataLoader
        for connection in analysis['player_network']:
            from_spid = connection['from_spid']
            to_spid = connection['to_spid']
            connection['from_player_name'] = MetadataLoader.get_player_name(from_spid)
            connection['to_player_name'] = MetadataLoader.get_player_name(to_spid)

        # Enrich top playmakers with player names
        for playmaker in analysis['top_playmakers']:
            spid = playmaker['spid']
            playmaker['player_name'] = MetadataLoader.get_player_name(spid)

        # Cache for 24 hours
        cache.set(cache_key, analysis, 86400)

        return Response(analysis)

    @action(detail=True, methods=['get'], url_path='shot-types')
    def shot_types(self, request, match_id=None):
        """
        GET /api/matches/{match_id}/shot-types/?ouid=xxx

        Returns detailed shot type analysis including:
        - Type breakdown (normal, heading, volley, etc.)
        - Box location analysis (inside vs outside)
        - Post hits analysis
        - Insights in Korean

        Query params:
        - ouid (optional): User's OUID to get their perspective of the match
        """
        user_ouid = request.query_params.get('ouid')

        match = self._get_match_safely(match_id, user_ouid)

        # Check cache first (24 hours)
        cache_key = f"shot_types:{match_id}:{match.ouid.ouid}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Get shot details with type information
        shot_details = ShotDetail.objects.filter(match=match).values(
            'shot_type', 'result', 'hit_post', 'in_penalty', 'x', 'y'
        )

        if not shot_details:
            from api.analyzers.shot_type_analyzer import ShotTypeAnalyzer
            return Response(ShotTypeAnalyzer._empty_analysis())

        # Analyze shot types
        shot_list = list(shot_details)
        from api.analyzers.shot_type_analyzer import ShotTypeAnalyzer
        analysis = ShotTypeAnalyzer.analyze_shot_types(shot_list)

        # Cache for 24 hours
        cache.set(cache_key, analysis, 86400)

        return Response(analysis)

    @action(detail=True, methods=['get'], url_path='pass-types')
    def pass_types(self, request, match_id=None):
        """
        GET /api/matches/{match_id}/pass-types/?ouid=xxx

        Pass type detailed analysis including:
        - Pass type breakdown (short, long, through, lobbed through, driven ground, bouncing lob)
        - Pass diversity score
        - Play style classification (ground vs aerial, build-up vs counter)
        - Korean language insights

        Query params:
        - ouid (optional): User's OUID to get their perspective of the match
        """
        # Get user's OUID from query params (optional)
        user_ouid = request.query_params.get('ouid')

        # Create cache key
        cache_key = f"pass_types_{match_id}_{user_ouid or 'no_ouid'}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)

        # Get match
        match = self._get_match_safely(match_id, user_ouid)

        # Extract pass data from raw_data
        if not match.raw_data:
            return Response({'error': '경기 데이터가 없습니다.'}, status=404)

        match_info = match.raw_data.get('matchInfo', [])
        if not match_info:
            return Response({'error': '경기 정보가 없습니다.'}, status=404)

        # Find user's pass data
        user_match_info = None
        if user_ouid:
            # Get specific user's data
            for info in match_info:
                if info.get('ouid') == user_ouid:
                    user_match_info = info
                    break
        else:
            # Use first player's data
            user_match_info = match_info[0]

        if not user_match_info:
            return Response({'error': '사용자 경기 정보를 찾을 수 없습니다.'}, status=404)

        pass_data = user_match_info.get('pass', {})
        if not pass_data:
            return Response({'error': '패스 데이터가 없습니다.'}, status=404)

        # Analyze pass types
        from api.analyzers.pass_type_analyzer import PassTypeAnalyzer
        analysis = PassTypeAnalyzer.analyze_pass_types(pass_data)

        # Cache for 24 hours
        cache.set(cache_key, analysis, 86400)

        return Response(analysis)

    @action(detail=True, methods=['get'], url_path='heading-analysis')
    def heading_analysis(self, request, match_id=None):
        """
        GET /api/matches/{match_id}/heading-analysis/?ouid=xxx

        Heading specialist analysis including:
        - Heading stats (total, goals, success rate, conversion rate)
        - Heading positions (where headers occurred)
        - Cross origins (where assists came from)
        - Target man identification
        - Aerial efficiency score
        - Korean language insights

        Query params:
        - ouid (optional): User's OUID to get their perspective of the match
        """
        # Get user's OUID from query params (optional)
        user_ouid = request.query_params.get('ouid')

        # Create cache key
        cache_key = f"heading_analysis_{match_id}_{user_ouid or 'no_ouid'}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)

        # Get match
        match = self._get_match_safely(match_id, user_ouid)

        # Get shot details for this match
        shot_details = ShotDetail.objects.filter(match=match)

        # Determine which player's shots to analyze
        if user_ouid:
            # Filter shots for specific user (need to implement user filtering in ShotDetail)
            # For now, analyze all shots from the match
            pass

        shot_list = list(shot_details.values(
            'shot_type', 'result', 'x', 'y', 'in_penalty', 'assist_spid', 'assist_y'
        ))

        if not shot_list:
            from api.analyzers.heading_analyzer import HeadingAnalyzer
            return Response(HeadingAnalyzer._empty_analysis())

        # Analyze heading
        from api.analyzers.heading_analyzer import HeadingAnalyzer
        analysis = HeadingAnalyzer.analyze_heading(shot_list)

        # Cache for 24 hours
        cache.set(cache_key, analysis, 86400)

        return Response(analysis)

    @action(detail=True, methods=['get'], url_path='analysis')
    def match_analysis(self, request, match_id=None):
        """
        GET /api/matches/{match_id}/analysis/?ouid=xxx

        Comprehensive match analysis including:
        - Match overview
        - Player performances (top 3 + all players)
        - Timeline analysis
        - Tactical insights (attack pattern, possession style, recommendations)

        Query params:
        - ouid (optional): User's OUID to get their perspective of the match
        """
        # Get user's OUID from query params (optional)
        user_ouid = request.query_params.get('ouid')

        match = self._get_match_safely(match_id, user_ouid)

        # Check cache first (24 hours) - include ouid in cache key
        cache_key = f"match_analysis:{match_id}:{match.ouid.ouid}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # 1. Match overview
        match_overview = {
            'match_id': match.match_id,
            'user_nickname': match.ouid.nickname,
            'opponent_nickname': match.opponent_nickname,
            'match_date': match.match_date,
            'result': match.result,
            'goals_for': match.goals_for,
            'goals_against': match.goals_against,
            'possession': match.possession,
            'shots': match.shots,
            'shots_on_target': match.shots_on_target,
            'pass_success_rate': float(match.pass_success_rate) if match.pass_success_rate else 0
        }

        # 2. Player performances (only participated players from user's team, rating > 0)
        performances = PlayerPerformance.objects.filter(
            match=match,
            user_ouid=match.ouid,  # Only user's team
            rating__gt=0           # Exclude bench players (rating = 0)
        ).order_by('-rating')

        player_performances = {
            'top_performers': PlayerPerformanceSerializer(performances[:3], many=True).data,
            'all_players': PlayerPerformanceSerializer(performances, many=True).data
        }

        # 3. Timeline analysis
        shot_details = ShotDetail.objects.filter(match=match).values(
            'x', 'y', 'result', 'shot_type', 'goal_time'
        )
        shot_list = list(shot_details)
        timeline = TimelineAnalyzer.analyze_timeline(shot_list) if shot_list else {
            'xg_by_period': {'first_half': 0.0, 'second_half': 0.0},
            'key_moments': [],
            'timeline_data': []
        }

        # 4. Tactical insights
        from api.analyzers.tactical_analyzer import TacticalInsightsAnalyzer
        tactical_insights = TacticalInsightsAnalyzer.analyze_tactical_approach(
            match, shot_list, timeline
        )

        # Combine all analysis
        analysis_data = {
            'match_overview': match_overview,
            'player_performances': player_performances,
            'timeline': timeline,
            'tactical_insights': tactical_insights
        }

        # Cache for 24 hours
        cache.set(cache_key, analysis_data, 86400)

        return Response(analysis_data)


class UserStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """User Statistics API ViewSet"""
    queryset = UserStats.objects.all()
    serializer_class = UserStatsSerializer

    @action(detail=False, methods=['get'], url_path='user/(?P<ouid>[^/.]+)')
    def by_user(self, request, ouid=None):
        """Get user statistics"""
        user = get_object_or_404(User, ouid=ouid)
        period = request.query_params.get('period', 'all_time')

        stats = UserStats.objects.filter(ouid=user, period=period).first()

        if not stats:
            return Response(
                {'error': 'Statistics not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(stats)
        return Response(serializer.data)



@api_view(["GET"])
def get_tier_info(request):
    """
    GET /api/tier-info/

    Returns tier system information for power rankings
    """
    from api.analyzers.player_power_ranking import PlayerPowerRanking

    tier_info = PlayerPowerRanking.get_tier_information()

    return Response({
        "tiers": tier_info,
        "total_tiers": len(tier_info)
    })


@api_view(["GET"])
def search_players(request):
    """
    GET /api/search-players/?q=호날두

    Search for players by name

    Query params:
        q: Player name to search (required)
        limit: Maximum results (default 20, max 50)
    """
    from nexon_api.metadata import MetadataLoader

    query = request.query_params.get('q', '').strip()
    limit = min(int(request.query_params.get('limit', 20)), 50)

    if not query:
        return Response(
            {'error': '검색어를 입력해주세요.'},
            status=400
        )

    if len(query) < 2:
        return Response(
            {'error': '검색어는 최소 2글자 이상이어야 합니다.'},
            status=400
        )

    # Search players using MetadataLoader
    try:
        spid_data = MetadataLoader.load_metadata('spid')
        if not spid_data:
            return Response(
                {'error': '선수 데이터를 불러올 수 없습니다.'},
                status=500
            )

        # Filter by name (case-insensitive partial match)
        matching_players = []
        query_lower = query.lower()

        for player in spid_data:
            player_name = player.get('name', '')
            spid = player.get('id')

            if not spid or not player_name:
                continue

            if query_lower in player_name.lower():
                season_id = spid // 1000000
                season_info = MetadataLoader.get_season_info(season_id)

                matching_players.append({
                    'spid': spid,
                    'name': player_name,
                    'season_id': season_id,
                    'season_name': season_info['name'],
                    'season_img': season_info['img'],
                    'image_url': f"https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png"
                })

        # Sort by season_id (newer first) and limit
        matching_players.sort(key=lambda x: x['season_id'], reverse=True)
        matching_players = matching_players[:limit]

        return Response({
            'query': query,
            'count': len(matching_players),
            'players': matching_players
        })

    except Exception as e:
        return Response(
            {'error': f'검색 중 오류가 발생했습니다: {str(e)}'},
            status=500
        )



@api_view(['GET'])
def opponent_dna(request):
    """
    GET /api/opponent-dna/?opponent_nickname=xxx&my_nickname=yyy&matchtype=50

    A1. 상대 DNA 프로파일 + 나와의 승부 예측 (공식경기 전용)
    - opponent_nickname: 분석할 상대 닉네임 (필수)
    - my_nickname: 내 닉네임 (선택 — 입력 시 승부 예측 섹션 포함)
    - matchtype: 경기 유형 (기본값 50 = 공식경기)
    """
    opponent_nickname = request.query_params.get('opponent_nickname', '').strip()
    my_nickname       = request.query_params.get('my_nickname', '').strip()
    matchtype         = int(request.query_params.get('matchtype', 50))

    if not opponent_nickname:
        return Response(
            {'error': 'opponent_nickname 파라미터가 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 캐시 키: my_nickname 포함 여부에 따라 분리
    cache_key = f'opponent_dna:{opponent_nickname}:{matchtype}:{my_nickname}'
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    try:
        client = NexonAPIClient()
        from .analyzers.opponent_dna_analyzer import OpponentDNAAnalyzer

        # ── 상대 데이터 수집 ──────────────────────────────────────────────
        try:
            opponent_ouid = client.get_user_ouid(opponent_nickname)
        except Exception:
            return Response(
                {'error': f'닉네임 "{opponent_nickname}"을(를) 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not opponent_ouid:
            return Response(
                {'error': f'닉네임 "{opponent_nickname}"을(를) 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            opp_match_ids = client.get_user_matches(opponent_ouid, matchtype=matchtype, limit=30)
        except Exception as e:
            return Response(
                {'error': f'상대 경기 목록을 가져오는 중 오류: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not opp_match_ids:
            return Response({
                'opponent_nickname': opponent_nickname,
                'opponent_ouid': opponent_ouid,
                'matches_analyzed': 0,
                'indices': {},
                'radar_data': [],
                'play_style': {
                    'style': 'unknown', 'label': '분석 불가',
                    'description': '경기 데이터 없음', 'counter_strategy': '', 'emoji': '❓',
                },
                'scouting_report': ['경기 데이터가 없습니다.'],
                'battle_prediction': None,
            })

        # Fetch match details in parallel using gevent pool
        def _fetch_match_detail(mid):
            try:
                return client.get_match_detail(mid)
            except Exception:
                return None

        pool = GeventPool(size=10)
        opponent_matches_raw = [r for r in pool.map(_fetch_match_detail, opp_match_ids[:30]) if r]

        # 상대 DNA 분석
        opp_result = OpponentDNAAnalyzer.analyze_opponent_dna(
            opponent_matches_raw=opponent_matches_raw,
            opponent_ouid=opponent_ouid,
        )

        response_data = {
            'opponent_nickname': opponent_nickname,
            'opponent_ouid': opponent_ouid,
            'matchtype': matchtype,
            **opp_result,
            'battle_prediction': None,
        }

        # ── 승부 예측 (my_nickname 제공 시) ──────────────────────────────
        if my_nickname:
            try:
                from .analyzers.battle_predictor import BattlePredictor

                my_ouid = client.get_user_ouid(my_nickname)
                if my_ouid:
                    my_match_ids = client.get_user_matches(
                        my_ouid, matchtype=matchtype, limit=30
                    )
                    my_matches_raw = [r for r in pool.map(_fetch_match_detail, (my_match_ids or [])[:30]) if r]

                    # 내 DNA 지수도 계산
                    my_dna = OpponentDNAAnalyzer.analyze_opponent_dna(
                        opponent_matches_raw=my_matches_raw,
                        opponent_ouid=my_ouid,
                    )

                    battle_prediction = BattlePredictor.predict(
                        my_indices=my_dna['indices'],
                        opp_indices=opp_result['indices'],
                        my_matches_raw=my_matches_raw,
                        opp_matches_raw=opponent_matches_raw,
                        my_ouid=my_ouid,
                        opp_ouid=opponent_ouid,
                        my_nickname=my_nickname,
                        opp_nickname=opponent_nickname,
                    )
                    response_data['battle_prediction'] = battle_prediction
                    response_data['my_nickname'] = my_nickname
                    response_data['my_indices'] = my_dna['indices']
            except Exception:
                # 승부 예측 실패는 무시 — 기본 스카우팅 결과는 반환
                pass

        cache.set(cache_key, response_data, 21600)  # 6 hours
        return Response(response_data)

    except NexonAPIException as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def send_support_message(request):
    """
    POST /api/support/
    
    Send support message (Buy Me a Coffee) to developer
    
    Request body:
    {
        "name": "User Name",
        "email": "user@example.com" (optional),
        "message": "Support message",
        "amount": 5000 (optional)
    }
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    name = request.data.get('name', '').strip()
    email = request.data.get('email', '').strip()
    message = request.data.get('message', '').strip()
    amount = request.data.get('amount')
    
    if not name or not message:
        return Response(
            {'error': 'Name and message are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Compose email
    subject = f'☕ FC Strategy Support Message from {name}'
    
    email_body = f"""
=== FC Strategy Support Message ===

From: {name}
Email: {email if email else 'Not provided'}
Amount: {f"{amount}원" if amount else "Not specified"}

Message:
{message}

---
Sent via FC Strategy Buy Me a Coffee feature
    """.strip()
    
    try:
        # Send email to developer
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEVELOPER_EMAIL],
            fail_silently=False,
        )
        
        return Response({
            'success': True,
            'message': 'Support message sent successfully'
        })
    except Exception:
        return Response(
            {'error': 'Failed to send message. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
def visitor_count(request):
    """
    GET  /api/visitor-count/ → total_visits만 반환
    POST /api/visitor-count/ → SiteVisit 1건 생성 + total_visits 반환
    """
    if request.method == 'POST':
        SiteVisit.objects.create()
        try:
            cache.incr('visitor_total')
        except ValueError:
            cache.set('visitor_total', SiteVisit.objects.count(), 3600)
        total_visits = cache.get('visitor_total')
    else:
        total_visits = cache.get('visitor_total')
        if total_visits is None:
            total_visits = SiteVisit.objects.count()
            cache.set('visitor_total', total_visits, 3600)

    return Response({'total_visits': total_visits})
