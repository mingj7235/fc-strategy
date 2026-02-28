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

    # In-memory lookup dicts (built once per process)
    _spid_lookup: Optional[Dict[int, str]] = None
    _season_lookup: Optional[Dict[int, dict]] = None
    _matchtype_lookup: Optional[Dict[int, str]] = None
    _division_lookup: Optional[Dict[int, str]] = None

    @classmethod
    def load_metadata(cls, metadata_type: str) -> Optional[Dict]:
        """Load metadata from cache, local file, or API (in that order)"""
        if metadata_type not in cls.METADATA_FILES:
            raise ValueError(f"Invalid metadata type: {metadata_type}")

        cache_key = f"metadata:{metadata_type}"

        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
        except Exception:
            pass

        # Try to load from local file first
        filename = cls.METADATA_FILES[metadata_type]
        local_file_path = cls.STATIC_DATA_DIR / filename

        if local_file_path.exists():
            try:
                with open(local_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                try:
                    cache.set(cache_key, data, 86400)
                except Exception:
                    pass

                return data
            except (json.JSONDecodeError, IOError):
                pass

        # Fallback to API if local file not available
        url = f"{cls.METADATA_BASE_URL}{filename}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            try:
                cache.set(cache_key, data, 86400)
            except Exception:
                pass

            return data
        except requests.exceptions.RequestException:
            return None

    @classmethod
    def _get_spid_lookup(cls) -> Dict[int, str]:
        """Build and cache {spid: name} lookup dict"""
        if cls._spid_lookup is None:
            spid_data = cls.load_metadata('spid')
            cls._spid_lookup = {
                p['id']: p.get('name', '')
                for p in (spid_data or []) if 'id' in p
            }
        return cls._spid_lookup

    @classmethod
    def _get_season_lookup(cls) -> Dict[int, dict]:
        """Build and cache {seasonId: {className, seasonImg}} lookup dict"""
        if cls._season_lookup is None:
            season_data = cls.load_metadata('seasonid')
            cls._season_lookup = {
                s['seasonId']: s
                for s in (season_data or []) if 'seasonId' in s
            }
        return cls._season_lookup

    @classmethod
    def _get_matchtype_lookup(cls) -> Dict[int, str]:
        """Build and cache {matchtype: desc} lookup dict"""
        if cls._matchtype_lookup is None:
            matchtype_data = cls.load_metadata('matchtype')
            cls._matchtype_lookup = {
                m['matchtype']: m.get('desc', '')
                for m in (matchtype_data or []) if 'matchtype' in m
            }
        return cls._matchtype_lookup

    @classmethod
    def _get_division_lookup(cls) -> Dict[int, str]:
        """Build and cache {divisionId: divisionName} lookup dict"""
        if cls._division_lookup is None:
            division_data = cls.load_metadata('division')
            cls._division_lookup = {
                d['divisionId']: d.get('divisionName', '')
                for d in (division_data or []) if 'divisionId' in d
            }
        return cls._division_lookup

    @classmethod
    def get_player_name(cls, spid: int) -> str:
        """Get player name from SPID — O(1) lookup"""
        lookup = cls._get_spid_lookup()
        return lookup.get(spid, f"Unknown Player ({spid})")

    @classmethod
    def get_season_name(cls, season_id: int) -> str:
        """Get season name from season ID — O(1) lookup"""
        lookup = cls._get_season_lookup()
        season = lookup.get(season_id)
        if season:
            return season.get('className', f"Unknown Season ({season_id})")
        return f"Unknown Season ({season_id})"

    @classmethod
    def get_season_img(cls, season_id: int) -> str:
        """Get season badge image URL from season ID — O(1) lookup"""
        lookup = cls._get_season_lookup()
        season = lookup.get(season_id)
        if season:
            return season.get('seasonImg', '')
        return ''

    @classmethod
    def get_season_info(cls, season_id: int) -> dict:
        """Get full season info (name + image URL) from season ID — O(1) lookup"""
        lookup = cls._get_season_lookup()
        season = lookup.get(season_id)
        if season:
            class_name = season.get('className', '')
            short_name = class_name.split('(')[0].strip() if '(' in class_name else class_name
            return {
                'name': short_name,
                'img': season.get('seasonImg', '')
            }
        return {'name': f'Unknown Season ({season_id})', 'img': ''}

    @classmethod
    def get_matchtype_name(cls, matchtype: int) -> str:
        """Get match type name — O(1) lookup"""
        lookup = cls._get_matchtype_lookup()
        return lookup.get(matchtype, f"Unknown Type ({matchtype})")

    @classmethod
    def get_division_name(cls, division: int) -> str:
        """Get division name — O(1) lookup"""
        lookup = cls._get_division_lookup()
        return lookup.get(division, f"Unknown Division ({division})")
