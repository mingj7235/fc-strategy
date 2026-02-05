"""
Management command to update player names in PlayerPerformance records
"""
from django.core.management.base import BaseCommand
from api.models import PlayerPerformance
from nexon_api.metadata import MetadataLoader


class Command(BaseCommand):
    help = 'Update player names in PlayerPerformance records using Nexon metadata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of records to update (default: all)',
        )

    def handle(self, *args, **options):
        limit = options.get('limit')

        # First, ensure metadata is loaded
        self.stdout.write('Loading metadata...')
        MetadataLoader.load_metadata('spid')

        # Get PlayerPerformance records with Unknown Player names
        query = PlayerPerformance.objects.filter(
            player_name__startswith='Unknown Player'
        )

        if limit:
            query = query[:limit]

        total = query.count()
        self.stdout.write(f'Found {total} players to update')

        updated = 0
        failed = 0

        for player_perf in query.iterator():
            # Get player name from metadata
            player_name = MetadataLoader.get_player_name(player_perf.spid)

            # Only update if we got a real name (not "Unknown Player")
            if not player_name.startswith('Unknown Player'):
                player_perf.player_name = player_name
                player_perf.save(update_fields=['player_name'])
                updated += 1

                if updated % 100 == 0:
                    self.stdout.write(f'Updated {updated}/{total}...', ending='\r')
            else:
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Updated {updated} player names'
        ))

        if failed > 0:
            self.stdout.write(self.style.WARNING(
                f'⚠ {failed} players still unknown (spid not in metadata)'
            ))
