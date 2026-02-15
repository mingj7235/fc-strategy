import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getControllerAnalysis } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import ControllerComparison from '../components/analysis/ControllerComparison';
import PlaystyleComparison from '../components/analysis/PlaystyleComparison';
import ControllerRecommendation from '../components/analysis/ControllerRecommendation';
import ControllerInsights from '../components/analysis/ControllerInsights';
import type { ControllerAnalysis } from '../types/match';

const ControllerAnalysisPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<ControllerAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState(50);
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!ouid) return;

      try {
        setLoading(true);
        const data = await getControllerAnalysis(ouid, matchtype, limit);
        setAnalysis(data);
        setError('');
      } catch (err: any) {
        console.error('Controller analysis fetch error:', err);
        setError(err.response?.data?.error || '컨트롤러 분석을 불러올 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [ouid, matchtype, limit]);

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '경기 데이터 수집 중...',
          '컨트롤러별 성적 계산 중...',
          '플레이 스타일 분석 중...',
          '추천 생성 중...',
        ]}
        estimatedDuration={3000}
        message="컨트롤러 분석"
      />
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-dark-bg p-8">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="text-accent-primary hover:text-blue-400 mb-4 transition-colors"
          >
            ← 돌아가기
          </button>
          <ErrorMessage message={error || '컨트롤러 분석 데이터를 찾을 수 없습니다.'} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-bg py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="text-accent-primary hover:text-blue-400 mb-4 flex items-center transition-colors"
          >
            ← 돌아가기
          </button>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <span className="text-4xl">🎮</span>
            컨트롤러 분석
          </h1>
          <p className="text-gray-400">
            키보드와 패드의 성적 및 플레이 스타일을 비교합니다
          </p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex gap-4 items-center">
          <div>
            <label className="text-sm text-gray-400 mr-2">경기 타입:</label>
            <select
              value={matchtype}
              onChange={(e) => setMatchtype(Number(e.target.value))}
              className="bg-dark-card border border-dark-border rounded px-3 py-2 text-white"
            >
              <option value={50}>공식경기</option>
              <option value={52}>공식 감독모드</option>
              <option value={40}>친선경기</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-400 mr-2">분석 경기 수:</label>
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="bg-dark-card border border-dark-border rounded px-3 py-2 text-white"
            >
              <option value={20}>20경기</option>
              <option value={50}>50경기</option>
              <option value={100}>100경기</option>
            </select>
          </div>
          <div className="ml-auto text-sm text-gray-400">
            {analysis.matches_analyzed}경기 분석됨
          </div>
        </div>

        {/* Recommendation Card */}
        <div className="mb-6">
          <ControllerRecommendation recommendation={analysis.recommendation} />
        </div>

        {/* Performance Comparison */}
        <div className="mb-6">
          <ControllerComparison
            keyboard={analysis.performance_comparison.keyboard}
            gamepad={analysis.performance_comparison.gamepad}
          />
        </div>

        {/* Playstyle Comparison */}
        <div className="mb-6">
          <PlaystyleComparison
            keyboard={analysis.playstyle_comparison.keyboard}
            gamepad={analysis.playstyle_comparison.gamepad}
          />
        </div>

        {/* Insights */}
        <div className="mb-6">
          <ControllerInsights
            insights={analysis.insights}
            matchesAnalyzed={analysis.matches_analyzed}
          />
        </div>

        {/* Info Card */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6">
          <div className="flex items-start gap-3">
            <span className="text-2xl">ℹ️</span>
            <div className="text-sm text-gray-300 space-y-2">
              <p>
                <strong>컨트롤러 분석이란?</strong> 키보드와 패드 간의 성적 및 플레이 스타일 차이를
                분석하여 어떤 컨트롤러가 더 잘 맞는지 확인할 수 있습니다.
              </p>
              <p>
                각 컨트롤러로 최소 <strong>5경기 이상</strong> 플레이해야 신뢰도 높은 분석이 가능합니다.
              </p>
              <p>
                컨트롤러 선택은 개인 선호도가 중요하므로, 분석 결과를 참고만 하시고 편한 것을 사용하세요.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ControllerAnalysisPage;
