import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getOpponentTypesAnalysis } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface ArchetypeSummary {
  archetype_id: string;
  label: string;
  emoji: string;
  description: string;
  typical_traits: string;
  weakness: string;
  match_count: number;
  win_rate: number;
  wins: number;
  losses: number;
  draws: number;
  avg_goals_for: number;
  avg_goals_against: number;
  avg_goal_diff: number;
  frequency_pct: number;
}

interface OpponentTypesData {
  total_classified: number;
  archetype_summary: ArchetypeSummary[];
  nemesis_type: ArchetypeSummary | null;
  best_matchup: ArchetypeSummary | null;
  insights: string[];
}

const LIMIT_OPTIONS = [
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const WIN_RATE_COLOR = (rate: number) =>
  rate >= 60 ? '#10b981' : rate >= 45 ? '#3b82f6' : rate >= 35 ? '#f59e0b' : '#ef4444';

const ArchetypeCard: React.FC<{ archetype: ArchetypeSummary; isNemesis: boolean; isBest: boolean }> = ({
  archetype, isNemesis, isBest,
}) => {
  const [expanded, setExpanded] = useState(false);
  const winColor = WIN_RATE_COLOR(archetype.win_rate);

  return (
    <div className={`bg-dark-card rounded-lg border overflow-hidden ${
      isNemesis ? 'border-red-600/50' : isBest ? 'border-green-600/50' : 'border-dark-border'
    }`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-4 p-4 hover:bg-dark-hover transition-colors text-left"
      >
        <div className="text-3xl">{archetype.emoji}</div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">{archetype.label}</span>
            {isNemesis && <span className="text-xs px-2 py-0.5 bg-red-900/40 text-red-400 rounded border border-red-700/30">🚨 천적</span>}
            {isBest && <span className="text-xs px-2 py-0.5 bg-green-900/40 text-green-400 rounded border border-green-700/30">✅ 강세</span>}
          </div>
          <div className="text-xs text-gray-400 mt-0.5">{archetype.description}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500 mb-1">{archetype.match_count}경기</div>
          <div className="w-16 bg-dark-hover rounded-full h-2 mb-1">
            <div
              className="h-2 rounded-full"
              style={{ width: `${archetype.frequency_pct}%`, backgroundColor: '#3b82f6' }}
            />
          </div>
          <div className="text-xs text-gray-400">{archetype.frequency_pct}%</div>
        </div>
        <div className="text-right w-20">
          <div className="text-2xl font-bold" style={{ color: winColor }}>{archetype.win_rate}%</div>
          <div className="text-xs text-gray-400">승률</div>
        </div>
        <span className="text-gray-400">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="border-t border-dark-border p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center bg-dark-hover rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">승</div>
              <div className="text-xl font-bold text-green-400">{archetype.wins}</div>
            </div>
            <div className="text-center bg-dark-hover rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">무</div>
              <div className="text-xl font-bold text-yellow-400">{archetype.draws}</div>
            </div>
            <div className="text-center bg-dark-hover rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">패</div>
              <div className="text-xl font-bold text-red-400">{archetype.losses}</div>
            </div>
            <div className="text-center bg-dark-hover rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-1">평균 득실차</div>
              <div className={`text-xl font-bold ${archetype.avg_goal_diff >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {archetype.avg_goal_diff >= 0 ? '+' : ''}{archetype.avg_goal_diff.toFixed(2)}
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="bg-dark-hover rounded-lg p-3">
              <div className="text-xs text-gray-500 mb-1">전형적 특징</div>
              <div className="text-gray-300">{archetype.typical_traits}</div>
            </div>
            <div className="bg-amber-900/20 border border-amber-700/20 rounded-lg p-3">
              <div className="text-xs text-amber-500 mb-1">💡 약점 & 공략법</div>
              <div className="text-gray-300">{archetype.weakness}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const OpponentTypesPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<OpponentTypesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState(50);
  const [limit, setLimit] = useState(30);

  useEffect(() => {
    fetchData();
  }, [ouid, matchtype, limit]);

  const fetchData = async () => {
    if (!ouid) return;
    setLoading(true);
    setError('');
    try {
      const result = await getOpponentTypesAnalysis(ouid, matchtype, limit);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.error || '상대 유형 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={['경기 이력 수집 중...', '상대팀 데이터 추출 중...', '전술 유형 분류 중...', '승률 맵 생성 중...']}
        estimatedDuration={7000}
        message="상대 유형 분류기"
      />
    );
  }

  if (error) return <ErrorMessage message={error} />;
  if (!data) return null;

  const chartData = data.archetype_summary.map(a => ({
    name: `${a.emoji} ${a.label}`,
    win_rate: a.win_rate,
    matches: a.match_count,
  }));

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>🗺️</span>
                상대 유형 분류기
              </h1>
              <p className="text-gray-400 mt-1">
                내가 상대한 적을 6개 전술 유형으로 분류 — 유형별 승률 맵 & 천적 분석
              </p>
            </div>
            <button onClick={() => navigate(-1)} className="px-4 py-2 bg-dark-hover border border-dark-border rounded-lg text-sm hover:bg-dark-border transition-colors">
              ← 돌아가기
            </button>
          </div>
          <div className="flex items-center gap-4">
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
            <div className="ml-auto text-sm text-gray-400">{data.total_classified}경기 분류 완료</div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {/* Nemesis + Best summary */}
        {(data.nemesis_type || data.best_matchup) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {data.nemesis_type && (
              <div className="bg-red-900/20 border border-red-700/30 rounded-lg p-5">
                <div className="text-red-400 text-sm font-bold mb-2">🚨 천적 유형 (가장 많이 지는 상대)</div>
                <div className="flex items-center gap-3">
                  <span className="text-4xl">{data.nemesis_type.emoji}</span>
                  <div>
                    <div className="text-xl font-bold text-white">{data.nemesis_type.label}</div>
                    <div className="text-sm text-gray-300">{data.nemesis_type.match_count}경기 · 승률 <span className="text-red-400 font-bold">{data.nemesis_type.win_rate}%</span></div>
                    <div className="text-xs text-gray-400 mt-1">💡 {data.nemesis_type.weakness}</div>
                  </div>
                </div>
              </div>
            )}
            {data.best_matchup && (
              <div className="bg-green-900/20 border border-green-700/30 rounded-lg p-5">
                <div className="text-green-400 text-sm font-bold mb-2">✅ 최고 궁합 (가장 잘 이기는 상대)</div>
                <div className="flex items-center gap-3">
                  <span className="text-4xl">{data.best_matchup.emoji}</span>
                  <div>
                    <div className="text-xl font-bold text-white">{data.best_matchup.label}</div>
                    <div className="text-sm text-gray-300">{data.best_matchup.match_count}경기 · 승률 <span className="text-green-400 font-bold">{data.best_matchup.win_rate}%</span></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Win rate chart */}
        {chartData.length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>📊</span>
              유형별 승률 비교
            </h2>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={chartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} stroke="#9ca3af" tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="name" stroke="#9ca3af" width={120} tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                  formatter={(val: number) => [`${val}%`, '승률']}
                />
                <Bar dataKey="win_rate" name="승률" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry, idx) => (
                    <Cell key={idx} fill={WIN_RATE_COLOR(entry.win_rate)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="flex gap-4 text-xs text-gray-400 mt-2 justify-center">
              <span><span className="inline-block w-3 h-3 rounded mr-1 bg-green-500"></span>60%+</span>
              <span><span className="inline-block w-3 h-3 rounded mr-1 bg-blue-500"></span>45-59%</span>
              <span><span className="inline-block w-3 h-3 rounded mr-1 bg-yellow-500"></span>35-44%</span>
              <span><span className="inline-block w-3 h-3 rounded mr-1 bg-red-500"></span>35% 미만</span>
            </div>
          </div>
        )}

        {/* Archetype cards */}
        {data.archetype_summary.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <div className="text-5xl mb-4">🗺️</div>
            <p>분석 가능한 경기 데이터가 부족합니다. 최소 10경기 이상 필요합니다.</p>
          </div>
        ) : (
          <div>
            <h2 className="text-xl font-bold text-white mb-4">전술 유형별 상세 분석</h2>
            <div className="space-y-3">
              {data.archetype_summary.map(a => (
                <ArchetypeCard
                  key={a.archetype_id}
                  archetype={a}
                  isNemesis={data.nemesis_type?.archetype_id === a.archetype_id}
                  isBest={data.best_matchup?.archetype_id === a.archetype_id}
                />
              ))}
            </div>
          </div>
        )}

        {/* Insights */}
        {data.insights.length > 0 && (
          <div className="mt-8 bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg p-6">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>💡</span> 상대 유형 인사이트
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

export default OpponentTypesPage;
