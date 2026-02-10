import React from 'react';
import type { PlayStyle } from '../../types/match';

interface PlayStyleCardProps {
  playStyle: PlayStyle;
}

const PlayStyleCard: React.FC<PlayStyleCardProps> = ({ playStyle }) => {
  // Icon mapping
  const getStyleIcon = (style: string) => {
    if (style.includes('땅볼')) return '⚽';
    if (style.includes('공중볼')) return '🎯';
    return '⚖️';
  };

  const getSecondaryIcon = (style: string) => {
    if (style.includes('속공')) return '⚡';
    if (style.includes('빌드업')) return '🏗️';
    return '🔄';
  };

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">🎨</span>
        패스 스타일 분석
      </h3>

      {/* Primary Style */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-4xl">{getStyleIcon(playStyle.primary_style)}</span>
          <div>
            <div className="text-2xl font-bold text-white">{playStyle.primary_style}</div>
            <div className="text-sm text-gray-400">{playStyle.description}</div>
          </div>
        </div>

        {/* Ground vs Aerial Ratio */}
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">땅볼 패스 비율</span>
              <span className="text-chart-green font-bold">{playStyle.ground_ratio}%</span>
            </div>
            <div className="w-full bg-dark-bg rounded-full h-3">
              <div
                className="bg-chart-green h-3 rounded-full transition-all"
                style={{ width: `${playStyle.ground_ratio}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">공중볼 패스 비율</span>
              <span className="text-chart-blue font-bold">{playStyle.aerial_ratio}%</span>
            </div>
            <div className="w-full bg-dark-bg rounded-full h-3">
              <div
                className="bg-chart-blue h-3 rounded-full transition-all"
                style={{ width: `${playStyle.aerial_ratio}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Secondary Style */}
      <div className="pt-4 border-t border-dark-border">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-2xl">{getSecondaryIcon(playStyle.secondary_style)}</span>
          <span className="text-lg font-bold text-white">{playStyle.secondary_style}</span>
        </div>

        {/* Pass Counts */}
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="bg-dark-bg p-3 rounded">
            <div className="text-xs text-gray-400 mb-1">땅볼 패스</div>
            <div className="text-lg font-bold text-chart-green">{playStyle.ground_passes}</div>
          </div>
          <div className="bg-dark-bg p-3 rounded">
            <div className="text-xs text-gray-400 mb-1">공중볼 패스</div>
            <div className="text-lg font-bold text-chart-blue">{playStyle.aerial_passes}</div>
          </div>
          <div className="bg-dark-bg p-3 rounded">
            <div className="text-xs text-gray-400 mb-1">관통 패스</div>
            <div className="text-lg font-bold text-chart-yellow">{playStyle.penetrative_passes}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayStyleCard;
