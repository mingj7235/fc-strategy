import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import type { PassTypeBreakdown } from '../../types/match';

interface PassTypeRadarChartProps {
  passBreakdown: PassTypeBreakdown[];
}

const PassTypeRadarChart: React.FC<PassTypeRadarChartProps> = ({ passBreakdown }) => {
  // Transform data for radar chart
  const chartData = passBreakdown.map((pass) => ({
    type: pass.type_name,
    성공률: pass.success_rate,
    시도: Math.min(pass.attempts, 100), // Cap at 100 for visualization
  }));

  if (passBreakdown.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p>패스 타입 데이터가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">📊</span>
        패스 타입별 성공률 레이더 차트
      </h3>

      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={chartData}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis
            dataKey="type"
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#9CA3AF', fontSize: 10 }}
          />
          <Radar
            name="성공률"
            dataKey="성공률"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.6}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#F3F4F6',
            }}
            formatter={(value: number | undefined) => (value != null ? `${value}%` : '') as unknown as [string, string]}
          />
          <Legend
            wrapperStyle={{ color: '#9CA3AF' }}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Legend for pass types */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
        {passBreakdown.map((pass, index) => (
          <div
            key={index}
            className="flex items-center justify-between bg-dark-bg p-2 rounded"
          >
            <span className="text-gray-300">{pass.type_name}</span>
            <span className="text-chart-blue font-bold">{pass.success_rate}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PassTypeRadarChart;
