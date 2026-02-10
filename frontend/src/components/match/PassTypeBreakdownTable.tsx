import React from 'react';
import type { PassTypeBreakdown, TotalPassStats } from '../../types/match';

interface PassTypeBreakdownTableProps {
  passBreakdown: PassTypeBreakdown[];
  totalStats: TotalPassStats;
}

const PassTypeBreakdownTable: React.FC<PassTypeBreakdownTableProps> = ({
  passBreakdown,
  totalStats,
}) => {
  if (passBreakdown.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p>패스 타입 데이터가 없습니다.</p>
      </div>
    );
  }

  // Get success rate color
  const getSuccessRateColor = (rate: number) => {
    if (rate >= 80) return 'text-chart-green';
    if (rate >= 60) return 'text-chart-yellow';
    return 'text-chart-red';
  };

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">📋</span>
        패스 타입별 상세 통계
      </h3>

      {/* Total Stats */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        <div className="bg-dark-bg border border-dark-border rounded-lg p-4 text-center">
          <div className="text-sm text-gray-400 mb-1">총 패스 시도</div>
          <div className="text-2xl font-bold text-white">{totalStats.total_attempts}</div>
        </div>
        <div className="bg-dark-bg border border-dark-border rounded-lg p-4 text-center">
          <div className="text-sm text-gray-400 mb-1">성공한 패스</div>
          <div className="text-2xl font-bold text-chart-green">{totalStats.total_success}</div>
        </div>
        <div className="bg-dark-bg border border-dark-border rounded-lg p-4 text-center">
          <div className="text-sm text-gray-400 mb-1">전체 성공률</div>
          <div className="text-2xl font-bold text-chart-blue">
            {totalStats.overall_success_rate}%
          </div>
        </div>
      </div>

      {/* Breakdown Table */}
      <div className="space-y-3">
        {passBreakdown.map((pass, index) => (
          <div
            key={index}
            className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-blue/50 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="text-lg font-bold text-white">{pass.type_name}</div>
              <div className={`text-2xl font-bold ${getSuccessRateColor(pass.success_rate)}`}>
                {pass.success_rate}%
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">시도</span>
                <span className="text-white font-bold">{pass.attempts}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">성공</span>
                <span className="text-chart-green font-bold">{pass.success}</span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-3">
              <div className="w-full bg-dark-bg rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    pass.success_rate >= 80
                      ? 'bg-chart-green'
                      : pass.success_rate >= 60
                      ? 'bg-chart-yellow'
                      : 'bg-chart-red'
                  }`}
                  style={{ width: `${pass.success_rate}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PassTypeBreakdownTable;
