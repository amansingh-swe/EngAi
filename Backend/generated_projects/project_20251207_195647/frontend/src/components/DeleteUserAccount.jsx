import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function DeleteUserAccount() {
  const [error, setError] = useState('');
  const [confirm, setConfirm] = useState(false);
  const navigate = useNavigate();

  // In a real app, you'd get the user ID from the token or context
  const userId = 'current_user_id'; // Placeholder

  const handleDelete = async () => {
    setError('');
    try {
      await api.deleteUserAccount(userId);
      localStorage.removeItem('token'); // Clear token on logout
      navigate('/login'); // Redirect to login after deletion
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Delete Account</h2>
      {error && <p className="error-message">{error}</p>}
      {!confirm ? (
        <>
          <p>Are you sure you want to delete your account? This action cannot be undone.</p>
          <button type="button" className="form-button danger" onClick={() => setConfirm(true)}>Delete Account</button>
          <button type="button" className="form-button secondary" onClick={() => navigate('/profile')} style={{ marginLeft: '10px' }}>Cancel</button>
        </>
      ) : (
        <>
          <p>Please confirm by typing "DELETE" below:</p>
          <input
            type="text"
            className="form-input"
            onChange={(e) => {
              if (e.target.value === "DELETE") {
                handleDelete();
              }
            }}
          />
        </>
      )}
    </div>
  );
}

export default DeleteUserAccount;