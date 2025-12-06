import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function UpdateUserProfileForm() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  // In a real app, you'd get the user ID from the token or context
  const userId = 'current_user_id'; // Placeholder

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const userData = await api.getUserProfile(userId);
        setUsername(userData.username);
        setEmail(userData.email);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchProfile();
  }, [userId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const updatedData = await api.updateUserProfile(userId, { username, email });
      setSuccess(updatedData.message);
      setTimeout(() => navigate('/profile'), 2000);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Update Profile</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username" className="form-label">Username</label>
          <input
            type="text"
            id="username"
            className="form-input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="email" className="form-label">Email</label>
          <input
            type="email"
            id="email"
            className="form-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="form-button">Update Profile</button>
        <button type="button" className="form-button secondary" onClick={() => navigate('/profile')} style={{ marginLeft: '10px' }}>Cancel</button>
      </form>
    </div>
  );
}

export default UpdateUserProfileForm;