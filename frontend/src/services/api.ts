import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// User API
export const searchUser = async (nickname: string) => {
  const response = await apiClient.get(`/users/search/`, {
    params: { nickname }
  });
  return response.data;
};

export const getUserByOuid = async (ouid: string) => {
  const response = await apiClient.get(`/users/${ouid}/`);
  return response.data;
};

export const getUserMatches = async (ouid: string, matchtype: number = 50, limit: number = 10) => {
  const response = await apiClient.get(`/users/${ouid}/matches/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getUserOverview = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/overview/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

// Match API
export const getMatchDetail = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/detail/`, { params });
  return response.data;
};

export const getMatchHeatmap = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/heatmap/`, { params });
  return response.data;
};

export const getPlayerStats = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/player-stats/`, { params });
  return response.data;
};

export const getTimeline = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/timeline/`, { params });
  return response.data;
};

export const getMatchAnalysis = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/analysis/`, { params });
  return response.data;
};

export const getAssistNetwork = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/assist-network/`, { params });
  return response.data;
};

export const getShotTypes = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/shot-types/`, { params });
  return response.data;
};

export const getPassTypes = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/pass-types/`, { params });
  return response.data;
};

export const getHeadingAnalysis = async (matchId: string, ouid?: string | null) => {
  const params = ouid ? { ouid } : {};
  const response = await apiClient.get(`/matches/${matchId}/heading-analysis/`, { params });
  return response.data;
};

// Stats API
export const getUserStats = async (ouid: string, period: string = 'all_time') => {
  const response = await apiClient.get(`/stats/user/${ouid}/`, {
    params: { period }
  });
  return response.data;
};

// Analysis API
export const getShotAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 10) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/shots/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getStyleAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/style/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getUserStatistics = async (ouid: string, matchtype: number = 50, limit: number = 10) => {
  const response = await apiClient.get(`/users/${ouid}/statistics/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getPowerRankings = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/power-rankings/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getPassAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/passes/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getTierInfo = async () => {
  const response = await apiClient.get('/tier-info/');
  return response.data;
};

export const getSetPieceAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/set-pieces/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getDefenseAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/defense/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getPassVarietyAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/pass-variety/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getShootingQualityAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/shooting-quality/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getControllerAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 50) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/controller/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

// Player Search API
export const searchPlayers = async (query: string, limit: number = 20) => {
  const response = await apiClient.get('/search-players/', {
    params: { q: query, limit }
  });
  return response.data;
};

// Advanced Analysis API (Phase 1 & 2)
export const getSkillGapAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/skill-gap/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getPlayerContributionAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 30) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/player-contribution/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getFormCycleAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 50) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/form-cycle/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getRankerGapAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 20) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/ranker-gap/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getHabitLoopAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 30) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/habit-loop/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getOpponentTypesAnalysis = async (ouid: string, matchtype: number = 50, limit: number = 30) => {
  const response = await apiClient.get(`/users/${ouid}/analysis/opponent-types/`, {
    params: { matchtype, limit }
  });
  return response.data;
};

export const getOpponentDNA = async (opponentNickname: string, myNickname?: string) => {
  const params: Record<string, string | number> = {
    opponent_nickname: opponentNickname,
    matchtype: 50,
  };
  if (myNickname) params.my_nickname = myNickname;
  const response = await apiClient.get('/opponent-dna/', { params });
  return response.data;
};

// Visitor Counter API
export const recordVisit = async () => {
  const response = await apiClient.post('/visitor-count/');
  return response.data;
};

export default apiClient;

// Support / Buy Me a Coffee
export interface SupportMessageData {
  name: string;
  email?: string;
  message: string;
  amount?: number;
}

export const sendSupportMessage = async (data: SupportMessageData) => {
  const response = await apiClient.post('/support/', data);
  return response.data;
};
