import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRankerGapAnalysis } from '../services/api';
import { cachedFetch } from '../services/apiCache';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface MetricEntry {
  label: string;
  my_value: number;
  ranker_avg: number;
  ranker_std: number;
  z_score: number;
  proximity_score: number;
  status: string;
  gap_description: string;
}

interface Grade {
  label: string;
  color: string;
  emoji: string;
  description: string;
}

interface RankerGapData {
  ranker_distance_score: number;
  grade: Grade;
  my_stats: Record<string, number>;
  metric_breakdown: Record<string, MetricEntry>;
  division: number;
  division_label: string;
  data_source: string;
  matches_analyzed: number;
  insights: string[];
}

const LIMIT_OPTIONS = [
  { value: 10, label: '10경기' },
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
];

const STATUS_COLORS: Record<string, string> = {
  elite: '#f59e0b',
  above_average: '#10b981',
  average: '#3b82f6',
  below_average: '#f59e0b',
  needs_work: '#ef4444',
};

const STATUS_LABELS: Record<string, string> = {
  elite: '엘리트급',
  above_average: '랭커 이상',
  average: '평균',
  below_average: '평균 이하',
  needs_work: '개선 필요',
};

const ScoreGauge: React.FC<{ score: number; grade: Grade }> = ({ score, grade }) => {
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;

  const scoreColor = score >= 80 ? '#f59e0b' : score >= 65 ? '#10b981' : score >= 50 ? '#3b82f6' : score >= 35 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-40 h-40">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="54" fill="none" stroke="#374151" strokeWidth="12" />
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke={scoreColor}
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-white">{score.toFixed(0)}</span>
          <span className="text-xs text-gray-400">/ 100</span>
        </div>
      </div>
      <div className="mt-2 text-center">
        <div className="text-lg font-bold" style={{ color: scoreColor }}>
          {grade.emoji} {grade.label}
        </div>
        <div className="text-xs text-gray-400">{grade.description}</div>
      </div>
    </div>
  );
};

const RankerGapPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<RankerGapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [matchtype, setMatchtype] = useState(50);
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    fetchData();
  }, [ouid, matchtype, limit]);

  const fetchData = async () => {
    if (!ouid) return;
    setLoading(true);
    setError('');
    try {
      const result = await cachedFetch(
        `rankerGap:${ouid}:${matchtype}:${limit}`,
        () => getRankerGapAnalysis(ouid, matchtype, limit),
        30 * 60 * 1000
      );
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.error || '랭커 격차 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={['매치 데이터 수집 중...', '랭커 벤치마크 비교 중...', '격차 점수 계산 중...', '인사이트 생성 중...']}
        estimatedDuration={6000}
        message="랭커 격차 대시보드"
      />
    );
  }

  if (error) return <ErrorMessage message={error} />;
  if (!data) return null;

  const radarData = Object.entries(data.metric_breakdown).map(([, metric]) => ({
    metric: metric.label,
    value: metric.proximity_score,
    fullMark: 100,
  }));

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>🏆</span>
                랭커 격차 대시보드
              </h1>
              <p className="text-gray-400 mt-1">
                내 플레이 전 차원을 랭커와 비교 — "랭커까지의 거리" 단일 점수 제공
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
            <div className="ml-auto flex items-center gap-3">
              <span className="text-sm text-gray-400">{data.matches_analyzed}경기 · {data.division_label}</span>
              {data.data_source === 'api' && (
                <span className="text-xs px-2 py-1 bg-green-900/30 border border-green-700/30 text-green-400 rounded">
                  실시간 랭커 데이터
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {/* Main score + radar */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-dark-card border border-dark-border rounded-lg p-8 flex flex-col items-center justify-center">
            <h2 className="text-xl font-bold text-white mb-6">랭커까지의 거리 점수</h2>
            <ScoreGauge score={data.ranker_distance_score} grade={data.grade} />
            <p className="text-xs text-gray-400 mt-4 text-center">
              100 = 랭커 이상 | 50 = 랭커 평균 | 0 = 많은 개선 필요
            </p>
          </div>

          {radarData.length > 0 && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">다차원 랭커 근접도</h2>
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="metric" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />
                  <Radar name="랭커 근접도" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                  <Radar name="랭커 기준" dataKey="fullMark" stroke="#f59e0b" fill="none" strokeDasharray="4 4" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                    formatter={(val: number | undefined) => [`${(val ?? 0).toFixed(0)}`, '근접도']}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Metric breakdown table */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>📋</span>
            메트릭별 세부 비교
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-400 border-b border-dark-border">
                  <th className="py-2 text-left">지표</th>
                  <th className="py-2 text-right">내 성적</th>
                  <th className="py-2 text-right">랭커 평균</th>
                  <th className="py-2 text-right">Z-score</th>
                  <th className="py-2 text-right">근접도</th>
                  <th className="py-2 text-left pl-4">상태</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(data.metric_breakdown).map(([key, metric]) => {
                  const statusColor = STATUS_COLORS[metric.status] || '#6b7280';
                  return (
                    <tr key={key} className="border-b border-dark-border/50 hover:bg-dark-hover">
                      <td className="py-3 text-gray-200">{metric.label}</td>
                      <td className="py-3 text-right font-bold text-white">{metric.my_value.toFixed(1)}</td>
                      <td className="py-3 text-right text-accent-primary">{metric.ranker_avg.toFixed(1)}</td>
                      <td className="py-3 text-right" style={{ color: statusColor }}>
                        {metric.z_score >= 0 ? '+' : ''}{metric.z_score.toFixed(2)}σ
                      </td>
                      <td className="py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <div className="w-16 bg-dark-hover rounded-full h-1.5">
                            <div
                              className="h-1.5 rounded-full"
                              style={{ width: `${metric.proximity_score}%`, backgroundColor: statusColor }}
                            />
                          </div>
                          <span style={{ color: statusColor }}>{metric.proximity_score.toFixed(0)}</span>
                        </div>
                      </td>
                      <td className="py-3 pl-4">
                        <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: statusColor + '20', color: statusColor }}>
                          {STATUS_LABELS[metric.status] || metric.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {Object.values(data.metric_breakdown).map((m) => (
            <p key={m.label} className="text-xs text-gray-500 mt-1">{m.gap_description}</p>
          ))}
        </div>

        {/* Insights */}
        {data.insights.length > 0 && (
          <div className="bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg p-6">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>💡</span> 랭커 격차 인사이트
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

export default RankerGapPage;
