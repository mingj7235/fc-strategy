import React, { useEffect, useState } from 'react';

interface LoadingProgressProps {
  steps?: string[];
  estimatedDuration?: number; // milliseconds
  message?: string;
}

const LoadingProgress: React.FC<LoadingProgressProps> = ({
  steps = [
    '데이터 불러오는 중...',
    '경기 정보 분석 중...',
    '선수 성능 계산 중...',
    '결과 정리 중...',
  ],
  estimatedDuration = 8000,
  message,
}) => {
  const [progress, setProgress] = useState(0);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    const totalSteps = steps.length;
    const progressInterval = 50; // Update every 50ms for smooth animation

    let currentProgress = 0;
    let currentStep = 0;

    const progressTimer = setInterval(() => {
      // Increase progress gradually
      const increment = (100 / estimatedDuration) * progressInterval;
      currentProgress = Math.min(currentProgress + increment, 95); // Stop at 95% until complete
      setProgress(currentProgress);

      // Update step
      const newStep = Math.min(
        Math.floor((currentProgress / 100) * totalSteps),
        totalSteps - 1
      );
      if (newStep !== currentStep) {
        currentStep = newStep;
        setCurrentStepIndex(currentStep);
      }
    }, progressInterval);

    return () => clearInterval(progressTimer);
  }, [steps.length, estimatedDuration]);

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center p-8">
      <div className="w-full max-w-2xl">
        {/* Main Card */}
        <div className="relative bg-gradient-to-br from-dark-card via-dark-hover to-dark-card border border-dark-border rounded-2xl shadow-2xl p-8 overflow-hidden">
          {/* Animated Background */}
          <div className="absolute inset-0 bg-gradient-to-r from-accent-primary/5 via-blue-500/5 to-purple-500/5 animate-pulse"></div>

          {/* Gradient Overlay Animation */}
          <div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-accent-primary/10 to-transparent"
            style={{
              animation: 'shimmer 2s infinite',
              backgroundSize: '200% 100%',
            }}
          ></div>

          {/* Content */}
          <div className="relative z-10">
            {/* Icon */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="w-20 h-20 bg-gradient-to-br from-accent-primary to-blue-600 rounded-full flex items-center justify-center shadow-lg">
                  <svg
                    className="w-10 h-10 text-white animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                </div>
                {/* Pulsing Ring */}
                <div className="absolute inset-0 w-20 h-20 rounded-full bg-accent-primary/30 animate-ping"></div>
              </div>
            </div>

            {/* Title */}
            <h2 className="text-2xl font-bold text-white text-center mb-2">
              {message || '분석 진행 중'}
            </h2>

            {/* Current Step */}
            <p className="text-center text-gray-300 mb-8 text-lg">
              {steps[currentStepIndex]}
            </p>

            {/* Progress Bar */}
            <div className="mb-8">
              <div className="relative h-3 bg-dark-bg rounded-full overflow-hidden shadow-inner">
                {/* Background Gradient */}
                <div className="absolute inset-0 bg-gradient-to-r from-gray-800 to-gray-700"></div>

                {/* Progress Fill */}
                <div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-accent-primary via-blue-500 to-purple-500 rounded-full transition-all duration-300 ease-out shadow-lg"
                  style={{ width: `${progress}%` }}
                >
                  {/* Shimmer Effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                </div>
              </div>

              {/* Percentage */}
              <div className="flex justify-between items-center mt-3">
                <span className="text-sm text-gray-400">
                  진행률
                </span>
                <span className="text-lg font-bold text-white">
                  {Math.round(progress)}%
                </span>
              </div>
            </div>

            {/* Steps Indicator */}
            <div className="flex justify-between items-center">
              {steps.map((_step, index) => (
                <div key={index} className="flex flex-col items-center flex-1">
                  {/* Step Circle */}
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center mb-2 transition-all duration-300 ${
                      index <= currentStepIndex
                        ? 'bg-gradient-to-br from-accent-primary to-blue-600 shadow-lg scale-110'
                        : 'bg-dark-bg border-2 border-dark-border'
                    }`}
                  >
                    {index < currentStepIndex ? (
                      <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : index === currentStepIndex ? (
                      <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                    ) : (
                      <span className="text-xs text-gray-500">{index + 1}</span>
                    )}
                  </div>

                  {/* Step Label */}
                  <span
                    className={`text-xs text-center transition-colors duration-300 ${
                      index <= currentStepIndex ? 'text-accent-primary font-semibold' : 'text-gray-500'
                    }`}
                  >
                    {index === 0 && '불러오기'}
                    {index === 1 && '분석'}
                    {index === 2 && '계산'}
                    {index === 3 && '완료'}
                  </span>

                  {/* Connection Line */}
                  {index < steps.length - 1 && (
                    <div className="absolute h-0.5 bg-dark-border" style={{
                      width: `calc(${100 / steps.length}% - 2rem)`,
                      left: `calc(${(index * 100) / steps.length}% + ${100 / (steps.length * 2)}%)`,
                      top: '1rem',
                    }}>
                      <div
                        className="h-full bg-gradient-to-r from-accent-primary to-blue-600 transition-all duration-300"
                        style={{ width: index < currentStepIndex ? '100%' : '0%' }}
                      ></div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Helper Text */}
            <p className="text-center text-xs text-gray-500 mt-6">
              잠시만 기다려주세요. 고품질 분석을 준비하고 있습니다.
            </p>
          </div>
        </div>

        {/* Floating Particles Effect */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-accent-primary/30 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${3 + Math.random() * 2}s`,
              }}
            ></div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes shimmer {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
            opacity: 0;
          }
          50% {
            opacity: 0.3;
          }
          100% {
            transform: translateY(-100vh) translateX(20px);
            opacity: 0;
          }
        }

        .animate-shimmer {
          animation: shimmer 2s infinite;
          background-size: 200% 100%;
        }

        .animate-float {
          animation: float 5s infinite;
        }
      `}</style>
    </div>
  );
};

export default LoadingProgress;
