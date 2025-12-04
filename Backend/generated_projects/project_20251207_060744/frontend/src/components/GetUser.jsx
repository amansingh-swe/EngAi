import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api';

function GetUser() {
  const { user_id } = useParams();
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      setError('');
      try {
        const userData = await apiService.getUser(user_id);
        setUser(userData);
      } catch (err) {
        setError(err.message);
        setUser(null);
      }
    };
    fetchUser();
  }, [user_id]);

  return (
    <div>
      <h2>User Details</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {user ? (
        <div>
          <p><strong>User ID:</strong> {user.user_id}</p>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Online:</strong> {user.is_online ? 'Yes' : 'No'}</p>
        </div>
      ) : (
        !error && <p>Loading user data...</p>
      )}
    </div>
  );
}

export default GetUser;