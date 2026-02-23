export const MATCH_TYPE_NAMES: Record<number, string> = {
  50: '공식경기',
  52: '감독모드',
  214: '볼타',
};

export const RESULT_COLORS = {
  win: 'text-green-600 bg-green-50',
  lose: 'text-red-600 bg-red-50',
  draw: 'text-gray-600 bg-gray-50',
};

export const SHOT_RESULT_COLORS = {
  goal: '#10b981', // green
  on_target: '#fbbf24', // yellow
  off_target: '#ef4444', // red
  blocked: '#6b7280', // gray
};

export const SHOT_RESULT_LABELS = {
  goal: '골',
  on_target: '유효슈팅',
  off_target: '빗나감',
  blocked: '막힘',
};
