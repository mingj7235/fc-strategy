"""
PlayerPerformance Extractor
Extracts detailed player statistics from Nexon API raw_data
"""
from typing import Dict, List, Any
from api.models import Match, PlayerPerformance
from nexon_api.metadata import MetadataLoader


class PlayerPerformanceExtractor:
    """
    Nexon API의 raw_data에서 선수별 상세 통계를 추출하여 PlayerPerformance 모델에 저장
    """

    @classmethod
    def extract_and_save(cls, match: Match) -> int:
        """
        매치에서 선수 성능 데이터 추출 및 저장

        Args:
            match: Match 객체

        Returns:
            생성된 PlayerPerformance 객체 수
        """
        if not match.raw_data:
            print(f"[PlayerExtractor] No raw_data for match {match.match_id}")
            return 0

        match_info_list = match.raw_data.get('matchInfo', [])
        if not match_info_list:
            print(f"[PlayerExtractor] No matchInfo in raw_data for match {match.match_id}")
            return 0

        created_count = 0

        # matchInfo 배열 순회 (user와 opponent)
        for match_info in match_info_list:
            players = match_info.get('player', [])

            if not players:
                continue

            # Get the OUID for this team
            team_ouid_str = match_info.get('ouid')

            # Find the User object for this OUID
            from api.models import User
            try:
                team_user = User.objects.get(ouid=team_ouid_str)
            except User.DoesNotExist:
                print(f"[PlayerExtractor] User not found for OUID {team_ouid_str}, skipping")
                continue

            # 각 선수 데이터 추출 (실제 경기 참여 선수만)
            # rating > 0인 선수들만 카운트하여 position 부여
            participated_index = 0
            for player_data in players:
                try:
                    # rating 확인 (실제 경기 참여 여부)
                    status = player_data.get('status', {})
                    rating = status.get('spRating', 0)

                    # rating이 0이면 경기에 참여하지 않은 선수 (스킵)
                    if rating == 0:
                        continue

                    # 실제 참여한 선수만 저장 (position은 참여 순서)
                    performance = cls._extract_player_performance(match, player_data, participated_index)
                    if performance:
                        performance.user_ouid = team_user  # Set which user this player belongs to
                        performance.save()
                        created_count += 1
                        participated_index += 1
                except Exception as e:
                    print(f"[PlayerExtractor] Error extracting player {player_data.get('spId')}: {e}")
                    continue

        print(f"[PlayerExtractor] Created {created_count} PlayerPerformance records for match {match.match_id}")
        return created_count

    @classmethod
    def _extract_player_performance(cls, match: Match, player_data: Dict[str, Any], lineup_index: int = 0) -> PlayerPerformance:
        """
        개별 선수 데이터를 PlayerPerformance 객체로 변환

        Args:
            match: Match 객체
            player_data: Nexon API의 player 데이터
            lineup_index: 라인업에서의 순서 (0-10: 주전, 11-17: 후보)

        Returns:
            PlayerPerformance 객체
        """
        spid = player_data.get('spId')
        lineup_position = lineup_index  # 배열 인덱스 (0-10: 주전, 11-17: 후보)
        sp_position = player_data.get('spPosition', 0)  # 실제 포지션 타입 (0=GK, 1-8=DF, 9-19=MF, 20-27=FW, 28=SUB)
        grade = player_data.get('spGrade', 0)

        # Get player name from metadata
        player_name = MetadataLoader.get_player_name(spid)

        # If name is unknown, use sp_position + grade
        if player_name and player_name.startswith('Unknown Player'):
            position_names = {
                0: 'GK', 1: 'SW', 2: 'RWB', 3: 'RB', 4: 'RCB',
                5: 'CB', 6: 'LCB', 7: 'LB', 8: 'LWB', 9: 'RDM',
                10: 'CDM', 11: 'LDM', 12: 'RM', 13: 'RCM', 14: 'CM',
                15: 'LCM', 16: 'LM', 17: 'RAM', 18: 'CAM', 19: 'LAM',
                20: 'RF', 21: 'CF', 22: 'LF', 23: 'RW', 24: 'RS',
                25: 'ST', 26: 'LS', 27: 'LW', 28: 'SUB'
            }
            position_name = position_names.get(sp_position, f'P{sp_position}')
            player_name = f"{position_name} {grade}등급"

        # Get season info
        season_id = spid // 1000000 if spid else None
        season_name = MetadataLoader.get_season_name(season_id) if season_id else None

        # Remove parentheses content: "BDO (Ballon d'Or)" -> "BDO"
        if season_name and '(' in season_name:
            season_name = season_name.split('(')[0].strip()

        # Extract status data.
        # The Nexon API returns two different layouts depending on endpoint version:
        #   Flat layout:   status = {'shoot': 5, 'effectiveShoot': 4, 'passTry': 50, ...}
        #   Nested layout: status = {'shoot': {'shootTotal': 5, ...}, 'pass': {'passTry': 50, ...}, ...}
        # We handle both by checking whether sub-fields are dicts.
        status = player_data.get('status', {})

        # Rating & cards (always flat)
        rating = status.get('spRating', 6.5)
        assists = status.get('assist', 0)
        interceptions = status.get('intercept', 0)
        yellow_cards = status.get('yellowCards', 0)
        red_cards = status.get('redCards', 0)
        aerial_success = status.get('aerialSuccess', 0)
        goals = status.get('goal', 0)

        # Shooting data — flat or nested
        shoot_raw = status.get('shoot', 0)
        if isinstance(shoot_raw, dict):
            shots = shoot_raw.get('shootTotal', 0)
            shots_on_target = shoot_raw.get('effectiveShootTotal', 0)
        else:
            shots = shoot_raw or 0
            shots_on_target = status.get('effectiveShoot', 0)
        shots_woodwork = 0
        shots_off_target = max(0, shots - shots_on_target - goals)

        # Passing data — flat or nested
        pass_raw = status.get('pass', {})
        if isinstance(pass_raw, dict):
            pass_attempts = pass_raw.get('passTry', 0)
            pass_success = pass_raw.get('passSuccess', 0)
            short_pass_attempts = pass_raw.get('shortPassTry', 0)
            short_pass_success = pass_raw.get('shortPassSuccess', 0)
            long_pass_attempts = pass_raw.get('longPassTry', 0)
            long_pass_success = pass_raw.get('longPassSuccess', 0)
            through_pass_attempts = pass_raw.get('throughPassTry', 0)
            through_pass_success = pass_raw.get('throughPassSuccess', 0)
        else:
            pass_attempts = status.get('passTry', 0)
            pass_success = status.get('passSuccess', 0)
            short_pass_attempts = 0
            short_pass_success = 0
            long_pass_attempts = 0
            long_pass_success = 0
            through_pass_attempts = 0
            through_pass_success = 0

        # Dribbling data — flat or nested
        dribble_raw = status.get('dribble', {})
        if isinstance(dribble_raw, dict):
            dribble_attempts = dribble_raw.get('dribbleTry', 0)
            dribble_success = dribble_raw.get('dribbleSuccess', 0)
        else:
            dribble_attempts = status.get('dribbleTry', 0)
            dribble_success = status.get('dribbleSuccess', 0)

        # Defensive data — flat or nested
        defence_raw = status.get('defence', {})
        if isinstance(defence_raw, dict):
            tackle_attempts = defence_raw.get('tackleTry', 0)
            tackle_success = defence_raw.get('tackleSuccess', 0)
            block_attempts = defence_raw.get('blockTry', 0)
            blocks = defence_raw.get('block', 0)
        else:
            tackle_attempts = status.get('tackleTry', 0)
            tackle_success = status.get('tackle', 0)
            block_attempts = status.get('blockTry', 0)
            blocks = status.get('block', 0)

        # Create PlayerPerformance object
        performance = PlayerPerformance(
            match=match,
            spid=spid,
            player_name=player_name or f"Unknown_{spid}",
            season_id=season_id,
            season_name=season_name,
            position=sp_position,  # FIXED: Use actual position type, not lineup index
            grade=grade,
            rating=rating,

            # Goals and assists
            goals=goals,
            assists=assists,  # Now extracted from API

            # Shooting
            shots=shots,
            shots_on_target=shots_on_target,
            shots_off_target=shots_off_target,
            shots_woodwork=shots_woodwork,

            # Passing
            pass_attempts=pass_attempts,
            pass_success=pass_success,
            short_pass_attempts=short_pass_attempts,
            short_pass_success=short_pass_success,
            long_pass_attempts=long_pass_attempts,
            long_pass_success=long_pass_success,
            through_pass_attempts=through_pass_attempts,
            through_pass_success=through_pass_success,

            # Dribbling
            dribble_attempts=dribble_attempts,
            dribble_success=dribble_success,

            # Defensive
            tackle_attempts=tackle_attempts,
            tackle_success=tackle_success,
            block_attempts=block_attempts,
            blocks=blocks,
            interceptions=interceptions,

            # Aerial
            aerial_success=aerial_success,

            # Cards
            yellow_cards=yellow_cards,
            red_cards=red_cards,
        )

        # Goalkeeper specific stats (if sp_position is GK)
        if sp_position == 0:  # GK position
            performance = cls._add_goalkeeper_stats(performance, match, player_data)

        return performance

    @classmethod
    def _add_goalkeeper_stats(cls, performance: PlayerPerformance, match: Match, player_data: Dict) -> PlayerPerformance:
        """
        골키퍼 전용 통계 추가

        Args:
            performance: PlayerPerformance 객체
            match: Match 객체
            player_data: player 데이터

        Returns:
            업데이트된 PlayerPerformance 객체
        """
        # Get match info to determine if this is user's GK or opponent's GK
        match_info_list = match.raw_data.get('matchInfo', [])

        # Find which side this player is on
        is_user_player = False
        opponent_match_info = None

        for info in match_info_list:
            players = info.get('player', [])
            player_ids = [p.get('spId') for p in players]

            if performance.spid in player_ids:
                # This is the player's team
                ouid = info.get('ouid')
                if ouid == match.ouid.ouid:
                    is_user_player = True
            else:
                # This is opponent's team
                opponent_match_info = info

        if opponent_match_info and is_user_player:
            # For user's GK, opponent shots = saves opportunity
            opponent_shoot = opponent_match_info.get('shoot', {})
            opponent_shots = opponent_shoot.get('shootTotal', 0)
            opponent_goals = opponent_shoot.get('goalTotalDisplay', 0)

            performance.opponent_shots = opponent_shots
            performance.saves = max(0, opponent_shots - opponent_goals)  # Approximate saves
            performance.goals_conceded = match.goals_against
        elif not is_user_player and opponent_match_info:
            # For opponent's GK
            user_match_info = None
            for info in match_info_list:
                if info.get('ouid') == match.ouid.ouid:
                    user_match_info = info
                    break

            if user_match_info:
                user_shoot = user_match_info.get('shoot', {})
                user_shots = user_shoot.get('shootTotal', 0)
                user_goals = user_shoot.get('goalTotalDisplay', 0)

                performance.opponent_shots = user_shots
                performance.saves = max(0, user_shots - user_goals)
                performance.goals_conceded = match.goals_for

        return performance

    @classmethod
    def backfill_existing_matches(cls, limit: int = None) -> Dict[str, int]:
        """
        기존 매치들에 대해 PlayerPerformance 데이터 생성

        Args:
            limit: 처리할 최대 매치 수 (None = 전체)

        Returns:
            {'processed': 처리된 매치 수, 'created': 생성된 performance 수}
        """
        # Get matches that don't have player performances yet
        matches_without_performances = Match.objects.filter(
            player_performances__isnull=True
        ).order_by('-match_date')

        if limit:
            matches_without_performances = matches_without_performances[:limit]

        total_created = 0
        processed = 0

        for match in matches_without_performances:
            count = cls.extract_and_save(match)
            total_created += count
            processed += 1

        print(f"[PlayerExtractor] Backfilled {total_created} PlayerPerformance records for {processed} matches")

        return {
            'processed': processed,
            'created': total_created
        }
