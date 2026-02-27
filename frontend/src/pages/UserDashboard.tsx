import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getUserMatches, getUserOverview } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import TabNavigation from '../components/common/TabNavigation';
import type { Tab } from '../components/common/TabNavigation';
import MatchList from '../components/match/MatchList';
import { DashboardOverviewSkeleton, MatchListSkeleton } from '../components/common/SkeletonLoader';
import type { Match } from '../types/match';

const TABS: Tab[] = [
  { id: 'official', label: '공식경기', matchtype: 50 },
  { id: 'manager', label: '공식 감독모드', matchtype: 52 },
  { id: 'friendly', label: '친선경기', matchtype: 40 },
];

const LIMIT_OPTIONS = [
  { value: 20, label: '20경기' },
  { value: 50, label: '50경기' },
  { value: 100, label: '100경기' },
];

interface UserOverview {
  user: {
    ouid: string;
    nickname: string;
  };
  total_matches: number;
  record: {
    wins: number;
    losses: number;
    draws: number;
    win_rate: number;
  };
  statistics: {
    avg_goals_for: number;
    avg_goals_against: number;
    goal_difference: number;
    avg_possession: number;
    avg_shots: number;
    avg_shots_on_target: number;
    shot_accuracy: number;
    avg_pass_success: number;
  };
  trends: {
    recent_form: string[];
    recent_wins: number;
    trend: string;
    first_half_win_rate: number;
    second_half_win_rate: number;
  };
  insights: string[];
}

