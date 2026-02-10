import React from 'react';
import type { PlayerConnection, TopPlaymaker } from '../../types/match';
import PlayerAvatar from '../common/PlayerAvatar';

interface AssistNetworkProps {
  playerNetwork: PlayerConnection[];
  topPlaymakers: TopPlaymaker[];
}

const AssistNetwork: React.FC<AssistNetworkProps> = ({
  playerNetwork,
  topPlaymakers,
}) => {
  if (playerNetwork.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p>어시스트 연결 데이터가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Playmakers */}
      {topPlaymakers.length > 0 && (
        <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            찬스 메이커 TOP {Math.min(3, topPlaymakers.length)}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {topPlaymakers.slice(0, 3).map((playmaker, index) => (
              <div
                key={playmaker.spid}
                className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-yellow/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {/* Rank badge */}
                  <div className={`
                    flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm
                    ${index === 0 ? 'bg-yellow-500 text-gray-900' : ''}
                    ${index === 1 ? 'bg-gray-400 text-gray-900' : ''}
                    ${index === 2 ? 'bg-orange-600 text-white' : ''}
                  `}>
                    {index + 1}
                  </div>

                  {/* Player info */}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">
                      {playmaker.player_name}
                    </div>
                    <div className="text-xs text-gray-400">
                      {playmaker.total_assists} 어시스트
                    </div>
                  </div>

                  {/* Player image */}
                  <PlayerAvatar
                    spid={playmaker.spid}
                    playerName={playmaker.player_name}
                    size={48}
                    className="flex-shrink-0"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Player Connections */}
      <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">🔗</span>
          선수 간 연결
        </h3>
        <div className="space-y-3">
          {playerNetwork.map((connection, index) => (
            <div
              key={index}
              className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-chart-blue/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                {/* From player */}
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <PlayerAvatar
                    spid={connection.from_spid}
                    playerName={connection.from_player_name}
                    size={40}
                    className="flex-shrink-0"
                  />
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-white truncate">
                      {connection.from_player_name}
                    </div>
                    <div className="text-xs text-gray-500">어시스터</div>
                  </div>
                </div>

                {/* Arrow and count */}
                <div className="flex items-center gap-2 px-4">
                  <div className="text-chart-yellow font-bold text-lg">
                    {connection.assists}
                  </div>
                  <div className="text-2xl text-chart-blue">→</div>
                </div>

                {/* To player */}
                <div className="flex items-center gap-3 flex-1 min-w-0 justify-end">
                  <div className="min-w-0 text-right">
                    <div className="text-sm font-medium text-white truncate">
                      {connection.to_player_name}
                    </div>
                    <div className="text-xs text-gray-500">득점자</div>
                  </div>
                  <PlayerAvatar
                    spid={connection.to_spid}
                    playerName={connection.to_player_name}
                    size={40}
                    className="flex-shrink-0"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AssistNetwork;
