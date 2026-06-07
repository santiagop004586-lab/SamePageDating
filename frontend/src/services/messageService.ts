import api from './api';

export interface Message {
  id: number;
  match_id: number;
  sender_id: number;
  message_type: string;
  content: string;
  is_read: boolean;
  read_at?: string;
  is_flagged: boolean;
  is_deleted: boolean;
  created_at: string;
}

export interface MessageCreate {
  match_id: number;
  message_type?: 'text' | 'photo' | 'voice' | 'gif';
  content: string;
}

export interface MessageListResponse {
  messages: Message[];
  total: number;
  page: number;
  page_size: number;
}

export interface Conversation {
  match_id: number;
  matched_profile_id: number;
  matched_profile_name: string;
  matched_profile_photo?: string;
  last_message?: Message;
  unread_count: number;
  created_at: string;
}

const messageService = {
  sendMessage: async (data: MessageCreate): Promise<Message> => {
    const response = await api.post('/messages/', data);
    return response.data;
  },

  getConversations: async (): Promise<Conversation[]> => {
    const response = await api.get('/messages/conversations');
    return response.data;
  },

  getConversation: async (
    matchId: number,
    page: number = 1,
    pageSize: number = 50
  ): Promise<MessageListResponse> => {
    const response = await api.get(`/messages/match/${matchId}`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  markRead: async (messageIds: number[]): Promise<void> => {
    await api.post('/messages/read', { message_ids: messageIds });
  },

  getUnreadCount: async (matchId: number): Promise<number> => {
    const response = await api.get(`/messages/match/${matchId}/unread-count`);
    return response.data.unread_count;
  },

  deleteMessage: async (messageId: number): Promise<void> => {
    await api.delete(`/messages/${messageId}`);
  },

  flagMessage: async (messageId: number): Promise<void> => {
    await api.post(`/messages/${messageId}/flag`);
  },
};

export default messageService;
