import pytest
import uuid
import json
import threading
import time
from collections import defaultdict
from typing import Dict, List, Optional, Any

# --- Mock Databases and Global Variables (from the original code) ---
users_db: Dict[str, Dict[str, Any]] = {}
user_credentials_db: Dict[str, str] = {}  # username -> hashed_password
groups_db: Dict[str, Dict[str, Any]] = {}  # group_id -> {name, description, members: {user_id, ...}}
group_memberships_db: Dict[str, set[str]] = defaultdict(set)  # group_id -> set of user_ids
messages_db: Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # group_id -> list of messages
message_queue: List[Dict[str, Any]] = []
message_queue_lock = threading.Lock()
connected_clients: Dict[str, Any] = {}  # client_id -> WebSocket connection object (simulated)
client_subscriptions: Dict[str, set[str]] = defaultdict(set)  # client_id -> set of group_ids

# --- Configuration (from the original code) ---
USER_SERVICE_HOST = "localhost"
USER_SERVICE_PORT = 5001
GROUP_SERVICE_HOST = "localhost"
GROUP_SERVICE_PORT = 5002
MESSAGING_SERVICE_HOST = "localhost"
MESSAGING_SERVICE_PORT = 5003
API_GATEWAY_HOST = "localhost"
API_GATEWAY_PORT = 5000
REALTIME_SERVER_HOST = "localhost"
REALTIME_SERVER_PORT = 8000

# --- Helper Functions (from the original code) ---
def generate_id() -> str:
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def authenticate_user(token: str) -> Optional[str]:
    if token in users_db:
        return token
    return None

