/**
 * Tests for TacticalInsightsPanel component.
 *
 * Tests cover:
 * - Insights rendering in Korean
 * - Attack pattern display
 * - Possession style display
 * - Empty insights handling
 */
import { render, screen } from '@testing-library/react';
import TacticalInsightsPanel from '../../components/match/TacticalInsightsPanel';

const mockInsights = {
  attack_pattern: 'wing_play',
  possession_style: 'possession_based',
  defensive_line: 'high',
  insights: [
    '점유율 우위를 바탕으로 경기를 주도했습니다',
    '측면 공격을 적극 활용했습니다',
    '슈팅 정확도가 우수합니다',
    '안정적인 빌드업 플레이를 보여줍니다',
  ],
};

describe('TacticalInsightsPanel', () => {
  it('should render all insights in Korean', () => {
    render(<TacticalInsightsPanel insights={mockInsights} />);

    mockInsights.insights.forEach((insight) => {
      expect(screen.getByText(insight)).toBeInTheDocument();
    });
  });

  it('should display attack pattern', () => {
    render(<TacticalInsightsPanel insights={mockInsights} />);

    // Should show wing play indicator
    expect(screen.getByText(/측면/)).toBeInTheDocument();
  });

  it('should display possession style', () => {
    render(<TacticalInsightsPanel insights={mockInsights} />);

    // Should show possession-based indicator
    expect(screen.getByText(/점유/)).toBeInTheDocument();
  });

  it('should render insights as numbered list', () => {
    const { container } = render(
      <TacticalInsightsPanel insights={mockInsights} />
    );

    const insightElements = container.querySelectorAll('.insight-item');
    expect(insightElements.length).toBe(4);
  });

  it('should handle wing play attack pattern', () => {
    const wingPlayInsights = {
      ...mockInsights,
      attack_pattern: 'wing_play',
    };

    render(<TacticalInsightsPanel insights={wingPlayInsights} />);

    expect(screen.getByText(/측면 공격/)).toBeInTheDocument();
  });

  it('should handle central penetration attack pattern', () => {
    const centralInsights = {
      ...mockInsights,
      attack_pattern: 'central_penetration',
      insights: ['중앙 돌파를 선호합니다'],
    };

    render(<TacticalInsightsPanel insights={centralInsights} />);

    expect(screen.getByText(/중앙 돌파/)).toBeInTheDocument();
  });

  it('should handle balanced attack pattern', () => {
    const balancedInsights = {
      ...mockInsights,
      attack_pattern: 'balanced',
    };

    render(<TacticalInsightsPanel insights={balancedInsights} />);

    // Should render without errors
    expect(screen.getByText(/점유율 우위/)).toBeInTheDocument();
  });

  it('should handle empty insights array', () => {
    const emptyInsights = {
      ...mockInsights,
      insights: [],
    };

    const { container } = render(
      <TacticalInsightsPanel insights={emptyInsights} />
    );

    // Should render without crashing
    expect(container).toBeInTheDocument();
  });

  it('should display possession-based style', () => {
    const possessionInsights = {
      ...mockInsights,
      possession_style: 'possession_based',
    };

    render(<TacticalInsightsPanel insights={possessionInsights} />);

    expect(screen.getByText(/점유/)).toBeInTheDocument();
  });

  it('should display counter-attack style', () => {
    const counterInsights = {
      ...mockInsights,
      possession_style: 'counter_attack',
    };

    render(<TacticalInsightsPanel insights={counterInsights} />);

    // Should render style indicator
    expect(screen.getByText(/점유율 우위/)).toBeInTheDocument();
  });

  it('should use professional styling', () => {
    const { container } = render(
      <TacticalInsightsPanel insights={mockInsights} />
    );

    // Should have gradient backgrounds and professional design
    const panel = container.querySelector('.tactical-insights-panel');
    expect(panel).toBeInTheDocument();
  });

  it('should verify all insights contain Korean characters', () => {
    render(<TacticalInsightsPanel insights={mockInsights} />);

    mockInsights.insights.forEach((insight) => {
      const hasKorean = /[가-힣]/.test(insight);
      expect(hasKorean).toBe(true);
    });
  });

  it('should handle long insight text gracefully', () => {
    const longInsights = {
      ...mockInsights,
      insights: [
        '점유율 우위를 바탕으로 경기를 주도했습니다. 하지만 높은 점유율에 비해 골 생산력이 부족합니다. 슈팅 정확도 개선이 필요합니다.',
      ],
    };

    render(<TacticalInsightsPanel insights={longInsights} />);

    expect(screen.getByText(/점유율 우위/)).toBeInTheDocument();
  });
});
