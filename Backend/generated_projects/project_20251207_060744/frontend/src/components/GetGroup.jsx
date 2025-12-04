import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api';

function GetGroup() {
  const { group_id } = useParams();
  const [group, setGroup] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchGroup = async () => {
      setError('');
      try {
        const groupData = await apiService.getGroup(group_id);
        setGroup(groupData);
      } catch (err) {
        setError(err.message);
        setGroup(null);
      }
    };
    fetchGroup();
  }, [group_id]);

  return (
    <div>
      <h2>Group Details</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {group ? (
        <div>
          <p><strong>Group ID:</strong> {group.group_id}</p>
          <p><strong>Name:</strong> {group.name}</p>
          <p><strong>Description:</strong> {group.description}</p>
          <p><strong>Members:</strong></p>
          <ul>
            {group.members.map((memberId, index) => (
              <li key={index}>{memberId}</li>
            ))}
          </ul>
        </div>
      ) : (
        !error && <p>Loading group data...</p>
      )}
    </div>
  );
}

export default GetGroup;