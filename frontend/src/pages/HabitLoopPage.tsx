import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getHabitLoopAnalysis } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';

interface PassChain {
  from: string;
  from_label: string;
  to: string;
  to_label: string;
  probability: number;
  is_predictable: boolean;
  habit_strength: 'strong' | 'moderate';
}

interface ShotZoneHabit {
  entropy: number | null;
  entropy_score: number | null;
  level: string;
  label: string;
  predictable: boolean;
  description?: string;
}

interface StressResponse {
  stress_detected: boolean;
  stress_level: 'none' | 'moderate' | 'high';
  low_possession_long_pass_rate: number | null;
  normal_long_pass_rate: number | null;
  delta: number;
  low_possession_matches: number;
}

interface PostGoalPattern {
  pattern: string;
  description: string;
  avg_possession_after_goal?: number;
  baseline_possession?: number;
  delta?: number;
}

interface HabitLoopData {
  matches_analyzed: number;
  pass_sequence_length: number;
  transition_matrix: Record<string, Record<string, number>>;
  dominant_pass_chains: PassChain[];
  good_habits: PassChain[];
  bad_habits: PassChain[];
  shot_zone_habit: ShotZoneHabit;
  stress_response: StressResponse;
  post_goal_pattern: PostGoalPattern;
  insights: string[];
}

