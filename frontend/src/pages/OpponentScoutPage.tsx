import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOpponentDNA } from '../services/api';
import ErrorMessage from '../components/common/ErrorMessage';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

/* ─── 타입 정의 ────────────────────────────────────────── */

interface RadarEntry {
  axis: string;
  value: number;
  raw: number;
  description: string;
}

interface PlayStyle {
  style: string;
  label: string;
  description: string;
  counter_strategy: string;
  emoji: string;
}

interface StrategyItem {
  icon: string;
  title?: string;
  action?: string;
  desc?: string;
  reason?: string;
  level?: string;
  category?: string;
}

interface StrategyCard {
  headline: string;
  weaknesses: StrategyItem[];
  do_list: StrategyItem[];
  dont_list: StrategyItem[];
}

interface Performance {
  win_rate: number;
  draw_rate: number;
  loss_rate: number;
  goals_for_avg: number;
  goals_against_avg: number;
  shot_accuracy: number;
  pass_accuracy: number;
  matches: number;
  wins: number;
  draws: number;
  losses: number;
}

interface Dimension {
  key: string;
  label: string;
  icon: string;
  my_score: number;
  opp_score: number;
  my_detail: string;
  opp_detail: string;
}

interface KeyBattle {
  label: string;
  icon: string;
  verdict: string;
  color: string;
  desc: string;
  my_score: number;
  opp_score: number;
}

interface Scenario {
  type: string;
  color: string;
  icon: string;
  label: string;
  detail: string;
  score_line: string;
}

interface BattlePrediction {
  my_nickname: string;
  opp_nickname: string;
  my_performance: Performance;
  opp_performance: Performance;
  win_probability: number;
  draw_probability: number;
  lose_probability: number;
  my_xg: number;
  opp_xg: number;
  style_advantage: number;
  dimensions: Dimension[];
  key_battles: KeyBattle[];
  scenarios: Scenario[];
  verdict: string;
  verdict_icon: string;
  verdict_desc: string;
  data_quality: {
    my_matches: number;
    opp_matches: number;
    reliability: string;
    reliability_label: string;
  };
}

interface OpponentDNAData {
  matches_analyzed: number;
  indices: {
    buildup_index: number;
    attack_width_index: number;
    setpiece_dependency: number;
    formation_rigidity: number;
    late_collapse_rate: number;
    through_pass_ratio: number;
    shot_efficiency: number;
    heading_tendency: number;
    long_pass_ratio: number;
    avg_possession: number;
  };
  radar_data: RadarEntry[];
  play_style: PlayStyle;
  scouting_report: string[];
  strategy_card: StrategyCard;
  battle_prediction: BattlePrediction | null;
}

/* ─── 상수 ──────────────────────────────────────────────── */

const INDEX_LABELS: Record<string, { label: string; desc: string; icon: string }> = {
  avg_possession:     { label: '평균 점유율',    desc: '% 값',                  icon: '⚽' },
  buildup_index:      { label: '빌드업 지수',    desc: '높을수록 점유형 빌드업',  icon: '🔗' },
  long_pass_ratio:    { label: '장패 비율',      desc: '높을수록 직접형/카운터', icon: '🚀' },
  through_pass_ratio: { label: '스루패스 비율',  desc: '창의적 공격 성향',       icon: '🎨' },
  attack_width_index: { label: '공격 폭 지수',   desc: '높을수록 측면 공격',     icon: '↔️' },
  shot_efficiency:    { label: '슈팅 정확도',    desc: '유효슛 / 총슛 비율',     icon: '🎯' },
  heading_tendency:   { label: '헤딩 성향',      desc: '헤딩 슈팅 비율',         icon: '🦅' },
  setpiece_dependency:{ label: '세트피스 의존도', desc: '프리킥/페널티 득점 비율', icon: '⚽' },
  formation_rigidity: { label: '전술 유연성',    desc: '높을수록 다양한 포지션', icon: '🔄' },
  late_collapse_rate: { label: '후반 취약성',    desc: '75분+ 실점 비중',        icon: '⏰' },
};

