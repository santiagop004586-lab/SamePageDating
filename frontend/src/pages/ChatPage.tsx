import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import messageService, { Message, Conversation } from '../services/messageService';
import matchService from '../services/matchService';

const ChatPage: React.FC = () => {
  const { matchId } = useParams<{ matchId: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [match, setMatch] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (matchId) {
      loadMatch();
      loadMessages();
    }
  }, [matchId]);

  const loadMatch = async () => {
    try {
      const data = await matchService.getMatch(parseInt(matchId!));
      setMatch(data);
    } catch (error) {
      console.error('Error loading match:', error);
    }
  };

  const loadMessages = async () => {
    try {
      const data = await messageService.getConversation(parseInt(matchId!), 1, 100);
      setMessages(data.messages);
      
      // Mark messages as read
      const unreadIds = data.messages
        .filter((m) => !m.is_read && m.sender_id !== match?.profile1_id)
        .map((m) => m.id);
      
      if (unreadIds.length > 0) {
        await messageService.markRead(unreadIds);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      await messageService.sendMessage({
        match_id: parseInt(matchId!),
        content: newMessage,
      });
      setNewMessage('');
      await loadMessages();
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  if (loading) return <div className="p-8">Loading conversation...</div>;

  return (
    <div className="max-w-4xl mx-auto h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b p-4">
        <h2 className="text-xl font-semibold">
          {match?.matched_profile?.display_name}
          {match?.compatibility_score && (
            <span className="text-sm text-blue-600 ml-2">
              {match.compatibility_score}% Compatible
            </span>
          )}
        </h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-12">
            <p className="text-lg mb-2">No messages yet</p>
            <p className="text-sm">Send the first message to break the ice!</p>
          </div>
        ) : (
          messages.map((message) => {
            const isOwnMessage = message.sender_id === match?.profile1_id;
            return (
              <div
                key={message.id}
                className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    isOwnMessage
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-900'
                  }`}
                >
                  <p>{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      isOwnMessage ? 'text-blue-200' : 'text-gray-500'
                    }`}
                  >
                    {new Date(message.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="bg-white border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 border rounded-full px-4 py-2 focus:outline-none focus:border-blue-600"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-full hover:bg-blue-700"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatPage;
