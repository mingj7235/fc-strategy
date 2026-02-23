/**
 * Comprehensive tests for API service functions.
 *
 * Tests cover:
 * - User search and retrieval
 * - Match data fetching with ouid parameter
 * - Analysis endpoints
 * - Error handling
 */
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import {
  searchUser,
  getUserByOuid,
  getUserMatches,
  getMatchDetail,
  getMatchHeatmap,
  getMatchAnalysis,
  getPlayerStats,
  getUserStatistics,
} from '../../services/api';

describe('API Service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  describe('User API', () => {
    it('should search user by nickname', async () => {
      const mockResponse = {
        ouid: 'test-ouid-123',
        nickname: 'TestPlayer',
        max_division: 2100,
      };

      mock.onGet('/api/users/search/').reply(200, mockResponse);

      const result = await searchUser('TestPlayer');

      expect(result.ouid).toBe('test-ouid-123');
      expect(result.nickname).toBe('TestPlayer');
    });

    it('should get user by ouid', async () => {
      const mockResponse = {
        ouid: 'test-ouid',
        nickname: 'Player1',
        max_division: 2000,
      };

      mock.onGet('/api/users/test-ouid/').reply(200, mockResponse);

      const result = await getUserByOuid('test-ouid');

      expect(result.ouid).toBe('test-ouid');
      expect(result.nickname).toBe('Player1');
    });

    it('should get user matches', async () => {
      const mockMatches = [
        {
          match_id: 'match-1',
          result: 'win',
          goals_for: 3,
          goals_against: 1,
          shots: 15,
          shots_on_target: 8,
          opponent_nickname: 'Opponent1',
        },
      ];

      mock.onGet('/api/users/test-ouid/matches/').reply(200, mockMatches);

      const result = await getUserMatches('test-ouid', 50, 10);

      expect(result).toHaveLength(1);
      expect(result[0].match_id).toBe('match-1');
      expect(result[0].shots).toBe(15);
      expect(result[0].opponent_nickname).toBe('Opponent1');
    });
  });

  describe('Match API with ouid parameter', () => {
    it('should get match detail with ouid parameter', async () => {
      const mockResponse = {
        match_id: 'match-123',
        result: 'win',
        goals_for: 2,
        goals_against: 1,
      };

      mock
        .onGet('/api/matches/match-123/detail/', { params: { ouid: 'user-ouid' } })
        .reply(200, mockResponse);

      const result = await getMatchDetail('match-123', 'user-ouid');

      expect(result.match_id).toBe('match-123');
      expect(result.result).toBe('win');
    });

    it('should get match detail without ouid parameter', async () => {
      const mockResponse = {
        match_id: 'match-123',
        result: 'win',
      };

      mock.onGet('/api/matches/match-123/detail/').reply(200, mockResponse);

      const result = await getMatchDetail('match-123');

      expect(result.match_id).toBe('match-123');
    });

    it('should get match heatmap with ouid', async () => {
      const mockHeatmap = [
        {
          x: 0.85,
          y: 0.50,
          result: 'goal',
          shot_type: 3,
        },
      ];

      mock
        .onGet('/api/matches/match-123/heatmap/', { params: { ouid: 'user-ouid' } })
        .reply(200, mockHeatmap);

      const result = await getMatchHeatmap('match-123', 'user-ouid');

      expect(result).toHaveLength(1);
      expect(result[0].result).toBe('goal');
    });

    it('should get match analysis with correct user perspective', async () => {
      const mockAnalysis = {
        match_overview: {
          user_nickname: '창동소년',
          opponent_nickname: 'ZinedineZidane05',
          result: 'lose',
          goals_for: 0,
          goals_against: 1,
        },
        player_performances: {
          top_performers: [],
          all_players: [],
        },
        timeline: {
          xg_by_period: { first_half: 0.5, second_half: 0.3 },
          key_moments: [],
        },
        tactical_insights: {
          insights: [],
        },
      };

      mock
        .onGet('/api/matches/match-123/analysis/', { params: { ouid: 'user-ouid' } })
        .reply(200, mockAnalysis);

      const result = await getMatchAnalysis('match-123', 'user-ouid');

      expect(result.match_overview.user_nickname).toBe('창동소년');
      expect(result.match_overview.result).toBe('lose');
      expect(result.match_overview.goals_for).toBe(0);
    });

    it('should get player stats filtered by user', async () => {
      const mockPlayerStats = {
        top_performers: [
          {
            spid: 103259207,
            player_name: 'Son Heung-min',
            rating: 8.5,
            goals: 2,
            assists: 1,
          },
        ],
        all_players: [
          {
            spid: 103259207,
            player_name: 'Son Heung-min',
            rating: 8.5,
          },
        ],
      };

      mock
        .onGet('/api/matches/match-123/player-stats/', { params: { ouid: 'user-ouid' } })
        .reply(200, mockPlayerStats);

      const result = await getPlayerStats('match-123', 'user-ouid');

      expect(result.top_performers).toHaveLength(1);
      expect(result.all_players[0].player_name).toBe('Son Heung-min');
    });
  });

  describe('Analysis API', () => {
    it('should get user statistics', async () => {
      const mockStats = {
        total_matches: 100,
        wins: 60,
        losses: 30,
        draws: 10,
        win_rate: 60.0,
      };

      mock.onGet('/api/users/test-ouid/statistics/').reply(200, mockStats);

      const result = await getUserStatistics('test-ouid', 50, 10);

      expect(result.total_matches).toBe(100);
      expect(result.win_rate).toBe(60.0);
    });
  });

  describe('Error Handling', () => {
    it('should handle 404 errors', async () => {
      mock.onGet('/api/users/search/').reply(404, { error: 'Not found' });

      await expect(searchUser('NonExistent')).rejects.toThrow();
    });

    it('should handle 500 errors', async () => {
      mock.onGet('/api/users/test-ouid/').reply(500, { error: 'Server error' });

      await expect(getUserByOuid('test-ouid')).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      mock.onGet('/api/users/search/').networkError();

      await expect(searchUser('TestPlayer')).rejects.toThrow();
    });
  });
});
