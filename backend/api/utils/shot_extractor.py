"""
Shot Data Extractor

Extracts shot details from Nexon API raw_data stored in Match.raw_data JSONField
and populates the ShotDetail table for heatmap visualization.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ShotDataExtractor:
    """Extract shot details from Nexon API raw_data"""

    # Mapping Nexon result codes to our model choices
    RESULT_MAP = {
        1: 'goal',
        2: 'on_target',
        3: 'off_target',
        6: 'blocked',
    }

    @classmethod
    def extract_and_save(cls, match, user_ouid: str) -> int:
        """
        Extract shot details from match.raw_data for specific user.
        Returns count of shots created.

        Args:
            match: Match instance with raw_data
            user_ouid: OUID of the user whose shots to extract

        Returns:
            int: Number of shot details created

        Nexon API raw_data structure:
        {
            "matchInfo": [
                {
                    "ouid": "...",
                    "shootDetail": [
                        {
                            "goalTime": 0,
                            "x": 0.8512,  # 0.0 to 1.0
                            "y": 0.4523,  # 0.0 to 1.0
                            "type": 3,
                            "result": 3,  # 1=goal, 2=on_target, 3=off_target, 6=blocked
                            "assistX": 0.7123,
                            "assistY": 0.5234,
                            "hitPost": false,
                            "inPenalty": true
                        }
                    ],
                    "shoot": {
                        "shootTotal": 10,
                        "effectiveShootTotal": 5,
                        "shootOutScore": 0,
                        "goalTotal": 2,
                        "goalTotalDisplay": 2,
                        "ownGoal": 0,
                        "shootHeading": 2,
                        "goalHeading": 0,
                        "shootFreekick": 1,
                        "goalFreekick": 0,
                        "shootInPenalty": 8,
                        "goalInPenalty": 2,
                        "shootOutPenalty": 2,
                        "goalOutPenalty": 0,
                        "shootPenalty": 0,
                        "goalPenalty": 0
                    }
                }
            ]
        }
        """
        # Import here to avoid circular imports
        from api.models import ShotDetail

        if not match.raw_data:
            logger.warning(f"Match {match.match_id} has no raw_data")
            return 0

        try:
            match_info_list = match.raw_data.get('matchInfo', [])

            # Find the user's match info
            user_match_info = None
            for info in match_info_list:
                if info.get('ouid') == user_ouid:
                    user_match_info = info
                    break

            if not user_match_info:
                logger.warning(
                    f"User {user_ouid} not found in match {match.match_id} matchInfo"
                )
                return 0

            shoot_details = user_match_info.get('shootDetail', [])

            if not shoot_details:
                logger.info(f"No shots found for user {user_ouid} in match {match.match_id}")
                return 0

            # Get official goal/shot counts from shoot summary.
            # shootDetail.result field is unreliable, so we prefer official counts
            # when a shoot summary is present.  If no summary exists (e.g. in tests
            # or older API responses), fall back to the raw RESULT_MAP codes.
            shoot_summary = user_match_info.get('shoot', {})
            official_goal_count = shoot_summary.get('goalTotalDisplay', 0)
            official_effective_count = shoot_summary.get('effectiveShootTotal', 0)
            use_official_counts = bool(shoot_summary) and (
                official_goal_count > 0 or official_effective_count > 0
            )

            # Sort shootDetail by goalTime to process in chronological order
            # This ensures we keep the earliest goals when adjusting result values
            sorted_shoot_details = sorted(shoot_details, key=lambda s: s.get('goalTime', 0))

            # Delete existing shot details for this match (in case of re-extraction)
            ShotDetail.objects.filter(match=match).delete()

            # Track how many goals and effective shots we've assigned
            goals_assigned = 0
            effective_assigned = 0

            # First pass: collect shots by their original result
            shots_by_result = {'goal': [], 'on_target': [], 'off_target': [], 'blocked': []}

            for shot in sorted_shoot_details:
                result_code = shot.get('result')
                raw_result = cls.RESULT_MAP.get(result_code, 'off_target')
                shots_by_result[raw_result].append(shot)

            # Second pass: assign results based on official counts
            # Priority: goal > on_target > off_target
            shot_objects = []

            for raw_result in ['goal', 'on_target', 'off_target', 'blocked']:
                for shot in shots_by_result[raw_result]:
                    # Get coordinates
                    x = shot.get('x')
                    y = shot.get('y')

                    # Skip invalid coordinates
                    if x is None or y is None:
                        logger.warning(f"Shot missing coordinates in match {match.match_id}")
                        continue

                    # Assign result.
                    # When an official shoot summary is available, re-assign results
                    # in priority order so the counts match the official figures.
                    # When no summary is present, trust the raw RESULT_MAP code.
                    if not use_official_counts:
                        result = raw_result
                    elif goals_assigned < official_goal_count:
                        result = 'goal'
                        goals_assigned += 1
                        effective_assigned += 1
                    elif effective_assigned < official_effective_count:
                        result = 'on_target'
                        effective_assigned += 1
                    elif raw_result == 'blocked':
                        result = 'blocked'  # Keep blocked as-is
                    else:
                        result = 'off_target'

                    # Get shooter information
                    shooter_spid = shot.get('spId')

                    # Get shot type and characteristics
                    shot_type = shot.get('type', 0)
                    hit_post = shot.get('hitPost', False)
                    in_penalty = shot.get('inPenalty', False)

                    # Get assist information (optional).
                    # The API may return flat keys (assistX, assistY) or a nested
                    # 'assist' dict ({x: ..., y: ...}) depending on version.
                    assist_dict = shot.get('assist') or {}
                    assist_x = shot.get('assistX') or (assist_dict.get('x') if assist_dict else None)
                    assist_y = shot.get('assistY') or (assist_dict.get('y') if assist_dict else None)
                    assist_spid = shot.get('assistSpId')  # -1 means no assist

                    # Normalize assist_spid: -1 or None = no assist
                    if assist_spid == -1:
                        assist_spid = None

                    # Nexon FC Online goalTime uses a period-based bit encoding:
                    #   Period 0 (bits[25:24] = 0):  First half     → actual = offset          (0–45 min)
                    #   Period 1 (bits[25:24] = 1):  Second half    → actual = 2700 + offset   (45–90 min)
                    #   Period 2 (bits[25:24] = 2):  ET first half  → actual = 5400 + offset   (90–105 min)
                    #   Period 3 (bits[25:24] = 3):  ET second half → actual = 8100 + offset   (105–120 min)
                    # PERIOD_BASE = 2^24 = 16777216; period = goalTime >> 24; offset = goalTime & 0xFFFFFF
                    raw_goal_time = shot.get('goalTime') or 0
                    if raw_goal_time > 0:
                        period = raw_goal_time >> 24       # Which game period (0-3)
                        offset = raw_goal_time & 0xFFFFFF  # Seconds within that period
                        goal_time = period * 2700 + offset
                        if goal_time > 10800:              # Sanity cap at 180 min
                            goal_time = 0
                    else:
                        goal_time = 0

                    # Create ShotDetail object
                    shot_obj = ShotDetail(
                        match=match,
                        shooter_spid=shooter_spid,
                        assist_spid=assist_spid,
                        x=Decimal(str(x)),
                        y=Decimal(str(y)),
                        result=result,
                        shot_type=shot_type,
                        hit_post=hit_post,
                        in_penalty=in_penalty,
                        goal_time=goal_time,
                        assist_x=Decimal(str(assist_x)) if assist_x is not None else None,
                        assist_y=Decimal(str(assist_y)) if assist_y is not None else None,
                    )
                    shot_objects.append(shot_obj)

            # Bulk create for efficiency
            created = ShotDetail.objects.bulk_create(shot_objects)
            logger.info(
                f"Created {len(created)} shot details for match {match.match_id}, user {user_ouid}"
            )

            return len(created)

        except Exception as e:
            logger.error(
                f"Error extracting shots from match {match.match_id}: {str(e)}",
                exc_info=True
            )
            return 0

    @classmethod
    def backfill_matches(cls, user_ouid: Optional[str] = None) -> Dict[str, int]:
        """
        Backfill shot details for existing matches.

        Args:
            user_ouid: If provided, only backfill for this user. Otherwise all users.

        Returns:
            Dict with statistics: {'total_matches': int, 'total_shots': int}
        """
        from api.models import Match

        matches_query = Match.objects.filter(raw_data__isnull=False)

        if user_ouid:
            matches_query = matches_query.filter(ouid__ouid=user_ouid)

        total_matches = 0
        total_shots = 0

        for match in matches_query:
            shots_created = cls.extract_and_save(match, match.ouid.ouid)
            if shots_created > 0:
                total_matches += 1
                total_shots += shots_created

        logger.info(
            f"Backfill complete: {total_matches} matches, {total_shots} shots"
        )

        return {
            'total_matches': total_matches,
            'total_shots': total_shots
        }
