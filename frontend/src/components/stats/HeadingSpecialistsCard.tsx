import React from 'react';
import type { HeadingSpecialists } from '../../types/match';

interface HeadingSpecialistsCardProps {
  specialists: HeadingSpecialists;
}

const HeadingSpecialistsCard: React.FC<HeadingSpecialistsCardProps> = ({ specialists }) => {
  const getGrade = (rate: number) => {
    if (rate >= 40) return { grade: 'S', color: 'text-chart-green' };
    if (rate >= 30) return { grade: 'A', color: 'text-chart-blue' };
    if (rate >= 20) return { grade: 'B', color: 'text-chart-yellow' };
    if (rate >= 10) return { grade: 'C', color: 'text-chart-red' };
    return { grade: 'D', color: 'text-gray-400' };
  };

  const successGrade = getGrade(specialists.heading_success_rate);
  const conversionGrade = getGrade(specialists.heading_conversion_rate);

  const getHeadingStyle = () => {
    if (specialists.cross_dependency >= 70) {
      return {
        style: '크로스 의존형',
        icon: '📐',
        description: '측면 크로스에 크게 의존하는 공중볼 플레이',
        color: 'text-chart-blue'
      };
    } else if (specialists.cross_dependency >= 40) {
      return {
        style: '혼합형',
        icon: '🔄',
        description: '크로스와 중앙 플레이를 적절히 혼합',
        color: 'text-chart-purple'
      };
    } else {
      return {
        style: '중앙 돌파형',
        icon: '⚡',
        description: '중앙 침투를 통한 헤딩 기회 창출',
        color: 'text-chart-green'
      };
    }
  };

  const headingStyle = getHeadingStyle();

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">🎯</span>
        헤딩 전문 통계
      </h3>

      {specialists.total_headers === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <p>헤딩 슈팅 데이터가 없습니다.</p>
        </div>
      ) : (
        <>
          {/* Heading Style Badge */}
          <div className="mb-6 p-4 bg-dark-bg rounded-lg border-l-4 border-accent-primary">
            <div className="flex items-start gap-3">
              <span className="text-3xl">{headingStyle.icon}</span>
              <div>
                <div className={`text-lg font-bold ${headingStyle.color}`}>
                  {headingStyle.style}
                </div>
                <div className="text-sm text-gray-300 mt-1">
                  {headingStyle.description}
                </div>
              </div>
            </div>
          </div>

          {/* Main Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-dark-bg p-4 rounded-lg text-center">
              <div className="text-xs text-gray-400 mb-1">총 헤딩</div>
              <div className="text-2xl font-bold text-white">{specialists.total_headers}</div>
            </div>
            <div className="bg-dark-bg p-4 rounded-lg text-center">
              <div className="text-xs text-gray-400 mb-1">헤딩 골</div>
              <div className="text-2xl font-bold text-chart-green">{specialists.heading_goals}</div>
            </div>
            <div className="bg-dark-bg p-4 rounded-lg text-center">
              <div className="text-xs text-gray-400 mb-1">성공률</div>
              <div className={`text-lg font-bold ${successGrade.color}`}>
                {specialists.heading_success_rate.toFixed(1)}%
              </div>
              <div className={`text-xs ${successGrade.color}`}>{successGrade.grade}</div>
            </div>
            <div className="bg-dark-bg p-4 rounded-lg text-center">
              <div className="text-xs text-gray-400 mb-1">전환율</div>
              <div className={`text-lg font-bold ${conversionGrade.color}`}>
                {specialists.heading_conversion_rate.toFixed(1)}%
              </div>
              <div className={`text-xs ${conversionGrade.color}`}>{conversionGrade.grade}</div>
            </div>
          </div>

          {/* Success Rate Bar */}
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>유효 슈팅 성공률</span>
              <span>{specialists.heading_success_rate.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-dark-card rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  specialists.heading_success_rate >= 40
                    ? 'bg-gradient-to-r from-chart-green to-chart-blue'
                    : specialists.heading_success_rate >= 20
                    ? 'bg-gradient-to-r from-chart-blue to-chart-purple'
                    : 'bg-gradient-to-r from-chart-yellow to-chart-red'
                }`}
                style={{ width: `${Math.min(specialists.heading_success_rate * 2, 100)}%` }}
              />
            </div>
          </div>

          {/* Conversion Rate Bar */}
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>골 전환율</span>
              <span>{specialists.heading_conversion_rate.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-dark-card rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  specialists.heading_conversion_rate >= 30
                    ? 'bg-gradient-to-r from-chart-green to-chart-blue'
                    : specialists.heading_conversion_rate >= 15
                    ? 'bg-gradient-to-r from-chart-blue to-chart-purple'
                    : 'bg-gradient-to-r from-chart-yellow to-chart-red'
                }`}
                style={{ width: `${Math.min(specialists.heading_conversion_rate * 3, 100)}%` }}
              />
            </div>
          </div>

          {/* Cross Dependency */}
          <div className="bg-dark-bg p-4 rounded-lg mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-400">크로스 의존도</span>
              <span className="text-xl font-bold text-white">
                {specialists.cross_dependency.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-dark-card rounded-full h-2">
              <div
                className="h-2 rounded-full bg-gradient-to-r from-chart-blue to-chart-purple"
                style={{ width: `${specialists.cross_dependency}%` }}
              />
            </div>
            <div className="text-xs text-gray-400 mt-2">
              헤딩 중 크로스/어시스트로 연결된 비율
            </div>
          </div>

          {/* Insights */}
          <div className="space-y-2">
            {specialists.heading_conversion_rate >= 25 && (
              <div className="p-3 bg-chart-green/10 border border-chart-green/30 rounded-lg">
                <p className="text-sm text-chart-green">
                  ⚽ 헤딩 골 전환율이 매우 우수합니다! 공중볼 전술을 적극 활용하세요.
                </p>
              </div>
            )}

            {specialists.cross_dependency >= 70 && (
              <div className="p-3 bg-chart-blue/10 border border-chart-blue/30 rounded-lg">
                <p className="text-sm text-chart-blue">
                  📐 크로스 의존도가 높습니다. 측면 공격수의 크로스 능력이 중요합니다.
                </p>
              </div>
            )}

            {specialists.heading_success_rate >= 40 && (
              <div className="p-3 bg-chart-purple/10 border border-chart-purple/30 rounded-lg">
                <p className="text-sm text-chart-purple">
                  💪 헤딩 정확도가 뛰어납니다. 키가 크고 헤딩 능력이 좋은 선수를 적극 활용하세요.
                </p>
              </div>
            )}

            {specialists.heading_conversion_rate < 15 && specialists.total_headers >= 5 && (
              <div className="p-3 bg-chart-yellow/10 border border-chart-yellow/30 rounded-lg">
                <p className="text-sm text-chart-yellow">
                  ⚠️ 헤딩 전환율이 낮습니다. 골대 반대편으로 방향을 틀거나, 더 좋은 위치에서 헤딩을 시도하세요.
                </p>
              </div>
            )}

            {specialists.cross_dependency < 30 && specialists.total_headers >= 5 && (
              <div className="p-3 bg-chart-green/10 border border-chart-green/30 rounded-lg">
                <p className="text-sm text-chart-green">
                  ⚡ 중앙 침투를 통한 헤딩이 많습니다. 수비 뒷공간을 적극 공략하고 있습니다.
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default HeadingSpecialistsCard;
