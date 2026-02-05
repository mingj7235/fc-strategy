"""
Management command to re-extract PlayerPerformance data from raw_data stored in matches.
Fixes position decoding: old code stored lineup_index (0-10) instead of spPosition (0-27).
"""
from django.core.management.base import BaseCommand
from api.models import Match, PlayerPerformance
from api.utils.player_extractor import PlayerPerformanceExtractor


class Command(BaseCommand):
    help = 'Re-extract PlayerPerformance from match raw_data to fix position data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nickname',
            type=str,
            help='Only re-extract for a specific user nickname',
        )
        parser.add_argument(
            '--match-type',
            type=int,
            default=None,
            help='Only re-extract for a specific match type (e.g. 50)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        qs = Match.objects.filter(raw_data__isnull=False)

        if options['nickname']:
            qs = qs.filter(ouid__nickname=options['nickname'])
            self.stdout.write(f"Filtering to user: {options['nickname']}")

        if options['match_type'] is not None:
            qs = qs.filter(match_type=options['match_type'])
            self.stdout.write(f"Filtering to match_type: {options['match_type']}")

        total = qs.count()
        self.stdout.write(f"Found {total} matches with raw_data to re-process")

        if options['dry_run']:
            self.stdout.write("DRY RUN - no changes made")
            return

        success = 0
        failed = 0
        total_performances = 0

        for i, match in enumerate(qs.select_related('ouid'), 1):
            try:
                # Delete existing PlayerPerformance records for this match
                deleted_count, _ = PlayerPerformance.objects.filter(match=match).delete()

                # Re-extract from raw_data
                count = PlayerPerformanceExtractor.extract_and_save(match)
                total_performances += count
                success += 1
                if i % 20 == 0 or i == total:
                    self.stdout.write(
                        f"  [{i}/{total}] Processed {success} matches, "
                        f"{failed} failed, {total_performances} performances total"
                    )
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"  [{i}/{total}] FAILED match {match.match_id}: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone: {success} succeeded, {failed} failed, "
                f"{total_performances} PlayerPerformance records created"
            )
        )
