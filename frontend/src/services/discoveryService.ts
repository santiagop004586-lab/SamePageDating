import api from './api';
import { Photo } from './profileService';

export interface DiscoveryProfile {
  id: number;
  display_name: string;
  age: number;
  bio?: string;
  city?: string;
  state?: string;
  distance_km?: number;
  photos: Photo[];
  compatibility_score?: number;
  is_verified: boolean;
}

export interface SwipeAction {
  target_profile_id: number;
  action: 'like' | 'pass' | 'super_like' | 'save';
}

export interface MatchNotification {
  is_match: boolean;
  match_id?: number;
  profile?: {
    id: number;
    display_name: string;
    age: number;
    photos: Photo[];
  };
}

export interface Swipe {
  id: number;
  swiper_id: number;
  swiped_id: number;
  action: string;
  is_match: boolean;
  created_at: string;
}

const discoveryService = {
  getDiscoveryFeed: async (limit: number = 10, offset: number = 0): Promise<DiscoveryProfile[]> => {
    const response = await api.get('/api/v1/discovery/feed', {
      params: { limit, offset },
    });
    return response.data;
  },

  swipe: async (action: SwipeAction): Promise<MatchNotification> => {
    const response = await api.post('/api/v1/discovery/swipe', action);
    return response.data;
  },

  getSwipeHistory: async (action?: string, limit: number = 50): Promise<Swipe[]> => {
    const response = await api.get('/api/v1/discovery/swipes/history', {
      params: { action, limit },
    });
    return response.data;
  },
};

export default discoveryService;
