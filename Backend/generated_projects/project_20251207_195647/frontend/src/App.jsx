import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate } from 'react-router-dom';
import api from './services/api';

// --- Component Imports ---
import RegisterForm from './components/RegisterForm';
import LoginForm from './components/LoginForm';
import UserProfile from './components/UserProfile';
import UpdateUserProfileForm from './components/UpdateUserProfileForm';
import DeleteUserAccount from './components/DeleteUserAccount';
import CreateGroupForm from './components/CreateGroupForm';
import GroupDetails from './components/GroupDetails';
import GroupList from './components/GroupList';
import UpdateGroupForm from './components/UpdateGroupForm';
import DeleteGroup from './components/DeleteGroup';
import AddMemberForm from './components/AddMemberForm';
import RemoveMember from './components/RemoveMember';
import MessageHistory from './components/MessageHistory';
import SendMessageForm from './components/SendMessageForm';
import MediaUpload from './components/MediaUpload';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // You might want to fetch user details here to confirm authentication
      // For simplicity, we'll assume token presence means authenticated
      setIsAuthenticated(true);
      // Optionally fetch user details:
      // api.getUserProfile('some_user_id_from_token').then(user => setCurrentUser(user));
    }
    setLoading(false);
  }, []);

  const handleLogin = (token, userId) => {
    localStorage.setItem('token', token);
    // Optionally fetch user details and set currentUser
    setIsAuthenticated(true);
    // api.getUserProfile(userId).then(user => setCurrentUser(user));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  if (loading) {
    return <div className="app-loading">Loading...</div>;
  }

  return (
    <Router>
      <div className="app-container">
        <nav className="navbar">
          <div className="navbar-brand">
            <Link to="/" className="navbar-logo">GroupChat</Link>
          </div>
          <ul className="navbar-links">
            {!isAuthenticated ? (
              <>
                <li><Link to="/register" className="nav-link">Register</Link></li>
                <li><Link to="/login" className="nav-link">Login</Link></li>
              </>
            ) : (
              <>
                <li><Link to="/groups" className="nav-link">Groups</Link></li>
                <li><Link to="/profile" className="nav-link">Profile</Link></li>
                <li><button onClick={handleLogout} className="nav-link logout-button">Logout</button></li>
              </>
            )}
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            {/* Public Routes */}
            <Route path="/register" element={<RegisterForm />} />
            <Route path="/login" element={<LoginForm onLogin={handleLogin} />} />

            {/* Protected Routes */}
            {isAuthenticated ? (
              <>
                <Route path="/" element={<GroupList />} />
                <Route path="/groups" element={<GroupList />} />
                <Route path="/groups/create" element={<CreateGroupForm />} />
                <Route path="/groups/:groupId" element={<GroupDetails />} />
                <Route path="/groups/:groupId/update" element={<UpdateGroupForm />} />
                <Route path="/groups/:groupId/delete" element={<DeleteGroup />} />
                <Route path="/groups/:groupId/add-member" element={<AddMemberForm />} />
                <Route path="/groups/:groupId/remove-member/:userId" element={<RemoveMember />} />
                <Route path="/groups/:groupId/messages" element={<MessageHistory />} />
                <Route path="/send-message" element={<SendMessageForm />} />
                <Route path="/profile" element={<UserProfile />} />
                <Route path="/profile/update" element={<UpdateUserProfileForm />} />
                <Route path="/profile/delete" element={<DeleteUserAccount />} />
                <Route path="/media/upload" element={<MediaUpload />} />
              </>
            ) : (
              // Redirect to login if not authenticated and trying to access protected routes
              <Route path="*" element={<LoginForm onLogin={handleLogin} />} />
            )}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;