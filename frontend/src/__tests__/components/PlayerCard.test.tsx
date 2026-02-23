/**
 * Tests for PlayerCard component.
 *
 * Tests cover:
 * - Player information display
 * - Image loading and fallback
 * - Rating color coding
 * - Stats display
 */
import { render, screen, fireEvent } from '@testing-library/react';
import PlayerCard from '../../components/match/PlayerCard';
import { PlayerPerformance } from '../../types/match';

const mockPlayer: PlayerPerformance = {
  spid: 103259207,
  player_name: 'Son Heung-min',
  image_url: 'https://photo.api.nexon.com/fifaonline4/103259207.png',
  rating: 8.5,
  goals: 2,
  assists: 1,
  shots: 5,
  shots_on_target: 4,
  shot_accuracy: 80.0,
  pass_success_rate: 85.5,
  pass_attempts: 50,
  pass_success: 42,
};

describe('PlayerCard', () => {
  it('should render player name', () => {
    render(<PlayerCard player={mockPlayer} rank={1} />);

    expect(screen.getByText('Son Heung-min')).toBeInTheDocument();
  });

  it('should render player rating', () => {
    render(<PlayerCard player={mockPlayer} rank={1} />);

    expect(screen.getByText('8.5')).toBeInTheDocument();
  });

  it('should render goals and assists', () => {
    render(<PlayerCard player={mockPlayer} rank={1} />);

    expect(screen.getByText(/2/)).toBeInTheDocument(); // goals
    expect(screen.getByText(/1/)).toBeInTheDocument(); // assists
  });

  it('should display rank badge for top 3', () => {
    const { container } = render(<PlayerCard player={mockPlayer} rank={1} />);

    expect(container.querySelector('[data-rank="1"]')).toBeInTheDocument();
  });

  it('should render player image', () => {
    render(<PlayerCard player={mockPlayer} rank={1} />);

    const image = screen.getByRole('img');
    expect(image).toHaveAttribute(
      'src',
      'https://photo.api.nexon.com/fifaonline4/103259207.png'
    );
  });

  it('should handle image loading error with fallback', () => {
    render(<PlayerCard player={mockPlayer} rank={1} />);

    const image = screen.getByRole('img') as HTMLImageElement;
    fireEvent.error(image);

    // Should still display without crashing
    expect(screen.getByText('Son Heung-min')).toBeInTheDocument();
  });

  it('should apply green color for high rating (>8.0)', () => {
    const highRatedPlayer = { ...mockPlayer, rating: 8.5 };
    const { container } = render(<PlayerCard player={highRatedPlayer} />);

    const ratingElement = screen.getByText('8.5');
    expect(ratingElement).toHaveClass('text-green-500');
  });

  it('should apply yellow color for medium rating (7-8)', () => {
    const mediumRatedPlayer = { ...mockPlayer, rating: 7.5 };
    const { container } = render(<PlayerCard player={mediumRatedPlayer} />);

    const ratingElement = screen.getByText('7.5');
    expect(ratingElement).toHaveClass('text-yellow-500');
  });

  it('should apply red color for low rating (<7)', () => {
    const lowRatedPlayer = { ...mockPlayer, rating: 6.5 };
    const { container } = render(<PlayerCard player={lowRatedPlayer} />);

    const ratingElement = screen.getByText('6.5');
    expect(ratingElement).toHaveClass('text-red-500');
  });

  it('should display shot accuracy if available', () => {
    render(<PlayerCard player={mockPlayer} rank={1} />);

    expect(screen.getByText(/80.*%/)).toBeInTheDocument();
  });

  it('should display pass success rate if available', () => {
    render(<PlayerCard player={mockPlayer} rank={1} />);

    expect(screen.getByText(/85.*%/)).toBeInTheDocument();
  });

  it('should handle player without goals or assists', () => {
    const playerNoGoals = {
      ...mockPlayer,
      goals: 0,
      assists: 0,
    };

    render(<PlayerCard player={playerNoGoals} />);

    expect(screen.getByText('Son Heung-min')).toBeInTheDocument();
    expect(screen.getByText('8.5')).toBeInTheDocument();
  });

  it('should handle player without rank', () => {
    render(<PlayerCard player={mockPlayer} />);

    expect(screen.getByText('Son Heung-min')).toBeInTheDocument();
  });
});
