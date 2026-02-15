import React from 'react';
import type { ControllerRecommendation as ControllerRecommendationType } from '../../types/match';

interface ControllerRecommendationProps {
  recommendation: ControllerRecommendationType;
}

const ControllerRecommendation: React.FC<ControllerRecommendationProps> = ({ recommendation }) => {
  const getControllerIcon = (controller: string | null) => {
    if (controller === 'keyboard') return '⌨️';
    if (controller === 'gamepad') return '🎮';
    return '⚖️';
  };

  const getControllerName = (controller: string | null) => {
    if (controller === 'keyboard') return '키보드';
    if (controller === 'gamepad') return '패드';
    if (controller === 'either') return '둘 다 괜찮음';
    return '데이터 부족';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 70) return 'text-chart-green';
    if (confidence >= 40) return 'text-chart-yellow';
    return 'text-gray-400';
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 70) return '높음';
    if (confidence >= 40) return '보통';
    if (confidence > 0) return '낮음';
    return '없음';
  };

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">💡</span>
        컨트롤러 추천
      </h3>

      <div className="text-center mb-6">
        <div className="text-6xl mb-4">
          {getControllerIcon(recommendation.recommended_controller)}
        </div>
        <div className="text-3xl font-bold text-white mb-2">
          {getControllerName(recommendation.recommended_controller)}
        </div>
        {recommendation.confidence > 0 && (
          <div className={`text-lg ${getConfidenceColor(recommendation.confidence)}`}>
            신뢰도: {recommendation.confidence}% ({getConfidenceBadge(recommendation.confidence)})
          </div>
        )}
      </div>

      {/* Reason */}
      <div className="bg-dark-bg border-l-4 border-accent-primary p-4 rounded">
        <p className="text-sm text-gray-300 leading-relaxed">{recommendation.reason}</p>
      </div>

      {/* Confidence Meter */}
      {recommendation.confidence > 0 && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>신뢰도</span>
            <span>{recommendation.confidence}%</span>
          </div>
          <div className="w-full bg-dark-bg rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                recommendation.confidence >= 70
                  ? 'bg-gradient-to-r from-chart-green to-chart-blue'
                  : recommendation.confidence >= 40
                  ? 'bg-gradient-to-r from-chart-yellow to-chart-green'
                  : 'bg-gradient-to-r from-chart-red to-chart-yellow'
              }`}
              style={{ width: `${recommendation.confidence}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="mt-6 p-4 bg-dark-card rounded-lg">
        <div className="text-xs text-gray-300 space-y-2">
          <div className="flex items-start gap-2">
            <span className="text-chart-green">💡</span>
            <p>컨트롤러 선택은 개인 선호도가 중요합니다. 편한 것을 사용하세요.</p>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-chart-blue">📊</span>
            <p>각 컨트롤러로 충분한 경기를 플레이해야 정확한 분석이 가능합니다.</p>
          </div>
          {recommendation.recommended_controller && recommendation.confidence >= 70 && (
            <div className="flex items-start gap-2">
              <span className="text-chart-yellow">⚡</span>
              <p>현재 데이터 기준으로는 {getControllerName(recommendation.recommended_controller)}를 추천합니다!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ControllerRecommendation;
