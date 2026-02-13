import React from 'react';
import type { PlayerPowerRanking } from '../../types/powerRanking';
import PlayerAvatar from '../common/PlayerAvatar';

interface PositionGroupViewProps {
  players: PlayerPowerRanking[];
  onPlayerClick: (spid: number) => void;
}

const PositionGroupView: React.FC<PositionGroupViewProps> = ({ players, onPlayerClick }) => {
  // 포지션 그룹 매핑
  // Position codes based on Nexon API:
  // 0: GK, 1: SW, 2: RWB, 3: RB, 4: RCB, 5: CB, 6: LCB, 7: LB, 8: LWB, 9: RDM
  // 10: CDM, 11: LDM, 12: RM, 13: RCM, 14: CM, 15: LCM, 16: LM, 17: RAM
  // 18: CAM, 19: LAM, 20: RF, 21: CF, 22: LF, 23: RW, 24: RS
  // 25: ST, 26: LS, 27: LW
  const getPositionGroup = (position: number): string => {
    if (position === 0) return 'GK';
    if ([1, 4, 5, 6].includes(position)) return 'CB'; // SW, RCB, CB, LCB
    if ([3, 7].includes(position)) return 'FB'; // RB, LB
    if ([2, 8].includes(position)) return 'WB'; // RWB, LWB
    if ([9, 10, 11].includes(position)) return 'CDM'; // RDM, CDM, LDM
    if ([13, 14, 15].includes(position)) return 'CM'; // RCM, CM, LCM
    if ([17, 18, 19].includes(position)) return 'CAM'; // RAM, CAM, LAM
    if ([12, 16].includes(position)) return 'WM'; // RM, LM
    if ([20, 22, 23, 27].includes(position)) return 'W'; // RF, LF, RW, LW
    if ([21, 24, 25, 26].includes(position)) return 'ST'; // CF, RS, ST, LS
    return 'CM';
  };

  // 포지션별로 그룹화
  const groupedPlayers: { [key: string]: PlayerPowerRanking[] } = {};

  players.forEach(player => {
    const group = player.position_rating?.position_group || getPositionGroup(player.position);
    if (!groupedPlayers[group]) {
      groupedPlayers[group] = [];
    }
    groupedPlayers[group].push(player);
  });

  // 각 그룹 내에서 파워 스코어순 정렬
  Object.keys(groupedPlayers).forEach(group => {
    groupedPlayers[group].sort((a, b) => b.power_score - a.power_score);
  });

  // 그룹 순서 및 정보
  const groupOrder = [
    { key: 'ST', name: '스트라이커', icon: '⚽', color: 'from-red-500 to-orange-500', bgColor: 'from-red-500/10 to-orange-500/10', borderColor: 'border-red-500/30' },
    { key: 'W', name: '윙어', icon: '⚡', color: 'from-yellow-500 to-orange-500', bgColor: 'from-yellow-500/10 to-orange-500/10', borderColor: 'border-yellow-500/30' },
    { key: 'CAM', name: '공격형 미드필더', icon: '🎯', color: 'from-purple-500 to-pink-500', bgColor: 'from-purple-500/10 to-pink-500/10', borderColor: 'border-purple-500/30' },
    { key: 'WM', name: '측면 미드필더', icon: '🔥', color: 'from-orange-500 to-red-500', bgColor: 'from-orange-500/10 to-red-500/10', borderColor: 'border-orange-500/30' },
    { key: 'CM', name: '중앙 미드필더', icon: '⚙️', color: 'from-blue-500 to-cyan-500', bgColor: 'from-blue-500/10 to-cyan-500/10', borderColor: 'border-blue-500/30' },
    { key: 'CDM', name: '수비형 미드필더', icon: '🛡️', color: 'from-green-500 to-teal-500', bgColor: 'from-green-500/10 to-teal-500/10', borderColor: 'border-green-500/30' },
    { key: 'WB', name: '윙백', icon: '🏃', color: 'from-indigo-500 to-purple-500', bgColor: 'from-indigo-500/10 to-purple-500/10', borderColor: 'border-indigo-500/30' },
    { key: 'FB', name: '풀백', icon: '🔷', color: 'from-blue-600 to-indigo-600', bgColor: 'from-blue-600/10 to-indigo-600/10', borderColor: 'border-blue-600/30' },
    { key: 'CB', name: '센터백', icon: '🧱', color: 'from-gray-600 to-gray-800', bgColor: 'from-gray-600/10 to-gray-800/10', borderColor: 'border-gray-600/30' },
    { key: 'GK', name: '골키퍼', icon: '🧤', color: 'from-yellow-600 to-amber-700', bgColor: 'from-yellow-600/10 to-amber-700/10', borderColor: 'border-yellow-600/30' },
  ];

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'SSS':
      case 'SS':
        return 'text-purple-400';
      case 'S':
        return 'text-purple-300';
      case 'A':
        return 'text-blue-400';
      case 'B':
        return 'text-green-400';
      case 'C':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {groupOrder.map(group => {
        const playersInGroup = groupedPlayers[group.key];
        if (!playersInGroup || playersInGroup.length === 0) return null;

        return (
          <div key={group.key} className={`bg-gradient-to-br ${group.bgColor} border ${group.borderColor} rounded-xl p-6`}>
            {/* Group Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{group.icon}</span>
                <div>
                  <h3 className="text-xl font-bold text-white">{group.name}</h3>
                  <p className="text-sm text-gray-400">{playersInGroup.length}명</p>
                </div>
              </div>
              <div className={`px-4 py-2 bg-gradient-to-r ${group.color} rounded-lg text-white font-bold text-sm`}>
                {group.key}
              </div>
            </div>

            {/* Players Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {playersInGroup.map((player, index) => (
                <button
                  key={player.spid}
                  onClick={() => onPlayerClick(player.spid)}
                  className="bg-dark-card hover:bg-dark-hover border border-dark-border hover:border-accent-primary/50 rounded-lg p-4 transition-all hover:scale-105 hover:shadow-lg text-left relative group"
                >
                  {/* Rank Badge */}
                  {index < 3 && (
                    <div className={`absolute -top-2 -left-2 ${
                      index === 0 ? 'bg-yellow-500' :
                      index === 1 ? 'bg-gray-400' :
                      'bg-orange-600'
                    } text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center shadow-lg`}>
                      {index + 1}
                    </div>
                  )}

                  <div className="flex items-start gap-3 mb-3">
                    {/* Player Image */}
                    <div className="relative flex-shrink-0">
                      <PlayerAvatar
                        spid={player.spid}
                        imageUrl={player.image_url}
                        playerName={player.player_name}
                        size={64}
                      />
                      {/* Tier Badge */}
                      <div className={`absolute -bottom-1 -right-1 ${getTierColor(player.tier)} text-[10px] font-bold bg-dark-bg px-1.5 py-0.5 rounded border border-dark-border`}>
                        {player.tier}
                      </div>
                    </div>

                    {/* Player Info */}
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-white truncate group-hover:text-accent-primary transition-colors">
                        {player.player_name}
                      </div>
                      {(player.season_img || player.season_name) && (
                        <div className="text-xs text-gray-500 truncate" title={player.season_name}>
                          {player.season_img ? (
                            <img src={player.season_img} alt={player.season_name} className="h-4 object-contain" />
                          ) : (
                            player.season_name
                          )}
                        </div>
                      )}
                      <div className="text-xs text-gray-400 mt-1">
                        {player.matches_played}경기 출전
                      </div>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-400">파워 스코어</span>
                      <span className="text-accent-primary font-bold">
                        {player.power_score.toFixed(1)}
                      </span>
                    </div>

                    {player.position_rating && (
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-400">포지션 점수</span>
                        <span className="text-green-400 font-bold">
                          {player.position_rating.position_score.toFixed(1)}
                        </span>
                      </div>
                    )}

                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-400">폼 지수</span>
                      <span className="text-blue-400 font-bold">
                        {player.form_analysis.form_index.toFixed(0)}
                      </span>
                    </div>
                  </div>

                  {/* Quick Strengths */}
                  {player.position_rating && player.position_rating.strengths.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-dark-border">
                      <div className="text-xs text-gray-500 mb-1">강점</div>
                      <div className="text-xs text-green-400 truncate">
                        {player.position_rating.strengths[0]}
                      </div>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default PositionGroupView;
