import React from 'react';
import type { AerialEfficiency } from '../../types/match';

interface AerialEfficiencyCardProps {
  efficiency: AerialEfficiency;
}

const AerialEfficiencyCard: React.FC<AerialEfficiencyCardProps> = ({ efficiency }) => {
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'S':
        return 'text-chart-green';
      case 'A':
        return 'text-chart-blue';
      case 'B':
        return 'text-chart-yellow';
      case 'C':
        return 'text-chart-red';
      default:
        return 'text-gray-400';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'from-chart-green to-chart-blue';
    if (score >= 60) return 'from-chart-blue to-chart-purple';
    if (score >= 40) return 'from-chart-yellow to-chart-green';
    if (score >= 20) return 'from-chart-red to-chart-yellow';
    return 'from-gray-600 to-gray-500';
  };

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">🏆</span>
        공중볼 전술 효율성
      </h3>

      <div className="text-center mb-6">
        <div className="inline-block">
          <div className={`text-7xl font-bold ${getGradeColor(efficiency.grade)} mb-2`}>
            {efficiency.grade}
          </div>
          <div className="text-lg text-gray-300">{efficiency.grade_text}</div>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>효율성 점수</span>
          <span>{efficiency.score} / 100</span>
        </div>
        <div className="w-full bg-dark-bg rounded-full h-6 overflow-hidden">
          <div
            className={`h-6 bg-gradient-to-r ${getScoreColor(efficiency.score)} transition-all flex items-center justify-center text-white text-sm font-bold`}
            style={{ width: `${efficiency.score}%` }}
          >
            {efficiency.score >= 20 && `${efficiency.score}점`}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-2">평가 기준</div>
          <div className="space-y-1 text-xs text-gray-300">
            <div>• 헤딩 골 전환율</div>
            <div>• 유효슈팅 성공률</div>
            <div>• 크로스 활용도</div>
            <div>• 박스 침투율</div>
          </div>
        </div>
        <div className="bg-dark-bg p-4 rounded-lg text-center">
          <div className="text-xs text-gray-400 mb-2">등급 기준</div>
          <div className="space-y-1 text-xs">
            <div className="text-chart-green">S: 80점 이상</div>
            <div className="text-chart-blue">A: 60-79점</div>
            <div className="text-chart-yellow">B: 40-59점</div>
            <div className="text-chart-red">C: 20-39점</div>
          </div>
        </div>
      </div>

      {efficiency.score >= 70 && (
        <div className="mt-6 p-4 bg-accent-success/10 border border-accent-success/30 rounded-lg">
          <p className="text-sm text-accent-success">
            ✨ 공중볼 전술이 매우 효과적입니다! 이 전략을 계속 활용하세요.
          </p>
        </div>
      )}

      {efficiency.score < 40 && efficiency.score > 0 && (
        <div className="mt-6 p-4 bg-chart-yellow/10 border border-chart-yellow/30 rounded-lg">
          <p className="text-sm text-chart-yellow">
            💡 헤딩 전술 개선이 필요합니다. 크로스 타이밍과 선수 위치 선정에 집중하세요.
          </p>
        </div>
      )}
    </div>
  );
};

export default AerialEfficiencyCard;
