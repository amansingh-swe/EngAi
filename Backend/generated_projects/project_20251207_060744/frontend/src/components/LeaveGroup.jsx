import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api';

function LeaveGroup() {
  const { group_id } = useParams();
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleLeave = async () => {
    setError('');
    setMessage('');
    try {
      const response = await apiService.leaveGroup(group_id);
      setMessage(response.message);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h2>Leave Group</h2>
      <p>Are you sure you want to leave group: <strong>{group_id}</strong>?</p>
      <button onClick={handleLeave}>Leave Group</button>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default LeaveGroup;