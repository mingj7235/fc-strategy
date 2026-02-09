import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getStyleAnalysis, getUserMatches } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import PossessionTrendChart from '../components/charts/PossessionTrendChart';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Match, AggregateStats } from '../types/match';
import ShootingEfficiencyCard from '../components/stats/ShootingEfficiencyCard';
import GoalTimingPatternCard from '../components/stats/GoalTimingPatternCard';
import PassDistributionRadar from '../components/stats/PassDistributionRadar';
import HeadingSpecialistsCard from '../components/stats/HeadingSpecialistsCard';

const LIMIT_OPTIONS = [
  { value: 20, label: '20경기' },
  { value: 50, label: '50경기' },
  { value: 100, label: '100경기' },
];

interface PatternStats {
  possession: number;
  shots: number;
  shots_on_target: number;
  pass_success_rate: number;
  goals: number;
  goals_against: number;
}

interface EfficiencyMetrics {
  shot_accuracy: number;
  conversion_rate: number;
  goals_per_possession: number;
  possession_efficiency: string;
}

interface ConsistencyMetrics {
  goal_scoring_consistency: string;
  possession_consistency: string;
  goal_variance: number;
  possession_variance: number;
}

interface ComebackStats {
  avg_win_margin: number;
  avg_loss_margin: number;
  close_game_wins: number;
  close_game_losses: number;
  mental_strength: string;
}

interface StyleAnalysisData {
  total_matches: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  attack_pattern: string;
  possession_style: string;
  defensive_approach: string;
  tempo: string;
  win_patterns: PatternStats;
  loss_patterns: PatternStats;
  time_analysis: {
    early_game_performance: string;
    late_game_performance: string;
  };
  efficiency: EfficiencyMetrics;
  consistency: ConsistencyMetrics;
  comeback_stats: ComebackStats;
  insights: {
    keep: string[];
    stop: string[];
    action_items: string[];
  };
  aggregate_stats?: AggregateStats;  // NEW: Aggregate statistics
}

const StyleAnalysisPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<StyleAnalysisData | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState<number>(50);
  const [limit, setLimit] = useState<number>(20);

  useEffect(() => {
    const fetchData = async () => {
      if (!ouid) return;

      try {
        setLoading(true);
        const [analysisData, matchData] = await Promise.all([
          getStyleAnalysis(ouid, matchtype, limit),
          getUserMatches(ouid, matchtype, limit),
        ]);
        setAnalysis(analysisData);
        setMatches(matchData);
        setError('');
      } catch (err: any) {
        console.error('Style analysis fetch error:', err);
        setError(err.response?.data?.error || '플레이 스타일 분석 데이터를 불러올 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [ouid, matchtype, limit]);

  const getAttackPatternBadge = (pattern: string) => {
    switch (pattern) {
      case 'possession_based':
        return { text: '⚽ 점유율 기반', icon: '⚽', color: 'from-chart-blue/20 to-dark-card', border: 'border-chart-blue/40', textColor: 'text-chart-blue' };
      case 'counter_attack':
        return { text: '⚡ 역습 중심', icon: '⚡', color: 'from-chart-yellow/20 to-dark-card', border: 'border-chart-yellow/40', textColor: 'text-chart-yellow' };
      case 'direct_play':
        return { text: '🎯 직접 플레이', icon: '🎯', color: 'from-chart-red/20 to-dark-card', border: 'border-chart-red/40', textColor: 'text-chart-red' };
      case 'balanced':
        return { text: '⚖️ 균형형', icon: '⚖️', color: 'from-chart-green/20 to-dark-card', border: 'border-chart-green/40', textColor: 'text-chart-green' };
      default:
        return { text: pattern, icon: '❓', color: 'from-dark-card to-dark-hover', border: 'border-dark-border', textColor: 'text-gray-400' };
    }
  };

  const getPossessionStyleBadge = (style: string) => {
    switch (style) {
      case 'tiki_taka':
        return { text: '🌟 티키타카', icon: '🌟', color: 'from-chart-purple/20 to-dark-card', border: 'border-chart-purple/40', textColor: 'text-chart-purple' };
      case 'high_possession':
        return { text: '📊 높은 점유율', icon: '📊', color: 'from-chart-blue/20 to-dark-card', border: 'border-chart-blue/40', textColor: 'text-chart-blue' };
      case 'counter_based':
        return { text: '⚡ 역습형', icon: '⚡', color: 'from-chart-yellow/20 to-dark-card', border: 'border-chart-yellow/40', textColor: 'text-chart-yellow' };
      case 'balanced':
        return { text: '⚖️ 균형형', icon: '⚖️', color: 'from-chart-green/20 to-dark-card', border: 'border-chart-green/40', textColor: 'text-chart-green' };
      case 'direct':
        return { text: '🎯 직접형', icon: '🎯', color: 'from-chart-red/20 to-dark-card', border: 'border-chart-red/40', textColor: 'text-chart-red' };
      default:
        return { text: style, icon: '❓', color: 'from-dark-card to-dark-hover', border: 'border-dark-border', textColor: 'text-gray-400' };
    }
  };

  const getDefensiveBadge = (approach: string) => {
    switch (approach) {
      case 'solid':
        return { text: '🛡️ 견고', icon: '🛡️', color: 'from-chart-green/20 to-dark-card', border: 'border-chart-green/40', textColor: 'text-chart-green' };
      case 'aggressive':
        return { text: '🔥 공격적', icon: '🔥', color: 'from-chart-red/20 to-dark-card', border: 'border-chart-red/40', textColor: 'text-chart-red' };
      case 'vulnerable':
        return { text: '⚠️ 취약', icon: '⚠️', color: 'from-chart-yellow/20 to-dark-card', border: 'border-chart-yellow/40', textColor: 'text-chart-yellow' };
      case 'balanced':
        return { text: '⚖️ 균형형', icon: '⚖️', color: 'from-chart-blue/20 to-dark-card', border: 'border-chart-blue/40', textColor: 'text-chart-blue' };
      default:
        return { text: approach, icon: '❓', color: 'from-dark-card to-dark-hover', border: 'border-dark-border', textColor: 'text-gray-400' };
    }
  };

  const getTempoBadge = (tempo: string) => {
    switch (tempo) {
      case 'fast':
        return { text: '⚡ 빠름', icon: '⚡', color: 'from-chart-red/20 to-dark-card', border: 'border-chart-red/40', textColor: 'text-chart-red' };
      case 'slow':
        return { text: '🐢 느림', icon: '🐢', color: 'from-chart-blue/20 to-dark-card', border: 'border-chart-blue/40', textColor: 'text-chart-blue' };
      case 'moderate':
        return { text: '➡️ 보통', icon: '➡️', color: 'from-chart-green/20 to-dark-card', border: 'border-chart-green/40', textColor: 'text-chart-green' };
      default:
        return { text: tempo, icon: '❓', color: 'from-dark-card to-dark-hover', border: 'border-dark-border', textColor: 'text-gray-400' };
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={[
          '경기 기록 불러오는 중...',
          '플레이 스타일 분류 중...',
          '승패 패턴 분석 중...',
          '전술 인사이트 생성 중...',
        ]}
        estimatedDuration={6000}
        message="플레이 스타일 분석"
      />
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-dark-bg p-8">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => navigate(`/user/${ouid}`)}
            className="text-accent-primary hover:text-blue-400 mb-4 transition-colors"
          >
            ← 돌아가기
          </button>
          <ErrorMessage message={error || '분석 데이터를 찾을 수 없습니다.'} />
        </div>
      </div>
    );
  }

  const attackBadge = getAttackPatternBadge(analysis.attack_pattern);
  const possessionBadge = getPossessionStyleBadge(analysis.possession_style);
  const defensiveBadge = getDefensiveBadge(analysis.defensive_approach);
  const tempoBadge = getTempoBadge(analysis.tempo);

  // Prepare comparison chart data
  const comparisonData = [
    {
      category: '점유율',
      승리: analysis.win_patterns.possession,
      패배: analysis.loss_patterns.possession,
    },
    {
      category: '슈팅',
      승리: analysis.win_patterns.shots,
      패배: analysis.loss_patterns.shots,
    },
    {
      category: '유효슈팅',
      승리: analysis.win_patterns.shots_on_target,
      패배: analysis.loss_patterns.shots_on_target,
    },
    {
      category: '패스 성공률',
      승리: analysis.win_patterns.pass_success_rate,
      패배: analysis.loss_patterns.pass_success_rate,
    },
    {
      category: '득점',
      승리: analysis.win_patterns.goals,
      패배: analysis.loss_patterns.goals,
    },
  ];

  return (
    <div className="min-h-screen bg-dark-bg py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(`/user/${ouid}`)}
            className="text-accent-primary hover:text-blue-400 mb-4 flex items-center transition-colors"
          >
            ← 돌아가기
          </button>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                <span>📈</span>
                플레이 스타일 분석
              </h1>
              <p className="text-gray-400 mt-2">최근 {limit}경기 종합 전술 분석</p>
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

        {/* Match Type Selector */}
        <div className="mb-6 flex items-center gap-3">
          <label className="text-sm text-gray-400 font-medium">경기 타입:</label>
          <MatchTypeSelector value={matchtype} onChange={setMatchtype} />
        </div>

        {/* Record Summary */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-gradient-to-br from-dark-card to-dark-hover border border-dark-border rounded-lg p-4 hover:border-accent-primary/50 transition-colors">
            <div className="text-xs text-gray-400 mb-1">총 경기</div>
            <div className="text-3xl font-bold text-white">{analysis.total_matches}</div>
          </div>
          <div className="bg-gradient-to-br from-chart-green/20 to-dark-card border border-chart-green/30 rounded-lg p-4 hover:border-chart-green/60 transition-colors">
            <div className="text-xs text-gray-400 mb-1">승</div>
            <div className="text-3xl font-bold text-chart-green">{analysis.wins}</div>
          </div>
          <div className="bg-gradient-to-br from-chart-red/20 to-dark-card border border-chart-red/30 rounded-lg p-4 hover:border-chart-red/60 transition-colors">
            <div className="text-xs text-gray-400 mb-1">패</div>
            <div className="text-3xl font-bold text-chart-red">{analysis.losses}</div>
          </div>
          <div className="bg-gradient-to-br from-chart-yellow/20 to-dark-card border border-chart-yellow/30 rounded-lg p-4 hover:border-chart-yellow/60 transition-colors">
            <div className="text-xs text-gray-400 mb-1">무</div>
            <div className="text-3xl font-bold text-chart-yellow">{analysis.draws}</div>
          </div>
          <div className="bg-gradient-to-br from-accent-primary/20 to-dark-card border border-accent-primary/30 rounded-lg p-4 hover:border-accent-primary/60 transition-colors">
            <div className="text-xs text-gray-400 mb-1">승률</div>
            <div className="text-3xl font-bold text-accent-primary">{analysis.win_rate}%</div>
          </div>
        </div>

        {/* Tactical Style Badges */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>⚽</span>
            전술 스타일 분류
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-400 mb-2">공격 패턴</div>
              <div className={`bg-gradient-to-br ${attackBadge.color} border ${attackBadge.border} rounded-lg px-4 py-3 text-center`}>
                <span className={`text-lg font-bold ${attackBadge.textColor}`}>
                  {attackBadge.text}
                </span>
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">점유 스타일</div>
              <div className={`bg-gradient-to-br ${possessionBadge.color} border ${possessionBadge.border} rounded-lg px-4 py-3 text-center`}>
                <span className={`text-lg font-bold ${possessionBadge.textColor}`}>
                  {possessionBadge.text}
                </span>
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">수비 성향</div>
              <div className={`bg-gradient-to-br ${defensiveBadge.color} border ${defensiveBadge.border} rounded-lg px-4 py-3 text-center`}>
                <span className={`text-lg font-bold ${defensiveBadge.textColor}`}>
                  {defensiveBadge.text}
                </span>
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-2">경기 템포</div>
              <div className={`bg-gradient-to-br ${tempoBadge.color} border ${tempoBadge.border} rounded-lg px-4 py-3 text-center`}>
                <span className={`text-lg font-bold ${tempoBadge.textColor}`}>
                  {tempoBadge.text}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Efficiency Metrics */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>📊</span>
            효율성 지표
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">슈팅 정확도</div>
              <div className="text-2xl font-bold text-chart-blue">
                {analysis.efficiency.shot_accuracy.toFixed(1)}%
              </div>
            </div>
            <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">골 전환율</div>
              <div className="text-2xl font-bold text-chart-green">
                {analysis.efficiency.conversion_rate.toFixed(1)}%
              </div>
            </div>
            <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">점유율당 득점</div>
              <div className="text-2xl font-bold text-chart-purple">
                {analysis.efficiency.goals_per_possession.toFixed(2)}
              </div>
            </div>
            <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">점유 효율성</div>
              <div className={`text-xl font-bold ${
                analysis.efficiency.possession_efficiency === 'high' ? 'text-chart-green' :
                analysis.efficiency.possession_efficiency === 'moderate' ? 'text-chart-yellow' : 'text-chart-red'
              }`}>
                {analysis.efficiency.possession_efficiency === 'high' ? '🔥 높음' :
                 analysis.efficiency.possession_efficiency === 'moderate' ? '👍 보통' : '⚠️ 낮음'}
              </div>
            </div>
          </div>
        </div>

        {/* Win vs Loss Comparison */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>📈</span>
            승패 패턴 비교
          </h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="category" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Bar dataKey="승리" fill="#10b981" />
                <Bar dataKey="패배" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="bg-gradient-to-br from-chart-green/20 to-dark-hover border border-chart-green/30 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-chart-green mb-3">승리 시 평균</h3>
              <div className="space-y-2 text-sm text-gray-300">
                <div className="flex justify-between">
                  <span>점유율:</span>
                  <span className="font-bold">{analysis.win_patterns.possession.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>슈팅:</span>
                  <span className="font-bold">{analysis.win_patterns.shots.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span>득점:</span>
                  <span className="font-bold">{analysis.win_patterns.goals.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span>실점:</span>
                  <span className="font-bold">{analysis.win_patterns.goals_against.toFixed(1)}</span>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-chart-red/20 to-dark-hover border border-chart-red/30 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-chart-red mb-3">패배 시 평균</h3>
              <div className="space-y-2 text-sm text-gray-300">
                <div className="flex justify-between">
                  <span>점유율:</span>
                  <span className="font-bold">{analysis.loss_patterns.possession.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>슈팅:</span>
                  <span className="font-bold">{analysis.loss_patterns.shots.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span>득점:</span>
                  <span className="font-bold">{analysis.loss_patterns.goals.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span>실점:</span>
                  <span className="font-bold">{analysis.loss_patterns.goals_against.toFixed(1)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Consistency & Comeback Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Consistency */}
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>📈</span>
              일관성 분석
            </h2>
            <div className="space-y-4">
              <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">득점 일관성</div>
                <div className={`text-xl font-bold ${
                  analysis.consistency.goal_scoring_consistency === 'high' ? 'text-chart-green' :
                  analysis.consistency.goal_scoring_consistency === 'moderate' ? 'text-chart-yellow' : 'text-chart-red'
                }`}>
                  {analysis.consistency.goal_scoring_consistency === 'high' ? '🎯 높음' :
                   analysis.consistency.goal_scoring_consistency === 'moderate' ? '➡️ 보통' : '⚠️ 낮음'}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  득점 분산: {analysis.consistency.goal_variance.toFixed(2)}
                </div>
              </div>
              <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">점유율 일관성</div>
                <div className={`text-xl font-bold ${
                  analysis.consistency.possession_consistency === 'high' ? 'text-chart-green' :
                  analysis.consistency.possession_consistency === 'moderate' ? 'text-chart-yellow' : 'text-chart-red'
                }`}>
                  {analysis.consistency.possession_consistency === 'high' ? '🎯 높음' :
                   analysis.consistency.possession_consistency === 'moderate' ? '➡️ 보통' : '⚠️ 낮음'}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  점유율 분산: {analysis.consistency.possession_variance.toFixed(1)}%
                </div>
              </div>
            </div>
          </div>

          {/* Comeback Potential */}
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>💪</span>
              역전력 분석
            </h2>
            <div className="space-y-4">
              <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">평균 승리 골 차</div>
                <div className="text-3xl font-bold text-chart-green">
                  +{analysis.comeback_stats.avg_win_margin.toFixed(1)}
                </div>
              </div>
              <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">평균 패배 골 차</div>
                <div className="text-3xl font-bold text-chart-red">
                  -{analysis.comeback_stats.avg_loss_margin.toFixed(1)}
                </div>
              </div>
              <div className="bg-dark-hover border border-dark-border rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">접전 승부 (1골 차)</div>
                <div className="flex items-center justify-between">
                  <div className="text-center">
                    <div className="text-xl font-bold text-chart-green">
                      {analysis.comeback_stats.close_game_wins}승
                    </div>
                  </div>
                  <div className="text-gray-500">vs</div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-chart-red">
                      {analysis.comeback_stats.close_game_losses}패
                    </div>
                  </div>
                </div>
                <div className={`text-sm text-center mt-3 font-semibold ${
                  analysis.comeback_stats.mental_strength === 'strong' ? 'text-chart-green' : 'text-chart-yellow'
                }`}>
                  {analysis.comeback_stats.mental_strength === 'strong' ? '💪 강한 멘탈' : '🎲 멘탈 보강 필요'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Possession Trend */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
          <PossessionTrendChart
            matches={matches.map((m) => ({
              result: m.result,
              possession: m.possession,
              shots: m.shots ?? 0,
              shots_on_target: m.shots_on_target ?? 0,
              goals: m.goals_for,
              pass_success_rate: typeof m.pass_success_rate === 'string' ? parseFloat(m.pass_success_rate) : (m.pass_success_rate ?? 0),
            }))}
          />
        </div>

        {/* Aggregate Statistics */}
        {analysis.aggregate_stats && (
          <>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <span>📊</span>
                통합 통계 분석
              </h2>
              <p className="text-sm text-gray-400 mt-2">
                {limit}경기의 데이터를 종합한 통계적 분석입니다
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Shooting Efficiency */}
              {analysis.aggregate_stats.shooting_efficiency && (
                <ShootingEfficiencyCard efficiency={analysis.aggregate_stats.shooting_efficiency} />
              )}

              {/* Goal Timing Patterns */}
              {analysis.aggregate_stats.goal_patterns && (
                <GoalTimingPatternCard patterns={analysis.aggregate_stats.goal_patterns} />
              )}

              {/* Pass Distribution */}
              {analysis.aggregate_stats.pass_distribution && (
                <PassDistributionRadar distribution={analysis.aggregate_stats.pass_distribution} />
              )}

              {/* Heading Specialists */}
              {analysis.aggregate_stats.heading_specialists && (
                <HeadingSpecialistsCard specialists={analysis.aggregate_stats.heading_specialists} />
              )}
            </div>
          </>
        )}

        {/* Professional Insights - Keep-Stop-Action Framework */}
        <div className="bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg shadow-dark-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <span>💡</span>
            전문가 전략 분석
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

          {(!analysis.insights.keep || analysis.insights.keep.length === 0) &&
           (!analysis.insights.stop || analysis.insights.stop.length === 0) &&
           (!analysis.insights.action_items || analysis.insights.action_items.length === 0) && (
            <div className="text-center py-8 text-gray-400">
              <p>분석 인사이트가 없습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StyleAnalysisPage;
