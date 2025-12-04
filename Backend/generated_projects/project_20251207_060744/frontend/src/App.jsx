import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import RegisterUser from './components/RegisterUser';
import LoginUser from './components/LoginUser';
import GetUser from './components/GetUser';
import UpdateUser from './components/UpdateUser';
import CreateGroup from './components/CreateGroup';
import GetGroups from './components/GetGroups';
import GetGroup from './components/GetGroup';
import JoinGroup from './components/JoinGroup';
import LeaveGroup from './components/LeaveGroup';
import CreateMessage from './components/CreateMessage';
import GetMessages from './components/GetMessages';
import UploadMedia from './components/UploadMedia';

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/register">Register</Link></li>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/users/123">Get User (Example ID)</Link></li>
            <li><Link to="/users/update/123">Update User (Example ID)</Link></li>
            <li><Link to="/groups/create">Create Group</Link></li>
            <li><Link to="/groups">Get Groups</Link></li>
            <li><Link to="/groups/abc">Get Group (Example ID)</Link></li>
            <li><Link to="/groups/abc/join">Join Group (Example ID)</Link></li>
            <li><Link to="/groups/abc/leave">Leave Group (Example ID)</Link></li>
            <li><Link to="/messages/create">Create Message</Link></li>
            <li><Link to="/messages/abc">Get Messages (Example Group ID)</Link></li>
            <li><Link to="/upload">Upload Media</Link></li>
          </ul>
        </nav>

        <Routes>
          <Route path="/register" element={<RegisterUser />} />
          <Route path="/login" element={<LoginUser />} />
          <Route path="/users/:user_id" element={<GetUser />} />
          <Route path="/users/update/:user_id" element={<UpdateUser />} />
          <Route path="/groups/create" element={<CreateGroup />} />
          <Route path="/groups" element={<GetGroups />} />
          <Route path="/groups/:group_id" element={<GetGroup />} />
          <Route path="/groups/:group_id/join" element={<JoinGroup />} />
          <Route path="/groups/:group_id/leave" element={<LeaveGroup />} />
          <Route path="/messages/create" element={<CreateMessage />} />
          <Route path="/messages/:group_id" element={<GetMessages />} />
          <Route path="/upload" element={<UploadMedia />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;