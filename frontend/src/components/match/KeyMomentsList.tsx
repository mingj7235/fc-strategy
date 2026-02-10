import React from 'react';
import type { KeyMoment } from './TimelineChart';

interface KeyMomentsListProps {
  moments: KeyMoment[];
}

const KeyMomentsList: React.FC<KeyMomentsListProps> = ({ moments }) => {
  if (!moments || moments.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>주요 순간이 기록되지 않았습니다.</p>
      </div>
    );
  }

  const getMomentIcon = (type: string) => {
    if (type === 'goal') {
      return '⚽';
    }
    return '⭐';
  };

  const getMomentLabel = (type: string) => {
    if (type === 'goal') {
      return '골';
    }
    return '빅 찬스';
  };

  const getMomentClass = (type: string) => {
    if (type === 'goal') {
      return 'bg-green-100 text-green-800 border-green-300';
    }
    return 'bg-orange-100 text-orange-800 border-orange-300';
  };

  return (
    <div className="space-y-3">
      {moments.map((moment, index) => (
        <div
          key={index}
          className="flex items-center gap-4 bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
        >
          {/* Time Badge */}
          <div className="flex-shrink-0">
            <div className="bg-blue-600 text-white rounded-lg px-3 py-2 text-center min-w-[60px]">
              <div className="text-xs font-medium">경기</div>
              <div className="text-lg font-bold">{moment.minute}'</div>
            </div>
          </div>

          {/* Moment Type */}
          <div className="flex-shrink-0">
            <span
              className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold border-2 ${getMomentClass(
                moment.type
              )}`}
            >
              <span className="text-lg">{getMomentIcon(moment.type)}</span>
              {getMomentLabel(moment.type)}
            </span>
          </div>

          {/* xG Value */}
          <div className="flex-1">
            <div className="text-sm text-gray-500">기대 득점</div>
            <div className="text-lg font-bold text-gray-900">xG: {moment.xg.toFixed(2)}</div>
          </div>

          {/* Position Info */}
          <div className="flex-shrink-0 text-right">
            <div className="text-xs text-gray-500">위치</div>
            <div className="text-sm font-medium text-gray-700">
              ({moment.x.toFixed(2)}, {moment.y.toFixed(2)})
            </div>
          </div>
        </div>
      ))}

      {/* Summary */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-green-600">
              {moments.filter((m) => m.type === 'goal').length}
            </div>
            <div className="text-sm text-gray-600">골</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-orange-600">
              {moments.filter((m) => m.type === 'big_chance').length}
            </div>
            <div className="text-sm text-gray-600">빅 찬스</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KeyMomentsList;
