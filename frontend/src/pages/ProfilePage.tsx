import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import profileService, { Profile, CreateProfileData, UpdateProfileData } from '../services/profileService';

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    display_name: '',
    date_of_birth: '',
    gender: 'male',
    bio: '',
    city: '',
    state: '',
    height_cm: '',
    looking_for_gender: '',
    min_age: 18,
    max_age: 99,
    max_distance_km: 50,
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await profileService.getMyProfile();
      setProfile(data);
      setFormData({
        display_name: data.display_name,
        date_of_birth: data.date_of_birth,
        gender: data.gender,
        bio: data.bio || '',
        city: data.city || '',
        state: data.state || '',
        height_cm: data.height_cm?.toString() || '',
        looking_for_gender: data.looking_for_gender,
        min_age: data.min_age,
        max_age: data.max_age,
        max_distance_km: data.max_distance_km,
      });
    } catch (error: any) {
      if (error.response?.status === 404) {
        setIsEditing(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (profile) {
        const updateData: UpdateProfileData = {
          display_name: formData.display_name,
          bio: formData.bio,
          city: formData.city,
          state: formData.state,
          height_cm: formData.height_cm ? parseInt(formData.height_cm) : undefined,
          looking_for_gender: formData.looking_for_gender,
          min_age: formData.min_age,
          max_age: formData.max_age,
          max_distance_km: formData.max_distance_km,
        };
        await profileService.updateProfile(updateData);
      } else {
        const createData: CreateProfileData = {
          display_name: formData.display_name,
          date_of_birth: formData.date_of_birth,
          gender: formData.gender,
          bio: formData.bio,
          city: formData.city,
          state: formData.state,
          height_cm: formData.height_cm ? parseInt(formData.height_cm) : undefined,
          looking_for_gender: formData.looking_for_gender,
          min_age: formData.min_age,
          max_age: formData.max_age,
          max_distance_km: formData.max_distance_km,
        };
        await profileService.createProfile(createData);
      }
      await loadProfile();
      setIsEditing(false);
      navigate('/compatibility-questionnaire');
    } catch (error) {
      console.error('Error saving profile:', error);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Your Profile</h1>

      {!isEditing && profile ? (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold">{profile.display_name}</h2>
            <p className="text-gray-600">{profile.bio}</p>
            <div className="mt-4 space-y-2">
              <p><strong>Location:</strong> {profile.city}, {profile.state}</p>
              <p><strong>Gender:</strong> {profile.gender}</p>
              <p><strong>Looking for:</strong> {profile.looking_for_gender}</p>
              <p><strong>Age range:</strong> {profile.min_age} - {profile.max_age}</p>
              <p><strong>Max distance:</strong> {profile.max_distance_km} km</p>
            </div>
          </div>
          <button
            onClick={() => setIsEditing(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
          >
            Edit Profile
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-medium mb-1">Display Name *</label>
            <input
              type="text"
              value={formData.display_name}
              onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
              required
              className="w-full border px-3 py-2 rounded"
            />
          </div>

          {!profile && (
            <div>
              <label className="block font-medium mb-1">Date of Birth *</label>
              <input
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                required
                className="w-full border px-3 py-2 rounded"
              />
            </div>
          )}

          {!profile && (
            <div>
              <label className="block font-medium mb-1">Gender *</label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                required
                className="w-full border px-3 py-2 rounded"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="non_binary">Non-binary</option>
                <option value="other">Other</option>
              </select>
            </div>
          )}

          <div>
            <label className="block font-medium mb-1">Bio</label>
            <textarea
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              rows={4}
              className="w-full border px-3 py-2 rounded"
              placeholder="Tell us about yourself..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-medium mb-1">City</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="w-full border px-3 py-2 rounded"
              />
            </div>
            <div>
              <label className="block font-medium mb-1">State</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                className="w-full border px-3 py-2 rounded"
              />
            </div>
          </div>

          <div>
            <label className="block font-medium mb-1">Looking for</label>
            <input
              type="text"
              value={formData.looking_for_gender}
              onChange={(e) => setFormData({ ...formData, looking_for_gender: e.target.value })}
              placeholder="e.g., male, female, or both"
              className="w-full border px-3 py-2 rounded"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-medium mb-1">Min Age</label>
              <input
                type="number"
                value={formData.min_age}
                onChange={(e) => setFormData({ ...formData, min_age: parseInt(e.target.value) })}
                className="w-full border px-3 py-2 rounded"
              />
            </div>
            <div>
              <label className="block font-medium mb-1">Max Age</label>
              <input
                type="number"
                value={formData.max_age}
                onChange={(e) => setFormData({ ...formData, max_age: parseInt(e.target.value) })}
                className="w-full border px-3 py-2 rounded"
              />
            </div>
          </div>

          <div>
            <label className="block font-medium mb-1">Max Distance (km)</label>
            <input
              type="number"
              value={formData.max_distance_km}
              onChange={(e) => setFormData({ ...formData, max_distance_km: parseInt(e.target.value) })}
              className="w-full border px-3 py-2 rounded"
            />
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              {profile ? 'Update Profile' : 'Create Profile'}
            </button>
            {profile && (
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="bg-gray-500 text-white px-6 py-2 rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      )}
    </div>
  );
};

export default ProfilePage;
