// Advanced Analysis Types for Phase 2 Week 3

// Set Piece Analysis
export interface FreekickAnalysis {
  shots: number;
  goals: number;
  conversion_rate: number;
}

export interface PenaltyAnalysis {
  shots: number;
  goals: number;
  conversion_rate: number;
}

export interface HeadingAnalysis {
  shots: number;
  goals: number;
  conversion_rate: number;
}

export interface SetPieceOverall {
  set_piece_goals: number;
  total_goals: number;
  set_piece_dependency: number;
  style: string;
}

export interface SetPieceAnalysisData {
  matchtype: number;
  matches_analyzed: number;
  freekick_analysis: FreekickAnalysis;
  penalty_analysis: PenaltyAnalysis;
  heading_analysis: HeadingAnalysis;
  overall: SetPieceOverall;
  insights: Insights;
}

// Defense Analysis
export interface TackleStats {
  total_attempts: number;
  total_success: number;
  success_rate: number;
  per_game: number;
}

export interface BlockStats {
  total_attempts: number;
  total_success: number;
  success_rate: number;
  per_game: number;
}

export interface DefenseOverall {
  defensive_intensity: number;
  defensive_style: string;
  matches_analyzed: number;
}

export interface DefenseAnalysisData {
  matchtype: number;
  matches_analyzed: number;
  tackle_stats: TackleStats;
  block_stats: BlockStats;
  overall: DefenseOverall;
  insights: Insights;
}

// Pass Variety Analysis
export interface PassTypeStats {
  attempts: number;
  success: number;
  success_rate: number;
  ratio: number;
}

export interface PassDistribution {
  short_passes: PassTypeStats;
  long_passes: PassTypeStats;
  through_passes: PassTypeStats;
}

export interface SpecialPassStats {
  attempts: number;
  success: number;
  success_rate: number;
}

export interface SpecialPasses {
  lobbed_through: SpecialPassStats;
  driven_ground: SpecialPassStats;
}

export interface PassVarietyOverall {
  diversity_index: number;
  buildup_style: string;
  total_passes: number;
  overall_accuracy: number;
  matches_analyzed: number;
}

export interface PassVarietyAnalysisData {
  matchtype: number;
  matches_analyzed: number;
  pass_distribution: PassDistribution;
  special_passes: SpecialPasses;
  overall: PassVarietyOverall;
  insights: Insights;
}

// Shooting Quality Analysis
export interface LocationShootingStats {
  shots: number;
  goals: number;
  conversion_rate: number;
  ratio: number;
}

export interface LocationAnalysis {
  inside_box: LocationShootingStats;
  outside_box: LocationShootingStats;
}

export interface ShotTypeAnalysis {
  heading: {
    shots: number;
    goals: number;
    conversion_rate: number;
    ratio: number;
  };
  total_shots: number;
  effective_shots: number;
  shot_on_target_rate: number;
}

export interface ShootingQualityOverall {
  conversion_rate: number;
  clinical_rating: number;
  shooting_style: string;
  shots_per_game: number;
  goals_per_game: number;
  matches_analyzed: number;
}

export interface ShootingQualityAnalysisData {
  matchtype: number;
  matches_analyzed: number;
  location_analysis: LocationAnalysis;
  shot_type_analysis: ShotTypeAnalysis;
  overall: ShootingQualityOverall;
  insights: Insights;
}

// Common Insights Structure
export interface Insights {
  keep: string[];
  stop: string[];
  action_items: string[];
}
