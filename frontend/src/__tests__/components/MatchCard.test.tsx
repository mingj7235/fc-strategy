/**
 * Tests for MatchCard component.
 *
 * Tests cover:
 * - Rendering match information correctly
 * - Displaying shots and shots_on_target (bug fix verification)
 * - Displaying opponent_nickname (bug fix verification)
 * - Result badge styling
 * - Navigation on click
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import MatchCard from '../../components/match/MatchCard';
import { Match } from '../../types/match';

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const mockMatch: Match = {
  id: 1,
  match_id: 'test-match-123',
  match_date: '2024-02-10T12:00:00Z',
  match_type: 50,
  result: 'win',
  goals_for: 3,
  goals_against: 1,
  possession: 60,
  shots: 15,
  shots_on_target: 8,
  pass_success_rate: 85.5,
  opponent_nickname: 'OpponentPlayer',
};

describe('MatchCard', () => {
  it('should render match result correctly', () => {
    render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    expect(screen.getByText('승리')).toBeInTheDocument();
  });

  it('should display score correctly', () => {
    render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('should display shots and shots_on_target (bug fix verification)', () => {
    render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    // Should show "8/15" format
    const shotsText = screen.getByText(/8.*\/.*15/);
    expect(shotsText).toBeInTheDocument();
  });

  it('should NOT display 0/0 for shots when data is present', () => {
    render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    // Should NOT have "0/0"
    expect(screen.queryByText('0/0')).not.toBeInTheDocument();
  });

  it('should display opponent nickname', () => {
    render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    expect(screen.getByText(/OpponentPlayer/)).toBeInTheDocument();
  });

  it('should display possession percentage', () => {
    render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    expect(screen.getByText(/60%/)).toBeInTheDocument();
  });

  it('should apply correct styling for win result', () => {
    const { container } = render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    const resultBadge = screen.getByText('승리');
    expect(resultBadge).toHaveClass('text-accent-success');
  });

  it('should apply correct styling for lose result', () => {
    const loseMatch = { ...mockMatch, result: 'lose' };

    const { container } = render(
      <BrowserRouter>
        <MatchCard match={loseMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    const resultBadge = screen.getByText('패배');
    expect(resultBadge).toHaveClass('text-accent-danger');
  });

  it('should navigate to match detail with ouid parameter on click', () => {
    render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user-ouid" />
      </BrowserRouter>
    );

    const card = screen.getByRole('button');
    fireEvent.click(card);

    expect(mockNavigate).toHaveBeenCalledWith(
      '/match/test-match-123?ouid=test-user-ouid'
    );
  });

  it('should format date correctly', () => {
    render(
      <BrowserRouter>
        <MatchCard match={mockMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    // Should display formatted date (implementation specific)
    expect(screen.getByText(/2024/)).toBeInTheDocument();
  });

  it('should handle draw result', () => {
    const drawMatch = { ...mockMatch, result: 'draw' };

    render(
      <BrowserRouter>
        <MatchCard match={drawMatch} userOuid="test-user" />
      </BrowserRouter>
    );

    expect(screen.getByText('무승부')).toBeInTheDocument();
  });

  it('should handle missing opponent nickname gracefully', () => {
    const matchWithoutOpponent = { ...mockMatch, opponent_nickname: undefined };

    render(
      <BrowserRouter>
        <MatchCard match={matchWithoutOpponent} userOuid="test-user" />
      </BrowserRouter>
    );

    expect(screen.getByText(/상대/)).toBeInTheDocument();
  });
});
