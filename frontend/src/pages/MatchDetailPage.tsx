import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { getMatchDetail, getMatchHeatmap, getMatchAnalysis, getAssistNetwork, getShotTypes, getPassTypes, getHeadingAnalysis } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import ShotHeatmap from '../components/visualizations/ShotHeatmap';
import PlayerCard from '../components/match/PlayerCard';
import PlayerStatsTable from '../components/match/PlayerStatsTable';
import TimelineChart from '../components/match/TimelineChart';
import KeyMomentsList from '../components/match/KeyMomentsList';
import TacticalInsightsPanel from '../components/match/TacticalInsightsPanel';
import AssistHeatmap from '../components/match/AssistHeatmap';
import AssistNetwork from '../components/match/AssistNetwork';
import AssistStats from '../components/match/AssistStats';
import ShotTypeBreakdown from '../components/match/ShotTypeBreakdown';
import BoxLocationAnalysis from '../components/match/BoxLocationAnalysis';
import ShotTypeInsights from '../components/match/ShotTypeInsights';
import PassTypeRadarChart from '../components/match/PassTypeRadarChart';
import PlayStyleCard from '../components/match/PlayStyleCard';
import PassTypeBreakdownTable from '../components/match/PassTypeBreakdownTable';
import PassTypeInsights from '../components/match/PassTypeInsights';
import HeadingStatsCard from '../components/match/HeadingStatsCard';
import AerialEfficiencyCard from '../components/match/AerialEfficiencyCard';
import HeadingInsights from '../components/match/HeadingInsights';
import type { ShotDetail, MatchAnalysis, AssistNetworkAnalysis, ShotTypeAnalysis, PassTypeAnalysis, HeadingAnalysis } from '../types/match';

