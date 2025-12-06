import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function CreateGroupForm() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [memberIds, setMemberIds] = useState(''); // Comma-separated string
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const membersArray = memberIds.split(',').map(id => id.trim()).filter(id => id);

    try {
      const newGroup = await api.createGroup({ name, description, member_ids: membersArray });
      setSuccess(`Group "${newGroup.name}" created successfully!`);
      setTimeout(() => navigate(`/groups/${newGroup.group_id}`), 2000);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Create New Group</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="groupName" className="form-label">Group Name</label>
          <input
            type="text"
            id="groupName"
            className="form-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="groupDescription" className="form-label">Description (Optional)</label>
          <textarea
            id="groupDescription"
            className="form-textarea"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="3"
          />
        </div>
        <div className="form-group">
          <label htmlFor="memberIds" className="form-label">Initial Member IDs (Optional, comma-separated)</label>
          <input
            type="text"
            id="memberIds"
            className="form-input"
            value={memberIds}
            onChange={(e) => setMemberIds(e.target.value)}
            placeholder="e.g., user123,user456"
          />
        </div>
        <button type="submit" className="form-button">Create Group</button>
        <button type="button" className="form-button secondary" onClick={() => navigate('/groups')} style={{ marginLeft: '10px' }}>Cancel</button>
      </form>
    </div>
  );
}

export default CreateGroupForm;