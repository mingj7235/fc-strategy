import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSetPieceAnalysis } from '../services/api';
import type { SetPieceAnalysisData } from '../types/advancedAnalysis';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import InsightsPanel from '../components/common/InsightsPanel';

const LIMIT_OPTIONS = [
  { value: 10, label: '10경기' },
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const SetPieceAnalysisPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<SetPieceAnalysisData | null>(null);
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
      const result = await getSetPieceAnalysis(ouid, matchtype, limit);
      setData(result);
    } catch (err: any) {
      console.error('Set piece analysis fetch error:', err);
      setError(err.response?.data?.error || '세트피스 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '세트피스 데이터 수집 중...',
          '프리킥/페널티킥 분석 중...',
          '헤딩 효율성 계산 중...',
          '전략 제안 생성 중...',
        ]}
        estimatedDuration={5000}
        message="세트피스 분석"
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
          <h1 className="text-3xl font-bold mb-4">세트피스 분석</h1>
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
      'set_piece_specialist': '세트피스 스페셜리스트',
      'efficient_set_pieces': '효율적인 세트피스',
      'open_play_focused': '오픈 플레이 중심',
      'balanced': '균형잡힌'
    };
    return styles[style] || style;
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>⚽</span>
                세트피스 분석
              </h1>
              <p className="text-gray-400 mt-1">
                프리킥, 페널티킥, 헤딩 효율성 분석 · {data.matches_analyzed}경기
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
          <div className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-lg p-4">
            <div className="text-yellow-500 text-2xl font-bold mb-1">
              {data.overall.set_piece_goals}
            </div>
            <div className="text-sm text-gray-300">세트피스 골</div>
          </div>

          <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-lg p-4">
            <div className="text-blue-400 text-2xl font-bold mb-1">
              {data.overall.set_piece_dependency.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-300">세트피스 의존도</div>
          </div>

          <div className="bg-gradient-to-br from-green-500/10 to-teal-500/10 border border-green-500/30 rounded-lg p-4">
            <div className="text-green-400 text-2xl font-bold mb-1">
              {data.penalty_analysis.conversion_rate.toFixed(0)}%
            </div>
            <div className="text-sm text-gray-300">페널티킥 성공률</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-lg p-4">
            <div className="text-purple-400 text-xl font-bold mb-1">
              {getStyleLabel(data.overall.style)}
            </div>
            <div className="text-sm text-gray-300">스타일</div>
          </div>
        </div>

        {/* Detailed Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Free Kick */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span>🎯</span>
              프리킥
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">시도</span>
                <span className="text-white font-bold">{data.freekick_analysis.shots}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">골</span>
                <span className="text-white font-bold">{data.freekick_analysis.goals}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">전환율</span>
                <span className={`font-bold ${data.freekick_analysis.conversion_rate > 15 ? 'text-chart-green' : data.freekick_analysis.conversion_rate > 5 ? 'text-chart-yellow' : 'text-chart-red'}`}>
                  {data.freekick_analysis.conversion_rate.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Penalty Kick */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span>⭐</span>
              페널티킥
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">시도</span>
                <span className="text-white font-bold">{data.penalty_analysis.shots}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">골</span>
                <span className="text-white font-bold">{data.penalty_analysis.goals}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">성공률</span>
                <span className={`font-bold ${data.penalty_analysis.conversion_rate >= 80 ? 'text-chart-green' : data.penalty_analysis.conversion_rate >= 60 ? 'text-chart-yellow' : 'text-chart-red'}`}>
                  {data.penalty_analysis.conversion_rate.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Heading */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span>🏐</span>
              헤딩
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">시도</span>
                <span className="text-white font-bold">{data.heading_analysis.shots}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">골</span>
                <span className="text-white font-bold">{data.heading_analysis.goals}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">전환율</span>
                <span className={`font-bold ${data.heading_analysis.conversion_rate > 25 ? 'text-chart-green' : data.heading_analysis.conversion_rate > 15 ? 'text-chart-yellow' : 'text-chart-red'}`}>
                  {data.heading_analysis.conversion_rate.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Insights */}
        <InsightsPanel insights={data.insights} title="세트피스 분석 인사이트" />
      </div>
    </div>
  );
};

export default SetPieceAnalysisPage;
