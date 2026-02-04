import requests
import json
import os
from pathlib import Path
from django.core.cache import cache
from typing import Dict, Optional


class MetadataLoader:
    """Loader for FC Online static metadata"""

    METADATA_BASE_URL = "https://static.api.nexon.co.kr/fifaonline4/latest/"

    # Local static_data directory path
    STATIC_DATA_DIR = Path(__file__).parent.parent / 'static_data'

    METADATA_FILES = {
        'spid': 'spid.json',
        'seasonid': 'seasonid.json',
        'matchtype': 'matchtype.json',
        'division': 'division.json',
        'position': 'position.json',
    }

    @classmethod
    def load_metadata(cls, metadata_type: str) -> Optional[Dict]:
        """Load metadata from local file, cache, or API (in that order)"""
        if metadata_type not in cls.METADATA_FILES:
            raise ValueError(f"Invalid metadata type: {metadata_type}")

        cache_key = f"metadata:{metadata_type}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        # Try to load from local file first
        filename = cls.METADATA_FILES[metadata_type]
        local_file_path = cls.STATIC_DATA_DIR / filename

        if local_file_path.exists():
            try:
                with open(local_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Cache for 24 hours
                cache.set(cache_key, data, 86400)
                print(f"Loaded {metadata_type} metadata from local file: {local_file_path}")

                return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Failed to load {metadata_type} from local file: {e}")

        # Fallback to API if local file not available
        url = f"{cls.METADATA_BASE_URL}{filename}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Cache for 24 hours (metadata rarely changes)
            cache.set(cache_key, data, 86400)

            return data
        except requests.exceptions.RequestException as e:
            print(f"Failed to load {metadata_type} metadata from API: {e}")
            return None

    @classmethod
    def get_player_name(cls, spid: int) -> str:
        """Get player name from SPID"""
        spid_data = cls.load_metadata('spid')
        if not spid_data:
            return f"Unknown Player ({spid})"

        for player in spid_data:
            if player.get('id') == spid:
                return player.get('name', f"Unknown Player ({spid})")

        return f"Unknown Player ({spid})"

    @classmethod
    def get_season_name(cls, season_id: int) -> str:
        """Get season name from season ID"""
        season_data = cls.load_metadata('seasonid')
        if not season_data:
            return f"Unknown Season ({season_id})"

        for season in season_data:
            if season.get('seasonId') == season_id:
                return season.get('className', f"Unknown Season ({season_id})")

        return f"Unknown Season ({season_id})"

    @classmethod
    def get_season_img(cls, season_id: int) -> str:
        """Get season badge image URL from season ID"""
        season_data = cls.load_metadata('seasonid')
        if not season_data:
            return ''

        for season in season_data:
            if season.get('seasonId') == season_id:
                return season.get('seasonImg', '')

        return ''

    @classmethod
    def get_season_info(cls, season_id: int) -> dict:
        """Get full season info (name + image URL) from season ID"""
        season_data = cls.load_metadata('seasonid')
        if not season_data:
            return {'name': f'Unknown Season ({season_id})', 'img': ''}

        for season in season_data:
            if season.get('seasonId') == season_id:
                class_name = season.get('className', '')
                short_name = class_name.split('(')[0].strip() if '(' in class_name else class_name
                return {
                    'name': short_name,
                    'img': season.get('seasonImg', '')
                }

        return {'name': f'Unknown Season ({season_id})', 'img': ''}

    @classmethod
    def get_matchtype_name(cls, matchtype: int) -> str:
        """Get match type name"""
        matchtype_data = cls.load_metadata('matchtype')
        if not matchtype_data:
            return f"Unknown Type ({matchtype})"

        for match_type in matchtype_data:
            if match_type.get('matchtype') == matchtype:
                return match_type.get('desc', f"Unknown Type ({matchtype})")

        return f"Unknown Type ({matchtype})"

    @classmethod
    def get_division_name(cls, division: int) -> str:
        """Get division name"""
        division_data = cls.load_metadata('division')
        if not division_data:
            return f"Unknown Division ({division})"

        for div in division_data:
            if div.get('divisionId') == division:
                return div.get('divisionName', f"Unknown Division ({division})")

        return f"Unknown Division ({division})"
