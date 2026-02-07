import React from 'react';
import type { Insights } from '../../types/advancedAnalysis';

interface InsightsPanelProps {
  insights: Insights;
  title?: string;
}

const InsightsPanel: React.FC<InsightsPanelProps> = ({ insights, title = "전문가 분석" }) => {
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span>💡</span>
        {title}
      </h3>

      <div className="space-y-6">
        {/* Keep */}
        {insights.keep.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">✅</span>
              <h4 className="text-lg font-bold text-chart-green">Keep (유지하세요)</h4>
            </div>
            <div className="space-y-2">
              {insights.keep.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-3"
                >
                  <p className="text-gray-200">{item}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stop */}
        {insights.stop.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🛑</span>
              <h4 className="text-lg font-bold text-chart-red">Stop (중단하세요)</h4>
            </div>
            <div className="space-y-2">
              {insights.stop.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/30 rounded-lg p-3"
                >
                  <p className="text-gray-200">{item}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Items */}
        {insights.action_items.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🎯</span>
              <h4 className="text-lg font-bold text-accent-primary">Action (실천하세요)</h4>
            </div>
            <div className="space-y-2">
              {insights.action_items.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-lg p-3"
                >
                  <p className="text-gray-200">{item}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No insights */}
        {insights.keep.length === 0 && insights.stop.length === 0 && insights.action_items.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            분석할 데이터가 충분하지 않습니다.
          </div>
        )}
      </div>
    </div>
  );
};

export default InsightsPanel;
