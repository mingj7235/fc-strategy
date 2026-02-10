import React from 'react';
import type { LocationStats } from '../../types/match';

interface BoxLocationAnalysisProps {
  insideBox: LocationStats;
  outsideBox: LocationStats;
}

const BoxLocationAnalysis: React.FC<BoxLocationAnalysisProps> = ({
  insideBox,
  outsideBox,
}) => {
  const totalShots = insideBox.shots + outsideBox.shots;
  const insidePercentage = totalShots > 0 ? Math.round((insideBox.shots / totalShots) * 100) : 0;
  const outsidePercentage = totalShots > 0 ? Math.round((outsideBox.shots / totalShots) * 100) : 0;

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">📍</span>
        박스 위치별 분석
      </h3>

      {/* Overall distribution */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>박스 내: {insidePercentage}%</span>
          <span>박스 외: {outsidePercentage}%</span>
        </div>
        <div className="flex w-full h-3 rounded-full overflow-hidden">
          <div
            className="bg-chart-green transition-all"
            style={{ width: `${insidePercentage}%` }}
          ></div>
          <div
            className="bg-chart-blue transition-all"
            style={{ width: `${outsidePercentage}%` }}
          ></div>
        </div>
      </div>

      {/* Detailed comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Inside Box */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-green/50 transition-colors">
          <div className="text-center mb-3">
            <div className="text-lg font-bold text-chart-green">박스 내 슈팅</div>
            <div className="text-3xl font-bold text-white mt-1">{insideBox.shots}회</div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">골</span>
              <span className="text-sm font-bold text-white">{insideBox.goals}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">유효슈팅</span>
              <span className="text-sm font-bold text-white">{insideBox.on_target}</span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-dark-border">
              <span className="text-sm text-gray-400">성공률</span>
              <span className="text-sm font-bold text-chart-green">
                {insideBox.success_rate}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">골 전환율</span>
              <span className="text-sm font-bold text-chart-yellow">
                {insideBox.conversion_rate}%
              </span>
            </div>
          </div>
        </div>

        {/* Outside Box */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-blue/50 transition-colors">
          <div className="text-center mb-3">
            <div className="text-lg font-bold text-chart-blue">박스 외 슈팅</div>
            <div className="text-3xl font-bold text-white mt-1">{outsideBox.shots}회</div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">골</span>
              <span className="text-sm font-bold text-white">{outsideBox.goals}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">유효슈팅</span>
              <span className="text-sm font-bold text-white">{outsideBox.on_target}</span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-dark-border">
              <span className="text-sm text-gray-400">성공률</span>
              <span className="text-sm font-bold text-chart-green">
                {outsideBox.success_rate}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">골 전환율</span>
              <span className="text-sm font-bold text-chart-yellow">
                {outsideBox.conversion_rate}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation */}
      <div className="mt-4 p-3 bg-dark-bg rounded-lg">
        <div className="text-xs text-gray-400">
          {insidePercentage >= 60 ? (
            <span className="text-chart-green">✓ 박스 침투가 좋습니다!</span>
          ) : insidePercentage < 40 ? (
            <span className="text-chart-yellow">⚠️ 박스 안으로 더 침투해보세요</span>
          ) : (
            <span className="text-gray-300">적절한 슈팅 위치 선택입니다</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default BoxLocationAnalysis;
