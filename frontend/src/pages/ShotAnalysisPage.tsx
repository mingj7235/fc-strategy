import React, { useEffect, useState } from 'react';
import PlayerAvatar from '../components/common/PlayerAvatar';
import { useParams, useNavigate } from 'react-router-dom';
import { getShotAnalysis } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import ShotHeatmap from '../components/visualizations/ShotHeatmap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const LIMIT_OPTIONS = [
  { value: 20, label: '20경기' },
  { value: 50, label: '50경기' },
  { value: 100, label: '100경기' },
];

const CHART_COLORS = {
  blue: '#3b82f6',
  green: '#10b981',
  yellow: '#f59e0b',
  red: '#ef4444',
  purple: '#a855f7',
  pink: '#ec4899',
};

interface ZoneStats {
  shots: number;
  goals: number;
  xg: number;
  efficiency: number;
  conversion_rate: number;
}

interface ShotTypeStats {
  count: number;
  goals: number;
  conversion: number;
  xg: number;
}

interface DistanceStats {
  shots: number;
  goals: number;
  conversion: number;
  range?: string;
}

interface AngleStats {
  shots: number;
  goals: number;
  conversion: number;
}

interface TopScorer {
  spid: number;
  player_name: string;
  image_url: string;
  shots: number;
  goals: number;
  on_target: number;
  conversion_rate: number;
  shot_accuracy: number;
  xg_total: number;
  goals_over_xg: number;
}

interface ShotAnalysisData {
  total_shots: number;
  goals: number;
  on_target: number;
  off_target: number;
  blocked: number;
  shot_accuracy: number;
  conversion_rate: number;
  xg_metrics: {
    xg_total: number;
    xg_per_shot: number;
    goals_over_xg: number;
    finishing_quality: string;
  };
  big_chances: {
    total: number;
    scored: number;
    conversion_rate: number;
  };
  heatmap_data: Array<{
    x: number;
    y: number;
    result: 'goal' | 'on_target' | 'off_target' | 'blocked';
    shot_type: number;
    xg: number;
  }>;
  zone_analysis: {
    inside_box: ZoneStats;
    outside_box: ZoneStats;
    center: ZoneStats;
    left: ZoneStats;
    right: ZoneStats;
    six_yard: ZoneStats;
  };
  shot_types: {
    [key: string]: ShotTypeStats;
  };
  distance_analysis: {
    [key: string]: DistanceStats;
  };
  angle_analysis: {
    [key: string]: AngleStats;
  };
  top_scorers: TopScorer[];
  feedback: {
    keep: string[];
    stop: string[];
    action_items: string[];
  };
}

const ShotAnalysisPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<ShotAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState<number>(50);
  const [limit, setLimit] = useState<number>(20);

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!ouid) return;

      try {
        setLoading(true);
        const data = await getShotAnalysis(ouid, matchtype, limit);
        setAnalysis(data);
        setError('');
      } catch (err: any) {
        console.error('Shot analysis fetch error:', err);
        setError(err.response?.data?.error || '슈팅 분석 데이터를 불러올 수 없습니다.');
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
          '슈팅 데이터 수집 중...',
          'xG 메트릭 계산 중...',
          '위치별 분석 진행 중...',
          '피드백 생성 중...',
        ]}
        estimatedDuration={6000}
        message="슈팅 분석"
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

  // Prepare chart data
  const zoneChartData = Object.entries(analysis.zone_analysis || {}).map(([zone, stats]) => ({
    name: zone === 'inside_box' ? '박스 안' :
          zone === 'outside_box' ? '박스 밖' :
          zone === 'center' ? '중앙' :
          zone === 'left' ? '좌측' :
          zone === 'right' ? '우측' : '골문 앞',
    슈팅: stats?.shots || 0,
    골: stats?.goals || 0,
    전환율: stats?.conversion_rate || 0,
  }));

  const shotTypeChartData = Object.entries(analysis.shot_types || {}).map(([type, stats]) => ({
    name: type,
    슈팅: stats?.count || 0,
    골: stats?.goals || 0,
    전환율: stats?.conversion || 0,
  }));

  const distanceChartData = Object.entries(analysis.distance_analysis || {}).map(([distance, stats]) => ({
    name: distance === 'very_close' ? '초근거리' :
          distance === 'inside_box' ? '박스 안' :
          distance === 'edge_of_box' ? '박스 경계' : '장거리',
    슈팅: stats?.shots || 0,
    골: stats?.goals || 0,
    전환율: stats?.conversion || 0,
  }));

  const angleChartData = Object.entries(analysis.angle_analysis || {}).map(([angle, stats]) => ({
    name: angle === 'central' ? '중앙' :
          angle === 'semi_central' ? '준중앙' : '측면',
    슈팅: stats?.shots || 0,
    골: stats?.goals || 0,
    전환율: stats?.conversion || 0,
  }));

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
                <span>⚽</span>
                슈팅 분석
              </h1>
              <p className="text-gray-400 mt-2">최근 {limit}경기 종합 슈팅 분석</p>
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

        {/* Core Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-gradient-to-br from-dark-card to-dark-hover border border-dark-border rounded-lg p-4 hover:border-accent-primary/50 transition-colors">
            <div className="text-xs text-gray-400 mb-1">총 슈팅</div>
            <div className="text-3xl font-bold text-white">{analysis.total_shots}</div>
          </div>
          <div className="bg-gradient-to-br from-chart-green/20 to-dark-card border border-chart-green/30 rounded-lg p-4 hover:border-chart-green/60 transition-colors">
            <div className="text-xs text-gray-400 mb-1">골</div>
            <div className="text-3xl font-bold text-chart-green">{analysis.goals}</div>
          </div>
          <div className="bg-gradient-to-br from-chart-blue/20 to-dark-card border border-chart-blue/30 rounded-lg p-4 hover:border-chart-blue/60 transition-colors">
            <div className="text-xs text-gray-400 mb-1">슈팅 정확도</div>
            <div className="text-2xl font-bold text-chart-blue">
              {analysis.shot_accuracy.toFixed(1)}%
            </div>
          </div>
          <div className="bg-gradient-to-br from-chart-purple/20 to-dark-card border border-chart-purple/30 rounded-lg p-4 hover:border-chart-purple/60 transition-colors">
            <div className="text-xs text-gray-400 mb-1">골 전환율</div>
            <div className="text-2xl font-bold text-chart-purple">
              {analysis.conversion_rate.toFixed(1)}%
            </div>
          </div>
          <div className="bg-gradient-to-br from-chart-yellow/20 to-dark-card border border-chart-yellow/30 rounded-lg p-4 hover:border-chart-yellow/60 transition-colors">
            <div className="text-xs text-gray-400 mb-1">빅찬스 전환</div>
            <div className="text-2xl font-bold text-chart-yellow">
              {analysis.big_chances?.scored || 0}/{analysis.big_chances?.total || 0}
            </div>
          </div>
        </div>

        {/* xG Metrics Panel */}
        <div className="bg-gradient-to-br from-accent-primary/20 to-dark-card border border-accent-primary/30 rounded-lg shadow-dark-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>📊</span>
            Expected Goals (xG) 분석
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-dark-card/50 border border-dark-border rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">총 xG</div>
              <div className="text-3xl font-bold text-accent-primary">
                {(analysis.xg_metrics?.xg_total || 0).toFixed(2)}
              </div>
            </div>
            <div className="bg-dark-card/50 border border-dark-border rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">슈팅당 xG</div>
              <div className="text-3xl font-bold text-chart-blue">
                {(analysis.xg_metrics?.xg_per_shot || 0).toFixed(3)}
              </div>
            </div>
            <div className="bg-dark-card/50 border border-dark-border rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">xG 대비 득점</div>
              <div className={`text-3xl font-bold ${
                (analysis.xg_metrics?.goals_over_xg || 0) > 0 ? 'text-chart-green' : 'text-chart-red'
              }`}>
                {(analysis.xg_metrics?.goals_over_xg || 0) > 0 ? '+' : ''}{(analysis.xg_metrics?.goals_over_xg || 0).toFixed(2)}
              </div>
            </div>
            <div className="bg-dark-card/50 border border-dark-border rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">마무리 능력</div>
              <div className={`text-xl font-bold ${
                analysis.xg_metrics?.finishing_quality === 'excellent' ? 'text-chart-green' :
                analysis.xg_metrics?.finishing_quality === 'good' ? 'text-chart-blue' :
                analysis.xg_metrics?.finishing_quality === 'average' ? 'text-chart-yellow' :
                'text-chart-red'
              }`}>
                {analysis.xg_metrics?.finishing_quality === 'excellent' ? '🔥 탁월' :
                 analysis.xg_metrics?.finishing_quality === 'good' ? '👍 좋음' :
                 analysis.xg_metrics?.finishing_quality === 'average' ? '➡️ 평균' :
                 '⚠️ 개선 필요'}
              </div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-dark-card/30 border border-accent-primary/20 rounded-lg">
            <p className="text-sm text-gray-300">
              {(analysis.xg_metrics?.goals_over_xg || 0) > 0
                ? `기대치보다 ${(analysis.xg_metrics?.goals_over_xg || 0).toFixed(1)}골 더 넣었습니다. 우수한 마무리 능력을 보여주고 있습니다! 🎯`
                : `기대치보다 ${Math.abs(analysis.xg_metrics?.goals_over_xg || 0).toFixed(1)}골 부족합니다. 슈팅 선택과 마무리 정확도 향상이 필요합니다.`}
            </p>
          </div>
        </div>

        {/* Top Scorers */}
        {analysis.top_scorers && analysis.top_scorers.length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
              <span>⚽</span>
              톱 스코어러
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysis.top_scorers.map((scorer, index) => (
                <div
                  key={scorer.spid}
                  className="bg-gradient-to-br from-dark-hover to-dark-card border border-dark-border rounded-lg p-4 hover:border-accent-primary/50 transition-all hover:scale-[1.02]"
                >
                  {/* Rank Badge */}
                  {index < 3 && (
                    <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                      #{index + 1}
                    </div>
                  )}

                  <div className="flex items-center gap-4 mb-3">
                    {/* Player Image */}
                    <PlayerAvatar
                      imageUrl={scorer.image_url}
                      playerName={scorer.player_name}
                      size={64}
                      className="bg-gradient-to-br from-dark-bg to-dark-hover rounded-lg p-1"
                    />

                    {/* Player Name */}
                    <div className="flex-1">
                      <div className="text-white font-bold text-sm mb-1">{scorer.player_name}</div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-chart-green font-bold">{scorer.goals}골</span>
                        <span className="text-gray-500">/</span>
                        <span className="text-gray-400">{scorer.shots}슈팅</span>
                      </div>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-dark-bg/50 rounded p-2">
                      <div className="text-gray-500 mb-0.5">전환율</div>
                      <div className="text-white font-bold">{scorer.conversion_rate}%</div>
                    </div>
                    <div className="bg-dark-bg/50 rounded p-2">
                      <div className="text-gray-500 mb-0.5">정확도</div>
                      <div className="text-white font-bold">{scorer.shot_accuracy}%</div>
                    </div>
                    <div className="bg-dark-bg/50 rounded p-2">
                      <div className="text-gray-500 mb-0.5">xG</div>
                      <div className="text-chart-blue font-bold">{scorer.xg_total.toFixed(2)}</div>
                    </div>
                    <div className="bg-dark-bg/50 rounded p-2">
                      <div className="text-gray-500 mb-0.5">xG 대비</div>
                      <div className={`font-bold ${scorer.goals_over_xg > 0 ? 'text-chart-green' : 'text-chart-red'}`}>
                        {scorer.goals_over_xg > 0 ? '+' : ''}{scorer.goals_over_xg.toFixed(1)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Heatmap */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <span>🎯</span>
            슈팅 히트맵
          </h2>
          <div className="flex justify-center bg-dark-hover rounded-lg p-4">
            {analysis.heatmap_data.length > 0 ? (
              <ShotHeatmap heatmapData={analysis.heatmap_data} width={900} height={585} />
            ) : (
              <div className="text-center py-12 text-gray-400">
                <p>슈팅 데이터가 없습니다.</p>
              </div>
            )}
          </div>
        </div>

        {/* Zone Analysis */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <span>📍</span>
            위치별 슈팅 분석
          </h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={zoneChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Bar dataKey="슈팅" fill={CHART_COLORS.blue} />
                <Bar dataKey="골" fill={CHART_COLORS.green} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4">
            {Object.entries(analysis.zone_analysis).map(([zone, stats]) => (
              <div key={zone} className="bg-dark-hover border border-dark-border rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-2">
                  {zone === 'inside_box' ? '박스 안' :
                   zone === 'outside_box' ? '박스 밖' :
                   zone === 'center' ? '중앙' :
                   zone === 'left' ? '좌측' :
                   zone === 'right' ? '우측' : '골문 앞'}
                </div>
                <div className="text-xs text-gray-500 space-y-1">
                  <div>슈팅: {stats?.shots || 0} / 골: {stats?.goals || 0}</div>
                  <div>전환율: <span className="text-chart-yellow font-bold">{(stats?.conversion_rate || 0).toFixed(1)}%</span></div>
                  <div>xG: {(stats?.xg || 0).toFixed(2)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Shot Types Analysis */}
        <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <span>⚡</span>
            슈팅 유형별 분석
          </h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={shotTypeChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Bar dataKey="슈팅" fill={CHART_COLORS.purple} />
                <Bar dataKey="골" fill={CHART_COLORS.green} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mt-4">
            {Object.entries(analysis.shot_types).map(([type, stats]) => (
              <div key={type} className="bg-dark-hover border border-dark-border rounded-lg p-3">
                <div className="text-sm text-gray-400 mb-2">{type}</div>
                <div className="text-xs text-gray-500 space-y-1">
                  <div>슈팅: {stats?.count || 0}</div>
                  <div>골: {stats?.goals || 0}</div>
                  <div>전환율: <span className="text-chart-yellow font-bold">{(stats?.conversion || 0).toFixed(1)}%</span></div>
                  <div>총 xG: {(stats?.xg || 0).toFixed(2)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Distance & Angle Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Distance Analysis */}
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>📏</span>
              거리별 분석
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distanceChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Bar dataKey="슈팅" fill={CHART_COLORS.blue} />
                  <Bar dataKey="골" fill={CHART_COLORS.green} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4">
              {Object.entries(analysis.distance_analysis).map(([distance, stats]) => (
                <div key={distance} className="bg-dark-hover border border-dark-border rounded-lg p-2 text-xs">
                  <div className="text-gray-400 mb-1">
                    {distance === 'very_close' ? '초근거리' :
                     distance === 'inside_box' ? '박스 안' :
                     distance === 'edge_of_box' ? '박스 경계' : '장거리'}
                  </div>
                  <div className="text-gray-500">
                    전환율: <span className="text-chart-yellow font-bold">{(stats?.conversion || 0).toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Angle Analysis */}
          <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>📐</span>
              각도별 분석
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={angleChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Bar dataKey="슈팅" fill={CHART_COLORS.pink} />
                  <Bar dataKey="골" fill={CHART_COLORS.green} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-4">
              {Object.entries(analysis.angle_analysis).map(([angle, stats]) => (
                <div key={angle} className="bg-dark-hover border border-dark-border rounded-lg p-2 text-xs">
                  <div className="text-gray-400 mb-1">
                    {angle === 'central' ? '중앙' :
                     angle === 'semi_central' ? '준중앙' : '측면'}
                  </div>
                  <div className="text-gray-500">
                    전환율: <span className="text-chart-yellow font-bold">{(stats?.conversion || 0).toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Professional Feedback - Keep-Stop-Action Framework */}
        <div className="bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg shadow-dark-lg p-6">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <span>💡</span>
            전문가 분석 및 코칭
          </h2>

          <div className="grid gap-6 md:grid-cols-1">
            {/* KEEP Section */}
            {analysis.feedback.keep && analysis.feedback.keep.length > 0 && (
              <div className="bg-dark-card border border-chart-green/30 rounded-lg p-5">
                <h3 className="text-lg font-bold text-chart-green mb-3 flex items-center gap-2">
                  <span>✅</span>
                  KEEP - 유지하세요
                </h3>
                <div className="space-y-2">
                  {analysis.feedback.keep.map((item, index) => (
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
            {analysis.feedback.stop && analysis.feedback.stop.length > 0 && (
              <div className="bg-dark-card border border-chart-red/30 rounded-lg p-5">
                <h3 className="text-lg font-bold text-chart-red mb-3 flex items-center gap-2">
                  <span>🛑</span>
                  STOP - 멈춰야 할 것들
                </h3>
                <div className="space-y-2">
                  {analysis.feedback.stop.map((item, index) => (
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
            {analysis.feedback.action_items && analysis.feedback.action_items.length > 0 && (
              <div className="bg-dark-card border border-chart-blue/30 rounded-lg p-5">
                <h3 className="text-lg font-bold text-chart-blue mb-3 flex items-center gap-2">
                  <span>🎯</span>
                  ACTION ITEMS - 개선 방안
                </h3>
                <div className="space-y-2">
                  {analysis.feedback.action_items.map((item, index) => (
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

          {(!analysis.feedback.keep || analysis.feedback.keep.length === 0) &&
           (!analysis.feedback.stop || analysis.feedback.stop.length === 0) &&
           (!analysis.feedback.action_items || analysis.feedback.action_items.length === 0) && (
            <div className="text-center py-8 text-gray-400">
              <p>분석 피드백이 없습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShotAnalysisPage;
