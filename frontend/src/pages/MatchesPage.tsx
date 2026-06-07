import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import matchService, { Match } from '../services/matchService';

const MatchesPage: React.FC = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      const data = await matchService.getMatches(1, 50);
      setMatches(data.matches);
    } catch (error) {
      console.error('Error loading matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMatchClick = (match: Match) => {
    navigate(`/chat/${match.id}`);
  };

  if (loading) return <div className="p-8">Loading matches...</div>;

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Your Matches</h1>

      {matches.length === 0 ? (
        <div className="text-center text-gray-600 mt-12">
          <p className="text-xl mb-4">No matches yet!</p>
          <p className="mb-6">Keep swiping to find your perfect match</p>
          <button
            onClick={() => navigate('/discovery')}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
          >
            Start Discovering
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {matches.map((match) => (
            <div
              key={match.id}
              onClick={() => handleMatchClick(match)}
              className="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer overflow-hidden"
            >
              {match.matched_profile?.photo && (
                <img
                  src={match.matched_profile.photo}
                  alt={match.matched_profile.display_name}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-4">
                <h3 className="font-semibold text-lg">
                  {match.matched_profile?.display_name}, {match.matched_profile?.age}
                </h3>
                {match.compatibility_score && (
                  <p className="text-sm text-blue-600 mt-1">
                    {match.compatibility_score}% Compatible
                  </p>
                )}
                <p className="text-sm text-gray-600 mt-2">
                  {match.has_messages ? (
                    <span className="text-green-600">💬 Start chatting</span>
                  ) : (
                    <span className="text-gray-400">Say hi!</span>
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MatchesPage;
