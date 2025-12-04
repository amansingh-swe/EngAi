import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api';

function GetMessages() {
  const { group_id } = useParams();
  const [messages, setMessages] = useState([]);
  const [limit, setLimit] = useState('');
  const [before, setBefore] = useState('');
  const [error, setError] = useState('');

  const fetchMessages = async () => {
    setError('');
    setMessages([]); // Clear previous messages
    const queryParams = {};
    if (limit) queryParams.limit = parseInt(limit, 10);
    if (before) queryParams.before = before;

    try {
      const messageList = await apiService.getMessages(group_id, queryParams);
      setMessages(messageList);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, [group_id]); // Re-fetch if group_id changes

  return (
    <div>
      <h2>Messages for Group: {group_id}</h2>
      <div>
        <label>Limit (optional):</label>
        <input type="number" value={limit} onChange={(e) => setLimit(e.target.value)} />
        <label>Before Message ID (optional):</label>
        <input type="text" value={before} onChange={(e) => setBefore(e.target.value)} />
        <button onClick={fetchMessages}>Fetch Messages</button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {messages.length > 0 ? (
        <ul>
          {messages.map(msg => (
            <li key={msg.message_id} style={{ borderBottom: '1px solid #eee', padding: '10px 0' }}>
              <strong>{msg.sender_id}</strong> ({new Date(msg.timestamp).toLocaleString()}):
              <p>{msg.content}</p>
              {msg.media_url && <img src={msg.media_url} alt="Media" style={{ maxWidth: '200px', maxHeight: '200px' }} />}
            </li>
          ))}
        </ul>
      ) : (
        !error && <p>No messages found or loading...</p>
      )}
    </div>
  );
}

export default GetMessages;