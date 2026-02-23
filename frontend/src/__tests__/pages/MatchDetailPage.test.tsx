/**
 * Tests for MatchDetailPage component.
 *
 * Tests cover:
 * - Loading state
 * - Error handling
 * - Correct user perspective display (critical bug fix verification)
 * - Match overview from analysis.match_overview
 * - Player filtering (only user's players shown)
 * - Timeline and tactical insights rendering
 */
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MatchDetailPage from '../../pages/MatchDetailPage';
import * as api from '../../services/api';

jest.mock('../../services/api');

const mockMatchDetail = {
  match_id: 'test-match',
  result: 'lose',
  goals_for: 0,
  goals_against: 1,
  possession: 45,
  shots: 10,
  shots_on_target: 4,
  pass_success_rate: 78,
  opponent_nickname: 'ZinedineZidane05',
};

const mockAnalysis = {
  match_overview: {
    user_nickname: '창동소년',
    opponent_nickname: 'ZinedineZidane05',
    result: 'lose',
    goals_for: 0,
    goals_against: 1,
    possession: 45,
    shots: 10,
    shots_on_target: 4,
    pass_success_rate: 78,
    match_date: '2024-02-10T12:00:00Z',
  },
  player_performances: {
    top_performers: [
      {
        spid: 103259207,
        player_name: 'Marcos Llorente',
        rating: 7.5,
        goals: 0,
        assists: 0,
        image_url: 'https://photo.api.nexon.com/fifaonline4/103259207.png',
      },
    ],
    all_players: [
      {
        spid: 103259207,
        player_name: 'Marcos Llorente',
        rating: 7.5,
        goals: 0,
        assists: 0,
      },
      {
        spid: 103259208,
        player_name: 'Koke',
        rating: 7.0,
        goals: 0,
        assists: 0,
      },
    ],
  },
  timeline: {
    timeline_data: [
      { minute: 0, xg: 0 },
      { minute: 45, xg: 0.5 },
      { minute: 90, xg: 0.8 },
    ],
    xg_by_period: {
      first_half: 0.5,
      second_half: 0.3,
    },
    key_moments: [
      {
        minute: 60,
        type: 'big_chance',
        xg: 0.4,
      },
    ],
  },
  tactical_insights: {
    attack_pattern: 'wing_play',
    possession_style: 'balanced',
    insights: [
      '측면 공격을 적극 활용했습니다',
      '슈팅 정확도 개선이 필요합니다',
    ],
  },
};

const mockHeatmap = [
  {
    x: 0.85,
    y: 0.50,
    result: 'on_target',
    shot_type: 2,
  },
];

