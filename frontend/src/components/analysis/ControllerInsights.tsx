import React from 'react';

interface ControllerInsightsProps {
  insights: string[];
  matchesAnalyzed: number;
}

const ControllerInsights: React.FC<ControllerInsightsProps> = ({ insights, matchesAnalyzed }) => {
  if (insights.length === 0) {
    return (
      <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">💭</span>
          인사이트
        </h3>
        <div className="text-center py-8 text-gray-400">
          <p>인사이트를 생성하기 위한 데이터가 부족합니다.</p>
          <p className="text-sm mt-2">두 가지 컨트롤러로 각각 최소 5경기 이상 플레이하세요.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">💡</span>
        전문가 인사이트
      </h3>

      <div className="mb-4 text-sm text-gray-400">
        {matchesAnalyzed}경기 데이터 분석 결과
      </div>

      <div className="space-y-3">
        {insights.map((insight, index) => (
          <div
            key={index}
            className="bg-dark-bg border-l-4 border-accent-primary p-4 rounded hover:border-chart-blue transition-colors"
          >
            <p className="text-sm text-gray-300 leading-relaxed">{insight}</p>
          </div>
        ))}
      </div>

      {/* Additional Tips */}
      <div className="mt-6 p-4 bg-dark-card rounded-lg">
        <div className="text-xs font-bold text-white mb-2">📚 컨트롤러 활용 팁</div>
        <div className="space-y-2 text-xs text-gray-300">
          <div className="flex items-start gap-2">
            <span className="text-chart-green">✓</span>
            <p>키보드는 정확한 조작이 필요한 패스 플레이에 유리할 수 있습니다</p>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-chart-green">✓</span>
            <p>패드는 드리블과 방향 전환이 부드러운 것이 장점입니다</p>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-chart-green">✓</span>
            <p>자신에게 맞는 컨트롤러를 찾으면 일관성 있는 플레이가 가능합니다</p>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-chart-green">✓</span>
            <p>각 컨트롤러의 장단점을 이해하고 상황에 맞게 활용해보세요</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ControllerInsights;
