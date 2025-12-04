import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiService } from '../services/api';

function UpdateUser() {
  const { user_id } = useParams();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Fetch current user data to pre-fill the form
  useEffect(() => {
    const fetchUserData = async () => {
      setError('');
      try {
        const userData = await apiService.getUser(user_id);
        setUsername(userData.username);
        setEmail(userData.email);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchUserData();
  }, [user_id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    const updateData = {};
    if (username) updateData.username = username;
    if (email) updateData.email = email;

    try {
      const response = await apiService.updateUser(user_id, updateData);
      setMessage(`User updated successfully! Username: ${response.username}, Email: ${response.email}`);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h2>Update User</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username (optional):</label>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div>
          <label>Email (optional):</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <button type="submit">Update User</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
    </div>
  );
}

export default UpdateUser;