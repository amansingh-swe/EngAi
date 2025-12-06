import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

function DeleteGroup() {
  const { groupId } = useParams();
  const [error, setError] = useState('');
  const [confirm, setConfirm] = useState(false);
  const navigate = useNavigate();

  const handleDelete = async () => {
    setError('');
    try {
      await api.deleteGroup(groupId);
      navigate('/groups'); // Redirect to group list after deletion
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Delete Group</h2>
      {error && <p className="error-message">{error}</p>}
      {!confirm ? (
        <>
          <p>Are you sure you want to delete this group? This action cannot be undone.</p>
          <button type="button" className="form-button danger" onClick={() => setConfirm(true)}>Delete Group</button>
          <button type="button" className="form-button secondary" onClick={() => navigate(`/groups/${groupId}`)} style={{ marginLeft: '10px' }}>Cancel</button>
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

export default DeleteGroup;