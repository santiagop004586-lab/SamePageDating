import React, { useState, useEffect } from 'react';
import discoveryService, { DiscoveryProfile, MatchNotification } from '../services/discoveryService';

const DiscoveryPage: React.FC = () => {
  const [profiles, setProfiles] = useState<DiscoveryProfile[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [matchNotification, setMatchNotification] = useState<MatchNotification | null>(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const data = await discoveryService.getDiscoveryFeed(10);
      setProfiles(data);
      setCurrentIndex(0);
    } catch (error) {
      console.error('Error loading profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (action: 'like' | 'pass' | 'super_like') => {
    if (currentIndex >= profiles.length) return;

    const profile = profiles[currentIndex];
    
    try {
      const result = await discoveryService.swipe({
        target_profile_id: profile.id,
        action,
      });

      if (result.is_match) {
        setMatchNotification(result);
      }

      // Move to next profile
      if (currentIndex < profiles.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        // Load more profiles
        await loadProfiles();
      }
    } catch (error) {
      console.error('Error swiping:', error);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (profiles.length === 0) return <div className="p-8 text-center">No more profiles to show. Check back later!</div>;

  const profile = profiles[currentIndex];

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Discover</h1>

      {matchNotification && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-lg max-w-md text-center">
            <h2 className="text-2xl font-bold mb-4">🎉 It's a Match!</h2>
            <p className="mb-6">You and {matchNotification.profile?.display_name} liked each other!</p>
            <button
              onClick={() => setMatchNotification(null)}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Photo carousel */}
        <div className="h-96 bg-gray-200 relative">
          {profile.photos.length > 0 ? (
            <img
              src={profile.photos[0].url}
              alt={profile.display_name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              No photo
            </div>
          )}
          
          {/* Compatibility score badge */}
          {profile.compatibility_score !== undefined && (
            <div className="absolute top-4 right-4 bg-white rounded-full px-4 py-2 shadow">
              <span className="font-bold text-blue-600">{profile.compatibility_score}%</span>
              <span className="text-xs text-gray-600 ml-1">Match</span>
            </div>
          )}
        </div>

        {/* Profile info */}
        <div className="p-6">
          <div className="flex items-center gap-2 mb-2">
            <h2 className="text-2xl font-bold">{profile.display_name}, {profile.age}</h2>
            {profile.is_verified && (
              <span className="text-blue-600">✓</span>
            )}
          </div>
          
          {profile.city && profile.state && (
            <p className="text-gray-600 mb-2">
              📍 {profile.city}, {profile.state}
              {profile.distance_km && ` • ${Math.round(profile.distance_km)} km away`}
            </p>
          )}

          {profile.bio && (
            <p className="text-gray-700 mt-4">{profile.bio}</p>
          )}
        </div>

        {/* Action buttons */}
        <div className="p-6 flex justify-center gap-4 border-t">
          <button
            onClick={() => handleSwipe('pass')}
            className="w-16 h-16 rounded-full bg-white border-2 border-gray-300 flex items-center justify-center hover:border-red-500 hover:text-red-500 transition"
          >
            ✕
          </button>
          <button
            onClick={() => handleSwipe('super_like')}
            className="w-16 h-16 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 transition"
          >
            ★
          </button>
          <button
            onClick={() => handleSwipe('like')}
            className="w-16 h-16 rounded-full bg-white border-2 border-gray-300 flex items-center justify-center hover:border-green-500 hover:text-green-500 transition"
          >
            ♥
          </button>
        </div>
      </div>
    </div>
  );
};

export default DiscoveryPage;
