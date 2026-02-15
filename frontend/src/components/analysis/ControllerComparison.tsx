import React from 'react';
import type { ControllerPerformance } from '../../types/match';

interface ControllerComparisonProps {
  keyboard?: ControllerPerformance;
  gamepad?: ControllerPerformance;
}

const ControllerComparison: React.FC<ControllerComparisonProps> = ({ keyboard, gamepad }) => {
  if (!keyboard && !gamepad) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p>컨트롤러 데이터가 없습니다.</p>
      </div>
    );
  }

  const getWinRateColor = (winRate: number) => {
    if (winRate >= 60) return 'text-chart-green';
    if (winRate >= 40) return 'text-chart-yellow';
    return 'text-chart-red';
  };

  const renderControllerCard = (controller: ControllerPerformance, name: string, icon: string) => (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-chart-blue/50 transition-colors">
      <div className="text-center mb-4">
        <div className="text-4xl mb-2">{icon}</div>
        <div className="text-xl font-bold text-white">{name}</div>
        <div className="text-sm text-gray-400">{controller.matches}경기</div>
      </div>

      {/* Win Rate */}
      <div className="mb-4">
        <div className={`text-4xl font-bold ${getWinRateColor(controller.win_rate)} text-center`}>
          {controller.win_rate}%
        </div>
        <div className="text-sm text-gray-400 text-center">승률</div>
      </div>

      {/* W-D-L */}
      <div className="grid grid-cols-3 gap-2 mb-4 text-center">
        <div className="bg-dark-bg p-2 rounded">
          <div className="text-chart-green font-bold">{controller.wins}</div>
          <div className="text-xs text-gray-400">승</div>
        </div>
        <div className="bg-dark-bg p-2 rounded">
          <div className="text-gray-300 font-bold">{controller.draws}</div>
          <div className="text-xs text-gray-400">무</div>
        </div>
        <div className="bg-dark-bg p-2 rounded">
          <div className="text-chart-red font-bold">{controller.losses}</div>
          <div className="text-xs text-gray-400">패</div>
        </div>
      </div>

      {/* Goals */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">평균 득점</span>
          <span className="text-chart-green font-bold">{controller.avg_goals_for}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-400">평균 실점</span>
          <span className="text-chart-red font-bold">{controller.avg_goals_against}</span>
        </div>
        <div className="flex justify-between items-center pt-2 border-t border-dark-border">
          <span className="text-gray-400">골 득실</span>
          <span className={`font-bold ${controller.goal_difference >= 0 ? 'text-chart-green' : 'text-chart-red'}`}>
            {controller.goal_difference >= 0 ? '+' : ''}{controller.goal_difference}
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">⚔️</span>
        컨트롤러별 성적 비교
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {keyboard && renderControllerCard(keyboard, '키보드', '⌨️')}
        {gamepad && renderControllerCard(gamepad, '패드', '🎮')}
      </div>

      {/* Comparison Summary */}
      {keyboard && gamepad && (
        <div className="mt-6 p-4 bg-dark-bg rounded-lg">
          <div className="text-sm text-gray-300">
            {keyboard.win_rate > gamepad.win_rate ? (
              <span>
                ✨ 키보드 승률이 <span className="text-chart-green font-bold">{(keyboard.win_rate - gamepad.win_rate).toFixed(1)}%p</span> 더 높습니다!
              </span>
            ) : gamepad.win_rate > keyboard.win_rate ? (
              <span>
                ✨ 패드 승률이 <span className="text-chart-green font-bold">{(gamepad.win_rate - keyboard.win_rate).toFixed(1)}%p</span> 더 높습니다!
              </span>
            ) : (
              <span>⚖️ 두 컨트롤러 간 승률이 동일합니다.</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ControllerComparison;
