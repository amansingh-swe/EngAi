import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

function GroupDetails() {
  const { groupId } = useParams();
  const [group, setGroup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchGroup = async () => {
      setLoading(true);
      setError('');
      try {
        const groupData = await api.getGroupDetails(groupId);
        setGroup(groupData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchGroup();
  }, [groupId]);

  const handleDeleteGroup = async () => {
    if (window.confirm('Are you sure you want to delete this group?')) {
      try {
        await api.deleteGroup(groupId);
        navigate('/groups');
      } catch (err) {
        setError(err.message);
      }
    }
  };

  if (loading) {
    return <div className="loading-indicator">Loading group details...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!group) {
    return <div className="error-message">Group not found.</div>;
  }

  return (
    <div className="group-details-container">
      <h2 className="group-details-title">{group.name}</h2>
      {group.description && <p className="group-details-description">{group.description}</p>}

      <div className="group-details-members-list">
        <h3>Members ({group.members.length})</h3>
        <ul>
          {group.members.map(memberId => (
            <li key={memberId} className="group-member-item">
              <span>{memberId}</span> {/* In a real app, display username */}
              <div className="list-item-actions">
                <Link to={`/groups/${groupId}/remove-member/${memberId}`} className="list-item-link">Remove</Link>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="group-details-messages-list">
        <h3>Messages</h3>
        <div className="card-actions">
          <Link to={`/groups/${groupId}/messages`} className="form-button">View Message History</Link>
          <Link to="/send-message" state={{ groupId: groupId }} className="form-button">Send Message</Link>
        </div>
      </div>

      <div className="group-actions">
        <Link to={`/groups/${groupId}/update`} className="form-button secondary">Edit Group</Link>
        <button onClick={handleDeleteGroup} className="form-button danger">Delete Group</button>
        <Link to={`/groups/${groupId}/add-member`} className="form-button accent">Add Member</Link>
      </div>
    </div>
  );
}

export default GroupDetails;