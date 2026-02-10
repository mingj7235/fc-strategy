import React from 'react';
import type { ShotTypeBreakdown as ShotTypeBreakdownType } from '../../types/match';

interface ShotTypeBreakdownProps {
  typeBreakdown: ShotTypeBreakdownType[];
}

const ShotTypeBreakdown: React.FC<ShotTypeBreakdownProps> = ({ typeBreakdown }) => {
  if (typeBreakdown.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p>슈팅 타입 데이터가 없습니다.</p>
      </div>
    );
  }

  // Get max values for progress bars
  const maxShots = Math.max(...typeBreakdown.map(t => t.shots));

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">⚽</span>
        슈팅 타입별 분석
      </h3>

      <div className="space-y-4">
        {typeBreakdown.map((type, index) => (
          <div
            key={index}
            className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-blue/50 transition-colors"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="text-lg font-bold text-white">{type.type_name}</div>
                <div className="text-sm text-gray-400">
                  {type.shots}회
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-xs text-gray-400">성공률</div>
                  <div className="text-lg font-bold text-chart-green">
                    {type.success_rate}%
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-400">골 전환율</div>
                  <div className="text-lg font-bold text-chart-yellow">
                    {type.conversion_rate}%
                  </div>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3 text-center text-sm mb-3">
              <div>
                <div className="text-gray-400">슈팅</div>
                <div className="text-white font-bold">{type.shots}</div>
              </div>
              <div>
                <div className="text-gray-400">유효슈팅</div>
                <div className="text-white font-bold">{type.on_target}</div>
              </div>
              <div>
                <div className="text-gray-400">골</div>
                <div className="text-white font-bold">{type.goals}</div>
              </div>
            </div>

            {/* Progress bar */}
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>슈팅 비율</span>
                  <span>{Math.round(type.shots / maxShots * 100)}%</span>
                </div>
                <div className="w-full bg-dark-bg rounded-full h-2">
                  <div
                    className="bg-chart-blue h-2 rounded-full transition-all"
                    style={{ width: `${(type.shots / maxShots) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ShotTypeBreakdown;
