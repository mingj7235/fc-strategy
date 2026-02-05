"""
Management command to pre-load Nexon metadata into cache
"""
from django.core.management.base import BaseCommand
from nexon_api.metadata import MetadataLoader


class Command(BaseCommand):
    help = 'Pre-load Nexon FC Online metadata into cache'

    def handle(self, *args, **options):
        self.stdout.write('Loading Nexon metadata...')

        # Load all metadata types
        metadata_types = ['spid', 'seasonid', 'matchtype', 'division', 'position']

        for metadata_type in metadata_types:
            self.stdout.write(f'Loading {metadata_type}...', ending='')
            data = MetadataLoader.load_metadata(metadata_type)

            if data:
                self.stdout.write(self.style.SUCCESS(f' ✓ ({len(data)} items)'))
            else:
                self.stdout.write(self.style.ERROR(' ✗ Failed'))

        self.stdout.write(self.style.SUCCESS('\nMetadata loading complete!'))
