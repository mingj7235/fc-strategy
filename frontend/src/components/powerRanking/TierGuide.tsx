import React, { useState, useEffect } from 'react';
import { getTierInfo } from '../../services/api';
import type { TierInfo } from '../../types/powerRanking';

const TierGuide: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [tiers, setTiers] = useState<TierInfo[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && tiers.length === 0) {
      fetchTierInfo();
    }
  }, [isOpen]);

  const fetchTierInfo = async () => {
    setLoading(true);
    try {
      const data = await getTierInfo();
      setTiers(data.tiers);
    } catch (error) {
      console.error('Failed to fetch tier info:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTierColorClass = (color: string) => {
    const colorMap: { [key: string]: string } = {
      rainbow: 'from-purple-500 via-pink-500 to-yellow-500',
      gold: 'from-yellow-500 to-orange-500',
      purple: 'from-purple-500 to-indigo-500',
      blue: 'from-blue-500 to-cyan-500',
      green: 'from-green-500 to-emerald-500',
      yellow: 'from-yellow-600 to-amber-600',
      gray: 'from-gray-500 to-gray-600'
    };
    return colorMap[color] || 'from-gray-500 to-gray-600';
  };

  return (
    <div className="mb-8">
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between bg-dark-card border border-dark-border rounded-lg p-4 hover:border-accent-primary/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">📊</span>
          <div className="text-left">
            <h3 className="text-lg font-bold text-white">등급 체계 가이드</h3>
            <p className="text-sm text-gray-400">
              파워 랭킹 티어 시스템 자세히 보기
            </p>
          </div>
        </div>
        <div className="text-white text-xl">
          {isOpen ? '▲' : '▼'}
        </div>
      </button>

      {/* Tier Guide Content */}
      {isOpen && (
        <div className="mt-4 bg-dark-card border border-dark-border rounded-lg p-6">
          {loading ? (
            <div className="text-center text-gray-400">로딩 중...</div>
          ) : (
            <div className="space-y-6">
              {tiers.map((tier) => (
                <div
                  key={tier.tier}
                  className="bg-dark-hover border border-dark-border rounded-lg p-5"
                >
                  {/* Tier Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div
                        className={`px-6 py-3 rounded-lg bg-gradient-to-r ${getTierColorClass(tier.color)} text-white font-bold text-2xl shadow-lg`}
                      >
                        {tier.tier}
                      </div>
                      <div>
                        <div className="text-xl font-bold text-white">{tier.name}</div>
                        <div className="text-sm text-gray-400">
                          파워 스코어: {tier.score_range}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-gray-300 mb-3">{tier.description}</p>

                  {/* Characteristics */}
                  <div>
                    <div className="text-sm font-semibold text-accent-primary mb-2">
                      특징:
                    </div>
                    <ul className="space-y-1">
                      {tier.characteristics.map((char, idx) => (
                        <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                          <span className="text-accent-primary mt-1">•</span>
                          <span>{char}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}

              {/* Additional Info */}
              <div className="bg-gradient-to-br from-accent-primary/10 to-accent-secondary/10 border border-accent-primary/30 rounded-lg p-4 mt-6">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">💡</span>
                  <div>
                    <h4 className="text-white font-bold mb-2">평가 기준</h4>
                    <p className="text-sm text-gray-300 leading-relaxed">
                      파워 스코어는 <strong>폼 지수(30%)</strong>, <strong>효율성(25%)</strong>,
                      <strong>일관성(20%)</strong>, <strong>영향력(25%)</strong>을 종합하여 산출됩니다.
                      각 지표는 최근 경기 데이터를 기반으로 계산되며, 경기 수가 많을수록 더 정확한 평가가 가능합니다.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TierGuide;
