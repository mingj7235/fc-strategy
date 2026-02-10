import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface MatchData {
  result: string;
  possession: number;
  shots: number;
  shots_on_target: number;
  goals: number;
  pass_success_rate: number;
}

interface PossessionTrendChartProps {
  matches: MatchData[];
}

const PossessionTrendChart: React.FC<PossessionTrendChartProps> = ({ matches }) => {
  // Reverse to show oldest to newest (left to right)
  const data = [...matches].reverse().map((match, index) => ({
    match: `경기 ${index + 1}`,
    possession: match.possession,
    result: match.result,
  }));

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    let fill = '#6b7280'; // gray for draw

    if (payload.result === 'win') {
      fill = '#10b981'; // chart-green for win
    } else if (payload.result === 'lose') {
      fill = '#ef4444'; // chart-red for lose
    }

    return <circle cx={cx} cy={cy} r={6} fill={fill} stroke="#1a1f2e" strokeWidth={2} />;
  };

  return (
    <div>
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span>📈</span>
        점유율 추세
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="match" stroke="#9ca3af" />
          <YAxis domain={[0, 100]} stroke="#9ca3af" label={{ value: '%', position: 'insideLeft', fill: '#9ca3af' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1f2e',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#fff',
            }}
            formatter={(value: number | undefined) => [`${value || 0}%`, '점유율']}
          />
          <Line
            type="monotone"
            dataKey="possession"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={<CustomDot />}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 flex justify-center gap-6 text-sm text-gray-300">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-chart-green"></div>
          <span>승리</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-chart-red"></div>
          <span>패배</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-gray-500"></div>
          <span>무승부</span>
        </div>
      </div>
    </div>
  );
};

export default PossessionTrendChart;
