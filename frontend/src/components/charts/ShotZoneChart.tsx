import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ZoneData {
  zone: string;
  shots: number;
  goals: number;
  efficiency: number;
}

interface ShotZoneChartProps {
  zoneAnalysis: {
    inside_box: { shots: number; goals: number; efficiency: number };
    outside_box: { shots: number; goals: number; efficiency: number };
    center: { shots: number; goals: number; efficiency: number };
    side: { shots: number; goals: number; efficiency: number };
  };
}

const ShotZoneChart: React.FC<ShotZoneChartProps> = ({ zoneAnalysis }) => {
  const data: ZoneData[] = [
    {
      zone: '박스 안',
      shots: zoneAnalysis.inside_box.shots,
      goals: zoneAnalysis.inside_box.goals,
      efficiency: zoneAnalysis.inside_box.efficiency,
    },
    {
      zone: '박스 밖',
      shots: zoneAnalysis.outside_box.shots,
      goals: zoneAnalysis.outside_box.goals,
      efficiency: zoneAnalysis.outside_box.efficiency,
    },
    {
      zone: '중앙',
      shots: zoneAnalysis.center.shots,
      goals: zoneAnalysis.center.goals,
      efficiency: zoneAnalysis.center.efficiency,
    },
    {
      zone: '측면',
      shots: zoneAnalysis.side.shots,
      goals: zoneAnalysis.side.goals,
      efficiency: zoneAnalysis.side.efficiency,
    },
  ];

  const COLORS = ['#3b82f6', '#22c55e'];

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">구역별 슈팅 분석</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="zone" stroke="#6b7280" />
          <YAxis stroke="#6b7280" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
            }}
            formatter={(value: number | undefined, name: string | undefined) => {
              if (name === 'efficiency') {
                return [`${(value || 0).toFixed(1)}%`, '효율성'];
              }
              return [value || 0, name === 'shots' ? '슈팅' : '골'];
            }}
          />
          <Legend
            formatter={(value: string) => {
              switch (value) {
                case 'shots':
                  return '슈팅';
                case 'goals':
                  return '골';
                default:
                  return value;
              }
            }}
          />
          <Bar dataKey="shots" fill={COLORS[0]} radius={[8, 8, 0, 0]} />
          <Bar dataKey="goals" fill={COLORS[1]} radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      {/* Efficiency Row */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        {data.map((zone, idx) => (
          <div key={idx} className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">{zone.zone} 효율</div>
            <div className="text-xl font-bold text-blue-600">{zone.efficiency.toFixed(1)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ShotZoneChart;
