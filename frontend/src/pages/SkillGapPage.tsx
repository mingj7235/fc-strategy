import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSkillGapAnalysis } from '../services/api';
import LoadingProgress from '../components/common/LoadingProgress';
import ErrorMessage from '../components/common/ErrorMessage';
import MatchTypeSelector from '../components/common/MatchTypeSelector';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface MetricGap {
  label: string;
  description: string;
  my_value: number;
  ranker_avg: number;
  ranker_std: number;
  z_score: number;
  percentile: number;
  gap_level: string;
  gap_level_info: { label: string; color: string; emoji: string };
}

interface PlayerGap {
  spid: number;
  player_name: string;
  position: number;
  appearances: number;
  image_url: string;
  metric_gaps: Record<string, MetricGap>;
  priority_improvements: Array<{ metric: string; label: string; gap: number; my_value: number; ranker_avg: number }>;
  overall_z_score: number;
  overall_level: string;
  overall_level_info: { label: string; color: string; emoji: string };
  ranker_proximity: number;
  improvement_guide: string[];
}

interface SkillGapData {
  matches_analyzed: number;
  players_analyzed: number;
  player_gaps: PlayerGap[];
  insights: string[];
}

const LIMIT_OPTIONS = [
  { value: 20, label: '20경기' },
  { value: 30, label: '30경기' },
  { value: 50, label: '50경기' },
];

const GAP_COLORS: Record<string, string> = {
  ranker_level: '#f59e0b',
  near_ranker: '#10b981',
  slight_gap: '#3b82f6',
  moderate_gap: '#f59e0b',
  significant_gap: '#ef4444',
  large_gap: '#7f1d1d',
};

const ZScoreBar: React.FC<{ z: number; label: string; myVal: number; rankerAvg: number }> = ({
  z, label, myVal, rankerAvg,
}) => {
  const clampedZ = Math.max(-3, Math.min(3, z));
  const barWidth = ((clampedZ + 3) / 6) * 100;
  const barColor = z >= 0 ? '#10b981' : z >= -1 ? '#f59e0b' : '#ef4444';

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-300">{label}</span>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span>내 성적: <strong className="text-white">{myVal.toFixed(1)}</strong></span>
          <span>랭커: <strong className="text-accent-primary">{rankerAvg.toFixed(1)}</strong></span>
          <span style={{ color: barColor }}>Z: {z >= 0 ? '+' : ''}{z.toFixed(2)}</span>
        </div>
      </div>
      <div className="relative h-3 bg-dark-hover rounded-full overflow-hidden">
        {/* Center line */}
        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-500 z-10" />
        <div
          className="absolute top-0 bottom-0 rounded-full transition-all"
          style={{
            left: 0,
            width: `${barWidth}%`,
            backgroundColor: barColor,
            opacity: 0.8,
          }}
        />
      </div>
      <div className="flex justify-between text-xs text-gray-600 mt-0.5">
        <span>랭커 -3σ</span>
        <span>랭커 평균</span>
        <span>랭커 +3σ</span>
      </div>
    </div>
  );
};

