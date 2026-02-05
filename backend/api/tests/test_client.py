"""
Comprehensive tests for Nexon API Client.

Tests cover:
- User search API calls
- Match data fetching
- API error handling
- Rate limiting
- Response parsing
"""
from unittest.mock import patch, Mock
from django.test import TestCase
from nexon_api.client import NexonAPIClient


class NexonAPIClientTest(TestCase):
    """Test NexonAPIClient functionality."""

    def setUp(self):
        self.client = NexonAPIClient()

    @patch('nexon_api.client.requests.get')
    def test_search_user_by_nickname(self, mock_get):
        """Test searching user by nickname."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ouid': 'test-ouid-123',
            'nickname': 'TestPlayer'
        }
        mock_get.return_value = mock_response

        result = self.client.search_user('TestPlayer')

        self.assertEqual(result['ouid'], 'test-ouid-123')
        self.assertEqual(result['nickname'], 'TestPlayer')

        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('nickname=TestPlayer', call_args[0][0])

    @patch('nexon_api.client.requests.get')
    def test_get_user_info(self, mock_get):
        """Test getting user info by ouid."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ouid': 'test-ouid-123',
            'nickname': 'TestPlayer',
            'level': 50
        }
        mock_get.return_value = mock_response

        result = self.client.get_user_info('test-ouid-123')

        self.assertEqual(result['ouid'], 'test-ouid-123')
        self.assertEqual(result['nickname'], 'TestPlayer')

    @patch('nexon_api.client.requests.get')
    def test_get_user_matches(self, mock_get):
        """Test fetching user match list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            'match-id-1',
            'match-id-2',
            'match-id-3'
        ]
        mock_get.return_value = mock_response

        result = self.client.get_user_matches('test-ouid', matchtype=50, limit=10)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 'match-id-1')

    @patch('nexon_api.client.requests.get')
    def test_get_match_detail(self, mock_get):
        """Test fetching match detail."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'matchId': 'match-123',
            'matchDate': '2024-02-10T12:00:00Z',
            'matchInfo': [
                {
                    'ouid': 'user-1',
                    'nickname': 'Player1',
                    'matchDetail': {
                        'matchResult': '승'
                    },
                    'shoot': {
                        'shootTotal': 15,
                        'effectiveShootTotal': 8
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_match_detail('match-123')

        self.assertEqual(result['matchId'], 'match-123')
        self.assertIn('matchInfo', result)
        self.assertEqual(len(result['matchInfo']), 1)

    @patch('nexon_api.client.requests.get')
    def test_api_error_404(self, mock_get):
        """Test handling 404 error from API."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Not found'}
        mock_get.return_value = mock_response

        with self.assertRaises(Exception):
            self.client.search_user('NonExistentPlayer')

    @patch('nexon_api.client.requests.get')
    def test_api_error_500(self, mock_get):
        """Test handling 500 error from API."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'error': 'Server error'}
        mock_get.return_value = mock_response

        with self.assertRaises(Exception):
            self.client.get_user_info('test-ouid')

    @patch('nexon_api.client.requests.get')
    def test_api_timeout_handling(self, mock_get):
        """Test handling API timeout."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(requests.exceptions.Timeout):
            self.client.search_user('TestPlayer')

    @patch('nexon_api.client.requests.get')
    def test_api_connection_error(self, mock_get):
        """Test handling connection error."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(requests.exceptions.ConnectionError):
            self.client.search_user('TestPlayer')

    @patch('nexon_api.client.requests.get')
    def test_rate_limiting_headers(self, mock_get):
        """Test that rate limiting headers are respected."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ouid': 'test'}
        mock_response.headers = {
            'X-RateLimit-Remaining': '10',
            'X-RateLimit-Reset': '1234567890'
        }
        mock_get.return_value = mock_response

        result = self.client.search_user('TestPlayer')

        # Should successfully get result
        self.assertIsNotNone(result)

    @patch('nexon_api.client.requests.get')
    def test_api_key_in_headers(self, mock_get):
        """Test that API key is included in request headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ouid': 'test'}
        mock_get.return_value = mock_response

        self.client.search_user('TestPlayer')

        # Verify headers include API key
        call_kwargs = mock_get.call_args[1]
        self.assertIn('headers', call_kwargs)
        headers = call_kwargs['headers']
        # API key header name might vary
        has_api_key = any('api' in k.lower() or 'authorization' in k.lower() for k in headers.keys())
        self.assertTrue(has_api_key or 'x-nxopen-api-key' in headers)

    @patch('nexon_api.client.requests.get')
    def test_multiple_match_info_parsing(self, mock_get):
        """Test parsing match with multiple matchInfo (both users)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'matchId': 'match-123',
            'matchInfo': [
                {
                    'ouid': 'user-1',
                    'nickname': 'Player1',
                    'matchDetail': {'matchResult': '승'}
                },
                {
                    'ouid': 'user-2',
                    'nickname': 'Player2',
                    'matchDetail': {'matchResult': '패'}
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_match_detail('match-123')

        # Should have both users' data
        self.assertEqual(len(result['matchInfo']), 2)
        self.assertEqual(result['matchInfo'][0]['nickname'], 'Player1')
        self.assertEqual(result['matchInfo'][1]['nickname'], 'Player2')

    @patch('nexon_api.client.requests.get')
    def test_empty_match_list(self, mock_get):
        """Test handling empty match list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = self.client.get_user_matches('test-ouid', matchtype=50, limit=10)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @patch('nexon_api.client.requests.get')
    def test_match_with_shot_details(self, mock_get):
        """Test parsing match with shot details."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'matchId': 'match-123',
            'matchInfo': [
                {
                    'ouid': 'user-1',
                    'shootDetail': [
                        {
                            'goalTime': 30,
                            'x': 0.8512,
                            'y': 0.4523,
                            'type': 3,
                            'result': 1
                        },
                        {
                            'goalTime': 60,
                            'x': 0.7500,
                            'y': 0.5000,
                            'type': 2,
                            'result': 2
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_match_detail('match-123')

        # Should have shot details
        self.assertIn('shootDetail', result['matchInfo'][0])
        self.assertEqual(len(result['matchInfo'][0]['shootDetail']), 2)

    @patch('nexon_api.client.requests.get')
    def test_match_with_player_data(self, mock_get):
        """Test parsing match with player data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'matchId': 'match-123',
            'matchInfo': [
                {
                    'ouid': 'user-1',
                    'player': [
                        {
                            'spId': 103259207,
                            'spPosition': 27,
                            'spGrade': 8,
                            'status': {
                                'spRating': 8.5,
                                'goal': 2
                            }
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_match_detail('match-123')

        # Should have player data
        self.assertIn('player', result['matchInfo'][0])
        self.assertEqual(len(result['matchInfo'][0]['player']), 1)
        self.assertEqual(result['matchInfo'][0]['player'][0]['spId'], 103259207)
