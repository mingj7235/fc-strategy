import React, { useState } from 'react';
import type { PlayerPowerRanking } from '../../types/powerRanking';
import RadarChart from '../charts/RadarChart';
import PlayerAvatar from '../common/PlayerAvatar';

// Translate technical metric names to Korean
const translateMetricKey = (key: string): string => {
  const translations: Record<string, string> = {
    // Main categories
    'scoring_ability': '득점 능력',
    'shooting_sense': '슈팅 감각',
    'link_play': '연계 플레이',
    'aerial_dominance': '공중볼 지배력',
    'consistency': '일관성',
    'defensive_ability': '수비 능력',
    'attacking_contribution': '공격 기여도',
    'stamina_consistency': '체력 및 일관성',
    'saving_ability': '선방 능력',
    'distribution': '배급',
    'buildup_contribution': '빌드업 기여',
    'stability': '안정성',
    'ball_winning': '볼 탈환',
    'pressing': '압박',
    'transition_play': '전환 플레이',
    'discipline_consistency': '규율 및 일관성',
    'creativity': '창의성',
    'passing_sense': '패스 감각',
    'finishing': '마무리',
    'dribbling': '드리블',
    'forward_contribution': '공격 가담',
    'passing': '패스',
    'rating': '평점',

    // Detailed metrics
    'score': '점수',
    'goals_per_game': '경기당 골',
    'shot_conversion': '슈팅 전환율 (%)',
    'goals_vs_xg': 'xG 대비',
    'total_goals': '총 골',
    'shot_accuracy': '정확도 (%)',
    'assists': '어시스트',
    'key_passes': '키패스',
    'aerial_wins_per_game': '경기당 공중볼',
    'consecutive_scoring_games': '연속 득점',
    'tackle_score': '태클',
    'tackle_success_rate': '태클 성공률 (%)',
    'defensive_actions_per_game': '경기당 수비',
    'blocks': '블록',
    'interceptions': '인터셉트',
    'cross_accuracy': '크로스 정확도',
    'dribble_success_rate': '드리블 성공률 (%)',
    'rating_variance': '평점 편차',
    'save_percentage': '선방률 (%)',
    'xg_prevention': 'xG 차단',
    'clean_sheets': '클린시트',
    'clean_sheet_rate': '클린시트 비율',
    'total_aerial_wins': '공중볼 성공',
    'passing_score': '패스',
    'pass_accuracy': '정확도 (%)',
    'long_pass_accuracy': '롱패스 정확도',
    'avg_passes_per_game': '경기당 패스',
    'total_errors': '실수',
    'avg_rating': '평균 평점',
    'through_passes': '스루패스',
    'long_passes': '롱패스',
    'goals': '골',
    'one_on_one_score': '1대1',
    'wing_defense_score': '측면수비',
    'positioning_score': '포지셔닝',
    'crossing_score': '크로스',
    'forward_play_score': '전진플레이',

    // Additional fields that were missing
    'assist_ability': '어시스트 능력',
    'successful_dribbles_per_game': '경기당 성공 드리블',
    'wing_activity': '측면 활동',
    'crosses_per_game': '경기당 크로스',
    'yellow_cards': '옐로카드',
    'red_cards': '레드카드',
    'discipline': '규율',
    'fouls': '파울',
    'crosses': '크로스',
  };

  return translations[key] || key;
};

interface PlayerPowerCardProps {
  player: PlayerPowerRanking;
  rank: number;
}

