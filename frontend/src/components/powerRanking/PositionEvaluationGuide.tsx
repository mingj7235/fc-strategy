import React, { useState } from 'react';

interface PositionEvaluationGuideProps {
  onClose: () => void;
}

const PositionEvaluationGuide: React.FC<PositionEvaluationGuideProps> = ({ onClose }) => {
  const [selectedPosition, setSelectedPosition] = useState<string>('ST');

  const positionGroups = [
    {
      group: 'ST',
      name: '스트라이커',
      icon: '⚽',
      color: 'from-red-500 to-orange-500',
      role: '득점, 마무리',
      criteria: {
        '득점': '50% - 경기당 골이 가장 중요',
        '슈팅 효율': '30% - 슈팅 전환율과 정확도',
        '어시스트': '10% - 찬스 메이킹 능력',
        '헤딩': '10% - 공중볼 마무리',
      },
      strengths: [
        '경기당 0.6골 이상: 일류 득점력',
        '슈팅 전환율 25% 이상: 뛰어난 마무리',
        '헤딩 성공률 70% 이상: 강력한 헤딩',
      ],
      tips: '스트라이커는 골 결정력이 가장 중요합니다. 높은 슈팅 전환율과 유효슈팅 비율을 유지하세요.',
    },
    {
      group: 'W',
      name: '윙어',
      icon: '⚡',
      color: 'from-yellow-500 to-orange-500',
      role: '측면 돌파, 득점, 찬스 메이킹',
      criteria: {
        '득점': '35% - 골과 슈팅 전환율',
        '어시스트': '30% - 찬스 메이킹',
        '드리블': '25% - 돌파 능력과 성공률',
        '슈팅 효율': '10% - 슈팅 정확도',
      },
      strengths: [
        '경기당 0.4골 이상: 일류 득점력',
        '드리블 성공률 75% 이상: 탁월한 드리블',
        '경기당 0.35 어시스트 이상: 우수한 찬스 메이킹',
      ],
      tips: '윙어는 득점과 어시스트가 균형있게 중요합니다. 드리블로 수비를 무너뜨리고 찬스를 만드세요.',
    },
    {
      group: 'CAM',
      name: '공격형 미드필더',
      icon: '🎯',
      color: 'from-purple-500 to-pink-500',
      role: '찬스 메이킹, 어시스트, 득점',
      criteria: {
        '어시스트': '35% - 킬패스와 찬스 메이킹',
        '득점': '30% - 골 기여',
        '드리블': '20% - 돌파 능력',
        '패스 정확도': '15% - 볼 배급',
      },
      strengths: [
        '경기당 0.4 어시스트 이상: 탁월한 찬스 메이킹',
        '경기당 0.3골 이상: 우수한 득점력',
        '드리블 성공률 75% 이상: 효과적인 돌파',
      ],
      tips: '공격형 미드필더는 어시스트가 가장 중요합니다. 킬패스와 스루패스로 공격을 조율하세요.',
    },
    {
      group: 'CM',
      name: '중앙 미드필더',
      icon: '⚙️',
      color: 'from-blue-500 to-cyan-500',
      role: '균형잡힌 공수, 볼 배급, 경기 흐름 조절',
      criteria: {
        '패스 플레이': '35% - 패스 정확도와 볼 순환',
        '공격 기여': '30% - 어시스트와 득점',
        '수비 기여': '20% - 태클과 인터셉트',
        '드리블': '15% - 볼 컨트롤',
      },
      strengths: [
        '패스 성공률 88% 이상: 정확한 패스 플레이',
        '경기당 0.3 어시스트: 우수한 찬스 메이킹',
        '경기당 2.5 태클 이상: 균형잡힌 수비 기여',
      ],
      tips: '중앙 미드필더는 공수 균형이 핵심입니다. 높은 패스 정확도로 경기를 조율하세요.',
    },
    {
      group: 'CDM',
      name: '수비형 미드필더',
      icon: '🛡️',
      color: 'from-green-500 to-teal-500',
      role: '공격 차단, 볼 탈취, 빌드업 시작',
      criteria: {
        '수비 지표': '45% - 태클, 인터셉트, 블록',
        '패스 정확도': '30% - 안정적인 볼 배급',
        '볼 순환': '15% - 패스 빈도',
        '안정성': '10% - 평점 일관성',
      },
      strengths: [
        '경기당 4태클 이상: 적극적인 볼 탈취',
        '경기당 3인터셉트 이상: 탁월한 공격 차단',
        '패스 성공률 88% 이상: 안정적인 볼 배급',
      ],
      tips: '수비형 미드필더는 수비 지표가 가장 중요합니다. 적극적인 인터셉트로 상대 공격을 차단하세요.',
    },
    {
      group: 'WB',
      name: '윙백',
      icon: '🔥',
      color: 'from-orange-500 to-red-500',
      role: '측면 공격 가담, 수비 복귀',
      criteria: {
        '공격 기여': '45% - 어시스트, 드리블, 슈팅',
        '수비 지표': '30% - 태클, 인터셉트',
        '활동량': '15% - 총 액션 수',
        '패스 정확도': '10%',
      },
      strengths: [
        '경기당 0.3 어시스트: 탁월한 공격 가담',
        '드리블 성공률 70% 이상: 효과적인 측면 돌파',
        '경기당 3태클 이상: 적극적인 수비 복귀',
      ],
      tips: '윙백은 공격 가담이 풀백보다 중요합니다. 측면을 따라 적극적으로 오버래핑하세요.',
    },
    {
      group: 'FB',
      name: '풀백',
      icon: '🏃',
      color: 'from-indigo-500 to-blue-500',
      role: '측면 수비, 공격 가담',
      criteria: {
        '수비 지표': '40% - 태클, 인터셉트',
        '공격 기여': '30% - 어시스트, 패스, 드리블',
        '활동량': '20% - 총 액션 수',
        '안정성': '10%',
      },
      strengths: [
        '경기당 3.5태클 이상: 강력한 수비력',
        '경기당 0.25 어시스트: 우수한 공격 지원',
        '드리블 성공률 70% 이상: 효과적인 측면 돌파',
      ],
      tips: '풀백은 수비가 우선이지만 공격 지원도 중요합니다. 균형잡힌 플레이를 유지하세요.',
    },
    {
      group: 'CB',
      name: '센터백',
      icon: '🧱',
      color: 'from-gray-600 to-gray-800',
      role: '수비 조직, 공중볼 경합, 태클',
      criteria: {
        '수비 지표': '50% - 태클, 인터셉트, 블록',
        '공중볼 경합': '25% - 헤딩 성공률',
        '빌드업': '15% - 패스 정확도',
        '안정성': '10%',
      },
      strengths: [
        '경기당 4태클 이상: 적극적인 태클',
        '공중볼 성공률 70% 이상: 강력한 공중볼 경합',
        '패스 성공률 85% 이상: 안정적인 빌드업',
      ],
      tips: '센터백은 수비 지표가 가장 중요합니다. 공중볼 경합에서 우위를 점하고 안정적으로 빌드업하세요.',
    },
    {
      group: 'GK',
      name: '골키퍼',
      icon: '🧤',
      color: 'from-yellow-600 to-amber-700',
      role: '안정성, 실점 방지',
      criteria: {
        '평점': '85% - 골키퍼는 평점이 가장 중요',
        '안정성': '15% - 일관된 퍼포먼스',
      },
      strengths: [
        '평점 7.5 이상: 뛰어난 평점 유지',
        '평점 분산 0.5 미만: 안정적인 퍼포먼스',
      ],
      tips: '골키퍼는 평점과 안정성이 전부입니다. 일관되게 높은 평점을 유지하세요.',
    },
  ];

  const selected = positionGroups.find(p => p.group === selectedPosition) || positionGroups[0];

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-dark-card border border-dark-border rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-accent-primary to-blue-600 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-3">
              <span>📊</span>
              포지션별 평가 기준 가이드
            </h2>
            <p className="text-blue-100 mt-1 text-sm">
              20년 경력 축구 전문가의 인사이트 기반 평가 시스템
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Position List */}
          <div className="w-64 bg-dark-hover border-r border-dark-border p-4 overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wide">포지션 선택</h3>
            <div className="space-y-2">
              {positionGroups.map((pos) => (
                <button
                  key={pos.group}
                  onClick={() => setSelectedPosition(pos.group)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-all ${
                    selectedPosition === pos.group
                      ? `bg-gradient-to-r ${pos.color} text-white shadow-lg scale-105`
                      : 'bg-dark-card hover:bg-dark-border text-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{pos.icon}</span>
                    <div>
                      <div className="font-semibold">{pos.name}</div>
                      <div className="text-xs opacity-75">{pos.group}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {/* Position Header */}
            <div className={`bg-gradient-to-r ${selected.color} rounded-xl p-6 mb-6 text-white`}>
              <div className="flex items-center gap-4 mb-3">
                <span className="text-5xl">{selected.icon}</span>
                <div>
                  <h3 className="text-3xl font-bold">{selected.name}</h3>
                  <p className="text-lg opacity-90">{selected.role}</p>
                </div>
              </div>
            </div>

            {/* Evaluation Criteria */}
            <div className="mb-6">
              <h4 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <span>📋</span>
                평가 기준 및 가중치
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(selected.criteria).map(([key, value]) => (
                  <div key={key} className="bg-dark-hover border border-dark-border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-white">{key}</span>
                      <span className="text-accent-primary font-bold">{value.split(' - ')[0]}</span>
                    </div>
                    <p className="text-sm text-gray-400">{value.split(' - ')[1] || value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Strengths Indicators */}
            <div className="mb-6">
              <h4 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <span>⭐</span>
                우수 기준
              </h4>
              <div className="space-y-2">
                {selected.strengths.map((strength, idx) => (
                  <div key={idx} className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-3 flex items-start gap-3">
                    <span className="text-green-400 text-xl mt-0.5">✓</span>
                    <p className="text-gray-200">{strength}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Tips */}
            <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-lg p-5">
              <h4 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <span>💡</span>
                전문가 팁
              </h4>
              <p className="text-gray-200 leading-relaxed">{selected.tips}</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-dark-hover border-t border-dark-border p-4 text-center">
          <p className="text-sm text-gray-400">
            이 평가 기준은 프로 축구 전문가의 20년 경험을 바탕으로 설계되었습니다
          </p>
        </div>
      </div>
    </div>
  );
};

export default PositionEvaluationGuide;
