import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { TimeBasedGoalPatterns } from '../../types/match';

interface GoalTimingPatternCardProps {
  patterns: TimeBasedGoalPatterns;
}

const GoalTimingPatternCard: React.FC<GoalTimingPatternCardProps> = ({ patterns }) => {
  const getPatternInfo = (pattern: string) => {
    switch (pattern) {
      case 'early_dominant':
        return {
          icon: '🚀',
          title: '초반 주도형',
          description: '경기 초반에 골을 많이 넣는 스타일입니다',
          color: 'text-chart-green'
        };
      case 'late_surge':
        return {
          icon: '⚡',
          title: '후반 폭발형',
          description: '후반전에 강력한 공격력을 보입니다',
          color: 'text-chart-red'
        };
      case 'first_half_strong':
        return {
          icon: '💪',
          title: '전반전 강세',
          description: '전반전에 더 많은 골을 넣습니다',
          color: 'text-chart-blue'
        };
      case 'second_half_strong':
        return {
          icon: '🔥',
          title: '후반전 강세',
          description: '후반전에 더 많은 골을 넣습니다',
          color: 'text-chart-yellow'
        };
      case 'balanced':
        return {
          icon: '⚖️',
          title: '밸런스형',
          description: '골이 전반/후반에 고르게 분포되어 있습니다',
          color: 'text-chart-purple'
        };
      default:
        return {
          icon: '📊',
          title: '데이터 부족',
          description: '골 패턴을 분석하기에 데이터가 부족합니다',
          color: 'text-gray-400'
        };
    }
  };

  const patternInfo = getPatternInfo(patterns.goal_timing_pattern);

  // Goals without valid time data (API sentinel values were sanitized to 0)
  const goalsWithoutTime = patterns.total_goals - patterns.first_half_goals - patterns.second_half_goals;

  // Prepare chart data
  const chartData = [
    {
      name: '전반전',
      goals: patterns.first_half_goals,
      fill: '#60A5FA'  // chart-blue
    },
    {
      name: '후반전',
      goals: patterns.second_half_goals,
      fill: '#F59E0B'  // chart-yellow
    }
  ];

  const detailChartData = [
    {
      name: '초반\n(0-30분)',
      goals: patterns.early_goals,
      fill: '#10B981'  // chart-green
    },
    {
      name: '중반\n(30-60분)',
      goals: (patterns.first_half_goals - patterns.early_goals) + (patterns.second_half_goals - patterns.late_goals),
      fill: '#8B5CF6'  // chart-purple
    },
    {
      name: '후반\n(60-90분)',
      goals: patterns.late_goals,
      fill: '#EF4444'  // chart-red
    }
  ];

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">⏱️</span>
        골 발생 시간대 분석
      </h3>

      {/* Pattern Badge */}
      <div className="mb-6 p-4 bg-dark-bg rounded-lg border-l-4 border-accent-primary">
        <div className="flex items-start gap-3">
          <span className="text-3xl">{patternInfo.icon}</span>
          <div>
            <div className={`text-lg font-bold ${patternInfo.color}`}>{patternInfo.title}</div>
            <div className="text-sm text-gray-300 mt-1">{patternInfo.description}</div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-1">총 골</div>
          <div className="text-2xl font-bold text-white">{patterns.total_goals}</div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-1">전반전</div>
          <div className="text-2xl font-bold text-chart-blue">{patterns.first_half_goals}</div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-1">후반전</div>
          <div className="text-2xl font-bold text-chart-yellow">{patterns.second_half_goals}</div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-1">초반 골</div>
          <div className="text-2xl font-bold text-chart-green">{patterns.early_goals}</div>
        </div>
      </div>

      {/* Note for goals without time data */}
      {goalsWithoutTime > 0 && (
        <div className="mb-4 px-3 py-2 bg-dark-bg rounded-lg border border-dark-border text-xs text-gray-500 flex items-center gap-2">
          <span>ℹ️</span>
          <span>
            총 {patterns.total_goals}골 중 {goalsWithoutTime}골은 Nexon API에서 시간 데이터가 제공되지 않아 시간대 차트에서 제외됩니다.
          </span>
        </div>
      )}

      {/* Half Comparison Chart */}
      {patterns.total_goals > 0 && (
        <div className="mb-6">
          <div className="text-sm font-bold text-white mb-3">전반 vs 후반</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '0.5rem'
                }}
              />
              <Bar dataKey="goals" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Detailed Time Chart */}
      {patterns.total_goals > 0 && (
        <div>
          <div className="text-sm font-bold text-white mb-3">상세 시간대별</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={detailChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '0.5rem'
                }}
              />
              <Bar dataKey="goals" radius={[8, 8, 0, 0]}>
                {detailChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Insights */}
      {patterns.early_goals > patterns.late_goals * 1.5 && (
        <div className="mt-4 p-3 bg-chart-green/10 border border-chart-green/30 rounded-lg">
          <p className="text-sm text-chart-green">
            💡 초반에 골을 많이 넣습니다. 이 리듬을 유지하되, 후반전 체력 관리에 신경 쓰세요.
          </p>
        </div>
      )}

      {patterns.late_goals > patterns.early_goals * 1.5 && (
        <div className="mt-4 p-3 bg-chart-red/10 border border-chart-red/30 rounded-lg">
          <p className="text-sm text-chart-red">
            🔥 후반전에 강합니다! 체력 안배가 좋거나, 상대가 지쳐갈 때 기회를 잘 활용하고 있습니다.
          </p>
        </div>
      )}

      {patterns.total_goals === 0 && (
        <div className="mt-4 p-3 bg-gray-500/10 border border-gray-500/30 rounded-lg">
          <p className="text-sm text-gray-400">
            아직 골 데이터가 없습니다.
          </p>
        </div>
      )}
    </div>
  );
};

export default GoalTimingPatternCard;
