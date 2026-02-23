/**
 * Tests for UserDashboard component.
 *
 * Tests cover:
 * - Tab display and functionality
 * - Friendly match support
 * - Tab position at top of page
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import UserDashboard from '../../pages/UserDashboard';
import * as api from '../../services/api';

jest.mock('../../services/api');

const mockOverview = {
  user: {
    ouid: 'test-ouid',
    nickname: 'TestPlayer',
  },
  total_matches: 100,
  record: {
    wins: 60,
    losses: 30,
    draws: 10,
    win_rate: 60,
  },
  statistics: {
    avg_goals_for: 2.1,
    avg_goals_against: 1.5,
    goal_difference: 0.6,
    avg_possession: 55,
    avg_shots: 12,
    avg_shots_on_target: 6,
    shot_accuracy: 50,
    avg_pass_success: 80,
  },
  trends: {
    recent_form: ['W', 'W', 'L', 'W', 'D'],
    recent_wins: 3,
    trend: 'improving',
    first_half_win_rate: 55,
    second_half_win_rate: 62,
  },
  insights: ['테스트 인사이트'],
};

const mockMatches = [
  {
    id: 1,
    match_id: 'match-1',
    match_date: '2024-02-10T12:00:00Z',
    match_type: 50,
    result: 'win',
    goals_for: 3,
    goals_against: 1,
    possession: 60,
    shots: 15,
    shots_on_target: 8,
    pass_success_rate: 85,
    opponent_nickname: 'Opponent1',
  },
];

describe('UserDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (api.getUserMatches as jest.Mock).mockResolvedValue(mockMatches);
    (api.getUserOverview as jest.Mock).mockResolvedValue(mockOverview);
  });

  it('should display match type tabs', async () => {
    render(
      <BrowserRouter>
        <Routes>
          <Route path="/user/:ouid" element={<UserDashboard />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('공식경기')).toBeInTheDocument();
      expect(screen.getByText('공식 감독모드')).toBeInTheDocument();
      expect(screen.getByText('친선경기')).toBeInTheDocument();
    });
  });

  it('should switch between tabs', async () => {
    render(
      <BrowserRouter initialEntries={['/user/test-ouid']} initialIndex={0}>
        <Routes>
          <Route path="/user/:ouid" element={<UserDashboard />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('공식경기')).toBeInTheDocument();
    });

    // Click on manager mode tab
    const managerTab = screen.getByText('공식 감독모드');
    fireEvent.click(managerTab);

    // Should call API with matchtype 52
    await waitFor(() => {
      expect(api.getUserMatches).toHaveBeenCalledWith('test-ouid', 52, 20);
    });
  });

  it('should support friendly matches (matchtype 40)', async () => {
    render(
      <BrowserRouter initialEntries={['/user/test-ouid']} initialIndex={0}>
        <Routes>
          <Route path="/user/:ouid" element={<UserDashboard />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('친선경기')).toBeInTheDocument();
    });

    // Click on friendly match tab
    const friendlyTab = screen.getByText('친선경기');
    fireEvent.click(friendlyTab);

    // Should call API with matchtype 40
    await waitFor(() => {
      expect(api.getUserMatches).toHaveBeenCalledWith('test-ouid', 40, 20);
    });
  });

  it('should display tabs at the top of the page', async () => {
    const { container } = render(
      <BrowserRouter initialEntries={['/user/test-ouid']} initialIndex={0}>
        <Routes>
          <Route path="/user/:ouid" element={<UserDashboard />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('공식경기')).toBeInTheDocument();
    });

    // Tab navigation should appear before user stats
    const tabNavigation = screen.getByText('공식경기').closest('div');
    const statsSection = screen.getByText(/전적/).parentElement;

    // Tabs should come before stats in DOM order
    expect(tabNavigation?.compareDocumentPosition(statsSection!)).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING
    );
  });

  it('should default to official match tab', async () => {
    render(
      <BrowserRouter initialEntries={['/user/test-ouid']} initialIndex={0}>
        <Routes>
          <Route path="/user/:ouid" element={<UserDashboard />} />
        </Routes>
      </BrowserRouter>
    );

    await waitFor(() => {
      // Should call API with matchtype 50 by default
      expect(api.getUserMatches).toHaveBeenCalledWith('test-ouid', 50, 20);
    });
  });
});
