import React from 'react';
import type { PlayerPowerRanking } from '../../types/powerRanking';
import PlayerAvatar from '../common/PlayerAvatar';

interface PowerRankingSummaryProps {
  players: PlayerPowerRanking[];
  onPlayerClick: (spid: number) => void;
}

const PowerRankingSummary: React.FC<PowerRankingSummaryProps> = ({ players, onPlayerClick }) => {
  const getTierBg = (tier: string) => {
    switch (tier) {
      case 'SSS': return 'bg-gradient-to-r from-purple-600 to-pink-600';
      case 'SS':  return 'bg-gradient-to-r from-purple-500 to-pink-500';
      case 'S':   return 'bg-gradient-to-r from-purple-400 to-indigo-500';
      case 'A':   return 'bg-gradient-to-r from-blue-500 to-cyan-500';
      case 'B':   return 'bg-gradient-to-r from-green-500 to-emerald-500';
      case 'C':   return 'bg-gradient-to-r from-yellow-500 to-orange-500';
      default:    return 'bg-gradient-to-r from-gray-500 to-gray-600';
    }
  };

  const getTierTextColor = (tier: string) => {
    switch (tier) {
      case 'SSS':
      case 'SS':  return 'text-purple-400';
      case 'S':   return 'text-purple-300';
      case 'A':   return 'text-blue-400';
      case 'B':   return 'text-green-400';
      case 'C':   return 'text-yellow-400';
      default:    return 'text-gray-400';
    }
  };

  const getRowAccent = (tier: string) => {
    switch (tier) {
      case 'SSS':
      case 'SS':  return 'border-l-purple-500';
      case 'S':   return 'border-l-indigo-400';
      case 'A':   return 'border-l-blue-500';
      case 'B':   return 'border-l-green-500';
      case 'C':   return 'border-l-yellow-500';
      default:    return 'border-l-gray-600';
    }
  };

  const getPositionName = (position: number) => {
    const positions: { [key: number]: string } = {
      0: 'GK', 1: 'SW', 2: 'RWB', 3: 'RB', 4: 'RCB',
      5: 'CB', 6: 'LCB', 7: 'LB', 8: 'LWB', 9: 'RDM',
      10: 'CDM', 11: 'LDM', 12: 'RM', 13: 'RCM', 14: 'CM',
      15: 'LCM', 16: 'LM', 17: 'RAM', 18: 'CAM', 19: 'LAM',
      20: 'RF', 21: 'CF', 22: 'LF', 23: 'RW', 24: 'RS',
      25: 'ST', 26: 'LS', 27: 'LW'
    };
    return positions[position] || '—';
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'improving') return { icon: '▲', cls: 'text-green-400' };
    if (trend === 'declining') return { icon: '▼', cls: 'text-red-400' };
    return { icon: '—', cls: 'text-gray-500' };
  };

  const getRankStyle = (index: number) => {
    if (index === 0) return 'text-yellow-400 font-black';
    if (index === 1) return 'text-gray-300 font-bold';
    if (index === 2) return 'text-orange-400 font-bold';
    return 'text-gray-500 font-semibold';
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-xl shadow-dark-lg mb-8 overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-dark-border flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <span>⚡</span>
            선수 파워 랭킹
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">출전 선수 {players.length}명 · 클릭하여 상세 확인</p>
        </div>
        {/* Tier Legend */}
        <div className="hidden sm:flex items-center gap-3 text-[10px] text-gray-400">
          {['SSS', 'SS', 'S', 'A', 'B', 'C'].map(t => (
            <div key={t} className="flex items-center gap-1">
              <div className={`w-2.5 h-2.5 rounded-sm ${getTierBg(t)}`} />
              <span>{t}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Column Labels */}
      <div className="grid grid-cols-[2rem_1fr_auto_auto_auto_auto] sm:grid-cols-[2.5rem_1fr_3rem_3rem_4rem_3.5rem] items-center px-3 py-1.5 bg-dark-hover/60 border-b border-dark-border text-[10px] text-gray-500 uppercase tracking-wide font-semibold">
        <div className="text-center">#</div>
        <div className="pl-2">선수</div>
        <div className="text-center hidden sm:block">포지션</div>
        <div className="text-center">티어</div>
        <div className="text-center">파워점수</div>
        <div className="text-center hidden sm:block">폼</div>
      </div>

      {/* Player Rows */}
      <div className="divide-y divide-dark-border/50">
        {players.map((player, index) => {
          const trend = getTrendIcon(player.form_analysis.trend);
          return (
            <button
              key={player.spid}
              onClick={() => onPlayerClick(player.spid)}
              className={`w-full grid grid-cols-[2rem_1fr_auto_auto_auto_auto] sm:grid-cols-[2.5rem_1fr_3rem_3rem_4rem_3.5rem] items-center px-3 py-2 border-l-2 ${getRowAccent(player.tier)} hover:bg-dark-hover/70 transition-colors text-left group`}
            >
              {/* Rank */}
              <div className={`text-center text-sm ${getRankStyle(index)}`}>
                {index + 1}
              </div>

              {/* Player: image + name + season */}
              <div className="flex items-center gap-2 pl-2 min-w-0">
                <div className="relative flex-shrink-0">
                  <PlayerAvatar
                    spid={player.spid}
                    imageUrl={player.image_url}
                    playerName={player.player_name}
                    size={40}
                  />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold text-white truncate group-hover:text-accent-primary transition-colors leading-tight">
                    {player.player_name}
                  </div>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    {player.season_img ? (
                      <img src={player.season_img} alt={player.season_name} className="h-3.5 object-contain" title={player.season_name} />
                    ) : player.season_name ? (
                      <span className="text-[10px] text-gray-500">{player.season_name}</span>
                    ) : null}
                    <span className="text-[10px] text-gray-600">
                      {player.position_rating?.position_group_name || ''}
                    </span>
                  </div>
                </div>
              </div>

              {/* Position */}
              <div className="hidden sm:flex justify-center">
                <span className="text-[10px] text-gray-400 bg-dark-bg px-1.5 py-0.5 rounded font-mono">
                  {getPositionName(player.position)}
                </span>
              </div>

              {/* Tier */}
              <div className="flex justify-center">
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded text-white ${getTierBg(player.tier)}`}>
                  {player.tier}
                </span>
              </div>

              {/* Power Score */}
              <div className="text-center">
                <span className={`text-base font-black ${getTierTextColor(player.tier)}`}>
                  {player.power_score.toFixed(0)}
                </span>
              </div>

              {/* Form */}
              <div className="hidden sm:flex flex-col items-center justify-center">
                <span className="text-xs font-bold text-white leading-none">
                  {player.form_analysis.form_index.toFixed(0)}
                </span>
                <span className={`text-[10px] font-bold ${trend.cls}`}>{trend.icon}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default PowerRankingSummary;