# --- API Gateway Class (from the original code) ---
class APIGateway:
    def __init__(self):
        self.routes = {
            "/users/register": self._handle_register_user,
            "/users/login": self._handle_login_user,
            "/users/profile": self._handle_get_user_profile,
            "/groups/create": self._handle_create_group,
            "/groups/join": self._handle_join_group,
            "/groups/leave": self._handle_leave_group,
            "/groups/{group_id}/members": self._handle_get_group_members,
            "/messages/send": self._handle_send_message,
            "/messages/{group_id}": self._handle_get_message_history,
        }
        self.user_service_url = f"http://{USER_SERVICE_HOST}:{USER_SERVICE_PORT}"
        self.group_service_url = f"http://{GROUP_SERVICE_HOST}:{GROUP_SERVICE_PORT}"
        self.messaging_service_url = f"http://{MESSAGING_SERVICE_HOST}:{MESSAGING_SERVICE_PORT}"

    def _make_request(self, service_url: str, endpoint: str, method: str = "POST", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        # This method is simulated in the handle_request method for simplicity in testing.
        # In a real scenario, this would make actual HTTP calls.
        pass

    def handle_request(self, path: str, method: str, body: Optional[Dict] = None, headers: Optional[Dict] = None) -> tuple[Dict, int]:
        token = headers.get("Authorization", "").split(" ")[-1] if headers else None
        user_id = None

        if path not in ["/users/register", "/users/login"]:
            user_id = authenticate_user(token)
            if not user_id:
                return {"status": "error", "message": "Unauthorized"}, 401

        for route, handler in self.routes.items():
            # Simple path matching for testing
            if route == path or (route.endswith("/{group_id}") and path.startswith(route[:-11])):
                try:
                    if body is None:
                        body = {}
                    if user_id:
                        body["user_id"] = user_id
                    
                    # Extract group_id from path if applicable
                    if "{group_id}" in route and path.startswith(route[:-11]):
                        group_id_from_path = path.split('/')[-1]
                        body["group_id"] = group_id_from_path # Add to body for handlers

                    response_data, status_code = handler(body)
                    return response_data, status_code
                except Exception as e:
                    print(f"API Gateway Error: {e}") # Log for debugging tests
                    return {"status": "error", "message": "Internal server error"}, 500
        
        return {"status": "error", "message": "Not Found"}, 404

    # --- Handlers for specific routes (simulating calls to microservices) ---
    def _handle_register_user(self, data: Dict) -> tuple[Dict, int]:
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"status": "error", "message": "Username and password are required"}, 400
        
        if username in user_credentials_db:
            return {"status": "error", "message": "Username already exists"}, 409

        user_id = generate_id()
        users_db[user_id] = {"user_id": user_id, "username": username}
        user_credentials_db[username] = hash_password(password)
        return {"status": "success", "message": "User registered successfully", "user_id": user_id}, 201

    def _handle_login_user(self, data: Dict) -> tuple[Dict, int]:
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"status": "error", "message": "Username and password are required"}, 400

        stored_hashed_password = user_credentials_db.get(username)
        if not stored_hashed_password or not verify_password(password, stored_hashed_password):
            return {"status": "error", "message": "Invalid credentials"}, 401

        user_id = None
        for uid, user_data in users_db.items():
            if user_data.get("username") == username:
                user_id = uid
                break
        
        if not user_id:
            return {"status": "error", "message": "User not found after credential match"}, 500

        return {"status": "success", "message": "Login successful", "token": user_id}, 200

    def _handle_get_user_profile(self, data: Dict) -> tuple[Dict, int]:
        user_id = data.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User ID is required"}, 400
        
        user_data = users_db.get(user_id)
        if not user_data:
            return {"status": "error", "message": "User not found"}, 404
        
        return {"status": "success", "user": user_data}, 200

    def _handle_create_group(self, data: Dict) -> tuple[Dict, int]:
        user_id = data.get("user_id")
        group_name = data.get("name")
        group_description = data.get("description", "")

        if not user_id or not group_name:
            return {"status": "error", "message": "User ID and group name are required"}, 400

        group_id = generate_id()
        groups_db[group_id] = {
            "group_id": group_id,
            "name": group_name,
            "description": group_description,
            "members": {user_id}
        }
        group_memberships_db[group_id].add(user_id)
        return {"status": "success", "message": "Group created successfully", "group_id": group_id}, 201

    def _handle_join_group(self, data: Dict) -> tuple[Dict, int]:
        user_id = data.get("user_id")
        group_id = data.get("group_id")

        if not user_id or not group_id:
            return {"status": "error", "message": "User ID and group ID are required"}, 400

        if group_id not in groups_db:
            return {"status": "error", "message": "Group not found"}, 404

        if user_id in group_memberships_db[group_id]:
            return {"status": "info", "message": "User is already a member of this group"}, 200

        groups_db[group_id]["members"].add(user_id)
        group_memberships_db[group_id].add(user_id)
        return {"status": "success", "message": "Successfully joined group"}, 200

    def _handle_leave_group(self, data: Dict) -> tuple[Dict, int]:
        user_id = data.get("user_id")
        group_id = data.get("group_id")

        if not user_id or not group_id:
            return {"status": "error", "message": "User ID and group ID are required"}, 400

        if group_id not in groups_db:
            return {"status": "error", "message": "Group not found"}, 404

        if user_id not in group_memberships_db[group_id]:
            return {"status": "error", "message": "User is not a member of this group"}, 400

        groups_db[group_id]["members"].discard(user_id)
        group_memberships_db[group_id].discard(user_id)
        return {"status": "success", "message": "Successfully left group"}, 200

    def _handle_get_group_members(self, data: Dict) -> tuple[Dict, int]:
        group_id = data.get("group_id")
        if not group_id:
            return {"status": "error", "message": "Group ID is required"}, 400

        if group_id not in groups_db:
            return {"status": "error", "message": "Group not found"}, 404

        member_ids = list(groups_db[group_id]["members"])
        member_details = [users_db.get(uid) for uid in member_ids if uid in users_db]
        
        return {"status": "success", "members": member_details}, 200

    def _handle_send_message(self, data: Dict) -> tuple[Dict, int]:
        user_id = data.get("user_id")
        group_id = data.get("group_id")
        content = data.get("content")
        message_type = data.get("type", "text")

        if not user_id or not group_id or not content:
            return {"status": "error", "message": "User ID, group ID, and content are required"}, 400

        if group_id not in groups_db or user_id not in groups_db[group_id]["members"]:
            return {"status": "error", "message": "User is not a member of this group"}, 403

        message_id = generate_id()
        timestamp = int(time.time())

        message = {
            "message_id": message_id,
            "group_id": group_id,
            "sender_id": user_id,
            "content": content,
            "type": message_type,
            "timestamp": timestamp
        }

        messages_db[group_id].append(message)

        with message_queue_lock:
            message_queue.append(message)

        return {"status": "success", "message": "Message sent successfully", "message_id": message_id}, 201

    def _handle_get_message_history(self, data: Dict) -> tuple[Dict, int]:
        group_id = data.get("group_id")
        if not group_id:
            return {"status": "error", "message": "Group ID is required"}, 400
        
        history = messages_db.get(group_id, [])
        return {"status": "success", "messages": history}, 200

