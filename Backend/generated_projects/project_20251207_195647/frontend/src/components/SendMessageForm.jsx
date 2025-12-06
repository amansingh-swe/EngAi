import React, { useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';

function SendMessageForm() {
  const [content, setContent] = useState('');
  const [mediaFile, setMediaFile] = useState(null);
  const [mediaUrl, setMediaUrl] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const groupId = location.state?.groupId;
  const fileInputRef = useRef(null);

  const handleMediaChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setMediaFile(file);
      setMediaUrl(URL.createObjectURL(file)); // Create a temporary URL for preview
    }
  };

  const handleUploadMedia = async () => {
    if (!mediaFile) return null;
    try {
      const response = await api.uploadMedia(mediaFile);
      return response.media_url;
    } catch (err) {
      setError(`Media upload failed: ${err.message}`);
      return null;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!groupId) {
      setError('Group ID is missing. Please select a group first.');
      return;
    }

    let uploadedMediaUrl = mediaUrl;
    if (mediaFile) {
      uploadedMediaUrl = await handleUploadMedia();
      if (!uploadedMediaUrl) {
        return; // Stop if media upload failed
      }
    }

    try {
      const messageData = {
        group_id: groupId,
        content: content,
        media_url: uploadedMediaUrl || undefined, // Send only if a URL exists
      };
      const newMessage = await api.sendMessage(messageData);
      setSuccess('Message sent!');
      setContent('');
      setMediaFile(null);
      setMediaUrl('');
      if (fileInputRef.current) {
        fileInputRef.current.value = ''; // Clear file input
      }
      // Navigate to message history and trigger scroll to bottom
      navigate(`/groups/${groupId}/messages`, { state: { scrollToBottom: true } });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Send Message</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      {!groupId && <p className="error-message">Please select a group to send a message.</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="messageContent" className="form-label">Message</label>
          <textarea
            id="messageContent"
            className="form-textarea"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows="4"
            required
            disabled={!groupId}
          />
        </div>
        <div className="form-group">
          <label htmlFor="mediaUpload" className="form-label">Attach Media (Optional)</label>
          <input
            type="file"
            id="mediaUpload"
            className="form-input"
            onChange={handleMediaChange}
            ref={fileInputRef}
            disabled={!groupId}
          />
          {mediaUrl && (
            <div className="media-upload-preview">
              <p>Preview:</p>
              <img src={mediaUrl} alt="Media Preview" style={{ maxWidth: '200px', height: 'auto', marginTop: '5px' }} />
            </div>
          )}
        </div>
        <button type="submit" className="form-button" disabled={!groupId}>Send Message</button>
        <button type="button" className="form-button secondary" onClick={() => navigate(groupId ? `/groups/${groupId}` : '/groups')} style={{ marginLeft: '10px' }}>Cancel</button>
      </form>
    </div>
  );
}

export default SendMessageForm;