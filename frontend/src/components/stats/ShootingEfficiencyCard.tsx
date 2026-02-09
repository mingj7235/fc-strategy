import React from 'react';
import type { ShootingEfficiencyTrend } from '../../types/match';

interface ShootingEfficiencyCardProps {
  efficiency: ShootingEfficiencyTrend;
}

const ShootingEfficiencyCard: React.FC<ShootingEfficiencyCardProps> = ({ efficiency }) => {
  const getEfficiencyColor = (rate: number) => {
    if (rate >= 20) return 'text-chart-green';
    if (rate >= 10) return 'text-chart-blue';
    if (rate >= 5) return 'text-chart-yellow';
    return 'text-chart-red';
  };

  const getAccuracyColor = (rate: number) => {
    if (rate >= 60) return 'text-chart-green';
    if (rate >= 45) return 'text-chart-blue';
    if (rate >= 30) return 'text-chart-yellow';
    return 'text-chart-red';
  };

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">⚽</span>
        슈팅 효율성 통계
      </h3>

      {/* Main Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-1">총 슈팅</div>
          <div className="text-2xl font-bold text-white">{efficiency.total_shots}</div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-1">총 골</div>
          <div className="text-2xl font-bold text-chart-green">{efficiency.total_goals}</div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-1">전환율</div>
          <div className={`text-2xl font-bold ${getEfficiencyColor(efficiency.overall_conversion)}`}>
            {efficiency.overall_conversion}%
          </div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-1">정확도</div>
          <div className={`text-2xl font-bold ${getAccuracyColor(efficiency.accuracy)}`}>
            {efficiency.accuracy}%
          </div>
        </div>
      </div>

      {/* Inside vs Outside Box */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Inside Box */}
        <div className="bg-dark-bg p-4 rounded-lg">
          <div className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <span className="text-chart-green">📍</span>
            박스 안
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">슈팅</span>
              <span className="text-white font-bold">{efficiency.inside_box_shots}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">골</span>
              <span className="text-chart-green font-bold">{efficiency.inside_box_goals}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">전환율</span>
              <span className={`font-bold ${getEfficiencyColor(efficiency.inside_box_efficiency)}`}>
                {efficiency.inside_box_efficiency}%
              </span>
            </div>
          </div>
          <div className="mt-3 w-full bg-dark-card rounded-full h-2">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-chart-green to-chart-blue"
              style={{ width: `${Math.min(efficiency.inside_box_efficiency * 3, 100)}%` }}
            />
          </div>
        </div>

        {/* Outside Box */}
        <div className="bg-dark-bg p-4 rounded-lg">
          <div className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <span className="text-chart-blue">📍</span>
            박스 밖
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">슈팅</span>
              <span className="text-white font-bold">{efficiency.outside_box_shots}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">골</span>
              <span className="text-chart-green font-bold">{efficiency.outside_box_goals}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">전환율</span>
              <span className={`font-bold ${getEfficiencyColor(efficiency.outside_box_efficiency)}`}>
                {efficiency.outside_box_efficiency}%
              </span>
            </div>
          </div>
          <div className="mt-3 w-full bg-dark-card rounded-full h-2">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-chart-purple to-chart-yellow"
              style={{ width: `${Math.min(efficiency.outside_box_efficiency * 10, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Insights */}
      {efficiency.inside_box_efficiency > efficiency.outside_box_efficiency * 2 && (
        <div className="mt-4 p-3 bg-accent-success/10 border border-accent-success/30 rounded-lg">
          <p className="text-sm text-accent-success">
            💡 박스 안에서의 마무리 능력이 우수합니다! 박스 침투를 계속 활용하세요.
          </p>
        </div>
      )}

      {efficiency.outside_box_efficiency > efficiency.inside_box_efficiency && (
        <div className="mt-4 p-3 bg-chart-blue/10 border border-chart-blue/30 rounded-lg">
          <p className="text-sm text-chart-blue">
            🎯 중거리 슈팅이 효과적입니다! 하지만 박스 침투로 더 높은 전환율을 노려보세요.
          </p>
        </div>
      )}

      {efficiency.overall_conversion < 10 && (
        <div className="mt-4 p-3 bg-chart-yellow/10 border border-chart-yellow/30 rounded-lg">
          <p className="text-sm text-chart-yellow">
            ⚠️ 슈팅 전환율이 낮습니다. 더 좋은 위치에서 슈팅하거나, 골키퍼 반대편으로 슈팅하세요.
          </p>
        </div>
      )}
    </div>
  );
};

export default ShootingEfficiencyCard;
