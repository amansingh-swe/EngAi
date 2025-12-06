import React, { useState, useEffect, useRef } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';

function MessageHistory() {
  const { groupId } = useParams();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const messagesEndRef = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();

  const messagesPerPage = 20; // Number of messages to fetch per page

  const fetchMessages = async (currentPage) => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getGroupMessages(groupId, {
        limit: messagesPerPage,
        offset: currentPage * messagesPerPage,
      });
      setMessages(prevMessages => [...data.messages.reverse(), ...prevMessages]); // Prepend new messages
      setHasMore(data.messages.length === messagesPerPage);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages(page);
  }, [groupId, page]); // Re-fetch if groupId or page changes

  useEffect(() => {
    // Scroll to bottom when new messages are loaded or component mounts
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleScroll = (e) => {
    if (e.target.scrollTop === 0 && hasMore && !loading) {
      setPage(prevPage => prevPage + 1);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Check if navigated from SendMessageForm to scroll to bottom
  useEffect(() => {
    if (location.state?.scrollToBottom) {
      scrollToBottom();
      // Clear the state to avoid scrolling on subsequent renders
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location.state, navigate]);


  if (loading && messages.length === 0) { // Only show full loading if no messages yet
    return <div className="loading-indicator">Loading messages...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="message-history-container">
      <h2 className="message-history-title">Message History</h2>
      <div className="message-list" onScroll={handleScroll}>
        {loading && messages.length > 0 && <div className="loading-indicator">Loading more messages...</div>}
        {messages.map((msg, index) => (
          <div key={msg.message_id || index} className={`message-item ${msg.sender_id === 'current_user_id' ? 'own' : ''}`}>
            <div className="message-sender">{msg.sender_id}</div> {/* Display username if available */}
            <div className="message-content">
              {msg.content}
              {msg.media_url && (
                <div className="message-media">
                  <img src={msg.media_url} alt="Media" />
                </div>
              )}
            </div>
            <div className="message-timestamp">{new Date(msg.timestamp).toLocaleString()}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="card-actions">
        <button onClick={() => navigate('/send-message', { state: { groupId: groupId } })} className="form-button">Send Message</button>
        <button onClick={() => navigate(`/groups/${groupId}`)} className="form-button secondary">Back to Group</button>
      </div>
    </div>
  );
}

export default MessageHistory;