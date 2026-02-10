import React from 'react';

interface HeadingInsightsProps {
  insights: string[];
}

const HeadingInsights: React.FC<HeadingInsightsProps> = ({ insights }) => {
  return (
    <div className="space-y-4">
      {/* Expert Insights */}
      {insights.length > 0 && (
        <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">💡</span>
            헤딩 전문가 인사이트
          </h3>

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
        </div>
      )}

      {/* Heading Tips */}
      <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">📚</span>
          헤딩 개선 팁
        </h3>

        <div className="space-y-3 text-sm text-gray-300">
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>크로스는 수비수와 골키퍼 사이 공간을 노리세요</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>헤딩 슈팅 전에 골대 반대편으로 움직여 각도를 만드세요</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>코너킥에서는 니어 포스트와 파 포스트에 선수를 배치하세요</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>키가 크고 헤딩 능력이 좋은 선수를 타겟맨으로 활용하세요</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>측면 공격수가 크로스 올릴 때 스트라이커가 박스로 침투하세요</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeadingInsights;
