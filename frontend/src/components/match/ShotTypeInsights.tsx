import React from 'react';
import type { PostHitsAnalysis } from '../../types/match';

interface ShotTypeInsightsProps {
  insights: string[];
  postHits: PostHitsAnalysis;
}

const ShotTypeInsights: React.FC<ShotTypeInsightsProps> = ({ insights, postHits }) => {
  return (
    <div className="space-y-4">
      {/* Post Hits Warning */}
      {postHits.post_hit_count > 0 && (
        <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">⚠️</span>
            골대 맞춤
          </h3>

          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-3xl font-bold text-chart-yellow">
                {postHits.post_hit_count}회
              </div>
              <div className="text-sm text-gray-400 mt-1">
                골대/크로스바 맞춤
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-chart-yellow">
                {postHits.unlucky_factor}%
              </div>
              <div className="text-sm text-gray-400 mt-1">
                불운 지수
              </div>
            </div>
          </div>

          {postHits.post_hit_count >= 3 && (
            <div className="bg-dark-bg border-l-4 border-chart-yellow p-3 rounded">
              <p className="text-sm text-gray-300">
                골대를 {postHits.post_hit_count}번이나 맞췄습니다.
                운이 따르지 않았지만, 좋은 위치에서 슈팅하고 있다는 증거입니다!
              </p>
            </div>
          )}
        </div>
      )}

      {/* Insights */}
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
          슈팅 개선 팁
        </h3>

        <div className="space-y-3 text-sm text-gray-300">
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>박스 내에서 슈팅 기회를 만들면 골 전환율이 크게 높아집니다</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>헤딩 슈팅은 크로스 타이밍과 위치 선정이 중요합니다</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>박스 외곽 슈팅은 상대 수비가 밀집되었을 때 효과적입니다</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-chart-green mt-1">✓</span>
            <p>골대를 자주 맞춘다면 파워보다 정확도에 집중해보세요</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShotTypeInsights;
