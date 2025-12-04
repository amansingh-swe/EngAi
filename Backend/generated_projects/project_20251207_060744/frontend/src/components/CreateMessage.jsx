import React, { useState } from 'react';
import { apiService } from '../services/api';

function CreateMessage() {
  const [groupId, setGroupId] = useState('');
  const [senderId, setSenderId] = useState('');
  const [content, setContent] = useState('');
  const [mediaUrl, setMediaUrl] = useState(''); // For demonstration, usually this would be from an upload
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    try {
      const response = await apiService.createMessage({ group_id: groupId, sender_id: senderId, content, media_url: mediaUrl || undefined });
      setMessage(`Message sent successfully! Message ID: ${response.message_id}`);
      // Clear form after successful submission
      setGroupId('');
      setSenderId('');
      setContent('');
      setMediaUrl('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h2>Send Message</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Group ID:</label>
          <input type="text" value={groupId} onChange={(e) => setGroupId(e.target.value)} required />
        </div>
        <div>
          <label>Sender ID:</label>
          <input type="text" value={senderId} onChange={(e) => setSenderId(e.target.value)} required />
        </div>
        <div>
          <label>Content:</label>
          <textarea value={content} onChange={(e) => setContent(e.target.value)} required></textarea>
        </div>
        <div>
          <label>Media URL (optional):</label>
          <input type="text" value={mediaUrl} onChange={(e) => setMediaUrl(e.target.value)} />
        </div>
        <button type="submit">Send Message</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default CreateMessage;