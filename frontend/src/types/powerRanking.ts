export interface FormAnalysis {
  form_index: number;
  trend: 'improving' | 'declining' | 'stable';
  form_grade: 'excellent' | 'good' | 'average' | 'poor';
  breakdown: {
    rating_score: number;
    goal_score: number;
    assist_score: number;
    shot_accuracy_score: number;
    pass_accuracy_score: number;
    win_score: number;
  };
}

export interface EfficiencyMetrics {
  efficiency_score: number;
  goals_per_game: number;
  assists_per_game: number;
  goal_conversion_rate: number;
  assist_rate: number;
  pass_accuracy: number;
  dribble_success_rate: number;
}

export interface ConsistencyRating {
  consistency_score: number;
  rating_variance: number;
  standard_deviation: number;
  grade: 'very_consistent' | 'consistent' | 'moderate' | 'inconsistent' | 'insufficient_data';
}

export interface ImpactAnalysis {
  avg_total_impact: number;
  avg_offensive_impact: number;
  avg_creative_impact: number;
  avg_clutch_impact: number;
  consistency: string;
}

export interface PositionRating {
  position_score: number;
  position_group: string;
  position_group_name: string;
  key_metrics: { [key: string]: number | string };
  strengths: string[];
  weaknesses: string[];
  evaluation_criteria: { [key: string]: string };
}

export interface RadarData {
  // New position-aware format
  values?: Record<string, number>;
  labels?: Record<string, string>;
  // Legacy flat format (backward compat)
  form?: number;
  efficiency?: number;
  consistency?: number;
  goal_threat?: number;
  creativity?: number;
  impact?: number;
}

export interface PlayerPowerRanking {
  spid: number;
  player_name: string;
  season_id: number;
  season_name?: string;
  season_img?: string;
  position: number;
  grade: number;
  matches_played: number;
  image_url: string;
  power_score: number;
  tier: 'SSS' | 'SS' | 'S' | 'A' | 'B' | 'C' | 'D';
  form_analysis: FormAnalysis;
  efficiency_metrics: EfficiencyMetrics;
  consistency_rating: ConsistencyRating;
  impact_analysis: ImpactAnalysis | null;
  position_rating: PositionRating | null;
  radar_data: RadarData;
  percentile_rank: number;
}

export interface PowerRankingsResponse {
  total_players: number;
  rankings: PlayerPowerRanking[];
  aggregate_stats?: import('./match').AggregateStats;  // NEW: Aggregate statistics across all matches
}

export interface TierInfo {
  tier: string;
  name: string;
  score_range: string;
  description: string;
  characteristics: string[];
  color: string;
}

export interface TierInfoResponse {
  tiers: TierInfo[];
  total_tiers: number;
}
