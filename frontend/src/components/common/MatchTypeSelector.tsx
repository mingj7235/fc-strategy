import React from 'react';

interface MatchTypeSelectorProps {
  value: number;
  onChange: (matchtype: number) => void;
}

const MatchTypeSelector: React.FC<MatchTypeSelectorProps> = ({ value, onChange }) => {
  return (
    <div className="inline-flex items-center gap-1 bg-dark-hover border border-dark-border rounded-xl p-1 shadow-lg">
      {/* Official Match Button */}
      <button
        onClick={() => onChange(50)}
        className={`relative px-6 py-3 rounded-lg font-bold text-sm transition-all duration-300 ease-out ${
          value === 50
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-xl shadow-blue-500/30 scale-105'
            : 'text-gray-400 hover:text-gray-200 hover:bg-dark-card/50'
        }`}
      >
        <span className="relative z-10 flex items-center gap-2">
          <span className="text-lg">🏆</span>
          <span>공식경기</span>
        </span>
      </button>

      {/* Manager Mode Button */}
      <button
        onClick={() => onChange(52)}
        className={`relative px-6 py-3 rounded-lg font-bold text-sm transition-all duration-300 ease-out ${
          value === 52
            ? 'bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-xl shadow-purple-500/30 scale-105'
            : 'text-gray-400 hover:text-gray-200 hover:bg-dark-card/50'
        }`}
      >
        <span className="relative z-10 flex items-center gap-2">
          <span className="text-lg">⚽</span>
          <span>감독모드</span>
        </span>
      </button>
    </div>
  );
};

export default MatchTypeSelector;
