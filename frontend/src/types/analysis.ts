export interface ShotAnalysis {
  total_shots: number;
  goals: number;
  on_target: number;
  off_target: number;
  blocked: number;
  shot_accuracy: number;
  conversion_rate: number;
  xg: number;
  heatmap_data: HeatmapPoint[];
  zone_analysis: ZoneAnalysis;
}

export interface HeatmapPoint {
  x: number;
  y: number;
  result: 'goal' | 'on_target' | 'off_target' | 'blocked';
  xg: number;
}

export interface ZoneAnalysis {
  inside_box: ZoneStats;
  outside_box: ZoneStats;
  center: ZoneStats;
  side: ZoneStats;
}

export interface ZoneStats {
  shots: number;
  goals: number;
  efficiency: number;
}

export interface StyleAnalysis {
  total_matches: number;
  wins: number;
  losses: number;
  draws: number;
  attack_pattern: 'possession_based' | 'counter_attack' | 'balanced' | 'unknown';
  possession_style: 'high_possession' | 'medium_possession' | 'low_possession' | 'unknown';
  win_patterns: PatternStats;
  loss_patterns: PatternStats;
}

export interface PatternStats {
  avg_possession: number;
  avg_shots: number;
  avg_shots_on_target: number;
  avg_goals: number;
  avg_pass_success: number;
}
