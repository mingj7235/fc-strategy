import React, { useEffect, useState } from 'react';
import PlayerAvatar from '../components/common/PlayerAvatar';
import { useParams, useNavigate } from 'react-router-dom';
import { getPassAnalysis } from '../services/api';
import type { PassAnalysisData } from '../types/passAnalysis';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const LIMIT_OPTIONS = [
  { value: 10, label: '10경기' },
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const CHART_COLORS = {
  blue: '#3b82f6',
  green: '#10b981',
  yellow: '#f59e0b',
  red: '#ef4444',
  purple: '#a855f7',
};

const PassAnalysisPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<PassAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState<number>(50);
  const [limit, setLimit] = useState<number>(20);

  useEffect(() => {
    fetchAnalysis();
  }, [ouid, matchtype, limit]);

  const fetchAnalysis = async () => {
    if (!ouid) return;

    setLoading(true);
    setError('');

    try {
      const data = await getPassAnalysis(ouid, matchtype, limit);
      setAnalysis(data);
    } catch (err: any) {
      console.error('Pass analysis fetch error:', err);
      setError(err.response?.data?.error || '패스 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '패스 데이터 수집 중...',
          '패스 네트워크 분석 중...',
          '다양성 지표 계산 중...',
          '인사이트 생성 중...',
        ]}
        estimatedDuration={5500}
        message="패스 분석"
      />
    );
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!analysis) {
    return (
      <div className="min-h-screen bg-dark-bg text-white p-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-3xl font-bold mb-4">패스 분석</h1>
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

  // Prepare chart data
  const topPassersChart = analysis.pass_network.top_passers.map(p => ({
    name: p.player_name,
    시도: p.pass_attempts,
    성공: p.pass_success,
    정확도: p.pass_success_rate,
  }));

  const getRiskRewardColor = (profile: string) => {
    if (profile === 'balanced') return CHART_COLORS.green;
    if (profile === 'aggressive') return CHART_COLORS.red;
    if (profile === 'conservative') return CHART_COLORS.blue;
    return CHART_COLORS.yellow;
  };

  const getRiskRewardLabel = (profile: string) => {
    if (profile === 'balanced') return '균형잡힌';
    if (profile === 'aggressive') return '공격적';
    if (profile === 'conservative') return '보수적';
    return '알 수 없음';
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
                패스 분석
              </h1>
              <p className="text-gray-400 mt-1">
                xA, 킬패스, 전진 패스, 패스 네트워크 분석
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
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-400 font-medium">경기 타입:</label>
              <MatchTypeSelector value={matchtype} onChange={setMatchtype} />
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

            <div className="ml-auto text-sm text-gray-400">
              {analysis.matches_analyzed}경기 분석
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto p-8">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <div className="text-gray-400 text-sm mb-2">총 패스 시도</div>
            <div className="text-3xl font-bold text-white">{analysis.overall_stats.total_attempts}</div>
            <div className="text-sm text-chart-green mt-1">
              성공: {analysis.overall_stats.total_success}
            </div>
          </div>

          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <div className="text-gray-400 text-sm mb-2">패스 정확도</div>
            <div className="text-3xl font-bold text-accent-primary">{analysis.overall_stats.accuracy}%</div>
            <div className={`text-sm mt-1 ${
              analysis.overall_stats.accuracy >= 85 ? 'text-chart-green' :
              analysis.overall_stats.accuracy >= 75 ? 'text-chart-yellow' : 'text-chart-red'
            }`}>
              {analysis.overall_stats.accuracy >= 85 ? '우수' :
               analysis.overall_stats.accuracy >= 75 ? '양호' : '개선 필요'}
            </div>
          </div>

          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <div className="text-gray-400 text-sm mb-2">총 어시스트</div>
            <div className="text-3xl font-bold text-chart-green">{analysis.key_pass_analysis.total_assists}</div>
            <div className="text-sm text-gray-300 mt-1">
              xA: {analysis.key_pass_analysis.estimated_xa.toFixed(2)}
            </div>
          </div>

          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <div className="text-gray-400 text-sm mb-2">전진 패스</div>
            <div className="text-3xl font-bold text-chart-blue">{analysis.progressive_passing.estimated_progressive_passes}</div>
            <div className="text-sm text-gray-300 mt-1">
              비율: {analysis.progressive_passing.progressive_rate}%
            </div>
          </div>
        </div>

        {/* Key Pass Analysis */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>🎯</span>
            킬패스 & xA 분석
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">예상 킬패스</div>
              <div className="text-2xl font-bold text-white mb-2">{analysis.key_pass_analysis.estimated_key_passes}</div>
              <div className="text-xs text-gray-300">
                경기당 {(analysis.key_pass_analysis.estimated_key_passes / analysis.matches_analyzed).toFixed(1)}개
              </div>
            </div>

            <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">xA (기대 어시스트)</div>
              <div className="text-2xl font-bold text-accent-primary mb-2">{analysis.key_pass_analysis.estimated_xa.toFixed(2)}</div>
              <div className="text-xs text-gray-300">
                킬패스당 xA: {analysis.key_pass_analysis.xa_per_key_pass.toFixed(2)}
              </div>
            </div>

            <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">어시스트 전환율</div>
              <div className="text-2xl font-bold text-chart-green mb-2">{analysis.key_pass_analysis.conversion_rate.toFixed(1)}%</div>
              <div className="text-xs text-gray-300">
                {analysis.key_pass_analysis.conversion_rate >= 30 ? '우수한 전환율' :
                 analysis.key_pass_analysis.conversion_rate >= 20 ? '양호한 전환율' : '개선 필요'}
              </div>
            </div>
          </div>
        </div>

        {/* Top Passers */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>👥</span>
            톱 패서
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topPassersChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1f2e',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="시도" fill={CHART_COLORS.blue} />
              <Bar dataKey="성공" fill={CHART_COLORS.green} />
            </BarChart>
          </ResponsiveContainer>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            {analysis.pass_network.top_passers.map((passer, idx) => (
              <div key={`${passer.spid}-${idx}`} className="bg-dark-hover border border-dark-border rounded-lg p-4 hover:border-accent-primary/50 transition-all relative">
                {/* Rank Badge */}
                <div className={`absolute -top-2 -right-2 w-8 h-8 rounded-full ${
                  idx === 0 ? 'bg-gradient-to-br from-yellow-400 to-orange-500' :
                  idx === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500' :
                  'bg-gradient-to-br from-orange-400 to-orange-600'
                } flex items-center justify-center text-white font-bold text-sm shadow-lg`}>
                  #{idx + 1}
                </div>

                <div className="flex items-center gap-3 mb-3">
                  {/* Player Image */}
                  <PlayerAvatar
                    imageUrl={passer.image_url}
                    playerName={passer.player_name}
                    size={64}
                    className="bg-gradient-to-br from-dark-bg to-dark-card rounded-lg p-1"
                  />

                  {/* Player Info */}
                  <div className="flex-1">
                    <div className="font-semibold text-white text-sm mb-1">{passer.player_name}</div>
                    {(passer.season_img || passer.season_name) && (
                      <div title={passer.season_name}>
                        {passer.season_img ? (
                          <img src={passer.season_img} alt={passer.season_name} className="h-4 object-contain" />
                        ) : (
                          <div className="inline-block bg-purple-500/20 border border-purple-500/30 text-purple-300 text-[10px] px-2 py-0.5 rounded-full font-medium">
                            {passer.season_name}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Stats */}
                <div className="text-sm text-gray-300 space-y-1">
                  <div>패스 시도: <span className="text-white font-semibold">{passer.pass_attempts}</span></div>
                  <div>패스 성공: <span className="text-white font-semibold">{passer.pass_success}</span></div>
                  <div className="text-accent-primary font-semibold">정확도: {passer.pass_success_rate}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Efficiency & Profile */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Efficiency */}
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>⚡</span>
              패스 효율성
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-dark-hover rounded-lg">
                <span className="text-gray-300">효율성 점수</span>
                <span className="text-2xl font-bold text-accent-primary">
                  {analysis.efficiency.efficiency_score.toFixed(1)}
                </span>
              </div>

              <div className="flex items-center justify-between p-4 bg-dark-hover rounded-lg">
                <span className="text-gray-300">어시스트당 패스</span>
                <span className="text-xl font-bold text-white">
                  {analysis.efficiency.passes_per_assist.toFixed(1)}
                </span>
              </div>

              <div className="flex items-center justify-between p-4 bg-dark-hover rounded-lg">
                <span className="text-gray-300">어시스트 비율</span>
                <span className="text-xl font-bold text-chart-green">
                  {analysis.efficiency.assist_rate.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          {/* Risk/Reward Profile */}
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>📊</span>
              플레이 스타일
            </h2>
            <div className="flex flex-col items-center justify-center h-64">
              <div
                className={`w-32 h-32 rounded-full flex items-center justify-center mb-4`}
                style={{
                  backgroundColor: getRiskRewardColor(analysis.efficiency.risk_reward_profile) + '20',
                  border: `3px solid ${getRiskRewardColor(analysis.efficiency.risk_reward_profile)}`
                }}
              >
                <span className="text-4xl font-bold" style={{ color: getRiskRewardColor(analysis.efficiency.risk_reward_profile) }}>
                  {getRiskRewardLabel(analysis.efficiency.risk_reward_profile)}
                </span>
              </div>
              <div className="text-center text-gray-300 text-sm max-w-md">
                {analysis.efficiency.risk_reward_profile === 'balanced' &&
                  '정확도와 창조성의 균형이 잘 잡혀있습니다'}
                {analysis.efficiency.risk_reward_profile === 'aggressive' &&
                  '위험을 감수하며 공격적인 패스를 시도합니다'}
                {analysis.efficiency.risk_reward_profile === 'conservative' &&
                  '안전한 패스를 선호하는 보수적인 스타일입니다'}
                {analysis.efficiency.risk_reward_profile === 'unknown' &&
                  '패스 스타일을 분석하기에 데이터가 부족합니다'}
              </div>
            </div>
          </div>
        </div>

        {/* Insights - Keep-Stop-Action */}
        <div className="bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg shadow-dark-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <span>💡</span>
            전문가 패스 분석
          </h2>

          <div className="grid gap-6 md:grid-cols-1">
            {/* KEEP Section */}
            {analysis.insights.keep && analysis.insights.keep.length > 0 && (
              <div className="bg-dark-card border border-chart-green/30 rounded-lg p-5">
                <h3 className="text-lg font-bold text-chart-green mb-3 flex items-center gap-2">
                  <span>✅</span>
                  KEEP - 유지하세요
                </h3>
                <div className="space-y-2">
                  {analysis.insights.keep.map((item, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-chart-green/5 border border-chart-green/20 rounded-lg">
                      <div className="flex-shrink-0 w-6 h-6 bg-chart-green text-dark-bg rounded-full flex items-center justify-center text-xs font-bold">
                        {index + 1}
                      </div>
                      <p className="text-gray-200 leading-relaxed text-sm">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* STOP Section */}
            {analysis.insights.stop && analysis.insights.stop.length > 0 && (
              <div className="bg-dark-card border border-chart-red/30 rounded-lg p-5">
                <h3 className="text-lg font-bold text-chart-red mb-3 flex items-center gap-2">
                  <span>🛑</span>
                  STOP - 멈춰야 할 것들
                </h3>
                <div className="space-y-2">
                  {analysis.insights.stop.map((item, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-chart-red/5 border border-chart-red/20 rounded-lg">
                      <div className="flex-shrink-0 w-6 h-6 bg-chart-red text-white rounded-full flex items-center justify-center text-xs font-bold">
                        {index + 1}
                      </div>
                      <p className="text-gray-200 leading-relaxed text-sm">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ACTION ITEMS Section */}
            {analysis.insights.action_items && analysis.insights.action_items.length > 0 && (
              <div className="bg-dark-card border border-chart-blue/30 rounded-lg p-5">
                <h3 className="text-lg font-bold text-chart-blue mb-3 flex items-center gap-2">
                  <span>🎯</span>
                  ACTION ITEMS - 개선 방안
                </h3>
                <div className="space-y-2">
                  {analysis.insights.action_items.map((item, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-chart-blue/5 border border-chart-blue/20 rounded-lg">
                      <div className="flex-shrink-0 w-6 h-6 bg-chart-blue text-white rounded-full flex items-center justify-center text-xs font-bold">
                        {index + 1}
                      </div>
                      <p className="text-gray-200 leading-relaxed text-sm">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PassAnalysisPage;
