"""
Django Signals for API App

Automatically trigger data processing when models are saved.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match
from .utils.shot_extractor import ShotDataExtractor
from .utils.player_extractor import PlayerPerformanceExtractor
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Match)
def extract_shot_details_on_match_save(sender, instance, created, **kwargs):
    """
    Automatically extract shot details when Match is created.

    This signal fires after a Match object is saved to the database.
    It extracts shot coordinates from the raw_data JSONField and
    populates the ShotDetail table for visualization.

    Args:
        sender: The Match model class
        instance: The actual Match instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created and instance.raw_data:
        try:
            logger.info(f"Auto-extracting shots for new match {instance.match_id}")
            shot_count = ShotDataExtractor.extract_and_save(
                instance,
                instance.ouid.ouid
            )
            logger.info(f"Extracted {shot_count} shots for match {instance.match_id}")
        except Exception as e:
            logger.error(
                f"Failed to extract shots for match {instance.match_id}: {str(e)}",
                exc_info=True
            )


@receiver(post_save, sender=Match)
def extract_player_performances_on_match_save(sender, instance, created, **kwargs):
    """
    Automatically extract player performances when Match is created.

    This signal fires after a Match object is saved to the database.
    It extracts player performance data from the raw_data JSONField and
    populates the PlayerPerformance table for analysis.

    Args:
        sender: The Match model class
        instance: The actual Match instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created and instance.raw_data:
        try:
            logger.info(f"Auto-extracting player performances for new match {instance.match_id}")
            player_count = PlayerPerformanceExtractor.extract_and_save(instance)
            logger.info(f"Extracted {player_count} player performances for match {instance.match_id}")
        except Exception as e:
            logger.error(
                f"Failed to extract player performances for match {instance.match_id}: {str(e)}",
                exc_info=True
            )
