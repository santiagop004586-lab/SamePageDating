import api from './api';

export interface Match {
  id: number;
  profile1_id: number;
  profile2_id: number;
  compatibility_score?: number;
  has_messages: boolean;
  last_message_at?: string;
  is_active: boolean;
  created_at: string;
  matched_profile?: {
    id: number;
    display_name: string;
    age: number;
    photo?: string;
  };
}

export interface MatchListResponse {
  matches: Match[];
  total: number;
  page: number;
  page_size: number;
}

export interface MatchStats {
  total_matches: number;
  matches_with_messages: number;
  matches_no_messages: number;
}

const matchService = {
  getMatches: async (page: number = 1, pageSize: number = 20): Promise<MatchListResponse> => {
    const response = await api.get('/matches/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getMatch: async (matchId: number): Promise<Match> => {
    const response = await api.get(`/matches/${matchId}`);
    return response.data;
  },

  unmatch: async (matchId: number, reason?: string): Promise<void> => {
    await api.post(`/matches/${matchId}/unmatch`, { reason });
  },

  getStats: async (): Promise<MatchStats> => {
    const response = await api.get('/matches/stats/me');
    return response.data;
  },
};

export default matchService;
