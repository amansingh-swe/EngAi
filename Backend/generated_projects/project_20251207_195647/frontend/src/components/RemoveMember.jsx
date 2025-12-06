import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

function RemoveMember() {
  const { groupId, userId } = useParams();
  const [error, setError] = useState('');
  const [confirm, setConfirm] = useState(false);
  const navigate = useNavigate();

  const handleRemove = async () => {
    setError('');
    try {
      await api.removeMemberFromGroup(groupId, userId);
      navigate(`/groups/${groupId}`); // Redirect back to group details
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Remove Member</h2>
      {error && <p className="error-message">{error}</p>}
      {!confirm ? (
        <>
          <p>Are you sure you want to remove user <strong>{userId}</strong> from this group?</p>
          <button type="button" className="form-button danger" onClick={() => setConfirm(true)}>Remove Member</button>
          <button type="button" className="form-button secondary" onClick={() => navigate(`/groups/${groupId}`)} style={{ marginLeft: '10px' }}>Cancel</button>
        </>
      ) : (
        <>
          <p>Please confirm by typing "REMOVE" below:</p>
          <input
            type="text"
            className="form-input"
            onChange={(e) => {
              if (e.target.value === "REMOVE") {
                handleRemove();
              }
            }}
          />
        </>
      )}
    </div>
  );
}

export default RemoveMember;