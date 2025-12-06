import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

function GroupList() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchGroups = async () => {
      setLoading(true);
      setError('');
      try {
        // Optionally filter by logged-in user if API supports it
        // const userId = 'current_user_id'; // Get from auth context/storage
        // const data = await api.getAllGroups(userId);
        const data = await api.getAllGroups();
        setGroups(data.groups);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchGroups();
  }, []);

  if (loading) {
    return <div className="loading-indicator">Loading groups...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div>
      <div className="card-actions" style={{ marginBottom: '2rem' }}>
        <Link to="/groups/create" className="form-button">Create New Group</Link>
      </div>
      <div className="list-container">
        {groups.length > 0 ? (
          groups.map(group => (
            <div key={group.group_id} className="list-item">
              <h3 className="list-item-title">{group.name}</h3>
              <p className="list-item-description">{group.description || 'No description'}</p>
              <p className="card-text">Members: {group.members.length}</p>
              <div className="list-item-actions">
                <Link to={`/groups/${group.group_id}`} className="list-item-link">View</Link>
              </div>
            </div>
          ))
        ) : (
          <p>No groups found. Create one to get started!</p>
        )}
      </div>
    </div>
  );
}

export default GroupList;