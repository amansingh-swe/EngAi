import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

function AddMemberForm() {
  const { groupId } = useParams();
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const result = await api.addMemberToGroup(groupId, userId);
      setSuccess(`Member ${userId} added successfully!`);
      setTimeout(() => navigate(`/groups/${groupId}`), 2000);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Add Member to Group</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="memberUserId" className="form-label">User ID to Add</label>
          <input
            type="text"
            id="memberUserId"
            className="form-input"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
            placeholder="Enter User ID"
          />
        </div>
        <button type="submit" className="form-button">Add Member</button>
        <button type="button" className="form-button secondary" onClick={() => navigate(`/groups/${groupId}`)} style={{ marginLeft: '10px' }}>Cancel</button>
      </form>
    </div>
  );
}

export default AddMemberForm;