"""
Management command to build player name cache from existing match raw_data
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from api.models import Match, PlayerPerformance
import json


class Command(BaseCommand):
    help = 'Build player name cache from existing match data'

    def handle(self, *args, **options):
        self.stdout.write('Building player name cache from match data...')

        # Dictionary to store spid -> name mapping
        player_mapping = {}

        # Get all matches with raw_data
        matches = Match.objects.filter(raw_data__isnull=False)
        total_matches = matches.count()

        self.stdout.write(f'Processing {total_matches} matches...')

        for idx, match in enumerate(matches, 1):
            if idx % 10 == 0:
                self.stdout.write(f'Processed {idx}/{total_matches}...', ending='\r')

            match_info = match.raw_data.get('matchInfo', [])

            for info in match_info:
                players = info.get('player', [])

                for player in players:
                    spid = player.get('spId')
                    if spid and spid not in player_mapping:
                        # Try to extract player name from spid
                        # spid format: typically base_id + season_id
                        # We'll store the spid for now
                        player_mapping[spid] = f"선수 {spid}"

        self.stdout.write(f'\nFound {len(player_mapping)} unique players')

        # Save to cache
        cache_key = 'player_spid_mapping'
        cache.set(cache_key, player_mapping, None)  # No expiration

        self.stdout.write(self.style.SUCCESS(
            f'✓ Player cache built with {len(player_mapping)} entries'
        ))

        # Now update PlayerPerformance records
        self.stdout.write('\nUpdating PlayerPerformance records...')

        updated = 0
        for player_perf in PlayerPerformance.objects.filter(player_name__startswith='Unknown Player').iterator():
            if player_perf.spid in player_mapping:
                player_perf.player_name = player_mapping[player_perf.spid]
                player_perf.save(update_fields=['player_name'])
                updated += 1

                if updated % 100 == 0:
                    self.stdout.write(f'Updated {updated}...', ending='\r')

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Updated {updated} player names'
        ))
