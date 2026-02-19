import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getFormCycleAnalysis } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Area, Legend,
} from 'recharts';

interface FormEntry {
  match_index: number;
  match_date: string;
  result: 'win' | 'lose' | 'draw';
  goals_for: number;
  goals_against: number;
  perf_score: number;
  form_5: number | null;
  form_10: number | null;
}

interface Streak {
  type: 'hot' | 'cold';
  start_idx: number;
  end_idx: number;
  length: number;
  match_date: string;
}

interface CurrentForm {
  last_5_results: string[];
  form_5: { form_index: number; win_rate: number } | null;
  form_10: { form_index: number; win_rate: number } | null;
  status: string;
}

interface SessionEntry {
  session: number;
  label: string;
  win_rate: number;
  total: number;
  wins: number;
}

interface FormCycleData {
  total_matches: number;
  win_rate: number;
  form_timeline: FormEntry[];
  rolling_5: Array<{ form_index: number; win_rate: number }>;
  rolling_10: Array<{ form_index: number; win_rate: number }>;
  streaks: {
    all: Streak[];
    hot: Streak[];
    cold: Streak[];
    longest_hot: number;
    longest_cold: number;
  };
  current_form: CurrentForm;
  avg_form_index: number | null;
  session_analysis: {
    by_session: SessionEntry[];
    optimal_session: SessionEntry | null;
    insight: string;
  };
  insights: string[];
}

const LIMIT_OPTIONS = [
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
  { value: 100, label: '100경기' },
];

const RESULT_COLORS: Record<string, string> = {
  win: '#10b981',
  draw: '#f59e0b',
  lose: '#ef4444',
};

const FORM_STATUS_CONFIG: Record<string, { label: string; color: string; emoji: string }> = {
  hot: { label: '핫 스트릭', color: '#f59e0b', emoji: '🔥' },
  good: { label: '좋음', color: '#10b981', emoji: '✅' },
  neutral: { label: '보통', color: '#3b82f6', emoji: '📊' },
  poor: { label: '저조', color: '#f59e0b', emoji: '📉' },
  cold: { label: '슬럼프', color: '#ef4444', emoji: '❄️' },
  unknown: { label: '알 수 없음', color: '#6b7280', emoji: '❓' },
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-3 text-xs">
      <p className="text-gray-400 mb-1">경기 #{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }}>{p.name}: {p.value?.toFixed ? p.value.toFixed(1) : p.value}</p>
      ))}
    </div>
  );
};

