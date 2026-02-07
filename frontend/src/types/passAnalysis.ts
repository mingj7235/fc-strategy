export interface PassOverallStats {
  total_attempts: number;
  total_success: number;
  accuracy: number;
}

export interface KeyPassAnalysis {
  total_assists: number;
  estimated_key_passes: number;
  estimated_xa: number;
  xa_per_key_pass: number;
  conversion_rate: number;
}

export interface ProgressivePassing {
  estimated_progressive_passes: number;
  progressive_rate: number;
  midfielder_contribution: number;
}

export interface TopPasser {
  player_name: string;
  pass_attempts: number;
  pass_success: number;
  pass_success_rate: number;
  spid?: number;
  image_url?: string;
  season_name?: string;
  season_img?: string;
}

export interface PassNetwork {
  top_passers: TopPasser[];
  total_connections: number;
  avg_passes_per_player: number;
}

export interface PassEfficiency {
  passes_per_assist: number;
  assist_rate: number;
  risk_reward_profile: 'balanced' | 'aggressive' | 'conservative' | 'unknown';
  efficiency_score: number;
}

export interface PassInsights {
  keep: string[];
  stop: string[];
  action_items: string[];
}

export interface PassAnalysisData {
  matchtype: number;
  matches_analyzed: number;
  overall_stats: PassOverallStats;
  key_pass_analysis: KeyPassAnalysis;
  progressive_passing: ProgressivePassing;
  pass_network: PassNetwork;
  efficiency: PassEfficiency;
  insights: PassInsights;
}
