import React from 'react';

interface FieldCanvasProps {
  width: number;
  height: number;
  children?: React.ReactNode;
}

/**
 * Soccer field SVG component with FIFA standard proportions (105m x 68m)
 * Coordinate system: 0-1 normalized (x: left to right, y: top to bottom)
 *
 * Field zones:
 * - Attacking third: x > 0.67 (right side)
 * - Middle third: 0.33 < x < 0.67
 * - Defensive third: x < 0.33 (left side)
 */
const FieldCanvas: React.FC<FieldCanvasProps> = ({ width, height, children }) => {
  // FIFA proportions: 105m x 68m = 1.544:1 aspect ratio
  const viewBoxWidth = 105;
  const viewBoxHeight = 68;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
      className="border border-gray-300 bg-green-50"
    >
      {/* Field background */}
      <rect x="0" y="0" width={viewBoxWidth} height={viewBoxHeight} fill="#2d5016" />

      {/* Grass pattern (stripes) */}
      {[...Array(7)].map((_, i) => (
        <rect
          key={`stripe-${i}`}
          x={i * 15}
          y="0"
          width="15"
          height={viewBoxHeight}
          fill={i % 2 === 0 ? '#2d5016' : '#32591a'}
          opacity="0.3"
        />
      ))}

      {/* Outer boundary */}
      <rect
        x="0.5"
        y="0.5"
        width={viewBoxWidth - 1}
        height={viewBoxHeight - 1}
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Center line */}
      <line
        x1={viewBoxWidth / 2}
        y1="0"
        x2={viewBoxWidth / 2}
        y2={viewBoxHeight}
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Center circle */}
      <circle
        cx={viewBoxWidth / 2}
        cy={viewBoxHeight / 2}
        r="9.15"
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Center spot */}
      <circle
        cx={viewBoxWidth / 2}
        cy={viewBoxHeight / 2}
        r="0.3"
        fill="white"
      />

      {/* Left penalty area */}
      <rect
        x="0"
        y={(viewBoxHeight - 40.32) / 2}
        width="16.5"
        height="40.32"
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Left goal area */}
      <rect
        x="0"
        y={(viewBoxHeight - 18.32) / 2}
        width="5.5"
        height="18.32"
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Left penalty spot */}
      <circle
        cx="11"
        cy={viewBoxHeight / 2}
        r="0.3"
        fill="white"
      />

      {/* Left penalty arc */}
      <path
        d={`M 16.5 ${viewBoxHeight / 2 - 9.15} A 9.15 9.15 0 0 1 16.5 ${viewBoxHeight / 2 + 9.15}`}
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Right penalty area */}
      <rect
        x={viewBoxWidth - 16.5}
        y={(viewBoxHeight - 40.32) / 2}
        width="16.5"
        height="40.32"
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Right goal area */}
      <rect
        x={viewBoxWidth - 5.5}
        y={(viewBoxHeight - 18.32) / 2}
        width="5.5"
        height="18.32"
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Right penalty spot */}
      <circle
        cx={viewBoxWidth - 11}
        cy={viewBoxHeight / 2}
        r="0.3"
        fill="white"
      />

      {/* Right penalty arc */}
      <path
        d={`M ${viewBoxWidth - 16.5} ${viewBoxHeight / 2 - 9.15} A 9.15 9.15 0 0 0 ${viewBoxWidth - 16.5} ${viewBoxHeight / 2 + 9.15}`}
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Corner arcs */}
      <path d="M 0 1 A 1 1 0 0 0 1 0" fill="none" stroke="white" strokeWidth="0.3" />
      <path d={`M 0 ${viewBoxHeight - 1} A 1 1 0 0 1 1 ${viewBoxHeight}`} fill="none" stroke="white" strokeWidth="0.3" />
      <path d={`M ${viewBoxWidth} 1 A 1 1 0 0 1 ${viewBoxWidth - 1} 0`} fill="none" stroke="white" strokeWidth="0.3" />
      <path d={`M ${viewBoxWidth} ${viewBoxHeight - 1} A 1 1 0 0 0 ${viewBoxWidth - 1} ${viewBoxHeight}`} fill="none" stroke="white" strokeWidth="0.3" />

      {/* Goals */}
      <rect
        x="-1"
        y={(viewBoxHeight - 7.32) / 2}
        width="1"
        height="7.32"
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />
      <rect
        x={viewBoxWidth}
        y={(viewBoxHeight - 7.32) / 2}
        width="1"
        height="7.32"
        fill="none"
        stroke="white"
        strokeWidth="0.3"
      />

      {/* Children (shot markers, heatmap, etc.) */}
      {children}
    </svg>
  );
};

export default FieldCanvas;