const MatchDetailPage: React.FC = () => {
  const { matchId } = useParams<{ matchId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const ouid = searchParams.get('ouid');
  const [shotDetails, setShotDetails] = useState<ShotDetail[]>([]);
  const [analysis, setAnalysis] = useState<MatchAnalysis | null>(null);
  const [assistNetwork, setAssistNetwork] = useState<AssistNetworkAnalysis | null>(null);
  const [shotTypes, setShotTypes] = useState<ShotTypeAnalysis | null>(null);
  const [passTypes, setPassTypes] = useState<PassTypeAnalysis | null>(null);
  const [headingAnalysis, setHeadingAnalysis] = useState<HeadingAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMatchData = async () => {
      if (!matchId) return;

      try {
        setLoading(true);
        const [, heatmapData, analysisData, assistNetworkData, shotTypesData, passTypesData, headingData] = await Promise.all([
          getMatchDetail(matchId, ouid),
          getMatchHeatmap(matchId, ouid),
          getMatchAnalysis(matchId, ouid),
          getAssistNetwork(matchId, ouid),
          getShotTypes(matchId, ouid),
          getPassTypes(matchId, ouid),
          getHeadingAnalysis(matchId, ouid),
        ]);

        setShotDetails(heatmapData);
        setAnalysis(analysisData);
        setAssistNetwork(assistNetworkData);
        setShotTypes(shotTypesData);
        setPassTypes(passTypesData);
        setHeadingAnalysis(headingData);
      } catch (err: any) {
        console.error('Match detail fetch error:', err);
        setError(err.response?.data?.error || '경기 상세 정보를 불러올 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchMatchData();
  }, [matchId, ouid]);

  const getResultBadgeClass = (result: string) => {
    switch (result) {
      case 'win':
        return 'bg-accent-success/20 text-accent-success border-accent-success';
      case 'lose':
        return 'bg-accent-danger/20 text-accent-danger border-accent-danger';
      case 'draw':
        return 'bg-gray-500/20 text-gray-300 border-gray-500';
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500';
    }
  };

  const getResultText = (result: string) => {
    switch (result) {
      case 'win':
        return '승리';
      case 'lose':
        return '패배';
      case 'draw':
        return '무승부';
      default:
        return '-';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '경기 정보 불러오는 중...',
          '선수 퍼포먼스 분석 중...',
          '타임라인 데이터 계산 중...',
          '전술 인사이트 생성 중...',
        ]}
        estimatedDuration={5000}
        message="경기 상세 분석"
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
          <ErrorMessage message={error || '경기를 찾을 수 없습니다.'} />
        </div>
      </div>
    );
  }

  // Use match overview from analysis for accurate user perspective
  const matchOverview = analysis.match_overview;

  return (
    <div className="min-h-screen bg-dark-bg py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="text-accent-primary hover:text-blue-400 mb-6 flex items-center transition-colors"
        >
          ← 돌아가기
        </button>

        {/* Match Header */}
        <div className="bg-gradient-card rounded-lg shadow-dark-lg border border-dark-border p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <span
              className={`inline-flex items-center px-4 py-2 rounded-lg text-lg font-semibold border-2 ${getResultBadgeClass(
                matchOverview.result
              )}`}
            >
              {getResultText(matchOverview.result)}
            </span>
            <span className="text-sm text-gray-400">{formatDate(matchOverview.match_date)}</span>
          </div>

          {/* Score */}
          <div className="flex items-center justify-center py-6">
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-2">{matchOverview.user_nickname}</div>
              <div className="text-5xl font-bold text-white">{matchOverview.goals_for}</div>
            </div>
            <div className="mx-8 text-3xl text-gray-600">-</div>
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-2">
                {matchOverview.opponent_nickname || '상대'}
              </div>
              <div className="text-5xl font-bold text-white">{matchOverview.goals_against}</div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4 mb-6">
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark p-4 hover:border-chart-blue/50 transition-colors">
            <div className="text-sm text-gray-400 mb-1">점유율</div>
            <div className="text-2xl font-bold text-chart-blue">{matchOverview.possession}%</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark p-4 hover:border-chart-green/50 transition-colors">
            <div className="text-sm text-gray-400 mb-1">슈팅</div>
            <div className="text-2xl font-bold text-chart-green">{matchOverview.shots}</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark p-4 hover:border-chart-yellow/50 transition-colors">
            <div className="text-sm text-gray-400 mb-1">유효슈팅</div>
            <div className="text-2xl font-bold text-chart-yellow">{matchOverview.shots_on_target}</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark p-4 hover:border-chart-purple/50 transition-colors">
            <div className="text-sm text-gray-400 mb-1">패스 성공률</div>
            <div className="text-2xl font-bold text-chart-purple">{matchOverview.pass_success_rate}%</div>
          </div>
        </div>

        {/* Tactical Insights Section */}
        {analysis && analysis.tactical_insights && (
          <div className="mb-6">
            <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-3xl">⚽</span>
                전술 인사이트
              </h2>
              <TacticalInsightsPanel insights={analysis.tactical_insights} />
            </div>
          </div>
        )}

        {/* Timeline Analysis Section */}
        {analysis && analysis.timeline && analysis.timeline.timeline_data.length > 0 && (
          <div className="mb-6">
            <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <span className="text-3xl">📊</span>
                타임라인 분석
              </h2>
              <TimelineChart
                timelineData={analysis.timeline.timeline_data}
                keyMoments={analysis.timeline.key_moments}
                firstHalfXg={analysis.timeline.xg_by_period.first_half}
                secondHalfXg={analysis.timeline.xg_by_period.second_half}
              />
            </div>

            {/* Key Moments */}
            {analysis.timeline.key_moments.length > 0 && (
              <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
                <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                  <span className="text-3xl">⚡</span>
                  주요 순간
                </h2>
                <KeyMomentsList moments={analysis.timeline.key_moments} />
              </div>
            )}
          </div>
        )}

        {/* Player Performance Section */}
        {analysis && analysis.player_performances && analysis.player_performances.all_players.length > 0 && (
          <div className="mb-6">
            {/* Top 3 Performers */}
            {analysis.player_performances.top_performers.length > 0 && (
              <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
                <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                  <span className="text-3xl">⭐</span>
                  베스트 플레이어
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {analysis.player_performances.top_performers.map((player, index) => (
                    <PlayerCard key={player.spid} player={player} rank={index + 1} />
                  ))}
                </div>
              </div>
            )}

            {/* All Players Stats Table */}
            <PlayerStatsTable players={analysis.player_performances.all_players} title="전체 선수 퍼포먼스" />
          </div>
        )}

        {/* Assist Network Analysis */}
        {assistNetwork && assistNetwork.total_goals > 0 && (
          <div className="mb-6">
            <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-3xl">🤝</span>
                어시스트 네트워크 분석
              </h2>

              {/* Assist Stats */}
              <div className="mb-6">
                <AssistStats
                  assistTypes={assistNetwork.assist_types}
                  distanceStats={assistNetwork.assist_distance_stats}
                  totalGoals={assistNetwork.total_goals}
                  goalsWithAssist={assistNetwork.goals_with_assist}
                />
              </div>

              {/* Player Network */}
              {assistNetwork.player_network.length > 0 && (
                <div className="mb-6">
                  <AssistNetwork
                    playerNetwork={assistNetwork.player_network}
                    topPlaymakers={assistNetwork.top_playmakers}
                  />
                </div>
              )}

              {/* Assist Heatmap */}
              {assistNetwork.assist_heatmap.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <span className="text-2xl">📍</span>
                    어시스트 발생 위치
                  </h3>
                  <AssistHeatmap heatmapData={assistNetwork.assist_heatmap} />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Shot Type Analysis */}
        {shotTypes && shotTypes.total_shots > 0 && (
          <div className="mb-6">
            <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-3xl">⚽</span>
                슈팅 타입 분석
              </h2>

              {/* Shot Type Breakdown */}
              {shotTypes.type_breakdown.length > 0 && (
                <div className="mb-6">
                  <ShotTypeBreakdown typeBreakdown={shotTypes.type_breakdown} />
                </div>
              )}

              {/* Box Location Analysis */}
              <div className="mb-6">
                <BoxLocationAnalysis
                  insideBox={shotTypes.location_analysis.inside_box}
                  outsideBox={shotTypes.location_analysis.outside_box}
                />
              </div>

              {/* Insights and Post Hits */}
              <ShotTypeInsights
                insights={shotTypes.insights}
                postHits={shotTypes.post_hits}
              />
            </div>
          </div>
        )}

        {/* Pass Type Analysis */}
        {passTypes && passTypes.pass_breakdown.length > 0 && (
          <div className="mb-6">
            <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-3xl">🎯</span>
                패스 타입 분석
              </h2>

              {/* Play Style Card */}
              <div className="mb-6">
                <PlayStyleCard playStyle={passTypes.play_style} />
              </div>

              {/* Pass Type Radar Chart */}
              <div className="mb-6">
                <PassTypeRadarChart passBreakdown={passTypes.pass_breakdown} />
              </div>

              {/* Grid Layout: Breakdown Table + Insights */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                <PassTypeBreakdownTable
                  passBreakdown={passTypes.pass_breakdown}
                  totalStats={passTypes.total_stats}
                />
                <PassTypeInsights
                  insights={passTypes.insights}
                  diversityScore={passTypes.diversity_score}
                />
              </div>
            </div>
          </div>
        )}

        {/* Heading Analysis */}
        {headingAnalysis && headingAnalysis.heading_stats.total_headers > 0 && (
          <div className="mb-6">
            <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-3xl">🏐</span>
                헤딩 전문 분석
              </h2>

              {/* Grid Layout: Stats + Efficiency */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="lg:col-span-2">
                  <HeadingStatsCard
                    stats={headingAnalysis.heading_stats}
                    positions={headingAnalysis.heading_positions}
                    crossOrigins={headingAnalysis.cross_origins}
                  />
                </div>
                <div>
                  <AerialEfficiencyCard efficiency={headingAnalysis.efficiency_score} />
                </div>
              </div>

              {/* Insights */}
              <HeadingInsights insights={headingAnalysis.insights} />
            </div>
          </div>
        )}

        {/* Shot Heatmap */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-3xl">🎯</span>
            슈팅 히트맵
          </h2>
          {shotDetails.length > 0 ? (
            <div className="flex justify-center">
              <ShotHeatmap
                heatmapData={shotDetails.map((shot) => ({
                  x: shot.x,
                  y: shot.y,
                  result: shot.result,
                  shot_type: shot.shot_type,
                }))}
                width={800}
                height={520}
              />
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <p>이 경기의 슈팅 데이터가 없습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MatchDetailPage;
