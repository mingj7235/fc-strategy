import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPassVarietyAnalysis } from '../services/api';
import { cachedFetch } from '../services/apiCache';
import type { PassVarietyAnalysisData } from '../types/advancedAnalysis';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import InsightsPanel from '../components/common/InsightsPanel';

const LIMIT_OPTIONS = [
  { value: 10, label: '10경기' },
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

const PassVarietyAnalysisPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<PassVarietyAnalysisData | null>(null);
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
        `passVarietyAnalysis:${ouid}:${matchtype}:${limit}`,
        () => getPassVarietyAnalysis(ouid, matchtype, limit),
        30 * 60 * 1000
      );
      setData(result);
    } catch (err: any) {
      console.error('Pass variety analysis fetch error:', err);
      setError(err.response?.data?.error || '패스 다양성 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '패스 데이터 수집 중...',
          '패스 타입별 분석 중...',
          '다양성 지표 계산 중...',
          '전략 인사이트 생성 중...',
        ]}
        estimatedDuration={5500}
        message="패스 다양성 분석"
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
          <h1 className="text-3xl font-bold mb-4">패스 다양성 분석</h1>
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
      'possession_based': '점유율 기반',
      'direct_play': '직접 플레이',
      'penetrative': '침투적',
      'balanced': '균형잡힌',
      'conservative': '보수적',
      'varied': '다양한'
    };
    return styles[style] || style;
  };

  const pieData = [
    { name: '숏패스', value: data.pass_distribution.short_passes.ratio },
    { name: '롱패스', value: data.pass_distribution.long_passes.ratio },
    { name: '스루패스', value: data.pass_distribution.through_passes.ratio },
  ];

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>⚡</span>
                패스 다양성 분석
              </h1>
              <p className="text-gray-400 mt-1">
                패스 타입별 활용도 및 빌드업 스타일 분석 · {data.matches_analyzed}경기
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
              {data.overall.diversity_index.toFixed(1)}
            </div>
            <div className="text-sm text-gray-300">다양성 지수</div>
          </div>

          <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-4">
            <div className="text-green-400 text-2xl font-bold mb-1">
              {data.overall.overall_accuracy.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-300">전체 패스 정확도</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-lg p-4">
            <div className="text-purple-400 text-xl font-bold mb-1">
              {getStyleLabel(data.overall.buildup_style)}
            </div>
            <div className="text-sm text-gray-300">빌드업 스타일</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-4">
            <div className="text-orange-400 text-2xl font-bold mb-1">
              {data.overall.total_passes}
            </div>
            <div className="text-sm text-gray-300">총 패스</div>
          </div>
        </div>

        {/* Charts and Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Pie Chart */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">패스 타입 분포</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a1f2e',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Pass Stats */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">패스 타입별 성공률</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">숏패스</span>
                  <span className="text-white font-bold">{data.pass_distribution.short_passes.success_rate.toFixed(1)}%</span>
                </div>
                <div className="h-3 bg-dark-hover rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500"
                    style={{ width: `${Math.min(data.pass_distribution.short_passes.success_rate, 100)}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">롱패스</span>
                  <span className="text-white font-bold">{data.pass_distribution.long_passes.success_rate.toFixed(1)}%</span>
                </div>
                <div className="h-3 bg-dark-hover rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500"
                    style={{ width: `${Math.min(data.pass_distribution.long_passes.success_rate, 100)}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">스루패스</span>
                  <span className="text-white font-bold">{data.pass_distribution.through_passes.success_rate.toFixed(1)}%</span>
                </div>
                <div className="h-3 bg-dark-hover rounded-full overflow-hidden">
                  <div
                    className="h-full bg-orange-500"
                    style={{ width: `${Math.min(data.pass_distribution.through_passes.success_rate, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Insights */}
        <InsightsPanel insights={data.insights} title="패스 다양성 인사이트" />
      </div>
    </div>
  );
};

export default PassVarietyAnalysisPage;
