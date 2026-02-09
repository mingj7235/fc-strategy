import React from 'react';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';
import type { PassTypeDistribution } from '../../types/match';

interface PassDistributionRadarProps {
  distribution: PassTypeDistribution;
}

const PassDistributionRadar: React.FC<PassDistributionRadarProps> = ({ distribution }) => {
  // Prepare radar chart data
  const radarData = [
    {
      category: '짧은 패스',
      value: distribution.avg_short_pass_rate,
      fullMark: 100
    },
    {
      category: '긴 패스',
      value: distribution.avg_long_pass_rate,
      fullMark: 100
    },
    {
      category: '스루 패스',
      value: distribution.avg_through_pass_rate,
      fullMark: 100
    }
  ];

  const getRateColor = (rate: number) => {
    if (rate >= 80) return 'text-chart-green';
    if (rate >= 70) return 'text-chart-blue';
    if (rate >= 60) return 'text-chart-yellow';
    return 'text-chart-red';
  };

  const getRateGrade = (rate: number) => {
    if (rate >= 85) return 'S';
    if (rate >= 75) return 'A';
    if (rate >= 65) return 'B';
    if (rate >= 55) return 'C';
    return 'D';
  };

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">🎯</span>
        패스 타입별 평균 성공률
      </h3>

      <div className="text-xs text-gray-400 mb-6 text-center">
        {distribution.matches_analyzed}경기 평균 데이터
      </div>

      {/* Radar Chart */}
      <div className="mb-6">
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#374151" />
            <PolarAngleAxis
              dataKey="category"
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 10 }}
            />
            <Radar
              name="성공률"
              dataKey="value"
              stroke="#60A5FA"
              fill="#60A5FA"
              fillOpacity={0.6}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '0.5rem'
              }}
              formatter={(value: any) => [`${value.toFixed(1)}%`, '성공률']}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Short Pass */}
        <div className="bg-dark-bg p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">짧은 패스</span>
            <span className={`text-lg font-bold ${getRateColor(distribution.avg_short_pass_rate)}`}>
              {getRateGrade(distribution.avg_short_pass_rate)}
            </span>
          </div>
          <div className={`text-2xl font-bold ${getRateColor(distribution.avg_short_pass_rate)} mb-2`}>
            {distribution.avg_short_pass_rate.toFixed(1)}%
          </div>
          <div className="w-full bg-dark-card rounded-full h-2">
            <div
              className="h-2 rounded-full bg-chart-green"
              style={{ width: `${distribution.avg_short_pass_rate}%` }}
            />
          </div>
        </div>

        {/* Long Pass */}
        <div className="bg-dark-bg p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">긴 패스</span>
            <span className={`text-lg font-bold ${getRateColor(distribution.avg_long_pass_rate)}`}>
              {getRateGrade(distribution.avg_long_pass_rate)}
            </span>
          </div>
          <div className={`text-2xl font-bold ${getRateColor(distribution.avg_long_pass_rate)} mb-2`}>
            {distribution.avg_long_pass_rate.toFixed(1)}%
          </div>
          <div className="w-full bg-dark-card rounded-full h-2">
            <div
              className="h-2 rounded-full bg-chart-blue"
              style={{ width: `${distribution.avg_long_pass_rate}%` }}
            />
          </div>
        </div>

        {/* Through Pass */}
        <div className="bg-dark-bg p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">스루 패스</span>
            <span className={`text-lg font-bold ${getRateColor(distribution.avg_through_pass_rate)}`}>
              {getRateGrade(distribution.avg_through_pass_rate)}
            </span>
          </div>
          <div className={`text-2xl font-bold ${getRateColor(distribution.avg_through_pass_rate)} mb-2`}>
            {distribution.avg_through_pass_rate.toFixed(1)}%
          </div>
          <div className="w-full bg-dark-card rounded-full h-2">
            <div
              className="h-2 rounded-full bg-chart-purple"
              style={{ width: `${distribution.avg_through_pass_rate}%` }}
            />
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="space-y-2">
        {distribution.avg_short_pass_rate >= 85 && (
          <div className="p-3 bg-chart-green/10 border border-chart-green/30 rounded-lg">
            <p className="text-sm text-chart-green">
              ✅ 짧은 패스 성공률이 매우 우수합니다! 안정적인 빌드업이 가능합니다.
            </p>
          </div>
        )}

        {distribution.avg_long_pass_rate >= 70 && (
          <div className="p-3 bg-chart-blue/10 border border-chart-blue/30 rounded-lg">
            <p className="text-sm text-chart-blue">
              💪 긴 패스 성공률이 우수합니다! 측면 전환 플레이를 적극 활용하세요.
            </p>
          </div>
        )}

        {distribution.avg_through_pass_rate >= 65 && (
          <div className="p-3 bg-chart-purple/10 border border-chart-purple/30 rounded-lg">
            <p className="text-sm text-chart-purple">
              🎯 스루 패스 성공률이 우수합니다! 침투 패스로 수비를 뚫어보세요.
            </p>
          </div>
        )}

        {distribution.avg_short_pass_rate < 75 && (
          <div className="p-3 bg-chart-yellow/10 border border-chart-yellow/30 rounded-lg">
            <p className="text-sm text-chart-yellow">
              ⚠️ 짧은 패스 성공률이 낮습니다. 무리한 패스보다는 안전한 선택지를 고려하세요.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PassDistributionRadar;
