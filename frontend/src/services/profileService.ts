import api from './api';

export interface Profile {
  id: number;
  user_id: number;
  display_name: string;
  date_of_birth: string;
  gender: string;
  bio?: string;
  city?: string;
  state?: string;
  country: string;
  height_cm?: number;
  latitude?: number;
  longitude?: number;
  looking_for_gender: string;
  min_age: number;
  max_age: number;
  max_distance_km: number;
  is_complete: boolean;
  is_active: boolean;
  is_paused: boolean;
  is_verified: boolean;
  is_flagged: boolean;
  is_banned: boolean;
  created_at: string;
  updated_at?: string;
  last_active_at?: string;
  photos: Photo[];
}

export interface Photo {
  id: number;
  url: string;
  thumbnail_url?: string;
  is_primary: boolean;
  order_index: number;
  is_approved: boolean;
  created_at: string;
}

export interface CreateProfileData {
  display_name: string;
  date_of_birth: string;
  gender: string;
  bio?: string;
  city?: string;
  state?: string;
  country?: string;
  height_cm?: number;
  looking_for_gender: string;
  min_age?: number;
  max_age?: number;
  max_distance_km?: number;
}

export interface UpdateProfileData {
  display_name?: string;
  bio?: string;
  city?: string;
  state?: string;
  height_cm?: number;
  looking_for_gender?: string;
  min_age?: number;
  max_age?: number;
  max_distance_km?: number;
  is_active?: boolean;
  is_paused?: boolean;
}

export interface PhotoUploadData {
  url: string;
  is_primary?: boolean;
  order_index?: number;
}

const profileService = {
  createProfile: async (data: CreateProfileData): Promise<Profile> => {
    const response = await api.post('/profile/', data);
    return response.data;
  },

  getMyProfile: async (): Promise<Profile> => {
    const response = await api.get('/profile/me');
    return response.data;
  },

  getProfile: async (profileId: number): Promise<Profile> => {
    const response = await api.get(`/profile/${profileId}`);
    return response.data;
  },

  updateProfile: async (data: UpdateProfileData): Promise<Profile> => {
    const response = await api.patch('/profile/me', data);
    return response.data;
  },

  addPhoto: async (data: PhotoUploadData): Promise<Photo> => {
    const response = await api.post('/profile/me/photos', data);
    return response.data;
  },

  deletePhoto: async (photoId: number): Promise<void> => {
    await api.delete(`/profile/me/photos/${photoId}`);
  },

  getMyPhotos: async (): Promise<Photo[]> => {
    const response = await api.get('/profile/me/photos');
    return response.data;
  },
};

export default profileService;
