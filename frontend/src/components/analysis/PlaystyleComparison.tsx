import React from 'react';
import type { ControllerPlaystyle } from '../../types/match';

interface PlaystyleComparisonProps {
  keyboard?: ControllerPlaystyle;
  gamepad?: ControllerPlaystyle;
}

const PlaystyleComparison: React.FC<PlaystyleComparisonProps> = ({ keyboard, gamepad }) => {
  if (!keyboard && !gamepad) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p>플레이 스타일 데이터가 없습니다.</p>
      </div>
    );
  }

  const renderStyleCard = (style: ControllerPlaystyle, name: string, icon: string) => (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6 hover:border-chart-blue/50 transition-colors">
      <div className="text-center mb-4">
        <div className="text-3xl mb-2">{icon}</div>
        <div className="text-lg font-bold text-white">{name}</div>
      </div>

      {/* Style Tags */}
      {style.style_tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4 justify-center">
          {style.style_tags.map((tag, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-accent-primary/20 text-accent-primary rounded-full text-xs font-semibold"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">평균 점유율</span>
            <span className="text-chart-blue font-bold">{style.avg_possession}%</span>
          </div>
          <div className="w-full bg-dark-bg rounded-full h-2">
            <div
              className="bg-chart-blue h-2 rounded-full transition-all"
              style={{ width: `${style.avg_possession}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">평균 슈팅</span>
            <span className="text-chart-green font-bold">{style.avg_shots}회</span>
          </div>
          <div className="w-full bg-dark-bg rounded-full h-2">
            <div
              className="bg-chart-green h-2 rounded-full transition-all"
              style={{ width: `${Math.min(style.avg_shots * 5, 100)}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">평균 유효슈팅</span>
            <span className="text-chart-yellow font-bold">{style.avg_shots_on_target}회</span>
          </div>
          <div className="w-full bg-dark-bg rounded-full h-2">
            <div
              className="bg-chart-yellow h-2 rounded-full transition-all"
              style={{ width: `${Math.min(style.avg_shots_on_target * 10, 100)}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">평균 패스 성공률</span>
            <span className="text-chart-purple font-bold">{style.avg_pass_success_rate}%</span>
          </div>
          <div className="w-full bg-dark-bg rounded-full h-2">
            <div
              className="bg-chart-purple h-2 rounded-full transition-all"
              style={{ width: `${style.avg_pass_success_rate}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-gradient-card border border-dark-border rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-2xl">🎯</span>
        컨트롤러별 플레이 스타일
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {keyboard && renderStyleCard(keyboard, '키보드', '⌨️')}
        {gamepad && renderStyleCard(gamepad, '패드', '🎮')}
      </div>

      {/* Comparison Insights */}
      {keyboard && gamepad && (
        <div className="mt-6 space-y-3">
          {Math.abs(keyboard.avg_possession - gamepad.avg_possession) >= 5 && (
            <div className="p-3 bg-dark-bg rounded-lg">
              <p className="text-sm text-gray-300">
                {keyboard.avg_possession > gamepad.avg_possession ? (
                  <>
                    📊 키보드로 플레이할 때 점유율이{' '}
                    <span className="text-chart-blue font-bold">
                      {(keyboard.avg_possession - gamepad.avg_possession).toFixed(1)}%p
                    </span>{' '}
                    더 높습니다
                  </>
                ) : (
                  <>
                    📊 패드로 플레이할 때 점유율이{' '}
                    <span className="text-chart-blue font-bold">
                      {(gamepad.avg_possession - keyboard.avg_possession).toFixed(1)}%p
                    </span>{' '}
                    더 높습니다
                  </>
                )}
              </p>
            </div>
          )}

          {Math.abs(keyboard.avg_shots - gamepad.avg_shots) >= 3 && (
            <div className="p-3 bg-dark-bg rounded-lg">
              <p className="text-sm text-gray-300">
                {keyboard.avg_shots > gamepad.avg_shots ? (
                  <>
                    ⚽ 키보드로 플레이할 때 슈팅이{' '}
                    <span className="text-chart-green font-bold">
                      {(keyboard.avg_shots - gamepad.avg_shots).toFixed(1)}회
                    </span>{' '}
                    더 많습니다
                  </>
                ) : (
                  <>
                    ⚽ 패드로 플레이할 때 슈팅이{' '}
                    <span className="text-chart-green font-bold">
                      {(gamepad.avg_shots - keyboard.avg_shots).toFixed(1)}회
                    </span>{' '}
                    더 많습니다
                  </>
                )}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PlaystyleComparison;
