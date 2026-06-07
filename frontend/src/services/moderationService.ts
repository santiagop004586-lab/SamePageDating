import api from './api';
import { Photo } from './profileService';

export interface ModerationAction {
  id: number;
  moderator_id?: number;
  target_user_id?: number;
  target_profile_id?: number;
  target_photo_id?: number;
  target_message_id?: number;
  action_type: string;
  reason: string;
  notes?: string;
  duration_days?: number;
  expires_at?: string;
  created_at: string;
}

export interface ModerationActionCreate {
  action_type: string;
  target_user_id?: number;
  target_profile_id?: number;
  target_photo_id?: number;
  target_message_id?: number;
  reason: string;
  notes?: string;
  duration_days?: number;
}

export interface ModerationStats {
  total_users: number;
  active_users: number;
  banned_users: number;
  suspended_users: number;
  flagged_profiles: number;
  flagged_photos: number;
  flagged_messages: number;
  pending_photo_approvals: number;
}

const moderationService = {
  createAction: async (data: ModerationActionCreate): Promise<ModerationAction> => {
    const response = await api.post('/moderation/actions', data);
    return response.data;
  },

  getFlaggedContent: async (contentType?: string): Promise<any[]> => {
    const response = await api.get('/moderation/flagged', {
      params: { content_type: contentType },
    });
    return response.data;
  },

  getPendingPhotos: async (limit: number = 50): Promise<Photo[]> => {
    const response = await api.get('/moderation/pending-photos', {
      params: { limit },
    });
    return response.data;
  },

  getStats: async (): Promise<ModerationStats> => {
    const response = await api.get('/moderation/stats');
    return response.data;
  },

  getActionHistory: async (
    moderatorId?: number,
    targetUserId?: number,
    limit: number = 50
  ): Promise<ModerationAction[]> => {
    const response = await api.get('/moderation/actions/history', {
      params: { moderator_id: moderatorId, target_user_id: targetUserId, limit },
    });
    return response.data;
  },

  approvePhoto: async (photoId: number): Promise<void> => {
    await api.post(`/moderation/photos/${photoId}/approve`);
  },

  flagPhoto: async (photoId: number, reason: string): Promise<void> => {
    await api.post(`/moderation/photos/${photoId}/flag`, { reason });
  },
};

export default moderationService;
