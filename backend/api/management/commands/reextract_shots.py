"""
Management command to re-extract shot details from raw_data stored in matches.
Fixes goalTime decoding: Nexon API uses period-based bit encoding for goalTime.
"""
from django.core.management.base import BaseCommand
from api.models import Match, ShotDetail
from api.utils.shot_extractor import ShotDataExtractor


class Command(BaseCommand):
    help = 'Re-extract shot details from match raw_data to fix goalTime decoding'

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
        total_shots = 0

        for i, match in enumerate(qs.select_related('ouid'), 1):
            try:
                count = ShotDataExtractor.extract_and_save(match, match.ouid.ouid)
                total_shots += count
                success += 1
                if i % 20 == 0 or i == total:
                    self.stdout.write(
                        f"  [{i}/{total}] Processed {success} matches, "
                        f"{failed} failed, {total_shots} shots total"
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
                f"\nDone: {success} succeeded, {failed} failed, {total_shots} shots extracted"
            )
        )
