export interface User {
  ouid: string;
  nickname: string;
  max_division: number | null;
  last_updated: string;
  created_at: string;
}

export interface UserStats {
  ouid: string;
  user_nickname: string;
  period: 'weekly' | 'monthly' | 'all_time';
  total_matches: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  avg_possession: number;
  avg_shots: number;
  avg_goals: number;
  shot_accuracy: number;
  xg: number;
  updated_at: string;
}
