import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

function UpdateGroupForm() {
  const { groupId } = useParams();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchGroup = async () => {
      try {
        const groupData = await api.getGroupDetails(groupId);
        setName(groupData.name);
        setDescription(groupData.description);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchGroup();
  }, [groupId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const updatedGroup = await api.updateGroup(groupId, { name, description });
      setSuccess(`Group "${updatedGroup.updated_group.name}" updated successfully!`);
      setTimeout(() => navigate(`/groups/${groupId}`), 2000);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Update Group</h2>
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
          <label htmlFor="groupDescription" className="form-label">Description</label>
          <textarea
            id="groupDescription"
            className="form-textarea"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="3"
          />
        </div>
        <button type="submit" className="form-button">Update Group</button>
        <button type="button" className="form-button secondary" onClick={() => navigate(`/groups/${groupId}`)} style={{ marginLeft: '10px' }}>Cancel</button>
      </form>
    </div>
  );
}

export default UpdateGroupForm;