export interface Match {
  match_id: string;
  ouid: string;
  user_nickname: string;
  match_date: string;
  match_type: number;
  result: 'win' | 'lose' | 'draw';
  goals_for: number;
  goals_against: number;
  possession: number;
  shots?: number;
  shots_on_target?: number;
  pass_success_rate?: number | string;  // Django DecimalField serializes to string
  opponent_nickname?: string;
  raw_data?: any;
}

export interface MatchDetail extends Match {
  shot_details: ShotDetail[];
}

export interface ShotDetail {
  id: number;
  x: number;
  y: number;
  result: 'goal' | 'on_target' | 'off_target' | 'blocked';
  shot_type: number;
  goal_time: number;
  assist_x?: number;
  assist_y?: number;
}

export interface PlayerPerformance {
  spid: number;
  player_name: string;
  season_id?: number;  // Extracted season ID from spid
  season_name?: string;  // Season className from metadata (e.g., "23 TOTY")
  season_img?: string;  // Season badge image URL from seasonid.json
  position: number;
  grade: number;
  rating: number | string;  // Django DecimalField serializes to string
  goals: number;
  assists: number;
  shots: number;
  shots_on_target: number;
  shot_accuracy: number | string | null;  // Django DecimalField serializes to string, can be null
  pass_attempts: number;
  pass_success: number;
  pass_success_rate: number | string | null;  // Django DecimalField serializes to string, can be null
  dribble_attempts: number;
  dribble_success: number;
  dribble_success_rate: number | string | null;  // Django DecimalField serializes to string, can be null
  tackle_success: number;
  interceptions: number;
  blocks: number;
  aerial_success: number;
  yellow_cards: number;
  red_cards: number;
  image_url: string;
}

export interface PlayerStatsResponse {
  top_performers: PlayerPerformance[];
  all_players: PlayerPerformance[];
  message?: string;
}

export interface KeyMoment {
  minute: number;
  type: 'goal' | 'big_chance';
  xg: number;
  x: number;
  y: number;
  result: string;
}

export interface TimelineDataPoint {
  minute: number;
  cumulative_xg: number;
  goals: number;
}

export interface TimelineAnalysis {
  xg_by_period: {
    first_half: number;
    second_half: number;
  };
  key_moments: KeyMoment[];
  timeline_data: TimelineDataPoint[];
  insights: string[];
}

export interface TacticalInsights {
  attack_pattern: {
    type: string;
    description: string;
    wing_shots: number;
    central_shots: number;
    total_shots: number;
  };
  possession_style: {
    type: string;
    description: string;
    possession: number;
    pass_success_rate: number;
  };
  defensive_approach: {
    type: string;
    description: string;
  };
  insights: string[];
  recommendations: string[];
}

export interface MatchAnalysis {
  match_overview: Match;
  player_performances: PlayerStatsResponse;
  timeline: TimelineAnalysis;
  tactical_insights: TacticalInsights;
}

export interface AssistHeatmapPoint {
  x: number;
  y: number;
  shooter_spid: number;
  assist_spid: number;
  goal_time: number;
}

export interface PlayerConnection {
  from_spid: number;
  to_spid: number;
  assists: number;
  from_player_name: string;
  to_player_name: string;
}

export interface AssistTypes {
  wing_assists: number;
  central_assists: number;
  deep_assists: number;
  forward_assists: number;
  total_assists: number;
  wing_percentage: number;
  central_percentage: number;
}

export interface AssistDistanceStats {
  avg_distance: number;
  max_distance: number;
  min_distance: number;
  short_passes: number;
  long_passes: number;
  total_measured: number;
}

export interface TopPlaymaker {
  spid: number;
  total_assists: number;
  player_name: string;
}

export interface AssistNetworkAnalysis {
  assist_heatmap: AssistHeatmapPoint[];
  player_network: PlayerConnection[];
  assist_types: AssistTypes;
  assist_distance_stats: AssistDistanceStats;
  top_playmakers: TopPlaymaker[];
  total_goals: number;
  goals_with_assist: number;
}

export interface ShotTypeBreakdown {
  type_name: string;
  shots: number;
  goals: number;
  on_target: number;
  success_rate: number;
  conversion_rate: number;
}

export interface LocationStats {
  shots: number;
  goals: number;
  on_target: number;
  success_rate: number;
  conversion_rate: number;
}

export interface PostHitShot {
  shot_type: number;
  result: string;
  hit_post: boolean;
  in_penalty: boolean;
  x: number;
  y: number;
}

export interface PostHitsAnalysis {
  post_hit_count: number;
  post_hit_shots: PostHitShot[];
  unlucky_factor: number;
}

export interface ShotTypeAnalysis {
  type_breakdown: ShotTypeBreakdown[];
  location_analysis: {
    inside_box: LocationStats;
    outside_box: LocationStats;
  };
  post_hits: PostHitsAnalysis;
  total_shots: number;
  insights: string[];
}

