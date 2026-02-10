import React from 'react';
import type { HeadingStats, HeadingPositions, CrossOrigins } from '../../types/match';

interface HeadingStatsCardProps {
  stats: HeadingStats;
  positions: HeadingPositions;
  crossOrigins: CrossOrigins;
}

const HeadingStatsCard: React.FC<HeadingStatsCardProps> = ({ stats, positions, crossOrigins }) => {
  if (stats.total_headers === 0) {
    return (
      <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">⚽</span>
          헤딩 통계
        </h3>
        <div className="text-center py-8 text-gray-400">
          <p>이 경기에는 헤딩 슈팅이 없습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">⚽</span>
        헤딩 통계
      </h3>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-sm text-gray-400 mb-1">총 헤딩</div>
          <div className="text-3xl font-bold text-white">{stats.total_headers}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-sm text-gray-400 mb-1">골</div>
          <div className="text-3xl font-bold text-chart-green">{stats.goals}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-sm text-gray-400 mb-1">유효슈팅</div>
          <div className="text-3xl font-bold text-chart-yellow">{stats.on_target}</div>
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 text-center">
          <div className="text-sm text-gray-400 mb-1">성공률</div>
          <div className="text-3xl font-bold text-chart-blue">{stats.success_rate}%</div>
        </div>
      </div>

      {/* Conversion Rate */}
      <div className="mb-6 p-4 bg-dark-bg rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-400">헤딩 골 전환율</span>
          <span className={`text-2xl font-bold ${
            stats.conversion_rate >= 30 ? 'text-chart-green' :
            stats.conversion_rate >= 15 ? 'text-chart-yellow' :
            'text-chart-red'
          }`}>
            {stats.conversion_rate}%
          </span>
        </div>
        <div className="w-full bg-dark-card rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${
              stats.conversion_rate >= 30 ? 'bg-chart-green' :
              stats.conversion_rate >= 15 ? 'bg-chart-yellow' :
              'bg-chart-red'
            }`}
            style={{ width: `${Math.min(stats.conversion_rate * 2, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Secondary Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-dark-bg p-4 rounded-lg">
          <div className="text-sm text-gray-400 mb-2">크로스 활용</div>
          <div className="text-xl font-bold text-white mb-1">{stats.cross_percentage}%</div>
          <div className="text-xs text-gray-400">{stats.headers_with_assist}회 크로스에서 발생</div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg">
          <div className="text-sm text-gray-400 mb-2">박스 내 헤딩</div>
          <div className="text-xl font-bold text-white mb-1">{stats.box_percentage}%</div>
          <div className="text-xs text-gray-400">{stats.inside_box}회</div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg">
          <div className="text-sm text-gray-400 mb-2">헤딩 위치</div>
          <div className="text-sm text-white">
            중앙 {positions.positions.central}회 |{' '}
            좌 {positions.positions.left}회 |{' '}
            우 {positions.positions.right}회
          </div>
        </div>
      </div>

      {/* Cross Origins */}
      {crossOrigins.cross_origins.left_wing + crossOrigins.cross_origins.right_wing + crossOrigins.cross_origins.central > 0 && (
        <div className="mt-6 p-4 bg-dark-bg rounded-lg">
          <div className="text-sm font-bold text-white mb-3">크로스 출발 위치</div>
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="text-xs text-gray-400 mb-1">좌측 측면</div>
              <div className="text-lg font-bold text-chart-green">
                {crossOrigins.cross_origins.left_wing}회
              </div>
            </div>
            <div className="flex-1">
              <div className="text-xs text-gray-400 mb-1">중앙</div>
              <div className="text-lg font-bold text-chart-yellow">
                {crossOrigins.cross_origins.central}회
              </div>
            </div>
            <div className="flex-1">
              <div className="text-xs text-gray-400 mb-1">우측 측면</div>
              <div className="text-lg font-bold text-chart-blue">
                {crossOrigins.cross_origins.right_wing}회
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HeadingStatsCard;
