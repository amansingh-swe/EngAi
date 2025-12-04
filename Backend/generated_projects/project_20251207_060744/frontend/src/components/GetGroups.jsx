import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

function GetGroups() {
  const [groups, setGroups] = useState([]);
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');

  const fetchGroups = async () => {
    setError('');
    if (!userId) {
      setError('Please enter a User ID to fetch groups.');
      return;
    }
    try {
      const groupList = await apiService.getGroups(userId);
      setGroups(groupList);
    } catch (err) {
      setError(err.message);
      setGroups([]);
    }
  };

  useEffect(() => {
    // Optionally fetch groups for a default user ID on mount if available
    // For now, requires manual input
  }, []);

  return (
    <div>
      <h2>Your Groups</h2>
      <div>
        <label>Enter User ID:</label>
        <input type="text" value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="e.g., user123" />
        <button onClick={fetchGroups}>Fetch My Groups</button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {groups.length > 0 ? (
        <ul>
          {groups.map(group => (
            <li key={group.group_id}>
              {group.name} (ID: {group.group_id})
            </li>
          ))}
        </ul>
      ) : (
        !error && <p>No groups found for this user ID or waiting for input.</p>
      )}
    </div>
  );
}

export default GetGroups;