import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getShootingQualityAnalysis } from '../services/api';
import { cachedFetch } from '../services/apiCache';
import type { ShootingQualityAnalysisData } from '../types/advancedAnalysis';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import InsightsPanel from '../components/common/InsightsPanel';

const LIMIT_OPTIONS = [
  { value: 10, label: '10경기' },
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const ShootingQualityAnalysisPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<ShootingQualityAnalysisData | null>(null);
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
        `shootingQualityAnalysis:${ouid}:${matchtype}:${limit}`,
        () => getShootingQualityAnalysis(ouid, matchtype, limit),
        30 * 60 * 1000
      );
      setData(result);
    } catch (err: any) {
      console.error('Shooting quality analysis fetch error:', err);
      setError(err.response?.data?.error || '슈팅 품질 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '슈팅 데이터 수집 중...',
          '슈팅 품질 평가 중...',
          '위치별 효율성 계산 중...',
          '인사이트 생성 중...',
        ]}
        estimatedDuration={5500}
        message="슈팅 품질 분석"
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
          <h1 className="text-3xl font-bold mb-4">슈팅 품질 분석</h1>
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
      'clinical_finisher': '클리니컬 피니셔',
      'long_shot_specialist': '중거리 슈팅 전문가',
      'volume_shooter': '대량 슈터',
      'efficient': '효율적',
      'needs_improvement': '개선 필요',
      'balanced': '균형잡힌'
    };
    return styles[style] || style;
  };

  const chartData = [
    {
      name: '박스 안',
      전환율: data.location_analysis.inside_box.conversion_rate,
      비율: data.location_analysis.inside_box.ratio
    },
    {
      name: '박스 밖',
      전환율: data.location_analysis.outside_box.conversion_rate,
      비율: data.location_analysis.outside_box.ratio
    }
  ];

  const getClinicalColor = (rating: number) => {
    if (rating >= 75) return 'text-chart-green';
    if (rating >= 50) return 'text-chart-blue';
    if (rating >= 30) return 'text-chart-yellow';
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
                <span>🎯</span>
                슈팅 품질 분석
              </h1>
              <p className="text-gray-400 mt-1">
                위치별 슈팅 효율 및 골 결정력 분석 · {data.matches_analyzed}경기
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
          <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-4">
            <div className="text-green-400 text-2xl font-bold mb-1">
              {data.location_analysis.inside_box.conversion_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-300">박스 안 전환율</div>
          </div>

          <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-lg p-4">
            <div className="text-blue-400 text-2xl font-bold mb-1">
              {data.shot_type_analysis.shot_on_target_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-300">유효슈팅 비율</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-lg p-4">
            <div className={`text-2xl font-bold mb-1 ${getClinicalColor(data.overall.clinical_rating)}`}>
              {data.overall.clinical_rating.toFixed(1)}
            </div>
            <div className="text-sm text-gray-300">골 결정력</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-4">
            <div className="text-orange-400 text-lg font-bold mb-1">
              {getStyleLabel(data.overall.shooting_style)}
            </div>
            <div className="text-sm text-gray-300">슈팅 스타일</div>
          </div>
        </div>

        {/* Location Analysis Chart */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
          <h3 className="text-xl font-bold text-white mb-6">위치별 슈팅 분석</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1f2e',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Legend />
              <Bar dataKey="전환율" fill="#3b82f6" />
              <Bar dataKey="비율" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Detailed Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Inside Box */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span>📍</span>
              박스 안
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">슈팅</span>
                <span className="text-white font-bold">{data.location_analysis.inside_box.shots}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">골</span>
                <span className="text-white font-bold">{data.location_analysis.inside_box.goals}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">전환율</span>
                <span className="text-chart-green font-bold">{data.location_analysis.inside_box.conversion_rate.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          {/* Outside Box */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span>🌐</span>
              박스 밖
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">슈팅</span>
                <span className="text-white font-bold">{data.location_analysis.outside_box.shots}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">골</span>
                <span className="text-white font-bold">{data.location_analysis.outside_box.goals}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">전환율</span>
                <span className="text-chart-blue font-bold">{data.location_analysis.outside_box.conversion_rate.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          {/* Overall Stats */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span>📊</span>
              종합
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">경기당 슈팅</span>
                <span className="text-white font-bold">{data.overall.shots_per_game.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">경기당 골</span>
                <span className="text-white font-bold">{data.overall.goals_per_game.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">전체 전환율</span>
                <span className="text-accent-primary font-bold">{data.overall.conversion_rate.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Clinical Rating Gauge */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
          <h3 className="text-xl font-bold text-white mb-6">골 결정력 게이지</h3>
          <div className="relative">
            <div className="h-8 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full" />
            <div
              className="absolute top-0 h-8 w-1 bg-white shadow-lg"
              style={{ left: `${data.overall.clinical_rating}%`, transform: 'translateX(-50%)' }}
            >
              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-white text-dark-bg px-2 py-1 rounded text-sm font-bold whitespace-nowrap">
                {data.overall.clinical_rating.toFixed(1)}
              </div>
            </div>
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-400">
            <span>낮음</span>
            <span>보통</span>
            <span>높음</span>
          </div>
        </div>

        {/* Insights */}
        <InsightsPanel insights={data.insights} title="슈팅 품질 인사이트" />
      </div>
    </div>
  );
};

export default ShootingQualityAnalysisPage;
