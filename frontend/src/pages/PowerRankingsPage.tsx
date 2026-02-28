import React, { useEffect, useState, useRef, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPowerRankings } from '../services/api';
import { cachedFetch } from '../services/apiCache';
import type { PowerRankingsResponse } from '../types/powerRanking';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import PlayerPowerCard from '../components/powerRanking/PlayerPowerCard';
import PowerRankingSummary from '../components/powerRanking/PowerRankingSummary';
import PositionGroupView from '../components/powerRanking/PositionGroupView';
import FormationView from '../components/powerRanking/FormationView';
import PositionEvaluationGuide from '../components/powerRanking/PositionEvaluationGuide';
import ShootingEfficiencyCard from '../components/stats/ShootingEfficiencyCard';
import GoalTimingPatternCard from '../components/stats/GoalTimingPatternCard';
import PassDistributionRadar from '../components/stats/PassDistributionRadar';
import HeadingSpecialistsCard from '../components/stats/HeadingSpecialistsCard';

const LIMIT_OPTIONS = [
  { value: 10, label: '10경기' },
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

type ViewMode = 'summary' | 'position' | 'formation' | 'detailed' | 'stats';

const PowerRankingsPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [rankings, setRankings] = useState<PowerRankingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState<number>(50);
  const [limit, setLimit] = useState<number>(20);
  const [sortBy, setSortBy] = useState<'power_score' | 'form' | 'efficiency'>('power_score');
  const [viewMode, setViewMode] = useState<ViewMode>('summary');
  const [showGuide, setShowGuide] = useState(false);
  const playerCardRefs = useRef<{ [key: number]: HTMLDivElement | null }>({});

  useEffect(() => {
    fetchRankings();
  }, [ouid, matchtype, limit]);

  const fetchRankings = async () => {
    if (!ouid) return;

    setLoading(true);
    setError('');

    try {
      const data = await cachedFetch(
        `powerRankings:${ouid}:${matchtype}:${limit}`,
        () => getPowerRankings(ouid, matchtype, limit),
        30 * 60 * 1000
      );
      setRankings(data);
    } catch (err: any) {
      console.error('Power rankings fetch error:', err);
      setError(err.response?.data?.error || '파워 랭킹을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // Sort rankings based on selected criteria
  const sortedRankings = useMemo(() => {
    if (!rankings) return [];

    const sorted = [...rankings.rankings];

    switch (sortBy) {
      case 'form':
        sorted.sort((a, b) => b.form_analysis.form_index - a.form_analysis.form_index);
        break;
      case 'efficiency':
        sorted.sort((a, b) => b.efficiency_metrics.efficiency_score - a.efficiency_metrics.efficiency_score);
        break;
      default: // power_score
        sorted.sort((a, b) => b.power_score - a.power_score);
    }

    return sorted;
  }, [rankings, sortBy]);

  // Scroll to player card
  const handlePlayerClick = (spid: number) => {
    // Switch to detailed view if not already
    if (viewMode !== 'detailed') {
      setViewMode('detailed');
      // Wait for DOM update
      setTimeout(() => {
        scrollToPlayer(spid);
      }, 100);
    } else {
      scrollToPlayer(spid);
    }
  };

  const scrollToPlayer = (spid: number) => {
    const element = playerCardRefs.current[spid];
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Highlight effect
      element.classList.add('ring-2', 'ring-accent-primary', 'ring-offset-2', 'ring-offset-dark-bg');
      setTimeout(() => {
        element.classList.remove('ring-2', 'ring-accent-primary', 'ring-offset-2', 'ring-offset-dark-bg');
      }, 2000);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '경기 데이터 불러오는 중...',
          '선수 성능 분석 중...',
          '포지션별 평가 계산 중...',
          '파워 랭킹 생성 중...',
        ]}
        estimatedDuration={6000}
        message="선수 파워 랭킹 분석"
      />
    );
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!rankings || rankings.total_players === 0) {
    return (
      <div className="min-h-screen bg-dark-bg text-white p-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-3xl font-bold mb-4">파워 랭킹</h1>
          <p className="text-gray-400">분석할 데이터가 충분하지 않습니다. (최소 3경기 이상 출전한 선수 필요)</p>
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

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Evaluation Guide Modal */}
      {showGuide && <PositionEvaluationGuide onClose={() => setShowGuide(false)} />}

      {/* Header */}
      <div className="bg-gradient-to-r from-dark-card via-dark-hover to-dark-card border-b border-dark-border py-4 md:py-6 px-4 md:px-8 shadow-dark-lg sticky top-0 z-40 backdrop-blur-sm bg-opacity-95">
        <div className="max-w-7xl mx-auto">
          {/* Title Row */}
          <div className="flex items-start md:items-center justify-between mb-4 gap-3">
            <h1 className="text-xl md:text-3xl font-bold text-white flex items-center gap-2 md:gap-3">
              <span className="text-2xl md:text-4xl">⭐</span>
              <div>
                <div>선수 파워 랭킹</div>
                <div className="text-xs md:text-sm text-gray-400 font-normal mt-1 hidden sm:block">
                  포지션별 차별화 평가 시스템 · {rankings.total_players}명 분석 (출전 선수만)
                </div>
              </div>
            </h1>
            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={() => setShowGuide(true)}
                className="px-3 md:px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg transition-all text-xs md:text-sm font-semibold shadow-lg hover:shadow-xl flex items-center gap-1 md:gap-2"
              >
                <span>📊</span>
                <span className="hidden sm:inline">평가 기준 가이드</span>
                <span className="sm:hidden">가이드</span>
              </button>
              <button
                onClick={() => navigate(-1)}
                className="px-3 md:px-4 py-2 bg-dark-hover hover:bg-dark-border border border-dark-border rounded-lg transition-colors text-xs md:text-sm"
              >
                ← <span className="hidden sm:inline">돌아가기</span>
              </button>
            </div>
          </div>

          {/* Filters Row */}
          <div className="flex flex-wrap items-center gap-2 md:gap-4">
            {/* Match Type */}
            <div className="flex items-center gap-2">
              <label className="text-xs md:text-sm text-gray-400 font-medium whitespace-nowrap">경기 타입:</label>
              <MatchTypeSelector value={matchtype} onChange={setMatchtype} />
            </div>

            {/* Limit */}
            <div className="flex items-center gap-2">
              <label className="text-xs md:text-sm text-gray-400 font-medium whitespace-nowrap">범위:</label>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="px-2 md:px-4 py-2 md:py-3 bg-dark-hover border border-dark-border rounded-lg text-white text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-accent-primary hover:border-accent-primary/50 transition-all font-medium"
              >
                {LIMIT_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    최근 {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort By */}
            <div className="flex items-center gap-2">
              <label className="text-xs md:text-sm text-gray-400 whitespace-nowrap">정렬:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-2 md:px-3 py-2 bg-dark-hover border border-dark-border rounded-lg text-white text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-accent-primary"
              >
                <option value="power_score">파워 스코어</option>
                <option value="form">폼 지수</option>
                <option value="efficiency">효율성</option>
              </select>
            </div>

            {/* View Mode Tabs - wraps to full width on mobile */}
            <div className="w-full md:w-auto md:ml-auto flex items-center gap-1 bg-dark-hover rounded-lg p-1 border border-dark-border overflow-x-auto">
              {([
                { mode: 'summary', icon: '⚡', label: '요약' },
                { mode: 'position', icon: '📋', label: '포지션별' },
                { mode: 'formation', icon: '⚽', label: '포메이션' },
                { mode: 'detailed', icon: '📊', label: '상세' },
                { mode: 'stats', icon: '📈', label: '통계' },
              ] as const).map(({ mode, icon, label }) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`px-2 md:px-4 py-2 rounded-md text-xs md:text-sm font-medium transition-all whitespace-nowrap ${
                    viewMode === mode
                      ? 'bg-accent-primary text-white shadow-lg'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <span className="mr-1">{icon}</span>
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto p-4 md:p-8">
        {/* Summary View */}
        {viewMode === 'summary' && (
          <PowerRankingSummary
            players={sortedRankings}
            onPlayerClick={handlePlayerClick}
          />
        )}

        {/* Position Group View */}
        {viewMode === 'position' && (
          <PositionGroupView
            players={sortedRankings}
            onPlayerClick={handlePlayerClick}
          />
        )}

        {/* Formation View */}
        {viewMode === 'formation' && (
          <FormationView
            players={sortedRankings}
            onPlayerClick={handlePlayerClick}
          />
        )}

        {/* Detailed View */}
        {viewMode === 'detailed' && (
          <>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                <span>📋</span>
                상세 선수 분석
              </h2>
              <p className="text-sm text-gray-400">
                각 선수의 포지션별 평가, 폼 분석, 효율성 지표, 일관성 평가를 확인하세요
              </p>
            </div>

            <div className="space-y-4">
              {sortedRankings.map((player, index) => (
                <div
                  key={player.spid}
                  ref={(el) => { playerCardRefs.current[player.spid] = el; }}
                  className="transition-all duration-300 rounded-lg"
                >
                  <PlayerPowerCard
                    player={player}
                    rank={index + 1}
                  />
                </div>
              ))}
            </div>
          </>
        )}

        {/* Aggregate Stats View */}
        {viewMode === 'stats' && (
          <>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                <span>📈</span>
                통합 통계 분석
              </h2>
              <p className="text-sm text-gray-400">
                {limit}경기의 데이터를 종합한 통계적 분석입니다
              </p>
            </div>

            {rankings?.aggregate_stats ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Shooting Efficiency */}
                {rankings.aggregate_stats.shooting_efficiency && (
                  <ShootingEfficiencyCard efficiency={rankings.aggregate_stats.shooting_efficiency} />
                )}

                {/* Goal Timing Patterns */}
                {rankings.aggregate_stats.goal_patterns && (
                  <GoalTimingPatternCard patterns={rankings.aggregate_stats.goal_patterns} />
                )}

                {/* Pass Distribution */}
                {rankings.aggregate_stats.pass_distribution && (
                  <PassDistributionRadar distribution={rankings.aggregate_stats.pass_distribution} />
                )}

                {/* Heading Specialists */}
                {rankings.aggregate_stats.heading_specialists && (
                  <HeadingSpecialistsCard specialists={rankings.aggregate_stats.heading_specialists} />
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <p>통계 데이터를 불러오는 중...</p>
              </div>
            )}
          </>
        )}

        {/* Legend and Info */}
        <div className="mt-8 bg-dark-card border border-dark-border rounded-lg p-6">
          <h3 className="text-lg font-bold text-white mb-4">파워 랭킹 시스템 소개</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-accent-primary font-semibold mb-2">🎯 포지션별 차별화 평가 (35-40%)</div>
              <p className="text-gray-300">각 포지션의 역할에 맞춘 맞춤형 평가 기준 적용</p>
            </div>
            <div>
              <div className="text-accent-primary font-semibold mb-2">📈 폼 지수 (25-30%)</div>
              <p className="text-gray-300">최근 경기 성적 추이 및 컨디션 분석</p>
            </div>
            <div>
              <div className="text-accent-primary font-semibold mb-2">⚡ 효율성 (20%)</div>
              <p className="text-gray-300">골 전환율, 패스 정확도, 드리블 성공률 등</p>
            </div>
            <div>
              <div className="text-accent-primary font-semibold mb-2">💥 영향력 (15%)</div>
              <p className="text-gray-300">골, 어시스트, 빅찬스로 측정한 경기 기여도</p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-dark-border">
            <button
              onClick={() => setShowGuide(true)}
              className="text-accent-primary hover:text-blue-400 transition-colors flex items-center gap-2"
            >
              <span>📖</span>
              <span className="underline">포지션별 상세 평가 기준 보기</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PowerRankingsPage;
