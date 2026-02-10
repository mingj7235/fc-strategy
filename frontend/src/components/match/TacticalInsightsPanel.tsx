import React from 'react';

interface TacticalInsight {
  attack_pattern: {
    type: string;
    description: string;
    wing_shots: number;
    central_shots: number;
    total_shots: number;
  };
  possession_style: {
    type: string;
    description: string;
    possession: number;
    pass_success_rate: number;
  };
  defensive_approach: {
    type: string;
    description: string;
  };
  insights: string[];
  recommendations: string[];
}

interface TacticalInsightsPanelProps {
  insights: TacticalInsight;
}

const TacticalInsightsPanel: React.FC<TacticalInsightsPanelProps> = ({ insights }) => {
  const getPatternIcon = (type: string) => {
    switch (type) {
      case 'wing_play':
        return '⚡';
      case 'central_penetration':
        return '🎯';
      default:
        return '⚖️';
    }
  };

  const getStyleIcon = (type: string) => {
    switch (type) {
      case 'tiki_taka':
        return '🎨';
      case 'possession_based':
        return '🎯';
      case 'counter_attack':
        return '⚡';
      case 'direct_play':
        return '➡️';
      default:
        return '⚖️';
    }
  };

  return (
    <div className="space-y-6">
      {/* Tactical Style Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Attack Pattern */}
        <div className="bg-gradient-to-br from-chart-blue/20 to-chart-blue/5 border border-chart-blue/30 rounded-lg p-4 hover:border-chart-blue/60 transition-colors">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{getPatternIcon(insights.attack_pattern.type)}</span>
            <h3 className="font-bold text-white">공격 패턴</h3>
          </div>
          <p className="text-sm text-gray-300 font-medium mb-3">
            {insights.attack_pattern.description}
          </p>
          <div className="space-y-1 text-xs text-gray-400">
            <div className="flex justify-between">
              <span>측면:</span>
              <span className="font-medium text-chart-blue">{insights.attack_pattern.wing_shots}회</span>
            </div>
            <div className="flex justify-between">
              <span>중앙:</span>
              <span className="font-medium text-chart-cyan">{insights.attack_pattern.central_shots}회</span>
            </div>
          </div>
        </div>

        {/* Possession Style */}
        <div className="bg-gradient-to-br from-chart-green/20 to-chart-green/5 border border-chart-green/30 rounded-lg p-4 hover:border-chart-green/60 transition-colors">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{getStyleIcon(insights.possession_style.type)}</span>
            <h3 className="font-bold text-white">점유 스타일</h3>
          </div>
          <p className="text-sm text-gray-300 font-medium mb-3">
            {insights.possession_style.description}
          </p>
          <div className="space-y-1 text-xs text-gray-400">
            <div className="flex justify-between">
              <span>점유율:</span>
              <span className="font-medium text-chart-green">{insights.possession_style.possession.toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span>패스 성공률:</span>
              <span className="font-medium text-chart-yellow">{insights.possession_style.pass_success_rate.toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* Defensive Approach */}
        <div className="bg-gradient-to-br from-chart-purple/20 to-chart-purple/5 border border-chart-purple/30 rounded-lg p-4 hover:border-chart-purple/60 transition-colors">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🛡️</span>
            <h3 className="font-bold text-white">수비 접근</h3>
          </div>
          <p className="text-sm text-gray-300 font-medium">
            {insights.defensive_approach.description}
          </p>
        </div>
      </div>

      {/* Insights Section */}
      <div className="bg-dark-card/50 border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <span>📊</span>
          경기 분석
        </h3>
        <div className="space-y-3">
          {insights.insights.map((insight, index) => (
            <div
              key={index}
              className="flex items-start gap-3 p-3 bg-chart-blue/10 border border-chart-blue/20 rounded-lg hover:bg-chart-blue/15 transition-colors"
            >
              <div className="flex-shrink-0 w-6 h-6 bg-chart-blue text-white rounded-full flex items-center justify-center text-xs font-bold">
                {index + 1}
              </div>
              <p className="text-sm text-gray-200 leading-relaxed">{insight}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations Section */}
      <div className="bg-gradient-to-r from-chart-yellow/10 to-chart-orange/10 border border-chart-yellow/30 rounded-lg p-6">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <span>💡</span>
          전술 추천
        </h3>
        <div className="space-y-3">
          {insights.recommendations.map((recommendation, index) => (
            <div
              key={index}
              className="flex items-start gap-3 p-3 bg-dark-card/50 border border-chart-yellow/20 rounded-lg hover:bg-dark-card/70 transition-colors"
            >
              <span className="flex-shrink-0 text-chart-yellow text-lg">💡</span>
              <p className="text-sm text-gray-200 leading-relaxed">{recommendation}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TacticalInsightsPanel;
