import React from 'react';
import type { PlayerPerformance } from '../../types/match';
import PlayerAvatar from '../common/PlayerAvatar';

interface PlayerCardProps {
  player: PlayerPerformance;
  rank?: number; // 1, 2, 3 for top performers
}

const PlayerCard: React.FC<PlayerCardProps> = ({ player, rank }) => {

  const getRatingColorClass = (rating: number | string) => {
    const ratingNum = typeof rating === 'string' ? parseFloat(rating) : rating;
    if (ratingNum >= 8.0) return 'text-chart-green bg-chart-green/20 border-chart-green';
    if (ratingNum >= 7.0) return 'text-chart-yellow bg-chart-yellow/20 border-chart-yellow';
    return 'text-chart-red bg-chart-red/20 border-chart-red';
  };

  const getRankBadge = (rank: number) => {
    const badges = [
      { color: 'bg-gradient-to-br from-chart-yellow to-amber-500 text-gray-900', label: '1st', emoji: '🥇' },
      { color: 'bg-gradient-to-br from-gray-300 to-gray-400 text-gray-900', label: '2nd', emoji: '🥈' },
      { color: 'bg-gradient-to-br from-orange-400 to-amber-600 text-white', label: '3rd', emoji: '🥉' }
    ];

    const badge = badges[rank - 1];
    if (!badge) return null;

    return (
      <div className={`absolute -top-2 -right-2 ${badge.color} rounded-full w-10 h-10 flex items-center justify-center text-lg font-bold shadow-dark-lg border-2 border-dark-bg`}>
        {badge.emoji}
      </div>
    );
  };

  return (
    <div className="relative bg-gradient-to-br from-dark-card to-dark-hover border border-dark-border rounded-lg p-4 hover:shadow-dark-lg hover:border-accent-primary/50 transition-all duration-200 transform hover:scale-[1.02]">
      {rank && getRankBadge(rank)}

      {/* Player Image and Rating */}
      <div className="flex flex-col items-center mb-3">
        <div className="w-20 h-20 mb-2 relative">
          <PlayerAvatar
            spid={player.spid}
            imageUrl={player.image_url}
            playerName={player.player_name}
            size={80}
            className="drop-shadow-lg"
          />
        </div>

        <h3 className="font-semibold text-white text-center text-sm truncate max-w-full">
          {player.player_name}
        </h3>

        {(player.season_img || player.season_name) && (
          <div className="mt-1" title={player.season_name}>
            {player.season_img ? (
              <img src={player.season_img} alt={player.season_name} className="h-4 object-contain" />
            ) : (
              <p className="text-xs text-gray-400">{player.season_name}</p>
            )}
          </div>
        )}

        <div className={`mt-2 px-3 py-1 rounded-full font-bold text-lg border ${getRatingColorClass(player.rating)}`}>
          {typeof player.rating === 'string' ? parseFloat(player.rating).toFixed(1) : player.rating.toFixed(1)}
        </div>
      </div>

      {/* Goals and Assists */}
      {(player.goals > 0 || player.assists > 0) && (
        <div className="flex justify-center gap-3 mb-3 text-sm">
          {player.goals > 0 && (
            <div className="flex items-center gap-1 bg-chart-green/20 px-2 py-1 rounded border border-chart-green/30">
              <span className="text-chart-green">⚽</span>
              <span className="font-semibold text-white">{player.goals}</span>
            </div>
          )}
          {player.assists > 0 && (
            <div className="flex items-center gap-1 bg-chart-blue/20 px-2 py-1 rounded border border-chart-blue/30">
              <span className="text-chart-blue">🎯</span>
              <span className="font-semibold text-white">{player.assists}</span>
            </div>
          )}
        </div>
      )}

      {/* Key Stats */}
      <div className="space-y-2 text-xs">
        {player.shots > 0 && player.shot_accuracy != null && (
          <div>
            <div className="flex justify-between text-gray-400 mb-1">
              <span>슈팅 정확도</span>
              <span className="font-medium text-white">{parseFloat(player.shot_accuracy.toString()).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-dark-bg rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-chart-blue to-chart-cyan h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(parseFloat(player.shot_accuracy.toString()), 100)}%` }}
              />
            </div>
          </div>
        )}

        {player.pass_attempts > 0 && player.pass_success_rate != null && (
          <div>
            <div className="flex justify-between text-gray-400 mb-1">
              <span>패스 성공률</span>
              <span className="font-medium text-white">{parseFloat(player.pass_success_rate.toString()).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-dark-bg rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-chart-green to-emerald-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(parseFloat(player.pass_success_rate.toString()), 100)}%` }}
              />
            </div>
          </div>
        )}

        {player.dribble_attempts > 0 && player.dribble_success_rate != null && (
          <div>
            <div className="flex justify-between text-gray-400 mb-1">
              <span>드리블 성공률</span>
              <span className="font-medium text-white">{parseFloat(player.dribble_success_rate.toString()).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-dark-bg rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-chart-purple to-violet-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(parseFloat(player.dribble_success_rate.toString()), 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerCard;