const FormCyclePage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<FormCycleData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState(50);
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    fetchData();
  }, [ouid, matchtype, limit]);

  const fetchData = async () => {
    if (!ouid) return;
    setLoading(true);
    setError('');
    try {
      const result = await getFormCycleAnalysis(ouid, matchtype, limit);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.error || '폼 사이클 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={['경기 이력 수집 중...', '롤링 폼 지수 계산 중...', '스트릭 탐지 중...', '패턴 분석 중...']}
        estimatedDuration={6000}
        message="폼 사이클 분석"
      />
    );
  }

  if (error) return <ErrorMessage message={error} />;
  if (!data) return null;

  const currentStatus = FORM_STATUS_CONFIG[data.current_form.status] || FORM_STATUS_CONFIG.unknown;

  // Prepare chart data
  const chartData = data.form_timeline.map((entry, idx) => ({
    idx: idx + 1,
    form_5: entry.form_5,
    form_10: entry.form_10,
    perf: entry.perf_score * 10,
    result: entry.result,
    goals_for: entry.goals_for,
    goals_against: entry.goals_against,
  }));

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>📈</span>
                폼 사이클 분석기
              </h1>
              <p className="text-gray-400 mt-1">
                핫 스트릭 & 슬럼프 주기 탐지 — 언제 잘하고 언제 무너지는지 파악
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
            <div className="ml-auto text-sm text-gray-400">{data.total_matches}경기 분석</div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {/* Current form + key stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-dark-card border border-dark-border rounded-lg p-5 col-span-2 md:col-span-1">
            <div className="text-gray-400 text-sm mb-2">현재 폼 상태</div>
            <div className="text-3xl font-bold" style={{ color: currentStatus.color }}>
              {currentStatus.emoji} {currentStatus.label}
            </div>
            {data.current_form.form_5 && (
              <div className="text-sm text-gray-400 mt-1">
                최근 5경기 폼 지수: {data.current_form.form_5.form_index.toFixed(0)}
              </div>
            )}
          </div>

          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">전체 승률</div>
            <div className="text-3xl font-bold text-white">{data.win_rate}%</div>
            <div className="text-sm text-gray-400 mt-1">{data.total_matches}경기</div>
          </div>

          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">최장 핫 스트릭</div>
            <div className="text-3xl font-bold text-amber-400">{data.streaks.longest_hot}경기</div>
            <div className="text-sm text-gray-400 mt-1">연속 폼 지수 70+</div>
          </div>

          <div className="bg-dark-card border border-dark-border rounded-lg p-5">
            <div className="text-gray-400 text-sm mb-2">최장 슬럼프</div>
            <div className="text-3xl font-bold text-blue-400">{data.streaks.longest_cold}경기</div>
            <div className="text-sm text-gray-400 mt-1">연속 폼 지수 40-</div>
          </div>
        </div>

        {/* Form timeline chart */}
        {chartData.length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <span>📊</span>
              폼 사이클 타임라인
            </h2>
            <p className="text-sm text-gray-400 mb-4">5경기 롤링 폼 지수 (핫: 70+, 슬럼프: 40-)</p>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="idx" stroke="#9ca3af" label={{ value: '경기 번호', position: 'insideBottom', offset: -5, fill: '#9ca3af' }} />
                <YAxis stroke="#9ca3af" domain={[0, 100]} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <ReferenceLine y={70} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: '핫', fill: '#f59e0b', fontSize: 11 }} />
                <ReferenceLine y={40} stroke="#3b82f6" strokeDasharray="4 4" label={{ value: '슬럼프', fill: '#3b82f6', fontSize: 11 }} />
                <Area type="monotone" dataKey="form_5" name="5경기 폼" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} dot={false} connectNulls />
                <Line type="monotone" dataKey="form_10" name="10경기 폼" stroke="#3b82f6" dot={false} connectNulls strokeDasharray="5 5" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Recent form */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>🎯</span>
              최근 경기 결과
            </h2>
            <div className="flex gap-2">
              {data.current_form.last_5_results.map((r, idx) => (
                <div
                  key={idx}
                  className="flex-1 h-10 rounded-lg flex items-center justify-center font-bold text-sm"
                  style={{ backgroundColor: RESULT_COLORS[r] + '30', color: RESULT_COLORS[r], border: `1px solid ${RESULT_COLORS[r]}` }}
                >
                  {r === 'win' ? '승' : r === 'lose' ? '패' : '무'}
                </div>
              ))}
            </div>
            {data.current_form.form_5 && (
              <div className="mt-3 text-sm text-gray-400">
                최근 5경기 승률: <span className="text-white font-bold">{data.current_form.form_5.win_rate}%</span>
              </div>
            )}
          </div>

          {/* Session analysis */}
          {data.session_analysis.by_session.length > 0 && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <span>⏰</span>
                세션별 승률
              </h2>
              <div className="space-y-2">
                {data.session_analysis.by_session.slice(0, 5).map((s) => {
                  const isOptimal = data.session_analysis.optimal_session?.session === s.session;
                  return (
                    <div key={s.session} className={`flex items-center gap-3 p-2 rounded-lg ${isOptimal ? 'bg-accent-primary/10 border border-accent-primary/30' : 'bg-dark-hover'}`}>
                      <span className="text-gray-400 text-sm w-20">{s.label}</span>
                      <div className="flex-1 bg-dark-bg rounded-full h-2">
                        <div
                          className="h-2 rounded-full"
                          style={{ width: `${s.win_rate}%`, backgroundColor: s.win_rate >= 55 ? '#10b981' : s.win_rate >= 45 ? '#f59e0b' : '#ef4444' }}
                        />
                      </div>
                      <span className={`text-sm font-bold w-12 text-right ${s.win_rate >= 55 ? 'text-chart-green' : s.win_rate >= 45 ? 'text-chart-yellow' : 'text-chart-red'}`}>
                        {s.win_rate}%
                      </span>
                      {isOptimal && <span className="text-xs text-accent-primary">최고 ✓</span>}
                    </div>
                  );
                })}
              </div>
              <p className="text-xs text-gray-400 mt-3">{data.session_analysis.insight}</p>
            </div>
          )}
        </div>

        {/* Streak list */}
        {data.streaks.all.length > 0 && (
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span>🔥</span>
              스트릭 기록
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.streaks.hot.map((s, idx) => (
                <div key={`hot-${idx}`} className="flex items-center gap-3 p-3 bg-amber-900/20 border border-amber-700/30 rounded-lg">
                  <span className="text-2xl">🔥</span>
                  <div>
                    <div className="font-bold text-amber-400">{s.length}경기 연속 핫 스트릭</div>
                    <div className="text-xs text-gray-400">{s.match_date?.slice(0, 10)}</div>
                  </div>
                </div>
              ))}
              {data.streaks.cold.map((s, idx) => (
                <div key={`cold-${idx}`} className="flex items-center gap-3 p-3 bg-blue-900/20 border border-blue-700/30 rounded-lg">
                  <span className="text-2xl">❄️</span>
                  <div>
                    <div className="font-bold text-blue-400">{s.length}경기 연속 슬럼프</div>
                    <div className="text-xs text-gray-400">{s.match_date?.slice(0, 10)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Insights */}
        {data.insights.length > 0 && (
          <div className="bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg p-6">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>💡</span> 폼 사이클 인사이트
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

export default FormCyclePage;