const PlayerPowerCard: React.FC<PlayerPowerCardProps> = ({ player, rank }) => {
  const [expanded, setExpanded] = useState(false);

  // Tier colors
  const getTierColor = (tier: string) => {
    if (tier === 'SSS') return 'from-purple-500 via-pink-500 to-yellow-500'; // Rainbow gradient
    if (tier === 'SS') return 'from-yellow-500 to-orange-500'; // Gold
    if (tier === 'S') return 'from-purple-500 to-indigo-500'; // Purple
    if (tier === 'A') return 'from-blue-500 to-cyan-500'; // Blue
    if (tier === 'B') return 'from-green-500 to-emerald-500'; // Green
    if (tier === 'C') return 'from-yellow-600 to-amber-600'; // Yellow
    return 'from-gray-500 to-gray-600'; // D tier - Gray
  };

  // Trend icons
  const getTrendIcon = (trend: string) => {
    if (trend === 'improving') return '📈';
    if (trend === 'declining') return '📉';
    return '➡️';
  };

  // Form grade color
  const getFormGradeColor = (grade: string) => {
    if (grade === 'excellent') return 'text-chart-green';
    if (grade === 'good') return 'text-chart-blue';
    if (grade === 'average') return 'text-chart-yellow';
    return 'text-chart-red';
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg shadow-dark-lg p-6 hover:border-accent-primary/50 transition-all">
      {/* Header: Rank, Image, Name, Tier */}
      <div className="flex items-start gap-4 mb-4">
        {/* Rank Badge */}
        <div className="flex-shrink-0">
          <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${rank <= 3 ? 'from-yellow-500 to-orange-500' : 'from-gray-600 to-gray-700'} flex items-center justify-center text-white font-bold text-xl shadow-lg`}>
            {rank}
          </div>
        </div>

        {/* Player Image */}
        <div className="flex-shrink-0 bg-dark-hover rounded-lg">
          <PlayerAvatar
            spid={player.spid}
            imageUrl={player.image_url}
            playerName={player.player_name}
            size={80}
          />
        </div>

        {/* Name and Tier */}
        <div className="flex-1">
          <h3 className="text-xl font-bold text-white mb-1">{player.player_name}</h3>
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-3 py-1 rounded-full bg-gradient-to-r ${getTierColor(player.tier)} text-white font-bold text-sm shadow-lg`}>
              {player.tier}
            </span>
            {player.position_rating && (
              <span className="px-2 py-1 bg-accent-primary/20 text-accent-primary rounded text-xs font-semibold">
                {player.position_rating.position_group_name}
              </span>
            )}
            <span className="text-gray-400 text-sm">{player.matches_played}경기</span>
          </div>
          <div className="text-sm text-gray-400 flex items-center gap-1 flex-wrap">
            {player.season_img ? (
              <img src={player.season_img} alt={player.season_name} className="h-4 object-contain" title={player.season_name} />
            ) : player.season_name ? (
              <span>{player.season_name}</span>
            ) : null}
            {(player.season_img || player.season_name) && <span>·</span>}
            <span>등급 {player.grade} · 상위 {player.percentile_rank}%</span>
          </div>
        </div>

        {/* Power Score */}
        <div className="flex-shrink-0 text-right">
          <div className="text-3xl font-bold text-accent-primary">{player.power_score}</div>
          <div className="text-xs text-gray-400">파워 스코어</div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        {/* Form */}
        <div className="bg-dark-hover border border-dark-border rounded-lg p-3">
          <div className="text-xs text-gray-400 mb-1">폼 지수</div>
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold text-white">{player.form_analysis.form_index}</span>
            <span className="text-lg">{getTrendIcon(player.form_analysis.trend)}</span>
          </div>
          <div className={`text-xs ${getFormGradeColor(player.form_analysis.form_grade)} font-semibold`}>
            {player.form_analysis.form_grade === 'excellent' ? '최고' :
             player.form_analysis.form_grade === 'good' ? '좋음' :
             player.form_analysis.form_grade === 'average' ? '보통' : '부진'}
          </div>
        </div>

        {/* Efficiency */}
        <div className="bg-dark-hover border border-dark-border rounded-lg p-3">
          <div className="text-xs text-gray-400 mb-1">효율성</div>
          <div className="text-xl font-bold text-white">{player.efficiency_metrics.efficiency_score.toFixed(1)}</div>
          <div className="text-xs text-gray-300">
            {player.efficiency_metrics.goals_per_game.toFixed(2)} G/경기
          </div>
        </div>

        {/* Consistency */}
        <div className="bg-dark-hover border border-dark-border rounded-lg p-3">
          <div className="text-xs text-gray-400 mb-1">일관성</div>
          <div className="text-xl font-bold text-white">{player.consistency_rating.consistency_score.toFixed(1)}</div>
          <div className="text-xs text-gray-300">
            {player.consistency_rating.grade === 'very_consistent' ? '매우 일관적' :
             player.consistency_rating.grade === 'consistent' ? '일관적' :
             player.consistency_rating.grade === 'moderate' ? '보통' : '불안정'}
          </div>
        </div>
      </div>

      {/* Expand/Collapse Button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full py-2 text-sm text-accent-primary hover:text-accent-secondary transition-colors font-semibold"
      >
        {expanded ? '▲ 접기' : '▼ 상세 보기'}
      </button>

      {/* Expanded Details */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-dark-border">
          {/* Radar Chart */}
          <div className="mb-6">
            <h4 className="text-sm font-bold text-white mb-3">종합 능력치</h4>
            <RadarChart data={player.radar_data} />
          </div>

          {/* Detailed Stats */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            {/* Goals & Assists */}
            <div className="bg-dark-hover border border-dark-border rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-2">공격 기여</div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">골/경기:</span>
                  <span className="text-white font-semibold">{player.efficiency_metrics.goals_per_game.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">어시/경기:</span>
                  <span className="text-white font-semibold">{player.efficiency_metrics.assists_per_game.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">골 전환율:</span>
                  <span className="text-white font-semibold">{player.efficiency_metrics.goal_conversion_rate.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* Accuracy */}
            <div className="bg-dark-hover border border-dark-border rounded-lg p-3">
              <div className="text-xs text-gray-400 mb-2">정확도</div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">패스:</span>
                  <span className="text-white font-semibold">{player.efficiency_metrics.pass_accuracy.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">드리블:</span>
                  <span className="text-white font-semibold">{player.efficiency_metrics.dribble_success_rate.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Position Rating */}
          {player.position_rating && (
            <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>🎯</span>
                  {player.position_rating.position_group_name} 평가
                </h4>
                <span className="text-2xl font-bold text-purple-400">
                  {player.position_rating.position_score.toFixed(1)}
                </span>
              </div>

              {/* Key Metrics */}
              {player.position_rating.key_metrics && Object.keys(player.position_rating.key_metrics).length > 0 && (
                <div className="mb-3 bg-dark-bg/50 rounded-lg p-3">
                  <div className="text-xs text-purple-300 font-semibold mb-2">핵심 지표</div>
                  <div className="space-y-2">
                    {Object.entries(player.position_rating.key_metrics).map(([key, value]) => {
                      // If value is an object, render it as a nested section
                      if (typeof value === 'object' && value !== null) {
                        return (
                          <div key={key} className="border-l-2 border-purple-500/30 pl-2 mb-2">
                            <div className="text-xs text-purple-200 font-semibold mb-1">
                              {translateMetricKey(key)}
                            </div>
                            <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                              {Object.entries(value as Record<string, any>).map(([subKey, subValue]) => (
                                <div key={subKey} className="text-xs flex justify-between">
                                  <span className="text-gray-400">{translateMetricKey(subKey)}</span>
                                  <span className="ml-2 text-white font-medium">
                                    {typeof subValue === 'number' ? subValue.toFixed(1) : String(subValue)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      }

                      // Simple value
                      return (
                        <div key={key} className="text-xs flex justify-between">
                          <span className="text-gray-400">{translateMetricKey(key)}</span>
                          <span className="ml-2 text-white font-semibold">
                            {typeof value === 'number' ? value.toFixed(1) : String(value)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Strengths */}
              {player.position_rating.strengths.length > 0 && (
                <div className="mb-3">
                  <div className="text-xs text-chart-green font-semibold mb-1">강점</div>
                  <div className="space-y-1">
                    {player.position_rating.strengths.map((strength, idx) => (
                      <div key={idx} className="text-sm text-gray-200 flex items-start gap-2">
                        <span className="text-chart-green">✓</span>
                        <span>{strength}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Weaknesses */}
              {player.position_rating.weaknesses.length > 0 && (
                <div className="mb-3">
                  <div className="text-xs text-chart-red font-semibold mb-1">약점</div>
                  <div className="space-y-1">
                    {player.position_rating.weaknesses.map((weakness, idx) => (
                      <div key={idx} className="text-sm text-gray-200 flex items-start gap-2">
                        <span className="text-chart-red">✗</span>
                        <span>{weakness}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Evaluation Criteria */}
              {player.position_rating.evaluation_criteria && Object.keys(player.position_rating.evaluation_criteria).length > 0 && (
                <div className="pt-3 border-t border-purple-500/20">
                  <div className="text-xs text-purple-300 font-semibold mb-2">평가 기준</div>
                  <div className="space-y-1">
                    {Object.entries(player.position_rating.evaluation_criteria).map(([key, value]) => (
                      <div key={key} className="text-xs text-gray-300 flex items-center justify-between">
                        <span>{key}</span>
                        <span className="text-purple-400 font-semibold">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Impact Analysis */}
          {player.impact_analysis && (
            <div className="mt-4 bg-dark-hover border border-dark-border rounded-lg p-4">
              <h4 className="text-sm font-bold text-white mb-3">영향력 분석</h4>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-xs text-gray-400">공격 영향력</div>
                  <div className="text-lg font-bold text-white">{player.impact_analysis.avg_offensive_impact.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400">창조 영향력</div>
                  <div className="text-lg font-bold text-white">{player.impact_analysis.avg_creative_impact.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400">클러치 영향력</div>
                  <div className="text-lg font-bold text-white">{player.impact_analysis.avg_clutch_impact.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400">총 영향력</div>
                  <div className="text-lg font-bold text-accent-primary">{player.impact_analysis.avg_total_impact.toFixed(1)}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PlayerPowerCard;