describe('MatchDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should show loading state initially', () => {
    (api.getMatchDetail as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );
    (api.getMatchHeatmap as jest.Mock).mockImplementation(
      () => new Promise(() => {})
    );
    (api.getMatchAnalysis as jest.Mock).mockImplementation(
      () => new Promise(() => {})
    );

    render(
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={<MatchDetailPage />}
          />
        </Routes>
      </BrowserRouter>
    );

    expect(screen.getByText(/경기 정보 불러오는 중/)).toBeInTheDocument();
  });

  it('should display correct user perspective (critical test)', async () => {
    (api.getMatchDetail as jest.Mock).mockResolvedValue(mockMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      // Should display user's nickname from analysis.match_overview
      expect(screen.getByText('창동소년')).toBeInTheDocument();
    });

    // Should display correct result (lose, not win)
    expect(screen.getByText('패배')).toBeInTheDocument();

    // Should display correct score from user's perspective (0-1)
    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();

    // Should display opponent nickname
    expect(screen.getByText('ZinedineZidane05')).toBeInTheDocument();
  });

  it('should use match_overview from analysis, not match state', async () => {
    // This test verifies the bug fix where frontend was using wrong data source
    const wrongMatchDetail = {
      ...mockMatchDetail,
      result: 'win', // Wrong perspective
      goals_for: 1,
      goals_against: 0,
    };

    (api.getMatchDetail as jest.Mock).mockResolvedValue(wrongMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      // Should use analysis.match_overview, not match state
      expect(screen.getByText('패배')).toBeInTheDocument();
      expect(screen.getByText('창동소년')).toBeInTheDocument();
    });

    // Should NOT show wrong perspective data
    expect(screen.queryByText('승리')).not.toBeInTheDocument();
  });

  it('should display only user\'s players (not opponent)', async () => {
    (api.getMatchDetail as jest.Mock).mockResolvedValue(mockMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      // Should show user's players (18 players, not 36)
      expect(screen.getByText('Marcos Llorente')).toBeInTheDocument();
      expect(screen.getByText('Koke')).toBeInTheDocument();
    });

    // all_players should only have user's players
    expect(mockAnalysis.player_performances.all_players).toHaveLength(2);
  });

  it('should display top performers', async () => {
    (api.getMatchDetail as jest.Mock).mockResolvedValue(mockMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('베스트 플레이어')).toBeInTheDocument();
      expect(screen.getByText('Marcos Llorente')).toBeInTheDocument();
    });
  });

  it('should display tactical insights in Korean', async () => {
    (api.getMatchDetail as jest.Mock).mockResolvedValue(mockMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('전술 인사이트')).toBeInTheDocument();
      expect(screen.getByText(/측면 공격을 적극 활용했습니다/)).toBeInTheDocument();
      expect(screen.getByText(/슈팅 정확도 개선이 필요합니다/)).toBeInTheDocument();
    });
  });

  it('should display timeline analysis', async () => {
    (api.getMatchDetail as jest.Mock).mockResolvedValue(mockMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('타임라인 분석')).toBeInTheDocument();
    });
  });

  it('should display shot heatmap', async () => {
    (api.getMatchDetail as jest.Mock).mockResolvedValue(mockMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('슈팅 히트맵')).toBeInTheDocument();
    });
  });

  it('should handle error state', async () => {
    (api.getMatchDetail as jest.Mock).mockRejectedValue(
      new Error('Failed to fetch')
    );
    (api.getMatchHeatmap as jest.Mock).mockRejectedValue(
      new Error('Failed to fetch')
    );
    (api.getMatchAnalysis as jest.Mock).mockRejectedValue(
      new Error('Failed to fetch')
    );

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(
        screen.getByText(/경기 상세 정보를 불러올 수 없습니다/)
      ).toBeInTheDocument();
    });
  });

  it('should pass ouid parameter to API calls', async () => {
    (api.getMatchDetail as jest.Mock).mockResolvedValue(mockMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=test-user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(api.getMatchDetail).toHaveBeenCalledWith(
        'test-match',
        'test-user-ouid'
      );
      expect(api.getMatchHeatmap).toHaveBeenCalledWith(
        'test-match',
        'test-user-ouid'
      );
      expect(api.getMatchAnalysis).toHaveBeenCalledWith(
        'test-match',
        'test-user-ouid'
      );
    });
  });

  it('should display match stats grid', async () => {
    (api.getMatchDetail as jest.Mock).mockResolvedValue(mockMatchDetail);
    (api.getMatchHeatmap as jest.Mock).mockResolvedValue(mockHeatmap);
    (api.getMatchAnalysis as jest.Mock).mockResolvedValue(mockAnalysis);

    render(
      <BrowserRouter
        initialEntries={['/match/test-match?ouid=user-ouid']}
        initialIndex={0}
      >
        <Routes>
          <Route path="/match/:matchId" element={<MatchDetailPage />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('점유율')).toBeInTheDocument();
      expect(screen.getByText('45%')).toBeInTheDocument();
      expect(screen.getByText('슈팅')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument();
      expect(screen.getByText('유효슈팅')).toBeInTheDocument();
      expect(screen.getByText('4')).toBeInTheDocument();
    });
  });
});
