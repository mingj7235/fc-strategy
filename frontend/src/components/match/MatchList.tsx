import React from 'react';
import type { Match } from '../../types/match';
import MatchCard from './MatchCard';
import { useNavigate } from 'react-router-dom';

interface MatchListProps {
  matches: Match[];
  userOuid: string;
}

const MatchList: React.FC<MatchListProps> = ({ matches, userOuid }) => {
  const navigate = useNavigate();

  const handleMatchClick = (matchId: string) => {
    navigate(`/match/${matchId}?ouid=${userOuid}`);
  };

  if (matches.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">경기 기록 없음</h3>
        <p className="mt-1 text-sm text-gray-500">이 매치 타입에 대한 경기 기록이 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {matches.map((match) => (
        <MatchCard
          key={match.match_id}
          match={match}
          onClick={() => handleMatchClick(match.match_id)}
        />
      ))}
    </div>
  );
};

export default MatchList;