const PlayerGapCard: React.FC<{ gap: PlayerGap; index: number }> = ({ gap, index }) => {
  const [expanded, setExpanded] = useState(index === 0);
  const levelInfo = gap.overall_level_info;
  const levelColor = GAP_COLORS[gap.overall_level] || '#6b7280';

  const radarData = Object.entries(gap.metric_gaps).map(([key, metric]) => ({
    metric: metric.label,
    value: Math.max(0, Math.min(100, 50 + metric.z_score * 15)),
    fullMark: 100,
  }));

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden mb-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-4 p-4 hover:bg-dark-hover transition-colors text-left"
      >
        <img
          src={gap.image_url}
          alt={gap.player_name}
          className="w-12 h-12 object-contain rounded-lg bg-dark-hover"
          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
        />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">{gap.player_name}</span>
            <span className="text-xs text-gray-400">({gap.appearances}경기)</span>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span
              className="text-xs px-2 py-0.5 rounded-full font-semibold"
              style={{ backgroundColor: levelColor + '20', color: levelColor }}
            >
              {levelInfo?.emoji} {levelInfo?.label}
            </span>
            <span className="text-xs text-gray-400">
              랭커 근접도 {gap.ranker_proximity.toFixed(0)}%ile
            </span>
          </div>
        </div>

        {/* Overall Z-score gauge */}
        <div className="text-right">
          <div
            className="text-2xl font-bold"
            style={{ color: gap.overall_z_score >= 0 ? '#10b981' : gap.overall_z_score >= -1 ? '#f59e0b' : '#ef4444' }}
          >
            {gap.overall_z_score >= 0 ? '+' : ''}{gap.overall_z_score.toFixed(2)}σ
          </div>
          <div className="text-xs text-gray-400">종합 Z-score</div>
        </div>

        <span className="text-gray-400">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="border-t border-dark-border p-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Metric Z-score bars */}
            <div>
              <h4 className="text-sm font-bold text-gray-300 mb-3">메트릭별 격차 분석</h4>
              {Object.entries(gap.metric_gaps).map(([key, metric]) => (
                <ZScoreBar
                  key={key}
                  z={metric.z_score}
                  label={metric.label}
                  myVal={metric.my_value}
                  rankerAvg={metric.ranker_avg}
                />
              ))}
            </div>

            {/* Radar chart */}
            {radarData.length > 0 && (
              <div>
                <h4 className="text-sm font-bold text-gray-300 mb-3">랭커 대비 역량 분포</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#374151" />
                    <PolarAngleAxis dataKey="metric" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />
                    <Radar
                      name="내 성적"
                      dataKey="value"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.3}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                      labelStyle={{ color: '#fff' }}
                      formatter={(val: number) => [`${val.toFixed(0)}`, '랭커 근접도']}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Priority improvements */}
          {gap.priority_improvements.length > 0 && (
            <div className="mt-4 bg-dark-hover border border-dark-border rounded-lg p-4">
              <h4 className="text-sm font-bold text-amber-400 mb-2">우선 개선 포인트</h4>
              {gap.priority_improvements.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm text-gray-300 mb-1">
                  <span className="text-red-400">#{idx + 1}</span>
                  <span>{item.label}: {item.my_value.toFixed(1)} → 랭커 {item.ranker_avg.toFixed(1)}
                    <span className="text-red-400 ml-1">({item.gap.toFixed(1)}σ 격차)</span>
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Improvement guide */}
          {gap.improvement_guide.length > 0 && (
            <div className="mt-4 bg-blue-900/20 border border-blue-800/30 rounded-lg p-4">
              <h4 className="text-sm font-bold text-blue-400 mb-2">개선 가이드</h4>
              {gap.improvement_guide.map((guide, idx) => (
                <p key={idx} className="text-sm text-gray-200 mb-1">{guide}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const SkillGapPage: React.FC = () => {
  const { ouid } = useParams<{ ouid: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<SkillGapData | null>(null);
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
      const result = await getSkillGapAnalysis(ouid, matchtype, limit);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.error || '실력 격차 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <LoadingProgress
        steps={['랭커 스탯 수집 중...', '내 성적과 비교 중...', 'Z-score 계산 중...', '개선 가이드 생성 중...']}
        estimatedDuration={8000}
        message="실력 격차 분석"
      />
    );
  }

  if (error) return <ErrorMessage message={error} />;
  if (!data) return null;

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>📊</span>
                실력 격차 인덱스
              </h1>
              <p className="text-gray-400 mt-1">
                내가 쓰는 선수로 랭커가 내는 성적 vs 내 성적 — Z-score 정량 비교
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
              {data.matches_analyzed}경기 · {data.players_analyzed}명 분석
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {/* Insights */}
        {data.insights.length > 0 && (
          <div className="bg-gradient-to-br from-accent-primary/10 to-dark-card border border-accent-primary/30 rounded-lg p-6 mb-8">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>💡</span> 종합 인사이트
            </h2>
            {data.insights.map((ins, idx) => (
              <p key={idx} className="text-gray-200 text-sm mb-2">{ins}</p>
            ))}
          </div>
        )}

        {/* Z-score explanation */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4 mb-6">
          <h3 className="text-sm font-bold text-gray-300 mb-2">Z-score 해석 가이드</h3>
          <div className="flex flex-wrap gap-3 text-xs">
            {[
              { range: '+1σ 이상', label: '랭커급', color: '#f59e0b' },
              { range: '0 ~ +1σ', label: '랭커 근접', color: '#10b981' },
              { range: '-0.5 ~ 0', label: '소폭 격차', color: '#3b82f6' },
              { range: '-1 ~ -0.5σ', label: '중간 격차', color: '#f59e0b' },
              { range: '-2 ~ -1σ', label: '큰 격차', color: '#ef4444' },
              { range: '-2σ 미만', label: '매우 큰 격차', color: '#7f1d1d' },
            ].map(({ range, label, color }) => (
              <span key={range} className="px-2 py-1 rounded" style={{ backgroundColor: color + '20', color }}>
                {range}: {label}
              </span>
            ))}
          </div>
        </div>

        {/* Player gap cards */}
        {data.player_gaps.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <div className="text-5xl mb-4">📊</div>
            <p className="text-lg">5경기 이상 플레이한 선수 데이터가 없습니다.</p>
            <p className="text-sm mt-2">더 많은 경기를 진행하면 분석이 가능합니다.</p>
          </div>
        ) : (
          <div>
            <h2 className="text-xl font-bold text-white mb-4">선수별 격차 분석</h2>
            {data.player_gaps.map((gap, idx) => (
              <PlayerGapCard key={gap.spid} gap={gap} index={idx} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SkillGapPage;
