import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPlayerContributionAnalysis } from '../services/api';
import { cachedFetch } from '../services/apiCache';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface Contribution {
  score: number;
  goals_per_game: number;
  assists_per_game: number;
  avg_rating: number;
  defensive_per_game: number;
  shots_on_per_game: number;
  dribble_ok_per_game: number;
  pass_success_rate: number;
  appearances: number;
  position_group: string;
  position_label: string;
  primary_metrics: string[];
  role_desc: string;
}

interface ContributionTier {
  label: string;
  color: string;
  emoji: string;
}

interface PlayerROI {
  spid: number;
  player_name: string;
  image_url: string;
  appearances: number;
  contribution: Contribution;
  roi_score: number;
  roi_tier: ContributionTier;
  position_group: string;
  position_label: string;
}

interface PositionGroupSummary {
  label: string;
  avg_contribution: number;
  max_contribution: number;
  count: number;
}

interface Summary {
  total_players_analyzed: number;
  avg_roi: number;
  best_value_player: string | null;
  worst_value_player: string | null;
  position_group_summary: Record<string, PositionGroupSummary>;
}

interface ROIData {
  matches_analyzed: number;
  trade_history_count: number;
  squad_roi: PlayerROI[];
  summary: Summary;
  insights: string[];
}

const LIMIT_OPTIONS = [
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const TIER_COLORS: Record<string, string> = {
  '압도적 에이스': '#f59e0b',
  '팀의 핵심':     '#f97316',
  '주전급':        '#10b981',
  '안정적 활용':   '#3b82f6',
  '보통 수준':     '#a3a3a3',
  '기여도 낮음':   '#ef4444',
};

// 포지션 맞춤 핵심 스탯
const getPositionStats = (player: PlayerROI) => {
  const c = player.contribution;
  const pg = player.position_group;
  if (pg === 'GK') return [
    { label: '평균 평점', value: c.avg_rating.toFixed(1) },
    { label: '패스 성공률', value: `${c.pass_success_rate.toFixed(0)}%` },
  ];
  if (pg === 'DEF') return [
    { label: '태클+블록', value: c.defensive_per_game.toFixed(2) },
    { label: '평균 평점', value: c.avg_rating.toFixed(1) },
    { label: 'G+A', value: `${(c.goals_per_game + c.assists_per_game).toFixed(2)}` },
  ];
  if (pg === 'CDM') return [
    { label: '태클', value: c.defensive_per_game.toFixed(2) },
    { label: '어시스트', value: c.assists_per_game.toFixed(2) },
    { label: '평균 평점', value: c.avg_rating.toFixed(1) },
  ];
  if (pg === 'CM') return [
    { label: '어시스트', value: c.assists_per_game.toFixed(2) },
    { label: '골', value: c.goals_per_game.toFixed(2) },
    { label: '평균 평점', value: c.avg_rating.toFixed(1) },
  ];
  if (pg === 'CAM') return [
    { label: '어시스트', value: c.assists_per_game.toFixed(2) },
    { label: '골', value: c.goals_per_game.toFixed(2) },
    { label: '유효슛', value: c.shots_on_per_game.toFixed(2) },
  ];
  if (pg === 'WG') return [
    { label: '골', value: c.goals_per_game.toFixed(2) },
    { label: '어시스트', value: c.assists_per_game.toFixed(2) },
    { label: '드리블', value: c.dribble_ok_per_game.toFixed(1) },
  ];
  return [
    { label: '골', value: c.goals_per_game.toFixed(2) },
    { label: '유효슛', value: c.shots_on_per_game.toFixed(2) },
    { label: '평균 평점', value: c.avg_rating.toFixed(1) },
  ];
};

const PlayerCard: React.FC<{ player: PlayerROI; rank: number }> = ({ player, rank }) => {
  const tierColor = TIER_COLORS[player.roi_tier.label] || '#6b7280';
  const posStats = getPositionStats(player);
  const score = player.contribution.score;

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-4 flex items-center gap-4 hover:border-accent-primary/30 transition-all">
      {/* Rank */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
        rank <= 3 ? 'bg-accent-primary text-white' : 'bg-dark-hover text-gray-400'
      }`}>
        #{rank}
      </div>

      {/* Player image */}
      <img
        src={player.image_url}
        alt={player.player_name}
        className="w-12 h-12 object-contain rounded-lg bg-dark-hover flex-shrink-0"
        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
      />

      {/* Player info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-bold text-white truncate">{player.player_name}</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-dark-hover text-gray-400 font-medium flex-shrink-0">
            {player.position_label}
          </span>
          <span
            className="text-xs px-2 py-0.5 rounded-full flex-shrink-0"
            style={{ backgroundColor: tierColor + '20', color: tierColor }}
          >
            {player.roi_tier.emoji} {player.roi_tier.label}
          </span>
        </div>
        <div className="text-xs text-gray-500 mt-0.5">
          {player.contribution.role_desc} · {player.appearances}경기
        </div>
      </div>

      {/* 포지션 맞춤 핵심 스탯 */}
      <div className="hidden md:flex gap-5 text-center">
        {posStats.map((s, i) => (
          <div key={i}>
            <div className="text-[10px] text-gray-500">{s.label}</div>
            <div className="text-sm font-bold text-white">{s.value}</div>
          </div>
        ))}
      </div>

      {/* 기여도 점수 */}
      <div className="text-right flex-shrink-0 w-16">
        <div className="text-2xl font-bold" style={{ color: tierColor }}>
          {score.toFixed(1)}
        </div>
        <div className="text-[10px] text-gray-400">기여도</div>
      </div>
    </div>
  );
};

const SquadROIPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<ROIData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState(50);
  const [limit, setLimit] = useState(30);

  useEffect(() => { fetchData(); }, [ouid, matchtype, limit]);

  const fetchData = async () => {
    if (!ouid) return;
    setLoading(true);
    setError('');
    try {
      const result = await cachedFetch(
        `playerContribution:${ouid}:${matchtype}:${limit}`,
        () => getPlayerContributionAnalysis(ouid, matchtype, limit),
        30 * 60 * 1000
      );
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.error || '선수 기여도 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={['경기 데이터 수집 중...', '포지션별 기여도 계산 중...', '스쿼드 분석 중...']}
        estimatedDuration={5000}
        message="선수 기여도 분석"
      />
    );
  }

  if (error) return <ErrorMessage message={error} />;
  if (!data) return null;

  const chartData = data.squad_roi.slice(0, 10).map(p => ({
    name: p.player_name.length > 6 ? p.player_name.slice(0, 6) + '…' : p.player_name,
    score: p.contribution.score,
    pos: p.position_label,
  }));

  const posGroups = Object.entries(data.summary.position_group_summary || {})
    .sort((a, b) => b[1].avg_contribution - a[1].avg_contribution);

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>💰</span>
                선수 기여도 분석
              </h1>
              <p className="text-gray-400 mt-1">
                포지션별 맞춤 기여도 — 에이스 발굴 & 약점 포지션 탐지
              </p>
            </div>
            <button onClick={() => navigate(-1)} className="px-4 py-2 bg-dark-hover border border-dark-border rounded-lg text-sm hover:bg-dark-border transition-colors">
              ← 돌아가기
            </button>
          </div>
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-400">경기 타입:</label>
              <MatchTypeSelector value={matchtype} onChange={setMatchtype} />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-400">분석 범위:</label>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="px-3 py-2 bg-dark-hover border border-dark-border rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-accent-primary"
              >
                {LIMIT_OPTIONS.map(o => <option key={o.value} value={o.value}>최근 {o.label}</option>)}
              </select>
            </div>
            <div className="ml-auto text-sm text-gray-400">
              {data.matches_analyzed}경기 분석
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">

        {/* Summary cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">분석 선수 수</div>
            <div className="text-3xl font-bold text-white">{data.summary.total_players_analyzed}</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">평균 기여도</div>
            <div className="text-3xl font-bold text-accent-primary">{data.summary.avg_roi.toFixed(1)}</div>
          </div>
          {data.summary.best_value_player && (
            <div className="bg-dark-card border border-amber-700/30 rounded-lg p-5">
              <div className="text-gray-400 text-sm mb-2">👑 최고 기여도</div>
              <div className="text-lg font-bold text-amber-400 truncate">{data.summary.best_value_player}</div>
            </div>
          )}
          {data.summary.worst_value_player && (
            <div className="bg-dark-card border border-red-700/30 rounded-lg p-5">
              <div className="text-gray-400 text-sm mb-2">🔻 최저 기여도</div>
              <div className="text-lg font-bold text-red-400 truncate">{data.summary.worst_value_player}</div>
            </div>
          )}
        </div>

        {/* 포지션별 평균 기여도 */}
        {posGroups.length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-5 mb-6">
            <h2 className="text-base font-bold text-white mb-3">포지션별 평균 기여도</h2>
            <div className="flex gap-3 flex-wrap">
              {posGroups.map(([pg, info]) => (
                <div key={pg} className="flex-1 min-w-[80px] bg-dark-hover rounded-lg p-3 text-center">
                  <div className="text-[11px] text-gray-400 mb-1">{info.label}</div>
                  <div className={`text-xl font-bold ${
                    info.avg_contribution >= 8 ? 'text-amber-400' :
                    info.avg_contribution >= 5 ? 'text-green-400' :
                    info.avg_contribution >= 3 ? 'text-blue-400' : 'text-red-400'
                  }`}>{info.avg_contribution.toFixed(1)}</div>
                  <div className="text-[10px] text-gray-500">{info.count}명 · 최고 {info.max_contribution.toFixed(1)}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 기여도 차트 */}
        {chartData.length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-6">
            <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
              <span>📊</span>상위 선수 기여도
            </h2>
            <p className="text-xs text-gray-500 mb-4">포지션별 맞춤 가중치 적용 (공격수는 골, 수비수는 태클+블록 등)</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" tick={{ fontSize: 11 }} />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                  formatter={(v: number | undefined) => [(v ?? 0).toFixed(2), '기여도']}
                />
                <Bar dataKey="score" name="기여도" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, idx) => (
                    <Cell key={idx} fill={
                      entry.score >= 15 ? '#f59e0b' :
                      entry.score >= 10 ? '#f97316' :
                      entry.score >= 7  ? '#10b981' :
                      entry.score >= 4.5 ? '#3b82f6' :
                      entry.score >= 2.5 ? '#a3a3a3' : '#ef4444'
                    } />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* 기여도 등급 안내 */}
        <div className="bg-dark-hover border border-dark-border rounded-lg p-4 mb-6 text-xs text-gray-400">
          <strong className="text-gray-200">기여도 등급:</strong>
          {' '}
          <span className="text-amber-400">👑압도적 에이스(15+)</span> ·{' '}
          <span className="text-orange-400">⭐팀의 핵심(10+)</span> ·{' '}
          <span className="text-green-400">✅주전급(7+)</span> ·{' '}
          <span className="text-blue-400">📊안정적 활용(4.5+)</span> ·{' '}
          <span className="text-gray-400">⚠️보통(2.5+)</span> ·{' '}
          <span className="text-red-400">🔻기여도 낮음</span>
          <br/>
          <span className="text-gray-500">
            GK=평점·패스 / DEF=태클·블록(+G&A보너스) / CDM=태클·패스·어시스트 / CM=어시스트·골·평점 / WG=G+A·드리블 / FWD=골·유효슛
          </span>
        </div>

        {/* 선수 랭킹 */}
        <div>
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>⭐</span>
            선수 기여도 랭킹
          </h2>
          {data.squad_roi.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <div className="text-5xl mb-4">📊</div>
              <p>분석 데이터가 부족합니다. 더 많은 경기 데이터가 필요합니다.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {data.squad_roi.map((player, idx) => (
                <PlayerCard key={player.spid} player={player} rank={idx + 1} />
              ))}
            </div>
          )}
        </div>

        {/* Insights */}
        {data.insights.length > 0 && (
          <div className="mt-8 bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg p-6">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>💡</span> 스쿼드 인사이트
            </h2>
            {data.insights.map((ins, idx) => (
              <p key={idx} className="text-gray-200 text-sm mb-2">{ins}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SquadROIPage;
