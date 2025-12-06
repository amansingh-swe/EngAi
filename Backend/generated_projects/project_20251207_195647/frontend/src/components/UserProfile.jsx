import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // In a real app, you'd get the user ID from the token or context
  const userId = 'current_user_id'; // Placeholder

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      setError('');
      try {
        // Replace 'current_user_id' with the actual logged-in user's ID
        const userData = await api.getUserProfile(userId);
        setUser(userData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [userId]);

  if (loading) {
    return <div className="loading-indicator">Loading profile...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!user) {
    return <div className="error-message">User profile not found.</div>;
  }

  return (
    <div className="profile-container">
      <h2 className="form-title">User Profile</h2>
      <div className="profile-field">
        <span className="profile-field-label">Username:</span>
        <span className="profile-field-value">{user.username}</span>
      </div>
      <div className="profile-field">
        <span className="profile-field-label">Email:</span>
        <span className="profile-field-value">{user.email}</span>
      </div>
      <div className="profile-field">
        <span className="profile-field-label">Member Since:</span>
        <span className="profile-field-value">{new Date(user.created_at).toLocaleDateString()}</span>
      </div>
      <div className="profile-actions">
        <Link to="/profile/update" className="form-button secondary">Edit Profile</Link>
        <Link to="/profile/delete" className="form-button danger">Delete Account</Link>
      </div>
    </div>
  );
}

export default UserProfile;