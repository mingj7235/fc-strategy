import React from 'react';
import type { Match } from '../../types/match';

interface MatchCardProps {
  match: Match;
  onClick: () => void;
}

const MatchCard: React.FC<MatchCardProps> = ({ match, onClick }) => {
  const getResultBadgeClass = (result: string) => {
    switch (result) {
      case 'win':
        return 'bg-accent-success/20 text-accent-success border border-accent-success/50';
      case 'lose':
        return 'bg-accent-danger/20 text-accent-danger border border-accent-danger/50';
      case 'draw':
        return 'bg-gray-500/20 text-gray-300 border border-gray-500/50';
      default:
        return 'bg-gray-500/20 text-gray-300 border border-gray-500/50';
    }
  };

  const getResultText = (result: string) => {
    switch (result) {
      case 'win':
        return '승';
      case 'lose':
        return '패';
      case 'draw':
        return '무';
      default:
        return '-';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${month}/${day} ${hours}:${minutes}`;
  };

  return (
    <div
      onClick={onClick}
      className="bg-dark-card border border-dark-border rounded-lg p-4 cursor-pointer hover:bg-dark-hover hover:border-accent-primary/50 hover:shadow-dark transition-all duration-200 transform hover:scale-[1.02]"
    >
      {/* Result and Date Row */}
      <div className="flex items-center justify-between mb-3">
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getResultBadgeClass(
            match.result
          )}`}
        >
          {getResultText(match.result)}
        </span>
        <span className="text-xs text-gray-400">{formatDate(match.match_date)}</span>
      </div>

      {/* Opponent Nickname */}
      {match.opponent_nickname && (
        <div className="text-sm text-gray-300 text-center mb-2">
          vs {match.opponent_nickname}
        </div>
      )}

      {/* Score Row */}
      <div className="flex items-center justify-center mb-3">
        <span className="text-2xl font-bold text-white">{match.goals_for}</span>
        <span className="mx-3 text-gray-500">-</span>
        <span className="text-2xl font-bold text-white">{match.goals_against}</span>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="text-center">
          <div className="text-gray-400 text-xs">점유율</div>
          <div className="font-medium text-gray-100">{match.possession}%</div>
        </div>
        <div className="text-center">
          <div className="text-gray-400 text-xs">슈팅</div>
          <div className="font-medium text-gray-100">
            {match.shots_on_target ?? 0}/{match.shots ?? 0}
          </div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(MatchCard);
