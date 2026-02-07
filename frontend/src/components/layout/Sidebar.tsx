import { useState, useEffect } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { getUserByOuid } from '../../services/api';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

interface DivisionInfo {
  matchtype: number;
  matchtype_label: string;
  division: number;
  tier_name: string;
  short: string;
  color: string;
  color2: string;
  bg: string;
  border: string;
  text_class: string;
  rank: number;
}

interface UserInfo {
  ouid: string;
  nickname: string;
  level?: number;
  max_division?: number;
  tier_name?: string;
  divisions?: DivisionInfo[];
}

interface NavigationItem {
  name: string;
  icon: string;
  path: string;
  description: string;
  category: string;
}

interface DividerItem {
  divider: true;
  label: string;
  category: string;
}

type MenuItem = NavigationItem | DividerItem;

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  // URL에서 ouid 추출 (경로 또는 쿼리 파라미터에서)
  const pathOuid = location.pathname.match(/\/user\/([^\/]+)/)?.[1];
  const queryOuid = searchParams.get('ouid');
  const ouid = pathOuid || queryOuid || null;

  // 유저 정보 상태
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loadingUser, setLoadingUser] = useState(false);

  // 유저 정보 가져오기
  useEffect(() => {
    if (!ouid) {
      setUserInfo(null);
      return;
    }

    const fetchUserInfo = async () => {
      setLoadingUser(true);
      try {
        const data = await getUserByOuid(ouid);
        setUserInfo(data);
      } catch (error) {
        console.error('Failed to fetch user info:', error);
      } finally {
        setLoadingUser(false);
      }
    };

    fetchUserInfo();
  }, [ouid]);

  // 현재 경로가 특정 패턴과 일치하는지 확인
  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.includes(path);
  };

  // 네비게이션 메뉴 항목들
  const navigationItems: MenuItem[] = [
    {
      name: '홈',
      icon: '🏠',
      path: '/',
      description: '닉네임 검색',
      category: 'main',
    },
    ...(ouid ? [
      {
        name: '대시보드',
        icon: '📊',
        path: `/user/${ouid}`,
        description: '종합 분석',
        category: 'main',
      },
      {
        name: '파워 랭킹',
        icon: '⭐',
        path: `/user/${ouid}/power-rankings`,
        description: '선수 평가',
        category: 'main',
      },
      // 구분선
      {
        divider: true as const,
        label: '경기 분석',
        category: 'analysis',
      },
      {
        name: '슈팅 히트맵',
        icon: '🎯',
        path: `/user/${ouid}/analysis/shots`,
        description: '슈팅 위치 분석',
        category: 'analysis',
      },
      {
        name: '플레이 스타일',
        icon: '🎨',
        path: `/user/${ouid}/analysis/style`,
        description: '전술 스타일',
        category: 'analysis',
      },
      {
        name: '패스 분석',
        icon: '↗️',
        path: `/user/${ouid}/analysis/passes`,
        description: '패스 정확도',
        category: 'analysis',
      },
      {
        name: '세트피스',
        icon: '⚽',
        path: `/user/${ouid}/analysis/set-pieces`,
        description: '코너킥/프리킥',
        category: 'analysis',
      },
      {
        name: '수비 분석',
        icon: '🛡️',
        path: `/user/${ouid}/analysis/defense`,
        description: '수비 지표',
        category: 'analysis',
      },
      // 구분선
      {
        divider: true as const,
        label: '고급 분석',
        category: 'advanced',
      },
      {
        name: '패스 다양성',
        icon: '🔀',
        path: `/user/${ouid}/analysis/pass-variety`,
        description: '패스 유형 분석',
        category: 'advanced',
      },
      {
        name: '슈팅 품질',
        icon: '🎪',
        path: `/user/${ouid}/analysis/shooting-quality`,
        description: 'xG 분석',
        category: 'advanced',
      },
      {
        name: '컨트롤러 분석',
        icon: '🎮',
        path: `/user/${ouid}/analysis/controller`,
        description: '키보드 vs 패드',
        category: 'advanced',
      },
      // 구분선
      {
        divider: true as const,
        label: '전략 인텔리전스',
        category: 'intelligence',
      },
      {
        name: '랭커 격차',
        icon: '🏆',
        path: `/user/${ouid}/analysis/ranker-gap`,
        description: '랭커까지의 거리',
        category: 'intelligence',
      },
      {
        name: '실력 격차 인덱스',
        icon: '📊',
        path: `/user/${ouid}/analysis/skill-gap`,
        description: '선수별 Z-score 비교',
        category: 'intelligence',
      },
      {
        name: '선수 기여도',
        icon: '📈',
        path: `/user/${ouid}/analysis/player-contribution`,
        description: '포지션별 기여도 분석',
        category: 'intelligence',
      },
      {
        name: '폼 사이클',
        icon: '📈',
        path: `/user/${ouid}/analysis/form-cycle`,
        description: '핫스트릭 & 슬럼프',
        category: 'intelligence',
      },
      {
        name: '습관 루프',
        icon: '🧠',
        path: `/user/${ouid}/analysis/habit-loop`,
        description: '마르코프 패스 분석',
        category: 'intelligence',
      },
      {
        name: '상대 유형 분류',
        icon: '🗺️',
        path: `/user/${ouid}/analysis/opponent-types`,
        description: '6개 유형 승률 맵',
        category: 'intelligence',
      },
    ] : []),
    // 상대 스카우터 (ouid 불필요)
    {
      name: '상대 DNA 스카우터',
      icon: '🔍',
      path: `/opponent-scout`,
      description: '경기 전 상대 분석',
      category: 'intelligence',
    },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-screen bg-gradient-to-b from-dark-card to-dark-bg border-r border-dark-border z-50 transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } w-64`}
      >
        {/* Header */}
        <div className="p-6 border-b border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-white">FC Strategy</h1>
              <p className="text-xs text-gray-400 mt-1">분석 플랫폼</p>
            </div>
            <button
              onClick={onToggle}
              className="lg:hidden text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* User Info Section */}
        {ouid && (
          <div className="border-b border-white/5">
            {loadingUser ? (
              <div className="flex items-center justify-center py-5">
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-accent-primary border-t-transparent" />
              </div>
            ) : userInfo ? (() => {
              const highestDiv = userInfo.divisions && userInfo.divisions.length > 0
                ? userInfo.divisions.reduce((best, d) => d.rank < best.rank ? d : best)
                : null;
              return (
                <div
                  className="relative px-4 pt-3 pb-2.5 overflow-hidden"
                  style={{
                    background: highestDiv
                      ? `linear-gradient(160deg, ${highestDiv.color}12 0%, transparent 55%)`
                      : 'transparent',
                  }}
                >
                  {/* Ambient glow blob */}
                  {highestDiv && (
                    <div
                      className="absolute -top-6 -left-6 w-28 h-28 rounded-full pointer-events-none"
                      style={{
                        background: highestDiv.color,
                        opacity: 0.12,
                        filter: 'blur(24px)',
                      }}
                    />
                  )}

                  {/* Avatar + Nickname row */}
                  <div className="relative flex items-center gap-2 mb-2">
                    <div
                      className="w-7 h-7 rounded-full flex items-center justify-center font-bold text-white text-xs flex-shrink-0"
                      style={{
                        background: 'linear-gradient(135deg, #2563eb, #1e40af)',
                        boxShadow: highestDiv
                          ? `0 0 0 2px ${highestDiv.border}55, 0 0 10px ${highestDiv.color}30`
                          : '0 0 0 2px #3b82f640',
                      }}
                    >
                      {userInfo.nickname.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-[12px] font-bold text-white truncate leading-tight">
                        {userInfo.nickname}
                      </div>
                      <div className="text-[8px] text-gray-600 mt-0.5 tracking-wide">FC ONLINE</div>
                    </div>
                  </div>

                  {/* Rank grid */}
                  {userInfo.divisions && userInfo.divisions.length > 0 ? (
                    <div className="relative grid grid-cols-2 gap-1">
                      {userInfo.divisions.map((div) => (
                        <div
                          key={div.matchtype}
                          className="relative rounded-md p-2 overflow-hidden"
                          style={{
                            background: div.bg,
                            border: `1px solid ${div.border}35`,
                          }}
                        >
                          {/* Top shimmer line */}
                          <div
                            className="absolute top-0 left-0 right-0 h-px"
                            style={{
                              background: `linear-gradient(90deg, transparent, ${div.color}70, transparent)`,
                            }}
                          />

                          {/* Mode label */}
                          <div className="text-[7px] font-semibold tracking-widest text-gray-600 uppercase mb-1">
                            {div.matchtype === 50 ? '공식' : '감독'}
                          </div>

                          {/* Short code — hero text */}
                          <div
                            className="text-[14px] font-black leading-none tracking-tighter"
                            style={{ color: div.color }}
                          >
                            {div.short}
                          </div>

                          {/* Tier name */}
                          <div
                            className="text-[8px] font-medium mt-0.5 leading-tight"
                            style={{ color: div.color, opacity: 0.6 }}
                          >
                            {div.tier_name}
                          </div>

                          {/* Watermark */}
                          <div
                            className="absolute -right-0.5 -bottom-1 text-[28px] font-black leading-none select-none pointer-events-none"
                            style={{ color: div.color, opacity: 0.06 }}
                          >
                            {div.short.replace('.', '').charAt(0)}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : userInfo.tier_name ? (
                    <div
                      className="text-[10px] px-2 py-0.5 rounded font-semibold inline-block"
                      style={{
                        background: 'rgba(59,130,246,0.15)',
                        color: '#60a5fa',
                      }}
                    >
                      {userInfo.tier_name}
                    </div>
                  ) : null}
                </div>
              );
            })() : null}
          </div>
        )}

        {/* Navigation */}
        <nav className="p-4 overflow-y-auto" style={{ height: ouid ? 'calc(100vh - 290px)' : 'calc(100vh - 180px)' }}>
          <div className="space-y-1">
            {navigationItems.map((item, index) => {
              // Render divider
              if ('divider' in item && item.divider) {
                return (
                  <div key={`divider-${index}`} className="pt-3 pb-2">
                    <div className="text-xs font-bold text-gray-500 uppercase tracking-wider px-4">
                      {item.label}
                    </div>
                    <div className="mt-2 border-t border-dark-border"></div>
                  </div>
                );
              }

              // Render navigation item (TypeScript now knows this is NavigationItem)
              const navItem = item as NavigationItem;
              return (
                <button
                  key={navItem.path}
                  onClick={() => {
                    navigate(navItem.path);
                    if (window.innerWidth < 1024) {
                      onToggle();
                    }
                  }}
                  className={`w-full flex items-start gap-3 px-4 py-2.5 rounded-lg transition-all ${
                    isActive(navItem.path)
                      ? 'bg-accent-primary text-white shadow-lg'
                      : 'text-gray-300 hover:bg-dark-hover hover:text-white'
                  }`}
                >
                  <span className="text-lg flex-shrink-0">{navItem.icon}</span>
                  <div className="flex-1 text-left">
                    <div className={`text-sm font-semibold ${
                      isActive(navItem.path) ? 'text-white' : 'text-gray-200'
                    }`}>
                      {navItem.name}
                    </div>
                    <div className={`text-[10px] mt-0.5 ${
                      isActive(navItem.path) ? 'text-white/80' : 'text-gray-500'
                    }`}>
                      {navItem.description}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-border bg-dark-bg/80 backdrop-blur-sm">
          <div className="text-xs text-gray-500 text-center">
            <div>FC Online 전문가급</div>
            <div className="mt-1">경기 분석 시스템</div>
          </div>
        </div>
      </aside>

      {/* Toggle Button for Mobile */}
      <button
        onClick={onToggle}
        className={`fixed top-4 left-4 z-30 lg:hidden bg-dark-card border border-dark-border text-white p-3 rounded-lg shadow-dark-lg transition-opacity ${
          isOpen ? 'opacity-0' : 'opacity-100'
        }`}
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
    </>
  );
};

export default Sidebar;
