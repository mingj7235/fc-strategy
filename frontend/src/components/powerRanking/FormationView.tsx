import React from 'react';
import type { PlayerPowerRanking } from '../../types/powerRanking';
import PlayerAvatar from '../common/PlayerAvatar';

interface FormationViewProps {
  players: PlayerPowerRanking[];
  onPlayerClick: (spid: number) => void;
}

const FormationView: React.FC<FormationViewProps> = ({ players, onPlayerClick }) => {
  // 포지션별로 라인 구분 및 위치 결정
  // Position codes from Nexon API (correct mapping from backend):
  // 0: GK, 1: SW, 2: RWB, 3: RB, 4: RCB, 5: CB, 6: LCB, 7: LB, 8: LWB, 9: RDM
  // 10: CDM, 11: LDM, 12: RM, 13: RCM, 14: CM, 15: LCM, 16: LM, 17: RAM
  // 18: CAM, 19: LAM, 20: RF, 21: CF, 22: LF, 23: RW, 24: RS, 25: ST, 26: LS, 27: LW
  const getFormationLine = (position: number): { line: string; order: number; sublane: 'left' | 'center' | 'right' } => {
    // GK
    if (position === 0) return { line: 'gk', order: 0, sublane: 'center' };

    // Defenders
    if (position === 1) return { line: 'def', order: 0, sublane: 'center' }; // SW (Sweeper)
    if ([4, 5, 6].includes(position)) { // RCB, CB, LCB
      if (position === 4) return { line: 'def', order: 1, sublane: 'right' }; // RCB
      if (position === 5) return { line: 'def', order: 0, sublane: 'center' }; // CB
      return { line: 'def', order: -1, sublane: 'left' }; // LCB
    }
    if ([2, 3].includes(position)) return { line: 'def', order: 2, sublane: 'right' }; // RWB, RB
    if ([7, 8].includes(position)) return { line: 'def', order: -2, sublane: 'left' }; // LB, LWB

    // Defensive Midfielders
    if ([9, 10, 11].includes(position)) { // RDM, CDM, LDM
      if (position === 9) return { line: 'dmf', order: 1, sublane: 'right' }; // RDM
      if (position === 10) return { line: 'dmf', order: 0, sublane: 'center' }; // CDM
      return { line: 'dmf', order: -1, sublane: 'left' }; // LDM
    }

    // Central Midfielders
    if ([13, 14, 15].includes(position)) { // RCM, CM, LCM
      if (position === 13) return { line: 'mid', order: 1, sublane: 'right' }; // RCM
      if (position === 14) return { line: 'mid', order: 0, sublane: 'center' }; // CM
      return { line: 'mid', order: -1, sublane: 'left' }; // LCM
    }

    // Wide Midfielders
    if (position === 12) return { line: 'mid', order: 2, sublane: 'right' }; // RM
    if (position === 16) return { line: 'mid', order: -2, sublane: 'left' }; // LM

    // Attacking Midfielders
    if ([17, 18, 19].includes(position)) { // RAM, CAM, LAM
      if (position === 17) return { line: 'amf', order: 1, sublane: 'right' }; // RAM
      if (position === 18) return { line: 'amf', order: 0, sublane: 'center' }; // CAM
      return { line: 'amf', order: -1, sublane: 'left' }; // LAM
    }

    // Forwards
    if (position === 20) return { line: 'fwd', order: 1, sublane: 'right' }; // RF
    if (position === 22) return { line: 'fwd', order: -1, sublane: 'left' }; // LF
    if (position === 21) return { line: 'fwd', order: 0, sublane: 'center' }; // CF

    // Wingers
    if (position === 23) return { line: 'fwd', order: 2, sublane: 'right' }; // RW
    if (position === 27) return { line: 'fwd', order: -2, sublane: 'left' }; // LW

    // Strikers
    if (position === 24) return { line: 'fwd', order: 1, sublane: 'right' }; // RS
    if (position === 26) return { line: 'fwd', order: -1, sublane: 'left' }; // LS
    if (position === 25) return { line: 'fwd', order: 0, sublane: 'center' }; // ST

    return { line: 'mid', order: 0, sublane: 'center' };
  };

  // 라인별로 그룹화
  const lines: { [key: string]: PlayerPowerRanking[] } = {
    gk: [],
    def: [],
    dmf: [],
    mid: [],
    amf: [],
    fwd: [],
  };

  players.forEach(player => {
    const { line } = getFormationLine(player.position);
    lines[line].push(player);
  });

  // 각 라인 내에서 order로 정렬
  Object.keys(lines).forEach(line => {
    lines[line].sort((a, b) => {
      const aPos = getFormationLine(a.position);
      const bPos = getFormationLine(b.position);
      return bPos.order - aPos.order;
    });
  });

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'SSS':
        return 'from-purple-600 to-pink-600';
      case 'SS':
        return 'from-purple-500 to-pink-500';
      case 'S':
        return 'from-purple-400 to-indigo-500';
      case 'A':
        return 'from-blue-500 to-cyan-500';
      case 'B':
        return 'from-green-500 to-emerald-500';
      case 'C':
        return 'from-yellow-500 to-orange-500';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const lineConfig = [
    { key: 'fwd', name: '공격', players: lines.fwd },
    { key: 'amf', name: '공격형 미드필더', players: lines.amf },
    { key: 'mid', name: '미드필더', players: lines.mid },
    { key: 'dmf', name: '수비형 미드필더', players: lines.dmf },
    { key: 'def', name: '수비', players: lines.def },
    { key: 'gk', name: '골키퍼', players: lines.gk },
  ];

  return (
    <div className="relative">
      {/* Soccer Field Background */}
      <div className="relative bg-gradient-to-b from-green-800 via-green-700 to-green-800 rounded-2xl p-4 md:p-8 overflow-hidden">
        {/* Field Lines */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-x-0 top-1/2 h-px bg-white transform -translate-y-1/2"></div>
          <div className="absolute left-1/2 inset-y-0 w-px bg-white transform -translate-x-1/2"></div>
          <div className="absolute left-1/2 top-1/2 w-24 h-24 border-2 border-white rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
        </div>

        {/* Formation Lines */}
        <div className="relative space-y-8">
          {lineConfig.map(line => {
            if (line.players.length === 0) return null;

            return (
              <div key={line.key} className="relative">
                {/* Line Label */}
                <div className="text-center mb-4">
                  <span className="inline-block bg-white/10 backdrop-blur-sm text-white text-xs font-semibold px-3 py-1 rounded-full border border-white/20">
                    {line.name} ({line.players.length})
                  </span>
                </div>

                {/* Players in Line */}
                <div className={`flex items-start justify-center gap-4 ${
                  line.players.length > 4 ? 'flex-wrap' : ''
                }`}>
                  {line.players.map(player => (
                    <button
                      key={player.spid}
                      onClick={() => onPlayerClick(player.spid)}
                      className="group relative flex flex-col items-center transform transition-all hover:scale-110 hover:z-10"
                      style={{ flexBasis: line.players.length > 4 ? '20%' : 'auto' }}
                    >
                      {/* Player Card */}
                      <div className={`relative bg-gradient-to-br ${getTierColor(player.tier)} rounded-xl p-3 shadow-2xl border-2 border-white/30 backdrop-blur-sm group-hover:border-white/60 transition-all w-28`}>
                        {/* Tier Badge */}
                        <div className="absolute -top-2 -right-2 bg-white text-xs font-bold px-2 py-1 rounded-full shadow-lg">
                          <span className={`bg-gradient-to-r ${getTierColor(player.tier)} bg-clip-text text-transparent`}>
                            {player.tier}
                          </span>
                        </div>

                        {/* Power Score */}
                        <div className="absolute -top-2 -left-2 bg-yellow-400 text-dark-bg text-xs font-bold px-2 py-1 rounded-full shadow-lg">
                          {player.power_score.toFixed(0)}
                        </div>

                        {/* Player Image */}
                        <div className="mb-2 flex justify-center">
                          <PlayerAvatar
                            spid={player.spid}
                            imageUrl={player.image_url}
                            playerName={player.player_name}
                            size={80}
                            className="filter drop-shadow-lg"
                          />
                        </div>

                        {/* Player Name & Season */}
                        <div className="text-center">
                          <div className="text-white font-bold text-sm truncate">
                            {player.player_name}
                          </div>
                          {(player.season_img || player.season_name) && (
                            <div className="flex justify-center mt-0.5" title={player.season_name}>
                              {player.season_img ? (
                                <img src={player.season_img} alt={player.season_name} className="h-4 object-contain" />
                              ) : (
                                <span className="text-white/60 text-[10px]">{player.season_name}</span>
                              )}
                            </div>
                          )}
                          {player.position_rating && (
                            <div className="text-white/90 text-xs mt-1 font-semibold">
                              {player.position_rating.position_group_name}
                            </div>
                          )}
                        </div>

                        {/* Quick Stats */}
                        <div className="mt-2 pt-2 border-t border-white/20 flex items-center justify-between text-xs text-white/90">
                          <span title="폼">📈 {player.form_analysis.form_index.toFixed(0)}</span>
                          <span title="경기수">🎮 {player.matches_played}</span>
                        </div>
                      </div>

                      {/* Hover Info */}
                      <div className="absolute -bottom-20 left-1/2 transform -translate-x-1/2 bg-dark-card border border-dark-border rounded-lg p-3 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none w-48 z-20">
                        <div className="text-xs space-y-1">
                          <div className="font-semibold text-white border-b border-dark-border pb-1 mb-1">
                            {player.player_name}
                          </div>
                          {player.position_rating && player.position_rating.strengths.length > 0 && (
                            <>
                              <div className="text-gray-400">강점:</div>
                              <div className="text-green-400">
                                {player.position_rating.strengths[0]}
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Formation Info */}
        <div className="mt-8 text-center">
          <div className="inline-block bg-white/10 backdrop-blur-sm text-white text-sm font-semibold px-4 py-2 rounded-full border border-white/20">
            총 {players.length}명의 선수
          </div>
        </div>
      </div>

      {/* Legend & Info */}
      <div className="mt-4 space-y-3">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex flex-wrap items-center justify-center gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded border-2 border-white/30"></div>
              <span className="text-gray-300">SSS/SS 티어</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-indigo-500 rounded border-2 border-white/30"></div>
              <span className="text-gray-300">S 티어</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded border-2 border-white/30"></div>
              <span className="text-gray-300">A 티어</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-500 rounded border-2 border-white/30"></div>
              <span className="text-gray-300">B 티어</span>
            </div>
          </div>
        </div>

        {/* Position Info Note */}
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <div className="flex items-start gap-2 text-xs text-blue-300">
            <span className="text-lg">ℹ️</span>
            <div>
              <div className="font-semibold mb-1">포지션 정보</div>
              <div className="text-blue-200/80">
                표시된 포지션은 실제 매치 데이터를 기반으로 하며, 여러 경기에서 사용된 포지션을 종합한 결과입니다.
                스쿼드 설정과 다를 수 있으며, 이는 경기 중 전술적 배치를 반영합니다.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormationView;
