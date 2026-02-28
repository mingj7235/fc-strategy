import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from django.core.cache import cache
from .exceptions import NexonAPIException, UserNotFoundException


class NexonAPIClient:
    """Nexon FC Online Open API Client"""

    BASE_URL = settings.NEXON_API_BASE_URL

    # Shared session with connection pooling (one per process)
    _session = None

    def __init__(self):
        self.api_key = settings.NEXON_API_KEY
        self.headers = {
            "x-nxopen-api-key": self.api_key
        }

    @classmethod
    def _get_session(cls):
        """Get or create a shared requests.Session with connection pooling and retry"""
        if cls._session is None:
            cls._session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
            )
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,
                pool_maxsize=20,
            )
            cls._session.mount("https://", adapter)
            cls._session.mount("http://", adapter)
        return cls._session

    def _make_request(self, endpoint, params=None, cache_key=None, cache_timeout=3600):
        """Make API request with caching support"""
        if cache_key:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

        url = f"{self.BASE_URL}{endpoint}"
        session = self._get_session()
        try:
            response = session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if cache_key:
                cache.set(cache_key, data, cache_timeout)

            return data
        except requests.exceptions.RequestException as e:
            # Log response body for debugging
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.text

                    # Parse error response JSON
                    try:
                        error_json = e.response.json()
                        error_code = error_json.get('error', {}).get('name', '')
                        error_message = error_json.get('error', {}).get('message', '')

                        # Handle specific error codes
                        if error_code == 'OPENAPI00004' or e.response.status_code == 400:
                            # Invalid parameter or 400 Bad Request - usually means user not found
                            raise UserNotFoundException("유저를 찾을 수 없습니다. 닉네임을 확인해주세요.")

                        error_detail = f"{error_code}: {error_message}" if error_code else str(e)
                    except (ValueError, KeyError):
                        # If JSON parsing fails but it's 400, still treat as user not found
                        if e.response.status_code == 400:
                            raise UserNotFoundException("유저를 찾을 수 없습니다. 닉네임을 확인해주세요.")
                        error_detail = f"{str(e)} - Response: {error_body[:200]}"
                except UserNotFoundException:
                    # Re-raise UserNotFoundException so it's not caught by the general except
                    raise
                except Exception:
                    pass
            raise NexonAPIException(f"API request failed: {error_detail}")

    def search_user(self, nickname):
        """Search user by nickname, returns full response dict"""
        session = self._get_session()
        url = f"{self.BASE_URL}/fconline/v1/id?nickname={nickname}"
        response = session.get(url, headers=self.headers, timeout=10)
        if response.status_code >= 400:
            raise NexonAPIException(f"API request failed: {response.status_code}")
        return response.json()

    def get_user_info(self, ouid):
        """Get user info by ouid, returns full response dict"""
        session = self._get_session()
        url = f"{self.BASE_URL}/fconline/v1/user/basic?ouid={ouid}"
        response = session.get(url, headers=self.headers, timeout=10)
        if response.status_code >= 400:
            raise NexonAPIException(f"API request failed: {response.status_code}")
        return response.json()

    def get_user_ouid(self, nickname):
        """Get user OUID by nickname"""
        cache_key = f"ouid:{nickname}"
        params = {"nickname": nickname}

        data = self._make_request(
            "/fconline/v1/id",
            params=params,
            cache_key=cache_key,
            cache_timeout=3600  # 1 hour
        )

        return data.get("ouid")

    def get_user_max_division(self, ouid):
        """Get user's maximum division"""
        cache_key = f"max_division:{ouid}"

        data = self._make_request(
            f"/fconline/v1/user/maxdivision",
            params={"ouid": ouid},
            cache_key=cache_key,
            cache_timeout=1800  # 30 minutes
        )

        return data

    def get_user_matches(self, ouid, matchtype=50, offset=0, limit=10):
        """Get user's match ID list"""
        params = {
            "ouid": ouid,
            "matchtype": matchtype,
            "offset": offset,
            "limit": limit
        }

        cache_key = f"match_list:{ouid}:{matchtype}:{offset}:{limit}"
        data = self._make_request(
            "/fconline/v1/user/match",
            params=params,
            cache_key=cache_key,
            cache_timeout=1800,  # 30 minutes
        )

        return data

    def get_match_detail(self, match_id):
        """Get match detail information"""
        params = {"matchid": match_id}

        cache_key = f"match_detail:{match_id}"
        data = self._make_request(
            "/fconline/v1/match-detail",
            params=params,
            cache_key=cache_key,
            cache_timeout=86400,  # 24 hours (match data is immutable)
        )

        return data

    def get_user_trade(self, ouid, tradetype='buy', offset=0, limit=10):
        """Get user's trade history"""
        params = {
            "ouid": ouid,
            "tradetype": tradetype,
            "offset": offset,
            "limit": limit
        }

        data = self._make_request(
            "/fconline/v1/user/trade",
            params=params,
            cache_key=None,
        )

        return data

    def get_ranker_stats(self, matchtype, players):
        """Get ranker stats for specific players

        Args:
            matchtype: Match type (50=공식경기, 52=감독모드, etc.)
            players: List of dicts with 'id' (spid) and 'po' (position)
                    Example: [{"id": 826250959, "po": 18}]

        Returns:
            List of player stats from TOP 10,000 rankers
        """
        import json

        cache_key = f"ranker_stats:{matchtype}:{hash(json.dumps(players, sort_keys=True))}"
        params = {
            "matchtype": matchtype,
            "players": json.dumps(players, separators=(',', ':'))  # No spaces
        }

        data = self._make_request(
            "/fconline/v1/ranker-stats",
            params=params,
            cache_key=cache_key,
            cache_timeout=3600  # 1 hour
        )

        return data