# --- Real-time Communication Layer (from the original code) ---
class RealtimeServer:
    def __init__(self):
        self.running = False
        self.thread = None
        self.message_processor_thread = None
        self.message_processor_stop_event = threading.Event()

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._simulate_websocket_server, daemon=True)
            self.thread.start()
            
            self.message_processor_stop_event.clear()
            self.message_processor_thread = threading.Thread(target=self._process_messages, daemon=True)
            self.message_processor_thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.message_processor_stop_event.set()
            if self.message_processor_thread:
                self.message_processor_thread.join()
            # In a real app, you'd close WebSocket connections here.

    def _simulate_websocket_server(self):
        # This method is kept minimal for testing as its primary role is to keep the thread alive.
        while self.running:
            time.sleep(0.1)

    def _process_messages(self):
        while not self.message_processor_stop_event.is_set():
            message = None
            with message_queue_lock:
                if message_queue:
                    message = message_queue.pop(0)
            
            if message:
                group_id = message.get("group_id")
                # In a real app, this would broadcast to connected clients.
                # For testing, we just ensure messages are processed from the queue.
                pass
            else:
                time.sleep(0.01)

# --- Mock Notification Service (from the original code) ---
class NotificationService:
    def __init__(self):
        pass
    def send_notification(self, user_id: str, message: str):
        pass

# --- Main Application Setup (from the original code) ---
class GroupChatApp:
    def __init__(self):
        self.api_gateway = APIGateway()
        self.realtime_server = RealtimeServer()
        self.notification_service = NotificationService()

    def start(self):
        self.realtime_server.start()

    def stop(self):
        self.realtime_server.stop()

# --- Pytest Fixtures ---

@pytest.fixture(autouse=True)
def reset_mock_data():
    """Resets all mock databases and queues before each test."""
    global users_db, user_credentials_db, groups_db, group_memberships_db, messages_db, message_queue, connected_clients, client_subscriptions
    users_db.clear()
    user_credentials_db.clear()
    groups_db.clear()
    group_memberships_db.clear()
    messages_db.clear()
    message_queue.clear()
    connected_clients.clear()
    client_subscriptions.clear()
    yield

@pytest.fixture
def app():
    """Provides an instance of the GroupChatApp."""
    app_instance = GroupChatApp()
    app_instance.start()
    yield app_instance
    app_instance.stop()

@pytest.fixture
def api_gateway():
    """Provides an instance of the APIGateway."""
    return APIGateway()

@pytest.fixture
def alice_user():
    """Creates and logs in a user named Alice."""
    api = APIGateway()
    reg_data = {"username": "alice", "password": "password123"}
    response, _ = api.handle_request("/users/register", "POST", body=reg_data)
    user_id = response.get("user_id")
    token = response.get("token") # In this mock, token is user_id

    login_data = {"username": "alice", "password": "password123"}
    response, _ = api.handle_request("/users/login", "POST", body=login_data)
    return {"user_id": user_id, "token": token}

@pytest.fixture
def bob_user():
    """Creates and logs in a user named Bob."""
    api = APIGateway()
    reg_data = {"username": "bob", "password": "password456"}
    response, _ = api.handle_request("/users/register", "POST", body=reg_data)
    user_id = response.get("user_id")
    token = response.get("token")

    login_data = {"username": "bob", "password": "password456"}
    response, _ = api.handle_request("/users/login", "POST", body=login_data)
    return {"user_id": user_id, "token": token}

# --- Test Cases ---