const LIMIT_OPTIONS = [
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const PASS_LABELS: Record<string, string> = {
  short: '단패',
  long: '장패',
  through: '스루패스',
  lob: '로브패스',
};

const ChainCard: React.FC<{ chain: PassChain; type: 'good' | 'bad' }> = ({ chain, type }) => {
  const color = type === 'bad' ? '#ef4444' : '#10b981';
  const bg = type === 'bad' ? 'bg-red-900/20 border-red-700/30' : 'bg-green-900/20 border-green-700/30';

  return (
    <div className={`p-4 rounded-lg border ${bg} flex items-center gap-4`}>
      <div className="flex items-center gap-2 flex-1">
        <span className="text-sm font-bold text-white px-2 py-1 bg-dark-hover rounded">
          {chain.from_label}
        </span>
        <span className="text-gray-400">→</span>
        <span className="text-sm font-bold text-white px-2 py-1 bg-dark-hover rounded">
          {chain.to_label}
        </span>
      </div>
      <div className="text-right">
        <div className="text-xl font-bold" style={{ color }}>{chain.probability}%</div>
        <div className="text-xs text-gray-400">{chain.is_predictable ? '⚠️ 예측 가능' : '✅ 자연스러운 루틴'}</div>
      </div>
    </div>
  );
};

const ShotZoneGauge: React.FC<{ habit: ShotZoneHabit }> = ({ habit }) => {
  const score = habit.entropy_score ?? 0;
  const color = habit.predictable ? '#ef4444' : score >= 80 ? '#10b981' : '#3b82f6';

  return (
    <div className="text-center">
      <div className="relative w-32 h-32 mx-auto">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="42" fill="none" stroke="#374151" strokeWidth="10" />
          <circle
            cx="50" cy="50" r="42"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeDasharray={`${2 * Math.PI * 42}`}
            strokeDashoffset={`${2 * Math.PI * 42 * (1 - score / 100)}`}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">{score.toFixed(0)}</span>
          <span className="text-xs text-gray-400">/ 100</span>
        </div>
      </div>
      <div className="mt-2">
        <div className="font-bold" style={{ color }}>{habit.label}</div>
        <div className="text-xs text-gray-400 mt-1">{habit.description}</div>
      </div>
    </div>
  );
};

const HabitLoopPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<HabitLoopData | null>(null);
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
      const result = await getHabitLoopAnalysis(ouid, matchtype, limit);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.error || '습관 루프 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={['경기 이력 수집 중...', '패스 시퀀스 인코딩 중...', '마르코프 체인 계산 중...', '습관 패턴 탐지 중...']}
        estimatedDuration={8000}
        message="습관 루프 탐지기"
      />
    );
  }

  if (error) return <ErrorMessage message={error} />;
  if (!data) return null;

  const stressColor = data.stress_response.stress_level === 'high'
    ? '#ef4444'
    : data.stress_response.stress_level === 'moderate'
    ? '#f59e0b'
    : '#10b981';

  const postGoalColor = data.post_goal_pattern.pattern === 'possession_increase'
    ? '#10b981'
    : data.post_goal_pattern.pattern === 'defensive_retreat'
    ? '#f59e0b'
    : '#3b82f6';

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>🧠</span>
                습관 루프 탐지기
              </h1>
              <p className="text-gray-400 mt-1">
                무의식적으로 반복하는 전술 습관 수치화 — 마르코프 체인 패스 시퀀스 분석
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
            <div className="ml-auto text-sm text-gray-400">
              {data.matches_analyzed}경기 · 시퀀스 {data.pass_sequence_length}개
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {/* Top stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">탐지된 습관 수</div>
            <div className="text-3xl font-bold text-white">{data.dominant_pass_chains.length}</div>
            <div className="text-xs text-gray-500 mt-1">반복 패스 시퀀스</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">위험 습관</div>
            <div className="text-3xl font-bold text-red-400">{data.bad_habits.length}</div>
            <div className="text-xs text-gray-500 mt-1">상대가 읽을 수 있는 패턴</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">압박 반응</div>
            <div className="text-xl font-bold" style={{ color: stressColor }}>
              {data.stress_response.stress_level === 'high' ? '⚠️ 강함'
                : data.stress_response.stress_level === 'moderate' ? '⚡ 중간'
                : '✅ 안정'}
            </div>
            <div className="text-xs text-gray-500 mt-1">저점유율 시 패스 변화</div>
          </div>
          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">득점 후 패턴</div>
            <div className="text-sm font-bold" style={{ color: postGoalColor }}>
              {data.post_goal_pattern.pattern === 'possession_increase' ? '✅ 지배력 유지'
                : data.post_goal_pattern.pattern === 'defensive_retreat' ? '⚠️ 수비 후퇴'
                : '📊 안정적'}
            </div>
            <div className="text-xs text-gray-500 mt-1">{data.post_goal_pattern.description}</div>
          </div>
        </div>

        {/* Markov explanation */}
        <div className="bg-dark-hover border border-dark-border rounded-lg p-4 mb-6 text-xs text-gray-400">
          <strong className="text-gray-200">마르코프 체인 분석:</strong> 패스 유형 간 전이 확률 계산.
          <span className="ml-2 text-gray-500">확률 60% 이상 = 예측 가능한 위험 습관 / 40-59% = 중간 강도 루틴</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Bad habits */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>⚠️</span> 위험한 습관 (상대가 읽음)
            </h2>
            {data.bad_habits.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <div className="text-3xl mb-2">✅</div>
                <p className="text-sm">예측 가능한 위험 습관이 없습니다!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {data.bad_habits.map((chain, idx) => (
                  <ChainCard key={idx} chain={chain} type="bad" />
                ))}
              </div>
            )}
          </div>

          {/* Good habits */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>✅</span> 강화할 루틴
            </h2>
            {data.good_habits.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <div className="text-3xl mb-2">💡</div>
                <p className="text-sm">분석 가능한 반복 루틴이 없습니다.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {data.good_habits.map((chain, idx) => (
                  <ChainCard key={idx} chain={chain} type="good" />
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Shot zone habit */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <span>🎯</span> 슈팅 위치 다양성
            </h2>
            <ShotZoneGauge habit={data.shot_zone_habit} />
            <div className="mt-4 text-xs text-gray-400 text-center">
              0 = 항상 같은 위치 (예측 쉬움) | 100 = 완전히 다양 (예측 어려움)
            </div>
          </div>

          {/* Stress response */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>😰</span> 압박 반응 패턴
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-dark-hover rounded-lg">
                <span className="text-sm text-gray-300">일반 상황 장패 비율</span>
                <span className="font-bold text-white">
                  {data.stress_response.normal_long_pass_rate !== null
                    ? `${data.stress_response.normal_long_pass_rate}%`
                    : '-'}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-dark-hover rounded-lg">
                <span className="text-sm text-gray-300">저점유율(40%↓) 장패 비율</span>
                <span className="font-bold" style={{ color: stressColor }}>
                  {data.stress_response.low_possession_long_pass_rate !== null
                    ? `${data.stress_response.low_possession_long_pass_rate}%`
                    : '-'}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg" style={{ backgroundColor: stressColor + '15', border: `1px solid ${stressColor}30` }}>
                <span className="text-sm text-gray-300">압박 시 증가폭</span>
                <span className="font-bold text-xl" style={{ color: stressColor }}>
                  +{data.stress_response.delta}%p
                </span>
              </div>
              {data.stress_response.stress_detected && (
                <p className="text-xs text-amber-400 mt-2">
                  ⚠️ 압박 상황에서 장패 의존도가 크게 증가합니다.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Transition matrix */}
        {Object.keys(data.transition_matrix).length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>📊</span> 패스 전이 행렬
            </h2>
            <div className="overflow-x-auto">
              <table className="text-sm">
                <thead>
                  <tr className="text-gray-400">
                    <th className="py-2 pr-4 text-left">현재 → 다음</th>
                    {['short', 'long', 'through'].map(t => (
                      <th key={t} className="py-2 px-4 text-center">{PASS_LABELS[t]}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.transition_matrix).map(([from, toMap]) => (
                    <tr key={from} className="border-t border-dark-border/50">
                      <td className="py-2 pr-4 text-gray-300 font-semibold">{PASS_LABELS[from] || from}</td>
                      {['short', 'long', 'through'].map(to => {
                        const prob = toMap[to] || 0;
                        const highlight = prob >= 0.6 ? '#ef444440' : prob >= 0.4 ? '#f59e0b20' : 'transparent';
                        return (
                          <td key={to} className="py-2 px-4 text-center rounded" style={{ backgroundColor: highlight }}>
                            <span className={prob >= 0.4 ? 'font-bold text-white' : 'text-gray-500'}>
                              {prob > 0 ? `${(prob * 100).toFixed(0)}%` : '-'}
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-gray-500 mt-3">🔴 60%+ = 위험 / 🟡 40-59% = 주의</p>
          </div>
        )}

        {/* Insights */}
        {data.insights.length > 0 && (
          <div className="bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg p-6">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>💡</span> 습관 루프 인사이트
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

export default HabitLoopPage;
