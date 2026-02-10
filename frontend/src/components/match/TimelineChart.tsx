import React from 'react';
import {
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart,
} from 'recharts';

export interface KeyMoment {
  minute: number;
  type: 'goal' | 'big_chance';
  xg: number;
  x: number;
  y: number;
  result: string;
}

export interface TimelineDataPoint {
  minute: number;
  cumulative_xg: number;
  goals: number;
}

interface TimelineChartProps {
  timelineData: TimelineDataPoint[];
  keyMoments: KeyMoment[];
  firstHalfXg: number;
  secondHalfXg: number;
}

const TimelineChart: React.FC<TimelineChartProps> = ({
  timelineData,
  keyMoments,
  firstHalfXg,
  secondHalfXg,
}) => {
  // Add key moments as scatter points
  const chartData = timelineData.map((point) => {
    const moment = keyMoments.find((m) => m.minute === point.minute);
    return {
      ...point,
      moment: moment ? moment.type : null,
      momentXg: moment ? moment.xg : null,
    };
  });

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white border border-gray-300 rounded-lg p-3 shadow-lg">
          <p className="font-semibold text-gray-900">{data.minute}분</p>
          <p className="text-sm text-blue-600">누적 xG: {data.cumulative_xg.toFixed(2)}</p>
          <p className="text-sm text-green-600">골: {data.goals}</p>
          {data.moment && (
            <p className="text-sm text-orange-600 mt-1">
              {data.moment === 'goal' ? '⚽ 골!' : '⭐ 빅 찬스'}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (!payload.moment) return null;

    const isGoal = payload.moment === 'goal';
    const color = isGoal ? '#22c55e' : '#f59e0b';
    const size = isGoal ? 12 : 8;

    return (
      <circle
        cx={cx}
        cy={cy}
        r={size}
        fill={color}
        stroke="#fff"
        strokeWidth={2}
        className="drop-shadow-md"
      />
    );
  };

  return (
    <div className="w-full">
      {/* xG Comparison Cards */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-sm text-blue-600 font-medium mb-1">전반전 xG</div>
          <div className="text-3xl font-bold text-blue-700">{firstHalfXg.toFixed(2)}</div>
          <div className="text-xs text-blue-500 mt-1">기대 득점</div>
        </div>
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="text-sm text-purple-600 font-medium mb-1">후반전 xG</div>
          <div className="text-3xl font-bold text-purple-700">{secondHalfXg.toFixed(2)}</div>
          <div className="text-xs text-purple-500 mt-1">기대 득점</div>
        </div>
      </div>

      {/* Timeline Chart */}
      <div className="bg-gray-50 rounded-lg p-4">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorXg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="minute"
              label={{ value: '경기 시간 (분)', position: 'insideBottom', offset: -5 }}
              tick={{ fontSize: 12 }}
              domain={[0, 90]}
            />
            <YAxis
              label={{ value: '누적 xG', angle: -90, position: 'insideLeft' }}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* 45분 구분선 */}
            <ReferenceLine
              x={45}
              stroke="#94a3b8"
              strokeDasharray="5 5"
              label={{ value: '후반전', position: 'top', fill: '#64748b', fontSize: 12 }}
            />

            {/* xG Area Chart */}
            <Area
              type="monotone"
              dataKey="cumulative_xg"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#colorXg)"
              dot={<CustomDot />}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex justify-center items-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500 border-2 border-white"></div>
          <span className="text-gray-600">골</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-orange-400 border-2 border-white"></div>
          <span className="text-gray-600">빅 찬스 (xG &gt; 0.3)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-blue-500"></div>
          <span className="text-gray-600">누적 xG</span>
        </div>
      </div>
    </div>
  );
};

export default TimelineChart;