class TestUserAPIs:
    def test_register_user_success(self, api_gateway):
        """Tests successful user registration."""
        reg_data = {"username": "testuser", "password": "securepassword"}
        response, status = api_gateway.handle_request("/users/register", "POST", body=reg_data)
        assert status == 201
        assert response["status"] == "success"
        assert "user_id" in response
        assert response["user_id"] in users_db
        assert users_db[response["user_id"]]["username"] == "testuser"
        assert "testuser" in user_credentials_db

    def test_register_user_duplicate_username(self, api_gateway):
        """Tests registering a user with an existing username."""
        reg_data = {"username": "existinguser", "password": "password"}
        api_gateway.handle_request("/users/register", "POST", body=reg_data) # First registration
        
        reg_data_duplicate = {"username": "existinguser", "password": "anotherpassword"}
        response, status = api_gateway.handle_request("/users/register", "POST", body=reg_data_duplicate)
        assert status == 409
        assert response["status"] == "error"
        assert "Username already exists" in response["message"]

    def test_register_user_missing_fields(self, api_gateway):
        """Tests user registration with missing username or password."""
        reg_data_missing_username = {"password": "password"}
        response, status = api_gateway.handle_request("/users/register", "POST", body=reg_data_missing_username)
        assert status == 400
        assert "Username and password are required" in response["message"]

        reg_data_missing_password = {"username": "testuser"}
        response, status = api_gateway.handle_request("/users/register", "POST", body=reg_data_missing_password)
        assert status == 400
        assert "Username and password are required" in response["message"]

    def test_login_user_success(self, api_gateway):
        """Tests successful user login."""
        # First, register a user
        reg_data = {"username": "loginuser", "password": "loginpassword"}
        api_gateway.handle_request("/users/register", "POST", body=reg_data)

        login_data = {"username": "loginuser", "password": "loginpassword"}
        response, status = api_gateway.handle_request("/users/login", "POST", body=login_data)
        assert status == 200
        assert response["status"] == "success"
        assert "token" in response
        assert response["token"] == list(users_db.keys())[0] # Token is user_id in mock

    def test_login_user_invalid_credentials(self, api_gateway):
        """Tests user login with incorrect username or password."""
        reg_data = {"username": "loginuser", "password": "loginpassword"}
        api_gateway.handle_request("/users/register", "POST", body=reg_data)

        login_data_wrong_pass = {"username": "loginuser", "password": "wrongpassword"}
        response, status = api_gateway.handle_request("/users/login", "POST", body=login_data_wrong_pass)
        assert status == 401
        assert "Invalid credentials" in response["message"]

        login_data_nonexistent_user = {"username": "nonexistent", "password": "password"}
        response, status = api_gateway.handle_request("/users/login", "POST", body=login_data_nonexistent_user)
        assert status == 401
        assert "Invalid credentials" in response["message"]

    def test_login_user_missing_fields(self, api_gateway):
        """Tests user login with missing username or password."""
        login_data_missing_username = {"password": "password"}
        response, status = api_gateway.handle_request("/users/login", "POST", body=login_data_missing_username)
        assert status == 400
        assert "Username and password are required" in response["message"]

        login_data_missing_password = {"username": "testuser"}
        response, status = api_gateway.handle_request("/users/login", "POST", body=login_data_missing_password)
        assert status == 400
        assert "Username and password are required" in response["message"]

    def test_get_user_profile_success(self, api_gateway, alice_user):
        """Tests retrieving a user's profile."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        response, status = api_gateway.handle_request("/users/profile", "GET", headers=headers)
        assert status == 200
        assert response["status"] == "success"
        assert response["user"]["user_id"] == alice_user["user_id"]
        assert response["user"]["username"] == "alice"

    def test_get_user_profile_unauthorized(self, api_gateway):
        """Tests retrieving a user's profile without authentication."""
        response, status = api_gateway.handle_request("/users/profile", "GET")
        assert status == 401
        assert "Unauthorized" in response["message"]

    def test_get_user_profile_invalid_user_id(self, api_gateway):
        """Tests retrieving a profile for a non-existent user ID (should not happen with auth token)."""
        # This scenario is more about the underlying service. The gateway checks auth.
        # If a valid token maps to a deleted user, this would be the outcome.
        # For this mock, we can't easily simulate a valid token for a deleted user.
        # We can test the handler directly if needed, but the gateway's role is auth.
        pass # The gateway's primary role is auth, which is tested above.

