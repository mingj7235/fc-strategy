import React from 'react';
import type { AssistHeatmapPoint } from '../../types/match';

interface AssistHeatmapProps {
  heatmapData: AssistHeatmapPoint[];
  width?: number;
  height?: number;
}

const AssistHeatmap: React.FC<AssistHeatmapProps> = ({
  heatmapData,
  width = 800,
  height = 520
}) => {
  // Convert normalized coordinates (0-1) to SVG coordinates
  const toSVGCoords = (x: number, y: number) => {
    return {
      x: x * width,
      y: y * height,
    };
  };

  // Group points by location for better visualization
  const renderAssistPoints = () => {
    return heatmapData.map((point, index) => {
      const coords = toSVGCoords(point.x, point.y);

      return (
        <g key={index}>
          {/* Assist origin marker (larger circle) */}
          <circle
            cx={coords.x}
            cy={coords.y}
            r={10}
            fill="rgba(255, 193, 7, 0.6)"
            stroke="#ffc107"
            strokeWidth={2}
            className="transition-all hover:r-12"
          />
          {/* Inner dot */}
          <circle
            cx={coords.x}
            cy={coords.y}
            r={4}
            fill="#ffc107"
          />
        </g>
      );
    });
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto">
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${width} ${height}`}
        className="bg-green-900 rounded-lg shadow-lg"
      >
        {/* Soccer field background */}
        <defs>
          <pattern id="grass" width="20" height="20" patternUnits="userSpaceOnUse">
            <rect width="20" height="20" fill="#1a5f3a" />
            <rect width="20" height="10" fill="#1e7045" />
          </pattern>
        </defs>

        {/* Field base */}
        <rect width={width} height={height} fill="url(#grass)" />

        {/* Field lines */}
        <g stroke="#ffffff" strokeWidth="2" fill="none" opacity="0.5">
          {/* Border */}
          <rect x="40" y="40" width={width - 80} height={height - 80} />

          {/* Center line */}
          <line x1={width / 2} y1="40" x2={width / 2} y2={height - 40} />

          {/* Center circle */}
          <circle cx={width / 2} cy={height / 2} r="60" />

          {/* Penalty boxes */}
          <rect x="40" y={(height - 200) / 2} width="120" height="200" />
          <rect x={width - 160} y={(height - 200) / 2} width="120" height="200" />

          {/* Goal boxes */}
          <rect x="40" y={(height - 120) / 2} width="60" height="120" />
          <rect x={width - 100} y={(height - 120) / 2} width="60" height="120" />
        </g>

        {/* Assist points */}
        {renderAssistPoints()}
      </svg>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-500 rounded-full border-2 border-yellow-400"></div>
          <span className="text-gray-300">어시스트 발생 위치</span>
        </div>
        <div className="text-gray-400">
          총 {heatmapData.length}개 어시스트
        </div>
      </div>
    </div>
  );
};

export default AssistHeatmap;
