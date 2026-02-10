import React from 'react';
import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

interface RadarChartProps {
  data: {
    // New position-aware format
    values?: Record<string, number>;
    labels?: Record<string, string>;
    // Legacy flat format (backward compat)
    form?: number;
    efficiency?: number;
    consistency?: number;
    goal_threat?: number;
    creativity?: number;
    impact?: number;
  };
}

const LEGACY_LABELS: Record<string, string> = {
  form: '폼',
  efficiency: '효율성',
  consistency: '일관성',
  goal_threat: '득점력',
  creativity: '창조력',
  impact: '영향력',
};

const RadarChart: React.FC<RadarChartProps> = ({ data }) => {
  let chartData: { metric: string; value: number; fullMark: number }[];

  if (data.values && data.labels) {
    // New position-aware format
    chartData = Object.entries(data.values).map(([key, value]) => ({
      metric: data.labels![key] ?? key,
      value: value ?? 0,
      fullMark: 100,
    }));
  } else {
    // Legacy flat format
    const LEGACY_KEYS = ['form', 'efficiency', 'consistency', 'goal_threat', 'creativity', 'impact'] as const;
    chartData = LEGACY_KEYS.map((key) => ({
      metric: LEGACY_LABELS[key],
      value: (data as Record<string, number>)[key] ?? 0,
      fullMark: 100,
    }));
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsRadarChart data={chartData}>
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis
          dataKey="metric"
          tick={{ fill: '#9ca3af', fontSize: 12 }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tick={{ fill: '#6b7280', fontSize: 10 }}
        />
        <Radar
          name="능력치"
          dataKey="value"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.5}
          strokeWidth={2}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1a1f2e',
            border: '1px solid #374151',
            borderRadius: '8px',
            color: '#fff',
          }}
          formatter={(value: number | undefined) => [`${(value || 0).toFixed(1)}`, '점수']}
        />
      </RechartsRadarChart>
    </ResponsiveContainer>
  );
};

export default RadarChart;