export interface PassTypeBreakdown {
  type_name: string;
  type_code: string;
  attempts: number;
  success: number;
  success_rate: number;
}

export interface PlayStyle {
  primary_style: string;
  secondary_style: string;
  description: string;
  ground_ratio: number;
  aerial_ratio: number;
  ground_passes: number;
  aerial_passes: number;
  penetrative_passes: number;
}

export interface TotalPassStats {
  total_attempts: number;
  total_success: number;
  overall_success_rate: number;
}

export interface PassTypeAnalysis {
  pass_breakdown: PassTypeBreakdown[];
  diversity_score: number;
  play_style: PlayStyle;
  total_stats: TotalPassStats;
  insights: string[];
}

export interface ControllerPerformance {
  matches: number;
  wins: number;
  draws: number;
  losses: number;
  win_rate: number;
  draw_rate: number;
  loss_rate: number;
  avg_goals_for: number;
  avg_goals_against: number;
  goal_difference: number;
}

export interface ControllerPlaystyle {
  avg_possession: number;
  avg_shots: number;
  avg_shots_on_target: number;
  avg_pass_success_rate: number;
  style_tags: string[];
}

export interface ControllerRecommendation {
  recommended_controller: string | null;
  reason: string;
  confidence: number;
}

export interface ControllerAnalysis {
  controller_stats: {
    keyboard: any;
    gamepad: any;
  };
  performance_comparison: {
    keyboard?: ControllerPerformance;
    gamepad?: ControllerPerformance;
  };
  playstyle_comparison: {
    keyboard?: ControllerPlaystyle;
    gamepad?: ControllerPlaystyle;
  };
  recommendation: ControllerRecommendation;
  insights: string[];
  matchtype: number;
  matches_analyzed: number;
}

export interface HeadingStats {
  total_headers: number;
  goals: number;
  on_target: number;
  success_rate: number;
  conversion_rate: number;
  headers_with_assist: number;
  cross_percentage: number;
  inside_box: number;
  box_percentage: number;
}

export interface HeadingPositions {
  positions: {
    central: number;
    left: number;
    right: number;
    box: number;
    edge: number;
  };
  position_percentages: {
    [key: string]: number;
  };
  position_goals: {
    [key: string]: number;
  };
}

export interface CrossOrigins {
  cross_origins: {
    left_wing: number;
    right_wing: number;
    central: number;
    no_assist: number;
  };
  origin_percentages: {
    [key: string]: number;
  };
  origin_goals: {
    [key: string]: number;
  };
}

export interface TargetMan {
  player_identified: boolean;
  total_headers: number;
  total_goals: number;
  message: string;
}

export interface AerialEfficiency {
  score: number;
  grade: string;
  grade_text: string;
}

export interface HeadingAnalysis {
  heading_stats: HeadingStats;
  heading_positions: HeadingPositions;
  cross_origins: CrossOrigins;
  target_man: TargetMan;
  efficiency_score: AerialEfficiency;
  insights: string[];
}

// === Aggregate Statistics Types (Multiple Matches) ===

export interface AssistNetworkAggregate {
  total_assisted_goals: number;
  total_goals: number;
  top_combinations: Array<{
    from_spid: number;
    to_spid: number;
    assists: number;
  }>;
  top_playmakers: Array<{
    spid: number;
    assists: number;
  }>;
  assist_coverage: number;  // Percentage of goals that were assisted
}

export interface HeadingSpecialists {
  total_headers: number;
  heading_goals: number;
  heading_success_rate: number;
  heading_conversion_rate: number;
  cross_dependency: number;  // Percentage of headers that came from assists/crosses
}

export interface ShootingEfficiencyTrend {
  total_shots: number;
  total_goals: number;
  overall_conversion: number;
  accuracy: number;  // Shots on target percentage
  inside_box_shots: number;
  inside_box_goals: number;
  inside_box_efficiency: number;
  outside_box_shots: number;
  outside_box_goals: number;
  outside_box_efficiency: number;
}

export interface PassTypeDistribution {
  avg_short_pass_rate: number;
  avg_long_pass_rate: number;
  avg_through_pass_rate: number;
  matches_analyzed: number;
}

export interface TimeBasedGoalPatterns {
  total_goals: number;
  first_half_goals: number;
  second_half_goals: number;
  early_goals: number;  // 0-30분
  late_goals: number;   // 60-90분
  goal_timing_pattern: 'early_dominant' | 'late_surge' | 'first_half_strong' | 'second_half_strong' | 'balanced' | 'insufficient_data';
}

export interface AggregateStats {
  assist_network?: AssistNetworkAggregate;
  heading_specialists?: HeadingSpecialists;
  shooting_efficiency?: ShootingEfficiencyTrend;
  goal_patterns?: TimeBasedGoalPatterns;
  pass_distribution?: PassTypeDistribution;
}