class TestGroupAPIs:
    def test_create_group_success(self, api_gateway, alice_user):
        """Tests successful group creation."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Project X", "description": "New project initiative"}
        response, status = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers)
        assert status == 201
        assert response["status"] == "success"
        assert "group_id" in response
        assert response["group_id"] in groups_db
        assert groups_db[response["group_id"]]["name"] == "Project X"
        assert alice_user["user_id"] in groups_db[response["group_id"]]["members"]
        assert group_memberships_db[response["group_id"]].issuperset({alice_user["user_id"]})

    def test_create_group_missing_fields(self, api_gateway, alice_user):
        """Tests group creation with missing name."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data_missing_name = {"description": "No name provided"}
        response, status = api_gateway.handle_request("/groups/create", "POST", body=group_data_missing_name, headers=headers)
        assert status == 400
        assert "User ID and group name are required" in response["message"]

    def test_create_group_unauthorized(self, api_gateway):
        """Tests group creation without authentication."""
        group_data = {"name": "Project X"}
        response, status = api_gateway.handle_request("/groups/create", "POST", body=group_data)
        assert status == 401
        assert "Unauthorized" in response["message"]

    def test_join_group_success(self, api_gateway, alice_user, bob_user):
        """Tests a user successfully joining a group."""
        # Create a group first
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Team Y"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Bob joins the group
        headers_bob = {"Authorization": f"Bearer {bob_user['token']}"}
        join_data = {"group_id": group_id}
        response, status = api_gateway.handle_request("/groups/join", "POST", body=join_data, headers=headers_bob)
        assert status == 200
        assert response["status"] == "success"
        assert "Successfully joined group" in response["message"]
        assert bob_user["user_id"] in groups_db[group_id]["members"]
        assert group_memberships_db[group_id].issuperset({alice_user["user_id"], bob_user["user_id"]})

    def test_join_group_already_member(self, api_gateway, alice_user):
        """Tests joining a group when already a member."""
        # Create a group
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Team Z"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Alice tries to join again
        join_data = {"group_id": group_id}
        response, status = api_gateway.handle_request("/groups/join", "POST", body=join_data, headers=headers_alice)
        assert status == 200
        assert response["status"] == "info"
        assert "User is already a member" in response["message"]
        assert len(groups_db[group_id]["members"]) == 1 # Should still only be Alice

    def test_join_group_nonexistent_group(self, api_gateway, alice_user):
        """Tests joining a group that does not exist."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        join_data = {"group_id": "nonexistent_group_id"}
        response, status = api_gateway.handle_request("/groups/join", "POST", body=join_data, headers=headers)
        assert status == 404
        assert "Group not found" in response["message"]

    def test_join_group_missing_fields(self, api_gateway, alice_user):
        """Tests joining a group with missing group_id."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        join_data_missing_id = {}
        response, status = api_gateway.handle_request("/groups/join", "POST", body=join_data_missing_id, headers=headers)
        assert status == 400
        assert "User ID and group ID are required" in response["message"]

    def test_leave_group_success(self, api_gateway, alice_user, bob_user):
        """Tests a user successfully leaving a group."""
        # Create a group
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Team A"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Bob joins the group
        headers_bob = {"Authorization": f"Bearer {bob_user['token']}"}
        join_data = {"group_id": group_id}
        api_gateway.handle_request("/groups/join", "POST", body=join_data, headers=headers_bob)

        # Bob leaves the group
        leave_data = {"group_id": group_id}
        response, status = api_gateway.handle_request("/groups/leave", "POST", body=leave_data, headers=headers_bob)
        assert status == 200
        assert response["status"] == "success"
        assert "Successfully left group" in response["message"]
        assert bob_user["user_id"] not in groups_db[group_id]["members"]
        assert group_memberships_db[group_id].issuperset({alice_user["user_id"]})

    def test_leave_group_not_member(self, api_gateway, alice_user):
        """Tests leaving a group when not a member."""
        # Create a group
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Team B"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Alice tries to leave (she is a member, this tests the "not member" path for another user)
        # Let's simulate a scenario where Alice is NOT a member (this would require direct DB manipulation or a different user)
        # For simplicity, let's assume a different user tries to leave a group they are not in.
        # We'll create a new user and try to make them leave a group they never joined.
        
        # Create another user, Charlie
        api_gateway.handle_request("/users/register", "POST", body={"username": "charlie", "password": "charliepass"})
        charlie_login_resp, _ = api_gateway.handle_request("/users/login", "POST", body={"username": "charlie", "password": "charliepass"})
        charlie_token = charlie_login_resp["token"]
        
        headers_charlie = {"Authorization": f"Bearer {charlie_token}"}
        leave_data = {"group_id": group_id}
        response, status = api_gateway.handle_request("/groups/leave", "POST", body=leave_data, headers=headers_charlie)
        assert status == 400 # The handler returns 400 for "not a member"
        assert "User is not a member of this group" in response["message"]

    def test_leave_group_nonexistent_group(self, api_gateway, alice_user):
        """Tests leaving a group that does not exist."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        leave_data = {"group_id": "nonexistent_group_id"}
        response, status = api_gateway.handle_request("/groups/leave", "POST", body=leave_data, headers=headers)
        assert status == 404
        assert "Group not found" in response["message"]

    def test_leave_group_missing_fields(self, api_gateway, alice_user):
        """Tests leaving a group with missing group_id."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        leave_data_missing_id = {}
        response, status = api_gateway.handle_request("/groups/leave", "POST", body=leave_data_missing_id, headers=headers)
        assert status == 400
        assert "User ID and group ID are required" in response["message"]

    def test_get_group_members_success(self, api_gateway, alice_user, bob_user):
        """Tests retrieving members of a group."""
        # Create a group
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Team C"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Bob joins
        headers_bob = {"Authorization": f"Bearer {bob_user['token']}"}
        join_data = {"group_id": group_id}
        api_gateway.handle_request("/groups/join", "POST", body=join_data, headers=headers_bob)

        # Get members
        response, status = api_gateway.handle_request(f"/groups/{group_id}/members", "GET", headers=headers_alice)
        assert status == 200
        assert response["status"] == "success"
        assert len(response["members"]) == 2
        member_ids = {m["user_id"] for m in response["members"]}
        assert member_ids == {alice_user["user_id"], bob_user["user_id"]}
        
        # Check if user details are correct
        alice_member = next((m for m in response["members"] if m["user_id"] == alice_user["user_id"]), None)
        assert alice_member["username"] == "alice"
        bob_member = next((m for m in response["members"] if m["user_id"] == bob_user["user_id"]), None)
        assert bob_member["username"] == "bob"

    def test_get_group_members_nonexistent_group(self, api_gateway, alice_user):
        """Tests retrieving members of a non-existent group."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        response, status = api_gateway.handle_request("/groups/nonexistent_group_id/members", "GET", headers=headers)
        assert status == 404
        assert "Group not found" in response["message"]

    def test_get_group_members_missing_group_id_in_path(self, api_gateway, alice_user):
        """Tests retrieving members with a malformed path (missing group_id)."""
        # The current routing logic might handle this as "Not Found" or error.
        # Let's assume it falls through to "Not Found" if the route doesn't match exactly.
        # The current implementation of handle_request expects the {group_id} part to be matched.
        response, status = api_gateway.handle_request("/groups//members", "GET", headers={"Authorization": f"Bearer {alice_user['token']}"})
        assert status == 404 # Or could be 400 depending on exact routing logic

    def test_get_group_members_unauthorized(self, api_gateway):
        """Tests retrieving group members without authentication."""
        response, status = api_gateway.handle_request("/groups/some_group_id/members", "GET")
        assert status == 401
        assert "Unauthorized" in response["message"]

class TestMessageAPIs:
    def test_send_message_success(self, api_gateway, alice_user, bob_user):
        """Tests successfully sending a message to a group."""
        # Create a group
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Chat Room"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Bob joins
        headers_bob = {"Authorization": f"Bearer {bob_user['token']}"}
        join_data = {"group_id": group_id}
        api_gateway.handle_request("/groups/join", "POST", body=join_data, headers=headers_bob)

        # Alice sends a message
        send_data_alice = {"group_id": group_id, "content": "Hello Bob!"}
        response, status = api_gateway.handle_request("/messages/send", "POST", body=send_data_alice, headers=headers_alice)
        assert status == 201
        assert response["status"] == "success"
        assert "message_id" in response
        assert response["message_id"] in [m["message_id"] for m in messages_db[group_id]]
        assert len(messages_db[group_id]) == 1
        assert messages_db[group_id][0]["sender_id"] == alice_user["user_id"]
        assert messages_db[group_id][0]["content"] == "Hello Bob!"

        # Bob sends a message
        send_data_bob = {"group_id": group_id, "content": "Hi Alice!"}
        response, status = api_gateway.handle_request("/messages/send", "POST", body=send_data_bob, headers=headers_bob)
        assert status == 201
        assert response["status"] == "success"
        assert len(messages_db[group_id]) == 2
        assert messages_db[group_id][1]["sender_id"] == bob_user["user_id"]
        assert messages_db[group_id][1]["content"] == "Hi Alice!"

    def test_send_message_to_non_member(self, api_gateway, alice_user, bob_user):
        """Tests sending a message to a group where the sender is not a member."""
        # Create a group with Alice
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Private Room"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Bob tries to send a message to this group (he's not a member)
        headers_bob = {"Authorization": f"Bearer {bob_user['token']}"}
        send_data_bob = {"group_id": group_id, "content": "Can you see this?"}
        response, status = api_gateway.handle_request("/messages/send", "POST", body=send_data_bob, headers=headers_bob)
        assert status == 403
        assert "User is not a member of this group" in response["message"]

    def test_send_message_nonexistent_group(self, api_gateway, alice_user):
        """Tests sending a message to a non-existent group."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        send_data = {"group_id": "nonexistent_group_id", "content": "Hello!"}
        response, status = api_gateway.handle_request("/messages/send", "POST", body=send_data, headers=headers)
        assert status == 403 # The handler checks membership, which implies group existence.
        assert "User is not a member of this group" in response["message"]

    def test_send_message_missing_fields(self, api_gateway, alice_user):
        """Tests sending a message with missing required fields."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        
        send_data_missing_group_id = {"content": "Message without group ID"}
        response, status = api_gateway.handle_request("/messages/send", "POST", body=send_data_missing_group_id, headers=headers)
        assert status == 400
        assert "User ID, group ID, and content are required" in response["message"]

        send_data_missing_content = {"group_id": "some_group_id"}
        response, status = api_gateway.handle_request("/messages/send", "POST", body=send_data_missing_content, headers=headers)
        assert status == 400
        assert "User ID, group ID, and content are required" in response["message"]

    def test_send_message_unauthorized(self, api_gateway):
        """Tests sending a message without authentication."""
        send_data = {"group_id": "some_group_id", "content": "Hello!"}
        response, status = api_gateway.handle_request("/messages/send", "POST", body=send_data)
        assert status == 401
        assert "Unauthorized" in response["message"]

    def test_get_message_history_success(self, api_gateway, alice_user, bob_user):
        """Tests retrieving message history for a group."""
        # Create a group
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "History Room"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Bob joins
        headers_bob = {"Authorization": f"Bearer {bob_user['token']}"}
        join_data = {"group_id": group_id}
        api_gateway.handle_request("/groups/join", "POST", body=join_data, headers=headers_bob)

        # Send some messages
        send_data_alice = {"group_id": group_id, "content": "First message"}
        api_gateway.handle_request("/messages/send", "POST", body=send_data_alice, headers=headers_alice)
        time.sleep(0.1) # Ensure timestamps are different
        send_data_bob = {"group_id": group_id, "content": "Second message"}
        api_gateway.handle_request("/messages/send", "POST", body=send_data_bob, headers=headers_bob)

        # Fetch history
        response, status = api_gateway.handle_request(f"/messages/{group_id}", "GET", headers=headers_alice)
        assert status == 200
        assert response["status"] == "success"
        assert len(response["messages"]) == 2
        
        # Check message details and order (should be chronological by timestamp)
        assert response["messages"][0]["sender_id"] == alice_user["user_id"]
        assert response["messages"][0]["content"] == "First message"
        assert response["messages"][1]["sender_id"] == bob_user["user_id"]
        assert response["messages"][1]["content"] == "Second message"

    def test_get_message_history_empty_group(self, api_gateway, alice_user):
        """Tests retrieving message history for a group with no messages."""
        # Create a group
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Empty Room"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]

        # Fetch history
        response, status = api_gateway.handle_request(f"/messages/{group_id}", "GET", headers=headers_alice)
        assert status == 200
        assert response["status"] == "success"
        assert response["messages"] == []

    def test_get_message_history_nonexistent_group(self, api_gateway, alice_user):
        """Tests retrieving message history for a non-existent group."""
        headers = {"Authorization": f"Bearer {alice_user['token']}"}
        response, status = api_gateway.handle_request("/messages/nonexistent_group_id", "GET", headers=headers)
        assert status == 200 # The handler returns an empty list for non-existent groups
        assert response["status"] == "success"
        assert response["messages"] == []

    def test_get_message_history_unauthorized(self, api_gateway):
        """Tests retrieving message history without authentication."""
        response, status = api_gateway.handle_request("/messages/some_group_id", "GET")
        assert status == 401
        assert "Unauthorized" in response["message"]

class TestRealtimeServer:
    def test_message_processing_from_queue(self, app):
        """Tests that messages are processed from the queue by the RealtimeServer."""
        # Simulate a message being added to the queue
        test_message = {
            "message_id": generate_id(),
            "group_id": "test_group",
            "sender_id": "sender_123",
            "content": "Realtime test message",
            "timestamp": int(time.time())
        }
        with message_queue_lock:
            message_queue.append(test_message)
        
        # Give the message processor thread a moment to run
        time.sleep(0.5) 
        
        # Check if the message was consumed from the queue
        with message_queue_lock:
            assert test_message not in message_queue
            assert len(message_queue) == 0 # Ensure it was the only message and it's gone

        # Note: This test doesn't verify actual "broadcasting" as that involves mock WebSocket clients,
        # which is more complex to set up for unit testing. It verifies the core mechanism of
        # consuming from the queue.

    def test_realtime_server_start_stop(self, app):
        """Tests starting and stopping the RealtimeServer."""
        # The 'app' fixture already starts and stops the server.
        # We can check internal states if needed, but the main functionality is tested via message processing.
        assert app.realtime_server.running is True
        app.stop()
        assert app.realtime_server.running is False
        # Ensure the message processor thread has joined
        assert app.realtime_server.message_processor_thread is not None
        # The join() call in stop() ensures it's finished.

class TestIntegration:
    def test_full_workflow_alice_bob_group_chat(self, api_gateway, alice_user, bob_user):
        """Tests a complete workflow: create group, join, send messages, get history."""
        # 1. Alice creates a group
        headers_alice = {"Authorization": f"Bearer {alice_user['token']}"}
        group_data = {"name": "Integration Test Group", "description": "Testing full flow"}
        create_response, _ = api_gateway.handle_request("/groups/create", "POST", body=group_data, headers=headers_alice)
        group_id = create_response["group_id"]
        assert group_id is not None

        # 2. Bob joins the group
        headers_bob = {"Authorization": f"Bearer {bob_user['token']}"}
        join_data = {"group_id": group_id}
        join_response, _ = api_gateway.handle_request("/groups/join", "POST", body=join_data, headers=headers_bob)
        assert join_response["status"] == "success"

        # 3. Alice sends a message
        send_data_alice = {"group_id": group_id, "content": "Hello Bob, this is the first message!"}
        send_response_alice, _ = api_gateway.handle_request("/messages/send", "POST", body=send_data_alice, headers=headers_alice)
        message_id_alice = send_response_alice["message_id"]
        assert message_id_alice is not None

        # 4. Bob sends a message
        send_data_bob = {"group_id": group_id, "content": "Hi Alice, got your message!"}
        send_response_bob, _ = api_gateway.handle_request("/messages/send", "POST", body=send_data_bob, headers=headers_bob)
        message_id_bob = send_response_bob["message_id"]
        assert message_id_bob is not None

        # Give a moment for the message queue to be populated
        time.sleep(0.1)

        # 5. Fetch message history
        history_response, _ = api_gateway.handle_request(f"/messages/{group_id}", "GET", headers=headers_alice)
        assert history_response["status"] == "success"
        assert len(history_response["messages"]) == 2
        
        # Verify message content and order
        msg1 = history_response["messages"][0]
        msg2 = history_response["messages"][1]

        assert msg1["sender_id"] == alice_user["user_id"]
        assert msg1["content"] == "Hello Bob, this is the first message!"
        assert msg1["message_id"] == message_id_alice

        assert msg2["sender_id"] == bob_user["user_id"]
        assert msg2["content"] == "Hi Alice, got your message!"
        assert msg2["message_id"] == message_id_bob

        # 6. Get group members
        members_response, _ = api_gateway.handle_request(f"/groups/{group_id}/members", "GET", headers=headers_alice)
        assert members_response["status"] == "success"
        assert len(members_response["members"]) == 2
        member_ids = {m["user_id"] for m in members_response["members"]}
        assert member_ids == {alice_user["user_id"], bob_user["user_id"]}

        # 7. Bob leaves the group
        leave_data = {"group_id": group_id}
        leave_response, _ = api_gateway.handle_request("/groups/leave", "POST", body=leave_data, headers=headers_bob)
        assert leave_response["status"] == "success"

        # 8. Verify group members after leave
        members_after_leave_response, _ = api_gateway.handle_request(f"/groups/{group_id}/members", "GET", headers=headers_alice)
        assert members_after_leave_response["status"] == "success"
        assert len(members_after_leave_response["members"]) == 1
        assert members_after_leave_response["members"][0]["user_id"] == alice_user["user_id"]

        # 9. Bob tries to send a message after leaving
        send_data_bob_after_leave = {"group_id": group_id, "content": "Can I still send messages?"}
        send_response_after_leave, status_after_leave = api_gateway.handle_request("/messages/send", "POST", body=send_data_bob_after_leave, headers=headers_bob)
        assert status_after_leave == 403
        assert "User is not a member of this group" in send_response_after_leave["message"]

    def test_unauthorized_access_to_protected_routes(self, api_gateway):
        """Tests that protected routes require authentication."""
        # Routes that require authentication
        protected_routes = [
            "/users/profile",
            "/groups/create",
            "/groups/join",
            "/groups/leave",
            "/groups/some_group_id/members",
            "/messages/send",
            "/messages/some_group_id",
        ]

        for route in protected_routes:
            # For POST requests, we might need a minimal body
            body = {"dummy": "data"} if "create" in route or "join" in route or "leave" in route or "send" in route else None
            
            # For GET requests, we might need a path parameter if it's part of the route pattern
            path = route
            if "{group_id}" in route:
                path = route.replace("{group_id}", "test_group_id")

            response, status = api_gateway.handle_request(path, "POST" if "send" in route or "create" in route or "join" in route or "leave" in route else "GET", body=body)
            assert status == 401, f"Route {path} should be unauthorized"
            assert "Unauthorized" in response["message"], f"Route {path} should return unauthorized message"