const LEVEL_COLORS: Record<string, string> = {
  high: '#ef4444', medium: '#f59e0b', low: '#6b7280',
};

const BATTLE_COLORS: Record<string, string> = {
  green: '#10b981', red: '#ef4444', blue: '#3b82f6', amber: '#f59e0b', gray: '#6b7280',
};

const SCENARIO_BG: Record<string, string> = {
  green:  'bg-green-950/30 border-green-700/40',
  yellow: 'bg-amber-950/30 border-amber-700/40',
  red:    'bg-red-950/30 border-red-700/40',
};

/* ─── 전략 카드 컴포넌트 ────────────────────────────────── */
const StrategyCardSection: React.FC<{
  card: StrategyCard; opponentName: string; playStyle: PlayStyle;
}> = ({ card, opponentName, playStyle }) => (
  <div className="mb-8">
    <div className="bg-gradient-to-r from-accent-primary/20 via-dark-card to-dark-card border border-accent-primary/40 rounded-xl p-5 mb-4 flex items-center gap-4">
      <div className="text-5xl flex-shrink-0">{playStyle.emoji}</div>
      <div className="flex-1 min-w-0">
        <div className="text-xs text-gray-400 mb-0.5">"{opponentName}" 즉각 전략 요약</div>
        <div className="text-lg font-bold text-white leading-tight">{card.headline}</div>
      </div>
      <div className="text-right flex-shrink-0">
        <div className="text-xs text-gray-500">10초 안에 파악하세요</div>
        <div className="text-2xl mt-0.5">⚡</div>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="bg-red-950/30 border border-red-700/40 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg">🔴</span>
          <span className="text-sm font-bold text-red-400 uppercase tracking-wide">상대 약점</span>
        </div>
        {card.weaknesses.length === 0 ? (
          <p className="text-xs text-gray-500">특이 약점 없음</p>
        ) : (
          <div className="space-y-2.5">
            {card.weaknesses.map((w, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-base flex-shrink-0 mt-0.5">{w.icon}</span>
                <div>
                  <div className="text-sm font-bold" style={{ color: LEVEL_COLORS[w.level || 'medium'] }}>
                    {w.title}
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5 leading-snug">{w.desc}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-green-950/30 border border-green-700/40 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg">✅</span>
          <span className="text-sm font-bold text-green-400 uppercase tracking-wide">이렇게 해라</span>
        </div>
        {card.do_list.length === 0 ? (
          <p className="text-xs text-gray-500">데이터 부족</p>
        ) : (
          <div className="space-y-2.5">
            {card.do_list.map((d, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-base flex-shrink-0 mt-0.5">{d.icon}</span>
                <div>
                  {d.category && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-900/50 text-green-400 mr-1">
                      {d.category}
                    </span>
                  )}
                  <span className="text-sm font-bold text-white">{d.action}</span>
                  <div className="text-xs text-gray-400 mt-0.5 leading-snug">{d.reason}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-amber-950/30 border border-amber-700/40 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg">⚠️</span>
          <span className="text-sm font-bold text-amber-400 uppercase tracking-wide">이건 하지 마라</span>
        </div>
        {card.dont_list.length === 0 ? (
          <p className="text-xs text-gray-500">데이터 부족</p>
        ) : (
          <div className="space-y-2.5">
            {card.dont_list.map((d, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-base flex-shrink-0 mt-0.5">{d.icon}</span>
                <div>
                  <div className="text-sm font-bold text-amber-300">{d.action}</div>
                  <div className="text-xs text-gray-400 mt-0.5 leading-snug">{d.reason}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  </div>
);

/* ─── 승부 예측 섹션 ─────────────────────────────────────── */
const BattlePredictionSection: React.FC<{
  prediction: BattlePrediction;
}> = ({ prediction }) => {
  const { win_probability, draw_probability, lose_probability,
          my_nickname, opp_nickname, my_xg, opp_xg,
          my_performance: mp, opp_performance: op,
          dimensions, key_battles, scenarios,
          verdict, verdict_icon, verdict_desc, data_quality } = prediction;

  const reliabilityColor =
    data_quality.reliability === 'high'   ? 'text-green-400' :
    data_quality.reliability === 'medium' ? 'text-yellow-400' : 'text-red-400';

  const verdictBorder =
    verdict.includes('우세') && !verdict.includes('상대') ? 'border-green-500/50 bg-green-950/20' :
    verdict.includes('상대')                              ? 'border-red-500/50 bg-red-950/20' :
                                                            'border-yellow-500/50 bg-yellow-950/20';

  return (
    <div className="mb-8">
      {/* 섹션 헤더 */}
      <div className="flex items-center gap-3 mb-4">
        <div className="h-6 w-1 bg-accent-primary rounded-full" />
        <h2 className="text-lg font-bold text-white">나와의 승부 예측</h2>
        <span className="text-xs px-2 py-0.5 rounded bg-blue-900/40 text-blue-300 border border-blue-700/40">
          공식경기 기반
        </span>
        <span className={`text-xs ml-auto ${reliabilityColor}`}>
          데이터 신뢰도: {data_quality.reliability_label}
        </span>
      </div>

      {/* 종합 판정 배너 */}
      <div className={`border rounded-xl p-5 mb-5 ${verdictBorder}`}>
        <div className="flex items-center gap-4">
          <div className="text-4xl flex-shrink-0">{verdict_icon}</div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xl font-black text-white">{verdict}</span>
              <span className="text-xs text-gray-400">— Poisson 모델 + 전술 매치업 보정</span>
            </div>
            <p className="text-sm text-gray-300">{verdict_desc}</p>
          </div>
          <div className="text-right flex-shrink-0">
            <div className="text-xs text-gray-400 mb-1">예상 득점</div>
            <div className="text-lg font-bold text-white">
              {my_xg.toFixed(1)} <span className="text-gray-500 text-sm">vs</span> {opp_xg.toFixed(1)}
            </div>
            <div className="text-[10px] text-gray-500">{my_nickname} vs {opp_nickname}</div>
          </div>
        </div>
      </div>

      {/* 승/무/패 확률 게이지 */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-5 mb-5">
        <div className="flex items-center justify-between mb-3">
          <div className="text-center">
            <div className="text-2xl font-black text-green-400">{win_probability.toFixed(1)}%</div>
            <div className="text-xs text-gray-400">승리</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-black text-yellow-400">{draw_probability.toFixed(1)}%</div>
            <div className="text-xs text-gray-400">무승부</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-black text-red-400">{lose_probability.toFixed(1)}%</div>
            <div className="text-xs text-gray-400">패배</div>
          </div>
        </div>
        {/* 3색 게이지 바 */}
        <div className="h-4 rounded-full overflow-hidden flex">
          <div
            className="h-full bg-green-500 transition-all"
            style={{ width: `${win_probability}%` }}
          />
          <div
            className="h-full bg-yellow-500 transition-all"
            style={{ width: `${draw_probability}%` }}
          />
          <div
            className="h-full bg-red-500 transition-all"
            style={{ width: `${lose_probability}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-gray-500 mt-1">
          <span>{my_nickname}</span>
          <span>{opp_nickname}</span>
        </div>
      </div>

      {/* 실제 성적 비교 테이블 */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-5 mb-5">
        <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
          <span>📊</span> 실제 경기 성적 비교
        </h3>
        <div className="grid grid-cols-3 gap-2 text-center">
          {/* 헤더 */}
          <div className="text-xs font-bold text-blue-400 truncate">{my_nickname}</div>
          <div className="text-xs text-gray-500">지표</div>
          <div className="text-xs font-bold text-amber-400 truncate">{opp_nickname}</div>
          {/* 분석 경기 수 */}
          <div className="text-sm font-bold text-white">{data_quality.my_matches}경기</div>
          <div className="text-xs text-gray-500 py-1">분석 경기</div>
          <div className="text-sm font-bold text-white">{data_quality.opp_matches}경기</div>
          {/* 승률 */}
          <div className="text-sm font-bold text-green-400">{(mp.win_rate * 100).toFixed(0)}%</div>
          <div className="text-xs text-gray-500 py-1">승률</div>
          <div className="text-sm font-bold text-green-400">{(op.win_rate * 100).toFixed(0)}%</div>
          {/* 승/무/패 */}
          <div className="text-xs text-gray-300">{mp.wins}승 {mp.draws}무 {mp.losses}패</div>
          <div className="text-xs text-gray-500 py-1">전적</div>
          <div className="text-xs text-gray-300">{op.wins}승 {op.draws}무 {op.losses}패</div>
          {/* 경기당 득점 */}
          <div className={`text-sm font-bold ${mp.goals_for_avg >= op.goals_for_avg ? 'text-blue-400' : 'text-gray-300'}`}>
            {mp.goals_for_avg.toFixed(2)}골
          </div>
          <div className="text-xs text-gray-500 py-1">경기당 득점</div>
          <div className={`text-sm font-bold ${op.goals_for_avg >= mp.goals_for_avg ? 'text-amber-400' : 'text-gray-300'}`}>
            {op.goals_for_avg.toFixed(2)}골
          </div>
          {/* 경기당 실점 */}
          <div className={`text-sm font-bold ${mp.goals_against_avg <= op.goals_against_avg ? 'text-blue-400' : 'text-gray-300'}`}>
            {mp.goals_against_avg.toFixed(2)}골
          </div>
          <div className="text-xs text-gray-500 py-1">경기당 실점</div>
          <div className={`text-sm font-bold ${op.goals_against_avg <= mp.goals_against_avg ? 'text-amber-400' : 'text-gray-300'}`}>
            {op.goals_against_avg.toFixed(2)}골
          </div>
          {/* 유효슛 */}
          <div className={`text-sm font-bold ${mp.shot_accuracy >= op.shot_accuracy ? 'text-blue-400' : 'text-gray-300'}`}>
            {(mp.shot_accuracy * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500 py-1">유효슛 비율</div>
          <div className={`text-sm font-bold ${op.shot_accuracy >= mp.shot_accuracy ? 'text-amber-400' : 'text-gray-300'}`}>
            {(op.shot_accuracy * 100).toFixed(0)}%
          </div>
          {/* 패스 성공률 */}
          <div className={`text-sm font-bold ${mp.pass_accuracy >= op.pass_accuracy ? 'text-blue-400' : 'text-gray-300'}`}>
            {(mp.pass_accuracy * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500 py-1">패스 성공률</div>
          <div className={`text-sm font-bold ${op.pass_accuracy >= mp.pass_accuracy ? 'text-amber-400' : 'text-gray-300'}`}>
            {(op.pass_accuracy * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* 6개 차원 대결 */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-5 mb-5">
        <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <span>⚔️</span> 6개 차원 전술 대결
        </h3>
        <div className="space-y-4">
          {dimensions.map((dim) => {
            const total = dim.my_score + dim.opp_score || 1;
            const myPct = (dim.my_score / total) * 100;
            const myWins = dim.my_score > dim.opp_score;
            return (
              <div key={dim.key}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    {dim.icon} {dim.label}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold ${myWins ? 'text-blue-400' : 'text-gray-400'}`}>
                      {dim.my_score.toFixed(1)}
                    </span>
                    <span className="text-xs text-gray-600">vs</span>
                    <span className={`text-xs font-bold ${!myWins ? 'text-amber-400' : 'text-gray-400'}`}>
                      {dim.opp_score.toFixed(1)}
                    </span>
                  </div>
                </div>
                {/* 듀얼 바 */}
                <div className="h-2.5 bg-dark-hover rounded-full overflow-hidden flex">
                  <div
                    className="h-full rounded-l-full transition-all"
                    style={{
                      width: `${myPct}%`,
                      backgroundColor: myWins ? '#3b82f6' : '#374151',
                    }}
                  />
                  <div
                    className="h-full rounded-r-full transition-all"
                    style={{
                      width: `${100 - myPct}%`,
                      backgroundColor: !myWins ? '#f59e0b' : '#374151',
                    }}
                  />
                </div>
                <div className="flex justify-between mt-1">
                  <span className="text-[10px] text-gray-500 truncate max-w-[45%]">{dim.my_detail}</span>
                  <span className="text-[10px] text-gray-500 truncate max-w-[45%] text-right">{dim.opp_detail}</span>
                </div>
              </div>
            );
          })}
        </div>
        {/* 범례 */}
        <div className="flex items-center gap-4 mt-4 pt-3 border-t border-dark-border">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm bg-blue-500" />
            <span className="text-xs text-gray-400">{my_nickname}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm bg-amber-500" />
            <span className="text-xs text-gray-400">{opp_nickname}</span>
          </div>
        </div>
      </div>

      {/* 핵심 승부처 */}
      {key_battles.length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-xl p-5 mb-5">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <span>🔑</span> 핵심 승부처
          </h3>
          <div className="space-y-3">
            {key_battles.map((battle, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 p-3 rounded-lg bg-dark-hover border border-dark-border"
              >
                <span className="text-lg flex-shrink-0">{battle.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-bold text-white">{battle.label}</span>
                    <span
                      className="text-[10px] font-bold px-1.5 py-0.5 rounded"
                      style={{
                        color: BATTLE_COLORS[battle.color],
                        backgroundColor: `${BATTLE_COLORS[battle.color]}20`,
                        border: `1px solid ${BATTLE_COLORS[battle.color]}50`,
                      }}
                    >
                      {battle.verdict}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 leading-snug">{battle.desc}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="text-xs text-gray-500">나 vs 상대</div>
                  <div className="text-sm font-bold text-white">
                    {battle.my_score.toFixed(0)} : {battle.opp_score.toFixed(0)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 예상 시나리오 */}
      {scenarios.length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-xl p-5">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <span>📽️</span> 예상 시나리오
          </h3>
          <div className="space-y-3">
            {scenarios.map((s, idx) => (
              <div key={idx} className={`border rounded-lg p-4 ${SCENARIO_BG[s.color]}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-base">{s.icon}</span>
                    <span className="text-sm font-bold text-white">{s.label}</span>
                  </div>
                  <span className="text-xs text-gray-400">{s.score_line}</span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">{s.detail}</p>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-gray-600 mt-3">
            * Poisson 분포 모델 기반 확률 + 전술 DNA 스타일 보정. 실제 결과와 다를 수 있습니다.
          </p>
        </div>
      )}
    </div>
  );
};

/* ─── 메인 페이지 ────────────────────────────────────────── */
const OpponentScoutPage: React.FC = () => {
  const MY_NICKNAME_KEY = 'scout_my_nickname';

  const navigate = useNavigate();
  const [myNickname, setMyNickname]         = useState(() => localStorage.getItem(MY_NICKNAME_KEY) ?? '');
  const [nickname, setNickname]             = useState('');
  const [data, setData]                     = useState<OpponentDNAData | null>(null);
  const [loading, setLoading]               = useState(false);
  const [error, setError]                   = useState('');
  const [searched, setSearched]             = useState('');
  const [searchedMy, setSearchedMy]         = useState('');

  // 내 닉네임 변경 시 localStorage에 저장
  useEffect(() => {
    if (myNickname.trim()) {
      localStorage.setItem(MY_NICKNAME_KEY, myNickname);
    } else {
      localStorage.removeItem(MY_NICKNAME_KEY);
    }
  }, [myNickname]);

  const handleSearch = async () => {
    const trimmed = nickname.trim();
    if (!trimmed) return;
    setLoading(true);
    setError('');
    setData(null);
    try {
      const result = await getOpponentDNA(trimmed, myNickname.trim() || undefined);
      setData(result);
      setSearched(trimmed);
      setSearchedMy(myNickname.trim());
    } catch (err: any) {
      setError(err.response?.data?.error || '상대 DNA 분석을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <div className="bg-dark-card border-b border-dark-border py-6 px-8 shadow-dark-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>🔍</span>
                상대 DNA 스카우터
              </h1>
              <p className="text-gray-400 mt-1">
                상대 닉네임 입력 → 10초 안에 파악하는 맞춤 전략 + 데이터 기반 승부 예측
              </p>
            </div>
            <button
              onClick={() => navigate(-1)}
              className="px-4 py-2 bg-dark-hover border border-dark-border rounded-lg text-sm hover:bg-dark-border transition-colors"
            >
              ← 돌아가기
            </button>
          </div>

          {/* 검색 바 — my vs opponent */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            {/* 내 닉네임 (선택) */}
            <div className="flex-1 min-w-0">
              <label className="text-[10px] text-blue-400 font-semibold uppercase tracking-wide mb-1 flex items-center gap-1.5">
                내 닉네임 (선택 — 승부예측용)
                {myNickname && (
                  <span className="text-[10px] text-blue-300/60 normal-case font-normal">· 저장됨</span>
                )}
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={myNickname}
                  onChange={(e) => setMyNickname(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="내 닉네임..."
                  className="w-full px-4 py-2.5 pr-9 bg-blue-950/30 border border-blue-700/50 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                {myNickname && (
                  <button
                    onClick={() => setMyNickname('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors text-base leading-none"
                    title="내 닉네임 지우기"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            <div className="flex items-end pb-0.5 self-end">
              <div className="text-gray-500 font-bold text-lg px-2">VS</div>
            </div>

            {/* 상대 닉네임 (필수) */}
            <div className="flex-1 min-w-0">
              <label className="text-[10px] text-amber-400 font-semibold uppercase tracking-wide mb-1 block">
                상대 닉네임 (필수)
              </label>
              <input
                type="text"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="분석할 상대 닉네임..."
                className="w-full px-4 py-2.5 bg-amber-950/20 border border-amber-700/50 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-amber-500 text-sm"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={handleSearch}
                disabled={loading || !nickname.trim()}
                className="px-6 py-2.5 bg-accent-primary hover:bg-accent-primary/80 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-sm font-semibold transition-colors whitespace-nowrap"
              >
                {loading ? '분석 중...' : '스카우팅 시작'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-accent-primary border-t-transparent mb-4" />
            <p className="text-gray-400 text-sm">"{nickname}" 의 최근 경기를 분석하고 있습니다...</p>
            {myNickname && (
              <p className="text-gray-500 text-xs mt-1">내 닉네임 "{myNickname}" 데이터도 함께 수집 중...</p>
            )}
            <p className="text-gray-500 text-xs mt-2">최대 30초 소요될 수 있습니다.</p>
          </div>
        )}

        {/* Error */}
        {error && !loading && <ErrorMessage message={error} />}

        {/* Empty state */}
        {!loading && !data && !error && (
          <div className="text-center py-20 text-gray-400">
            <div className="text-6xl mb-6">🔍</div>
            <h2 className="text-xl font-bold text-white mb-2">경기 시작 전, 상대를 먼저 파악하세요</h2>
            <p className="text-sm mb-8">상대 닉네임만 입력해도 전략 카드를 제공합니다.<br/>내 닉네임까지 입력하면 데이터 기반 승부 예측도 제공합니다.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-3xl mx-auto text-left">
              {[
                { icon: '🔴', title: '상대 약점 3가지', desc: '어디를 공략할지 한눈에' },
                { icon: '✅', title: '즉각 전략 카드', desc: '공격·수비 전략을 바로 실행' },
                { icon: '📊', title: '승/무/패 확률', desc: 'Poisson 모델 기반 수학적 예측' },
                { icon: '⚔️', title: '6개 차원 대결', desc: '전술·체력·슈팅·수비 비교' },
              ].map((item) => (
                <div key={item.title} className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <div className="text-2xl mb-2">{item.icon}</div>
                  <div className="text-sm font-bold text-white">{item.title}</div>
                  <div className="text-xs text-gray-400 mt-1">{item.desc}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <>
            {/* ① 전략 카드 */}
            {data.strategy_card && (
              <StrategyCardSection
                card={data.strategy_card}
                opponentName={searched}
                playStyle={data.play_style}
              />
            )}

            {/* ② 승부 예측 */}
            {data.battle_prediction ? (
              <BattlePredictionSection prediction={data.battle_prediction} />
            ) : searchedMy === '' && (
              <div className="mb-8 border border-blue-700/30 bg-blue-950/10 rounded-xl p-5 flex items-center gap-4">
                <div className="text-3xl">🎯</div>
                <div>
                  <div className="text-sm font-bold text-white mb-0.5">승부 예측을 보고 싶으세요?</div>
                  <div className="text-xs text-gray-400">
                    위 검색창에서 <span className="text-blue-400 font-semibold">내 닉네임</span>을 함께 입력하면
                    Poisson 모델 기반 승/무/패 확률, 6개 차원 대결, 핵심 승부처를 분석해드립니다.
                  </div>
                </div>
              </div>
            )}

            {/* ③ 플레이 스타일 요약 */}
            <div className="bg-dark-card border border-dark-border rounded-lg p-5 mb-6 flex items-center gap-4">
              <div className="text-4xl">{data.play_style.emoji}</div>
              <div className="flex-1">
                <div className="text-xs text-gray-400 mb-0.5">전술 성향</div>
                <div className="text-lg font-bold text-white">{data.play_style.label}</div>
                <div className="text-sm text-gray-300">{data.play_style.description}</div>
              </div>
              <div className="text-right text-sm text-gray-400">
                <div className="text-xl font-bold text-white">{data.matches_analyzed}</div>
                <div>경기 분석</div>
              </div>
            </div>

            {/* ④ 레이더 + 지수 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {data.radar_data.length > 0 && (
                <div className="bg-dark-card border border-dark-border rounded-lg p-6">
                  <h2 className="text-lg font-bold text-white mb-4">전술 DNA 레이더</h2>
                  <ResponsiveContainer width="100%" height={260}>
                    <RadarChart data={data.radar_data}>
                      <PolarGrid stroke="#374151" />
                      <PolarAngleAxis dataKey="axis" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />
                      <Radar
                        name={searched}
                        dataKey="value"
                        stroke="#f59e0b"
                        fill="#f59e0b"
                        fillOpacity={0.25}
                      />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1a1f2e', border: '1px solid #374151', borderRadius: '8px' }}
                        formatter={(val: number | undefined, _: string | undefined, entry: any) => [
                          `${(val as number ?? 0).toFixed(0)} — ${entry.payload?.description || ''}`,
                          entry.payload?.axis || '',
                        ]}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div className="bg-dark-card border border-dark-border rounded-lg p-6">
                <h2 className="text-lg font-bold text-white mb-4">지수별 상세</h2>
                <div className="space-y-3">
                  {Object.entries(data.indices).map(([key, value]) => {
                    const meta = INDEX_LABELS[key];
                    if (!meta) return null;
                    const displayValue = key === 'avg_possession'
                      ? `${value.toFixed(1)}%`
                      : `${(value * 100).toFixed(1)}%`;
                    const barWidth = key === 'avg_possession'
                      ? value
                      : Math.min(100, value * 200);
                    const radar = data.radar_data.find(r => r.axis === meta.label);
                    const normalized = radar?.value ?? barWidth;
                    const color = normalized >= 65 ? '#f59e0b' : normalized >= 35 ? '#3b82f6' : '#10b981';
                    return (
                      <div key={key}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-gray-300">{meta.icon} {meta.label}</span>
                          <span className="text-xs font-bold text-white">{displayValue}</span>
                        </div>
                        <div className="h-1.5 bg-dark-hover rounded-full overflow-hidden">
                          <div
                            className="h-1.5 rounded-full transition-all"
                            style={{ width: `${normalized}%`, backgroundColor: color }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* ⑤ 스카우팅 리포트 */}
            {data.scouting_report.length > 0 && (
              <div className="bg-gradient-to-br from-amber-900/20 to-dark-card border border-amber-700/30 rounded-lg p-5">
                <h2 className="text-base font-bold text-white mb-3 flex items-center gap-2">
                  <span>📋</span> 상세 스카우팅 리포트
                </h2>
                {data.scouting_report.map((line, idx) => (
                  <p key={idx} className="text-gray-300 text-sm mb-1.5">{line}</p>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default OpponentScoutPage;
