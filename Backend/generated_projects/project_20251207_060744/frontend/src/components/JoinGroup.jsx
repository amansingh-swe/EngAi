import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api';

function JoinGroup() {
  const { group_id } = useParams();
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleJoin = async () => {
    setError('');
    setMessage('');
    try {
      const response = await apiService.joinGroup(group_id);
      setMessage(response.message);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h2>Join Group</h2>
      <p>Are you sure you want to join group: <strong>{group_id}</strong>?</p>
      <button onClick={handleJoin}>Join Group</button>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default JoinGroup;