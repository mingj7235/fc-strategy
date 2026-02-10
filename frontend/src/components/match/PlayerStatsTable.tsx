import React from 'react';
import type { PlayerPerformance } from '../../types/match';
import PlayerAvatar from '../common/PlayerAvatar';

interface PlayerStatsTableProps {
  players: PlayerPerformance[];
  title: string;
}

const PlayerStatsTable: React.FC<PlayerStatsTableProps> = ({ players, title }) => {

  const getRatingColorClass = (rating: number | string) => {
    const ratingNum = typeof rating === 'string' ? parseFloat(rating) : rating;
    if (ratingNum >= 8.0) return 'text-chart-green font-bold';
    if (ratingNum >= 7.0) return 'text-chart-yellow font-semibold';
    return 'text-chart-red';
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden shadow-dark-lg">
      <div className="px-4 py-3 bg-dark-hover border-b border-dark-border">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>

      {/* Desktop Table View */}
      <div className="hidden md:block overflow-x-auto">
        <table className="min-w-full divide-y divide-dark-border">
          <thead className="bg-dark-hover/50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                선수
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                평점
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                골
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                AS
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                슈팅
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                패스
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                드리블
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                수비
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-border">
            {players.map((player) => (
              <tr key={player.spid} className="hover:bg-dark-hover/50 transition-colors">
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-10 h-10 mr-3">
                      <PlayerAvatar
                        spid={player.spid}
                        imageUrl={player.image_url}
                        playerName={player.player_name}
                        size={40}
                      />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-white max-w-[150px] truncate">
                        {player.player_name}
                      </div>
                      {(player.season_img || player.season_name) && (
                        <div className="text-xs text-gray-400" title={player.season_name}>
                          {player.season_img ? (
                            <img src={player.season_img} alt={player.season_name} className="h-4 object-contain" />
                          ) : (
                            player.season_name
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center">
                  <span className={`text-sm ${getRatingColorClass(player.rating)}`}>
                    {typeof player.rating === 'string' ? parseFloat(player.rating).toFixed(1) : player.rating.toFixed(1)}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center text-sm text-white">
                  {player.goals}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center text-sm text-white">
                  {player.assists}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center text-sm text-gray-300">
                  {player.shots_on_target}/{player.shots}
                  {player.shots > 0 && player.shot_accuracy != null && (
                    <span className="text-xs text-gray-500 ml-1">
                      ({parseFloat(player.shot_accuracy.toString()).toFixed(0)}%)
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center text-sm text-gray-300">
                  {player.pass_success}/{player.pass_attempts}
                  {player.pass_attempts > 0 && player.pass_success_rate != null && (
                    <span className="text-xs text-gray-500 ml-1">
                      ({parseFloat(player.pass_success_rate.toString()).toFixed(0)}%)
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center text-sm text-gray-300">
                  {player.dribble_success}/{player.dribble_attempts}
                  {player.dribble_attempts > 0 && player.dribble_success_rate != null && (
                    <span className="text-xs text-gray-500 ml-1">
                      ({parseFloat(player.dribble_success_rate.toString()).toFixed(0)}%)
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center text-sm text-gray-300">
                  {player.tackle_success + player.interceptions + player.blocks}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden divide-y divide-dark-border">
        {players.map((player) => (
          <div key={player.spid} className="p-4 hover:bg-dark-hover/50 transition-colors">
            <div className="flex items-center mb-3">
              <div className="w-12 h-12 mr-3">
                <PlayerAvatar
                  spid={player.spid}
                  imageUrl={player.image_url}
                  playerName={player.player_name}
                  size={48}
                />
              </div>
              <div className="flex-1">
                <div className="font-medium text-white">{player.player_name}</div>
                {(player.season_img || player.season_name) && (
                  <div className="text-xs text-gray-400" title={player.season_name}>
                    {player.season_img ? (
                      <img src={player.season_img} alt={player.season_name} className="h-4 object-contain" />
                    ) : (
                      player.season_name
                    )}
                  </div>
                )}
                <div className={`text-lg ${getRatingColorClass(player.rating)}`}>
                  평점: {typeof player.rating === 'string' ? parseFloat(player.rating).toFixed(1) : player.rating.toFixed(1)}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex justify-between bg-dark-bg/50 px-2 py-1 rounded">
                <span className="text-gray-400">골</span>
                <span className="font-medium text-white">{player.goals}</span>
              </div>
              <div className="flex justify-between bg-dark-bg/50 px-2 py-1 rounded">
                <span className="text-gray-400">AS</span>
                <span className="font-medium text-white">{player.assists}</span>
              </div>
              <div className="flex justify-between bg-dark-bg/50 px-2 py-1 rounded">
                <span className="text-gray-400">슈팅</span>
                <span className="font-medium text-white">{player.shots_on_target}/{player.shots}</span>
              </div>
              <div className="flex justify-between bg-dark-bg/50 px-2 py-1 rounded">
                <span className="text-gray-400">패스</span>
                <span className="font-medium text-white">
                  {player.pass_success}/{player.pass_attempts}
                  {player.pass_success_rate && (
                    <span className="text-xs text-gray-400 ml-1">
                      ({parseFloat(player.pass_success_rate.toString()).toFixed(0)}%)
                    </span>
                  )}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlayerStatsTable;
