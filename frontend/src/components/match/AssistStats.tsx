import React from 'react';
import type { AssistTypes, AssistDistanceStats } from '../../types/match';

interface AssistStatsProps {
  assistTypes: AssistTypes;
  distanceStats: AssistDistanceStats;
  totalGoals: number;
  goalsWithAssist: number;
}

const AssistStats: React.FC<AssistStatsProps> = ({
  assistTypes,
  distanceStats,
  totalGoals,
  goalsWithAssist,
}) => {
  const assistPercentage = totalGoals > 0 ? Math.round((goalsWithAssist / totalGoals) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Overall Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-blue/50 transition-colors">
          <div className="text-sm text-gray-400 mb-1">총 골</div>
          <div className="text-3xl font-bold text-chart-blue">{totalGoals}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-green/50 transition-colors">
          <div className="text-sm text-gray-400 mb-1">어시스트골</div>
          <div className="text-3xl font-bold text-chart-green">{goalsWithAssist}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-yellow/50 transition-colors">
          <div className="text-sm text-gray-400 mb-1">어시스트율</div>
          <div className="text-3xl font-bold text-chart-yellow">{assistPercentage}%</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-purple/50 transition-colors">
          <div className="text-sm text-gray-400 mb-1">개인골</div>
          <div className="text-3xl font-bold text-chart-purple">{totalGoals - goalsWithAssist}</div>
        </div>
      </div>

      {/* Assist Types */}
      <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">📍</span>
          어시스트 타입 분석
        </h3>
        <div className="space-y-4">
          {/* Wing vs Central */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-400">측면 어시스트</span>
              <span className="text-sm font-bold text-chart-blue">
                {assistTypes.wing_assists} ({assistTypes.wing_percentage}%)
              </span>
            </div>
            <div className="w-full bg-dark-card rounded-full h-3">
              <div
                className="bg-chart-blue h-3 rounded-full transition-all"
                style={{ width: `${assistTypes.wing_percentage}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-400">중앙 어시스트</span>
              <span className="text-sm font-bold text-chart-green">
                {assistTypes.central_assists} ({assistTypes.central_percentage}%)
              </span>
            </div>
            <div className="w-full bg-dark-card rounded-full h-3">
              <div
                className="bg-chart-green h-3 rounded-full transition-all"
                style={{ width: `${assistTypes.central_percentage}%` }}
              ></div>
            </div>
          </div>

          {/* Deep vs Forward */}
          <div className="pt-4 border-t border-dark-border">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <div className="text-sm text-gray-400 mb-1">후방 지원</div>
                <div className="text-2xl font-bold text-white">{assistTypes.deep_assists}</div>
              </div>
              <div>
                <div className="text-sm text-gray-400 mb-1">전방 지원</div>
                <div className="text-2xl font-bold text-white">{assistTypes.forward_assists}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Distance Stats */}
      <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">📏</span>
          어시스트 거리 통계
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-dark-card border border-dark-border rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">평균 거리</div>
            <div className="text-xl font-bold text-chart-blue">
              {distanceStats.avg_distance.toFixed(3)}
            </div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">최대 거리</div>
            <div className="text-xl font-bold text-chart-yellow">
              {distanceStats.max_distance.toFixed(3)}
            </div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">최소 거리</div>
            <div className="text-xl font-bold text-chart-green">
              {distanceStats.min_distance.toFixed(3)}
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-dark-border grid grid-cols-2 gap-4 text-center">
          <div>
            <div className="text-sm text-gray-400 mb-1">짧은 패스</div>
            <div className="text-2xl font-bold text-white">{distanceStats.short_passes}</div>
            <div className="text-xs text-gray-500 mt-1">거리 &lt; 0.2</div>
          </div>
          <div>
            <div className="text-sm text-gray-400 mb-1">긴 패스</div>
            <div className="text-2xl font-bold text-white">{distanceStats.long_passes}</div>
            <div className="text-xs text-gray-500 mt-1">거리 &gt; 0.4</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssistStats;