const UserDashboard = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<string>('official');
  const [limit, setLimit] = useState<number>(20);
  const [matches, setMatches] = useState<Match[]>([]);
  const [overview, setOverview] = useState<UserOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [refetching, setRefetching] = useState(false);
  const isFirstLoad = useRef(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      if (!ouid) return;

      try {
        if (isFirstLoad.current) {
          setLoading(true);
        } else {
          setRefetching(true);
        }

        const currentTab = TABS.find(tab => tab.id === activeTab);
        const matchtype = currentTab?.matchtype ?? 50;

        // matches를 먼저 호출하여 DB에 데이터 저장 후 overview 호출
        const matchesData = await getUserMatches(ouid, matchtype, limit);
        setMatches(matchesData);

        const overviewData = await getUserOverview(ouid, matchtype, limit);
        setOverview(overviewData);
        setError('');
      } catch (err: any) {
        console.error('Dashboard fetch error:', err);
        const errorMsg = err.response?.data?.error || '데이터를 불러올 수 없습니다.';
        setError(errorMsg);
      } finally {
        setLoading(false);
        setRefetching(false);
        isFirstLoad.current = false;
      }
    };

    fetchData();
  }, [ouid, activeTab, limit]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    setError('');
  };

  const getFormIcon = (result: string) => {
    switch (result) {
      case 'win': return '🟢';
      case 'lose': return '🔴';
      case 'draw': return '🟡';
      default: return '⚪';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return '📈';
      case 'declining': return '📉';
      default: return '➡️';
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '유저 정보 불러오는 중...',
          '최근 경기 기록 조회 중...',
          '통계 데이터 계산 중...',
          '대시보드 준비 중...',
        ]}
        estimatedDuration={5000}
        message="대시보드 로딩"
      />
    );
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/')}
            className="text-accent-primary hover:text-blue-400 mb-4 flex items-center transition-colors"
          >
            ← 돌아가기
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                ⚽ {overview?.user?.nickname || '유저'} 대시보드
              </h1>
              <p className="text-gray-400">종합 경기 분석 및 통계</p>
            </div>

            {/* Limit Selector */}
            <div className="flex gap-2">
              {LIMIT_OPTIONS.map(option => (
                <button
                  key={option.value}
                  onClick={() => setLimit(option.value)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    limit === option.value
                      ? 'bg-accent-primary text-white shadow-dark'
                      : 'bg-dark-card border border-dark-border text-gray-300 hover:border-accent-primary/50'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} />
          </div>
        )}

        {/* Tab Navigation - Moved to top for better UX */}
        <div className="mb-8 bg-dark-card rounded-lg shadow-dark border border-dark-border">
          <div className="px-6">
            <TabNavigation tabs={TABS} activeTab={activeTab} onTabChange={handleTabChange} />
          </div>
        </div>

        {/* Overview Stats Grid */}
        {refetching && !overview && <DashboardOverviewSkeleton />}
        {overview && (
          <div className="mb-8 space-y-6">
            {/* Record Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-dark-card to-dark-hover border border-dark-border rounded-lg p-4 hover:border-accent-primary/50 transition-colors">
                <div className="text-sm text-gray-400 mb-1">총 경기</div>
                <div className="text-3xl font-bold text-white">{overview.total_matches ?? 0}</div>
              </div>
              <div className="bg-gradient-to-br from-chart-green/20 to-dark-card border border-chart-green/30 rounded-lg p-4 hover:border-chart-green/60 transition-colors">
                <div className="text-sm text-gray-400 mb-1">승리</div>
                <div className="text-3xl font-bold text-chart-green">{overview.record?.wins ?? 0}</div>
              </div>
              <div className="bg-gradient-to-br from-chart-red/20 to-dark-card border border-chart-red/30 rounded-lg p-4 hover:border-chart-red/60 transition-colors">
                <div className="text-sm text-gray-400 mb-1">패배</div>
                <div className="text-3xl font-bold text-chart-red">{overview.record?.losses ?? 0}</div>
              </div>
              <div className="bg-gradient-to-br from-chart-yellow/20 to-dark-card border border-chart-yellow/30 rounded-lg p-4 hover:border-chart-yellow/60 transition-colors">
                <div className="text-sm text-gray-400 mb-1">승률</div>
                <div className="text-3xl font-bold text-chart-yellow">{overview.record?.win_rate ?? 0}%</div>
              </div>
            </div>

            {/* Stats & Trends Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Average Statistics */}
              <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <span>📊</span>
                  평균 지표
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-gray-400 mb-1">평균 득점</div>
                    <div className="text-2xl font-bold text-chart-green">{(overview.statistics.avg_goals_for ?? 0).toFixed(1)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-1">평균 실점</div>
                    <div className="text-2xl font-bold text-chart-red">{(overview.statistics.avg_goals_against ?? 0).toFixed(1)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-1">평균 점유율</div>
                    <div className="text-2xl font-bold text-chart-blue">{(overview.statistics.avg_possession ?? 0).toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-1">슈팅 정확도</div>
                    <div className="text-2xl font-bold text-chart-purple">{(overview.statistics.shot_accuracy ?? 0).toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-1">평균 슈팅</div>
                    <div className="text-xl font-bold text-gray-300">{(overview.statistics.avg_shots ?? 0).toFixed(1)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-1">패스 성공률</div>
                    <div className="text-xl font-bold text-gray-300">{(overview.statistics.avg_pass_success ?? 0).toFixed(1)}%</div>
                  </div>
                </div>
              </div>

              {/* Trends */}
              <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <span>{getTrendIcon(overview.trends?.trend ?? 'stable')}</span>
                  경기력 트렌드
                </h3>

                {/* Recent Form */}
                <div className="mb-4">
                  <div className="text-sm text-gray-400 mb-2">최근 5경기</div>
                  <div className="flex gap-2">
                    {(overview.trends?.recent_form ?? []).map((result, index) => (
                      <div key={index} className="text-2xl">
                        {getFormIcon(result)}
                      </div>
                    ))}
                  </div>
                  <div className="text-sm text-gray-300 mt-2">
                    {overview.trends?.recent_wins ?? 0}승 {5 - (overview.trends?.recent_wins ?? 0)}패
                  </div>
                </div>

                {/* Win Rate Comparison */}
                <div>
                  <div className="text-sm text-gray-400 mb-2">승률 변화</div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="text-xs text-gray-500 mb-1">전반부</div>
                      <div className="text-lg font-bold text-gray-300">{(overview.trends?.first_half_win_rate ?? 0).toFixed(1)}%</div>
                    </div>
                    <div className="text-2xl text-gray-500">→</div>
                    <div className="flex-1">
                      <div className="text-xs text-gray-500 mb-1">후반부</div>
                      <div className={`text-lg font-bold ${
                        (overview.trends?.second_half_win_rate ?? 0) > (overview.trends?.first_half_win_rate ?? 0)
                          ? 'text-chart-green'
                          : (overview.trends?.second_half_win_rate ?? 0) < (overview.trends?.first_half_win_rate ?? 0)
                          ? 'text-chart-red'
                          : 'text-gray-300'
                      }`}>
                        {(overview.trends?.second_half_win_rate ?? 0).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Insights Panel */}
            <div className="bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg shadow-dark-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <span>💡</span>
                AI 인사이트
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {(overview.insights ?? []).map((insight, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-2 p-3 bg-dark-card/50 border border-dark-border rounded-lg hover:bg-dark-card transition-colors"
                  >
                    <span className="flex-shrink-0 text-accent-primary">•</span>
                    <p className="text-sm text-gray-200 leading-relaxed">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Matches List */}
        <div className="bg-dark-card rounded-lg shadow-dark border border-dark-border">
          <div className="px-6 py-4 border-b border-dark-border">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              📋 최근 경기
              {refetching
                ? <span className="inline-block w-12 h-4 bg-dark-hover animate-pulse rounded ml-1" />
                : <span>({matches.length}경기)</span>
              }
            </h2>
          </div>

          <div className="px-6 py-6">
            {refetching
              ? <MatchListSkeleton count={5} />
              : <MatchList matches={matches} userOuid={ouid || ''} />
            }
          </div>
        </div>

        {/* Analysis Links */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <button
            onClick={() => navigate(`/user/${ouid}/analysis/shots`)}
            className="bg-gradient-to-br from-dark-card to-dark-hover border border-dark-border rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-accent-primary/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">📊</span>
              슈팅 분석
            </h3>
            <p className="text-gray-400 text-sm">히트맵, 효율성, 위치별 분석</p>
          </button>
          <button
            onClick={() => navigate(`/user/${ouid}/analysis/passes`)}
            className="bg-gradient-to-br from-green-500/10 to-teal-500/10 border border-green-500/30 rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-green-500/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">⚽</span>
              패스 분석
            </h3>
            <p className="text-gray-400 text-sm">xA, 킬패스, 전진 패스</p>
          </button>
          <button
            onClick={() => navigate(`/user/${ouid}/analysis/style`)}
            className="bg-gradient-to-br from-dark-card to-dark-hover border border-dark-border rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-accent-primary/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">📈</span>
              플레이 스타일
            </h3>
            <p className="text-gray-400 text-sm">공격 패턴, 점유율, 승패</p>
          </button>
          <button
            onClick={() => navigate(`/user/${ouid}/power-rankings`)}
            className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-yellow-500/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">⭐</span>
              파워 랭킹
            </h3>
            <p className="text-gray-400 text-sm">선수별 종합 평가</p>
          </button>
          <button
            onClick={() => navigate(`/user/${ouid}/analysis/set-pieces`)}
            className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-blue-500/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">⚽</span>
              세트피스 분석
            </h3>
            <p className="text-gray-400 text-sm">프리킥, 페널티킥, 헤딩</p>
          </button>
          <button
            onClick={() => navigate(`/user/${ouid}/analysis/defense`)}
            className="bg-gradient-to-br from-purple-500/10 to-indigo-500/10 border border-purple-500/30 rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-purple-500/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">🛡️</span>
              수비 및 압박 분석
            </h3>
            <p className="text-gray-400 text-sm">태클, 블록, 수비 강도</p>
          </button>
          <button
            onClick={() => navigate(`/user/${ouid}/analysis/pass-variety`)}
            className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-orange-500/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">⚡</span>
              패스 다양성 분석
            </h3>
            <p className="text-gray-400 text-sm">패스 타입별 활용도</p>
          </button>
          <button
            onClick={() => navigate(`/user/${ouid}/analysis/shooting-quality`)}
            className="bg-gradient-to-br from-pink-500/10 to-rose-500/10 border border-pink-500/30 rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-pink-500/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">🎯</span>
              슈팅 품질 분석
            </h3>
            <p className="text-gray-400 text-sm">위치별 효율, 골 결정력</p>
          </button>
          <button
            onClick={() => navigate(`/user/${ouid}/analysis/controller`)}
            className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg shadow-dark p-6 hover:shadow-dark-lg hover:border-cyan-500/50 transition-all text-left transform hover:scale-[1.02]"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <span className="text-2xl">🎮</span>
              컨트롤러 분석
            </h3>
            <p className="text-gray-400 text-sm">키보드 vs 패드 성적 비교</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;
