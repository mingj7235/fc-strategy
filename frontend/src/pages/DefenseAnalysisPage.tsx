import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getDefenseAnalysis } from '../services/api';
import { cachedFetch } from '../services/apiCache';
import type { DefenseAnalysisData } from '../types/advancedAnalysis';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import InsightsPanel from '../components/common/InsightsPanel';

const LIMIT_OPTIONS = [
  { value: 10, label: '10경기' },
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const DefenseAnalysisPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<DefenseAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState<number>(50);
  const [limit, setLimit] = useState<number>(20);

  useEffect(() => {
    fetchData();
  }, [ouid, matchtype, limit]);

  const fetchData = async () => {
    if (!ouid) return;

    setLoading(true);
    setError('');

    try {
      const result = await cachedFetch(
        `defenseAnalysis:${ouid}:${matchtype}:${limit}`,
        () => getDefenseAnalysis(ouid, matchtype, limit),
        30 * 60 * 1000
      );
      setData(result);
    } catch (err: any) {
      console.error('Defense analysis fetch error:', err);
      setError(err.response?.data?.error || '수비 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '경기 데이터 불러오는 중...',
          '수비 지표 계산 중...',
          '실점 패턴 분석 중...',
          '개선 방안 도출 중...',
        ]}
        estimatedDuration={5000}
        message="수비 분석"
      />
    );
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-dark-bg text-white p-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-3xl font-bold mb-4">수비 분석</h1>
          <p className="text-gray-400">분석할 데이터가 없습니다.</p>
          <button
            onClick={() => navigate(-1)}
            className="mt-4 px-6 py-2 bg-accent-primary hover:bg-accent-secondary rounded-lg transition-colors"
          >
            돌아가기
          </button>
        </div>
      </div>
    );
  }

  const getStyleLabel = (style: string) => {
    const styles: { [key: string]: string } = {
      'aggressive_pressing': '공격적 압박',
      'risky_pressing': '위험한 압박',
      'organized_defense': '조직적 수비',
      'balanced_defense': '균형잡힌 수비',
      'passive_defense': '소극적 수비'
    };
    return styles[style] || style;
  };

  const getIntensityColor = (intensity: number) => {
    if (intensity >= 75) return 'text-chart-green';
    if (intensity >= 50) return 'text-chart-blue';
    if (intensity >= 30) return 'text-chart-yellow';
    return 'text-chart-red';
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>🛡️</span>
                수비 및 압박 분석
              </h1>
              <p className="text-gray-400 mt-1">
                태클, 블록, 수비 강도 분석 · {data.matches_analyzed}경기
              </p>
            </div>
            <button
              onClick={() => navigate(-1)}
              className="px-4 py-2 bg-dark-hover hover:bg-dark-border border border-dark-border rounded-lg transition-colors text-sm"
            >
              ← 돌아가기
            </button>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-400">경기 타입:</label>
              <select
                value={matchtype}
                onChange={(e) => setMatchtype(Number(e.target.value))}
                className="px-3 py-2 bg-dark-hover border border-dark-border rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-accent-primary"
              >
                <option value={50}>공식경기</option>
                <option value={52}>감독모드</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-400">분석 범위:</label>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="px-3 py-2 bg-dark-hover border border-dark-border rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-accent-primary"
              >
                {LIMIT_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    최근 {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto p-8">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-lg p-4">
            <div className="text-blue-400 text-2xl font-bold mb-1">
              {data.tackle_stats.success_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-300">태클 성공률</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/10 to-indigo-500/10 border border-purple-500/30 rounded-lg p-4">
            <div className="text-purple-400 text-2xl font-bold mb-1">
              {data.block_stats.success_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-300">블록 성공률</div>
          </div>

          <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-4">
            <div className={`text-2xl font-bold mb-1 ${getIntensityColor(data.overall.defensive_intensity)}`}>
              {data.overall.defensive_intensity.toFixed(1)}
            </div>
            <div className="text-sm text-gray-300">수비 강도</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-4">
            <div className="text-orange-400 text-lg font-bold mb-1">
              {getStyleLabel(data.overall.defensive_style)}
            </div>
            <div className="text-sm text-gray-300">수비 스타일</div>
          </div>
        </div>

        {/* Detailed Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Tackle Stats */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <span>⚔️</span>
              태클 통계
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">총 시도</span>
                  <span className="text-white font-bold text-xl">{data.tackle_stats.total_attempts}</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">성공</span>
                  <span className="text-white font-bold text-xl">{data.tackle_stats.total_success}</span>
                </div>
                <div className="h-2 bg-dark-hover rounded-full overflow-hidden">
                  <div
                    className={`h-full ${data.tackle_stats.success_rate > 70 ? 'bg-chart-green' : data.tackle_stats.success_rate > 50 ? 'bg-chart-yellow' : 'bg-chart-red'}`}
                    style={{ width: `${data.tackle_stats.success_rate}%` }}
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-dark-border">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">경기당 평균</span>
                  <span className="text-accent-primary font-bold text-lg">{data.tackle_stats.per_game.toFixed(1)}회</span>
                </div>
              </div>
            </div>
          </div>

          {/* Block Stats */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <span>🚧</span>
              블록 통계
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">총 시도</span>
                  <span className="text-white font-bold text-xl">{data.block_stats.total_attempts}</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">성공</span>
                  <span className="text-white font-bold text-xl">{data.block_stats.total_success}</span>
                </div>
                <div className="h-2 bg-dark-hover rounded-full overflow-hidden">
                  <div
                    className={`h-full ${data.block_stats.success_rate > 60 ? 'bg-chart-green' : data.block_stats.success_rate > 40 ? 'bg-chart-yellow' : 'bg-chart-red'}`}
                    style={{ width: `${Math.min(data.block_stats.success_rate, 100)}%` }}
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-dark-border">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">경기당 평균</span>
                  <span className="text-accent-primary font-bold text-lg">{data.block_stats.per_game.toFixed(1)}회</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Defensive Intensity Gauge */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
          <h3 className="text-xl font-bold text-white mb-6">수비 강도 게이지</h3>
          <div className="relative">
            <div className="h-8 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full" />
            <div
              className="absolute top-0 h-8 w-1 bg-white shadow-lg"
              style={{ left: `${data.overall.defensive_intensity}%`, transform: 'translateX(-50%)' }}
            >
              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-white text-dark-bg px-2 py-1 rounded text-sm font-bold whitespace-nowrap">
                {data.overall.defensive_intensity.toFixed(1)}
              </div>
            </div>
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-400">
            <span>소극적</span>
            <span>보통</span>
            <span>공격적</span>
          </div>
        </div>

        {/* Insights */}
        <InsightsPanel insights={data.insights} title="수비 분석 인사이트" />
      </div>
    </div>
  );
};

export default DefenseAnalysisPage;
