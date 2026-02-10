import React from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

interface ComparisonData {
  possession: number;
  shots: number;
  shots_on_target: number;
  pass_success_rate: number;
  goals: number;
}

interface StatComparisonChartProps {
  winPatterns: ComparisonData;
  lossPatterns: ComparisonData;
}

const StatComparisonChart: React.FC<StatComparisonChartProps> = ({
  winPatterns,
  lossPatterns,
}) => {
  // Normalize data to 0-100 scale for better visualization
  const normalizeValue = (value: number, max: number) => {
    return (value / max) * 100;
  };

  const data = [
    {
      stat: '점유율',
      승리: winPatterns.possession,
      패배: lossPatterns.possession,
    },
    {
      stat: '슈팅',
      승리: normalizeValue(winPatterns.shots, 20), // Assume max 20 shots
      패배: normalizeValue(lossPatterns.shots, 20),
    },
    {
      stat: '유효슈팅',
      승리: normalizeValue(winPatterns.shots_on_target, 15), // Assume max 15 on target
      패배: normalizeValue(lossPatterns.shots_on_target, 15),
    },
    {
      stat: '패스성공',
      승리: winPatterns.pass_success_rate,
      패배: lossPatterns.pass_success_rate,
    },
    {
      stat: '득점',
      승리: normalizeValue(winPatterns.goals, 5), // Assume max 5 goals
      패배: normalizeValue(lossPatterns.goals, 5),
    },
  ];

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">승리 vs 패배 패턴</h3>
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis dataKey="stat" stroke="#6b7280" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#6b7280" />
          <Radar
            name="승리 시"
            dataKey="승리"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.5}
            strokeWidth={2}
          />
          <Radar
            name="패배 시"
            dataKey="패배"
            stroke="#ef4444"
            fill="#ef4444"
            fillOpacity={0.5}
            strokeWidth={2}
          />
          <Legend
            wrapperStyle={{
              paddingTop: '20px',
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
            }}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Insights */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">패턴 분석</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          {winPatterns.possession > lossPatterns.possession + 5 && (
            <li>✓ 점유율이 높을 때 승률이 더 좋습니다</li>
          )}
          {winPatterns.shots > lossPatterns.shots && (
            <li>✓ 승리한 경기에서 슈팅 시도가 더 많습니다</li>
          )}
          {winPatterns.pass_success_rate > lossPatterns.pass_success_rate && (
            <li>✓ 패스 정확도가 승리의 핵심 요소입니다</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default StatComparisonChart;
