import React from 'react';

interface PassTypeInsightsProps {
  insights: string[];
  diversityScore: number;
}

const PassTypeInsights: React.FC<PassTypeInsightsProps> = ({ insights, diversityScore }) => {
  // Get diversity score color and description
  const getDiversityColor = (score: number) => {
    if (score >= 70) return 'text-chart-green';
    if (score >= 40) return 'text-chart-yellow';
    return 'text-chart-red';
  };

  const getDiversityBadge = (score: number) => {
    if (score >= 70) return '🌟 우수';
    if (score >= 40) return '⚠️ 보통';
    return '❌ 낮음';
  };

  return (
    <div className="space-y-4">
      {/* Diversity Score Card */}
      <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          패스 다양성 점수
        </h3>

        <div className="flex items-center justify-between mb-4">
          <div>
            <div className={`text-5xl font-bold ${getDiversityColor(diversityScore)}`}>
              {diversityScore}
            </div>
            <div className="text-sm text-gray-400 mt-1">100점 만점</div>
          </div>
          <div className="text-right">
            <div className="text-3xl mb-1">{getDiversityBadge(diversityScore)}</div>
            <div className="text-sm text-gray-400">다양성 등급</div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-dark-bg rounded-full h-4">
          <div
            className={`h-4 rounded-full transition-all ${
              diversityScore >= 70
                ? 'bg-gradient-to-r from-chart-green to-chart-blue'
                : diversityScore >= 40
                ? 'bg-gradient-to-r from-chart-yellow to-chart-green'
                : 'bg-gradient-to-r from-chart-red to-chart-yellow'
            }`}
            style={{ width: `${diversityScore}%` }}
          ></div>
        </div>

        <div className="mt-4 p-3 bg-dark-bg rounded-lg">
          <p className="text-xs text-gray-300">
            {diversityScore >= 70
              ? '✨ 다양한 패스 타입을 골고루 사용하여 상대를 예측하기 어렵게 만듭니다!'
              : diversityScore >= 40
              ? '💡 패스 다양성을 높이면 공격 패턴이 더 예측 불가능해집니다.'
              : '⚠️ 한 가지 패스 타입에만 의존하고 있습니다. 다양한 패스를 시도해보세요.'}
          </p>
        </div>
      </div>

      {/* Expert Insights */}
      {insights.length > 0 && (
        <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">💡</span>
            전문가 인사이트
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

      {/* Tips */}
      <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">📚</span>
          패스 개선 팁
        </h3>

        <div className="space-y-3 text-sm text-gray-300">
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>짧은 패스로 안전하게 점유율을 높이고, 긴 패스로 측면을 공략하세요</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>스루 패스는 수비수 뒷공간이 열렸을 때 효과적입니다</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>상대 압박이 심할 때는 롱 패스로 템포를 바꿔보세요</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>다양한 패스 타입을 섞어 사용하면 상대가 예측하기 어려워집니다</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PassTypeInsights;
