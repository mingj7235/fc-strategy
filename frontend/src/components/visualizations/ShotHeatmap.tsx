import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
import FieldCanvas from './FieldCanvas';

interface ShotPoint {
  x: number;
  y: number;
  result: 'goal' | 'on_target' | 'off_target' | 'blocked';
  shot_type?: number;
}

interface ShotHeatmapProps {
  heatmapData: ShotPoint[];
  width?: number;
  height?: number;
}

/**
 * Interactive shot heatmap using D3.js
 * Displays shot locations on a soccer field with color-coded results
 */
const ShotHeatmap: React.FC<ShotHeatmapProps> = ({
  heatmapData,
  width = 800,
  height = 520,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Color mapping for shot results
  const getColor = (result: string): string => {
    switch (result) {
      case 'goal':
        return '#22c55e'; // green-500
      case 'on_target':
        return '#eab308'; // yellow-500
      case 'off_target':
        return '#9ca3af'; // gray-400
      case 'blocked':
        return '#ef4444'; // red-500
      default:
        return '#6b7280'; // gray-500
    }
  };

  // Size based on result importance
  const getSize = (result: string): number => {
    switch (result) {
      case 'goal':
        return 8;
      case 'on_target':
        return 6;
      case 'off_target':
        return 4;
      case 'blocked':
        return 5;
      default:
        return 4;
    }
  };

  // Korean text for result
  const getResultText = (result: string): string => {
    switch (result) {
      case 'goal':
        return '골';
      case 'on_target':
        return '유효슈팅';
      case 'off_target':
        return '빗나감';
      case 'blocked':
        return '막힘';
      default:
        return '알 수 없음';
    }
  };

  useEffect(() => {
    if (!svgRef.current || !heatmapData.length) return;

    const svg = d3.select(svgRef.current);
    const tooltip = d3.select(tooltipRef.current);

    // Clear previous markers
    svg.selectAll('.shot-marker').remove();

    // Field dimensions (FIFA proportions)
    const viewBoxWidth = 105;
    const viewBoxHeight = 68;

    // Create shot markers
    const markers = svg
      .selectAll('.shot-marker')
      .data(heatmapData)
      .enter()
      .append('circle')
      .attr('class', 'shot-marker')
      .attr('cx', (d) => d.x * viewBoxWidth)
      .attr('cy', (d) => d.y * viewBoxHeight)
      .attr('r', (d) => getSize(d.result))
      .attr('fill', (d) => getColor(d.result))
      .attr('stroke', 'white')
      .attr('stroke-width', 0.5)
      .attr('opacity', 0.8)
      .style('cursor', 'pointer');

    // Add hover interactions
    markers
      .on('mouseover', function (event, d) {
        // Enlarge marker
        d3.select(this)
          .transition()
          .duration(150)
          .attr('r', getSize(d.result) * 1.5)
          .attr('opacity', 1);

        // Show tooltip
        tooltip
          .style('display', 'block')
          .html(
            `
            <div class="bg-gray-900 text-white text-xs rounded px-3 py-2 shadow-lg">
              <div class="font-semibold">${getResultText(d.result)}</div>
              <div class="text-gray-300 mt-1">
                위치: (${(d.x * 100).toFixed(1)}%, ${(d.y * 100).toFixed(1)}%)
              </div>
            </div>
            `
          )
          .style('left', event.pageX + 10 + 'px')
          .style('top', event.pageY - 10 + 'px');
      })
      .on('mouseout', function (_event, d) {
        // Reset marker
        d3.select(this)
          .transition()
          .duration(150)
          .attr('r', getSize(d.result))
          .attr('opacity', 0.8);

        // Hide tooltip
        tooltip.style('display', 'none');
      });

    // Add entrance animation
    markers
      .attr('r', 0)
      .transition()
      .duration(500)
      .delay((_d, i) => i * 10)
      .attr('r', (d) => getSize(d.result));
  }, [heatmapData]);

  return (
    <div className="relative">
      <FieldCanvas width={width} height={height}>
        <g ref={svgRef} />
      </FieldCanvas>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 justify-center text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-green-500"></div>
          <span>골 ({heatmapData.filter((d) => d.result === 'goal').length})</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
          <span>유효슈팅 ({heatmapData.filter((d) => d.result === 'on_target').length})</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-gray-400"></div>
          <span>빗나감 ({heatmapData.filter((d) => d.result === 'off_target').length})</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-red-500"></div>
          <span>막힘 ({heatmapData.filter((d) => d.result === 'blocked').length})</span>
        </div>
      </div>

      {/* Tooltip container */}
      <div
        ref={tooltipRef}
        style={{
          position: 'absolute',
          display: 'none',
          pointerEvents: 'none',
          zIndex: 1000,
        }}
      />
    </div>
  );
};

export default ShotHeatmap;
