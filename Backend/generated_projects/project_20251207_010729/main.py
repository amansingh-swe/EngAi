import uuid
import json
import threading
import time
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Any

# --- Configuration ---
# In a real-world scenario, these would be loaded from environment variables or config files.
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

# --- Mock Databases ---
# In a real application, these would be actual database connections.

# User Service Database
users_db: Dict[str, Dict[str, Any]] = {}
user_credentials_db: Dict[str, str] = {}  # username -> hashed_password

# Group Service Database
groups_db: Dict[str, Dict[str, Any]] = {}  # group_id -> {name, description, members: {user_id, ...}}
group_memberships_db: Dict[str, set[str]] = defaultdict(set)  # group_id -> set of user_ids

# Message Database
messages_db: Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # group_id -> list of messages

# --- Mock Message Queue ---
# In a real application, this would be Kafka, RabbitMQ, etc.
message_queue: List[Dict[str, Any]] = []
message_queue_lock = threading.Lock()

# --- Mock WebSocket Server ---
# In a real application, this would be a robust WebSocket server.
# For simplicity, we'll simulate broadcasting.
connected_clients: Dict[str, Any] = {}  # client_id -> WebSocket connection object (simulated)
client_subscriptions: Dict[str, set[str]] = defaultdict(set)  # client_id -> set of group_ids

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---

def generate_id() -> str:
    """Generates a unique identifier."""
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """Simulates password hashing."""
    # In production, use a strong hashing algorithm like bcrypt.
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simulates password verification."""
    return hash_password(plain_password) == hashed_password

def authenticate_user(token: str) -> Optional[str]:
    """Simulates JWT token validation. Returns user_id if valid, else None."""
    # In a real app, this would involve decoding and verifying a JWT.
    # For this example, we'll assume a simple token mapping.
    # Let's assume tokens are just user_ids for simplicity in this mock.
    if token in users_db:
        return token
    return None

# --- API Gateway ---

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
        """Simulates making a request to a microservice."""
        # In a real application, this would use a library like 'requests'.
        # For this example, we'll simulate direct calls to the service methods.
        logging.info(f"API Gateway: Routing request to {service_url}{endpoint} with method {method}")
        try:
            if service_url == self.user_service_url:
                if endpoint == "/users/register":
                    return self._handle_register_user(data)
                elif endpoint == "/users/login":
                    return self._handle_login_user(data)
                elif endpoint == "/users/profile":
                    return self._handle_get_user_profile(data)
            elif service_url == self.group_service_url:
                if endpoint == "/groups/create":
                    return self._handle_create_group(data)
                elif endpoint == "/groups/join":
                    return self._handle_join_group(data)
                elif endpoint == "/groups/leave":
                    return self._handle_leave_group(data)
                elif endpoint == "/groups/{group_id}/members":
                    group_id = data.get("group_id")
                    return self._handle_get_group_members(group_id)
            elif service_url == self.messaging_service_url:
                if endpoint == "/messages/send":
                    return self._handle_send_message(data)
                elif endpoint == "/messages/{group_id}":
                    group_id = data.get("group_id")
                    return self._handle_get_message_history(group_id)
            return {"status": "error", "message": "Endpoint not found"}
        except Exception as e:
            logging.error(f"API Gateway: Error during service call: {e}")
            return {"status": "error", "message": "Internal server error"}

    def handle_request(self, path: str, method: str, body: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """Main request handler for the API Gateway."""
        logging.info(f"API Gateway: Received {method} request for {path}")
        
        # Authentication (simplified)
        token = headers.get("Authorization", "").split(" ")[-1] if headers else None
        user_id = None
        if path not in ["/users/register", "/users/login"]:
            user_id = authenticate_user(token)
            if not user_id:
                return {"status": "error", "message": "Unauthorized"}, 401

        # Route the request
        for route, handler in self.routes.items():
            if route == path:
                try:
                    # Add user_id to the body for services that need it
                    if body is None:
                        body = {}
                    if user_id:
                        body["user_id"] = user_id
                    
                    response_data, status_code = handler(body)
                    return response_data, status_code
                except Exception as e:
                    logging.error(f"API Gateway: Error handling request for {path}: {e}")
                    return {"status": "error", "message": "Internal server error"}, 500
        
        return {"status": "error", "message": "Not Found"}, 404

    # --- Handlers for specific routes (simulating calls to microservices) ---

    def _handle_register_user(self, data: Dict) -> tuple[Dict, int]:
        """Simulates User Service registration."""
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"status": "error", "message": "Username and password are required"}, 400
        
        if username in user_credentials_db:
            return {"status": "error", "message": "Username already exists"}, 409

        user_id = generate_id()
        users_db[user_id] = {"user_id": user_id, "username": username}
        user_credentials_db[username] = hash_password(password)
        logging.info(f"User Service: Registered user {username} with ID {user_id}")
        return {"status": "success", "message": "User registered successfully", "user_id": user_id}, 201

    def _handle_login_user(self, data: Dict) -> tuple[Dict, int]:
        """Simulates User Service login."""
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return {"status": "error", "message": "Username and password are required"}, 400

        stored_hashed_password = user_credentials_db.get(username)
        if not stored_hashed_password or not verify_password(password, stored_hashed_password):
            return {"status": "error", "message": "Invalid credentials"}, 401

        # In a real app, generate and return a JWT
        user_id = None
        for uid, user_data in users_db.items():
            if user_data.get("username") == username:
                user_id = uid
                break
        
        if not user_id:
            return {"status": "error", "message": "User not found after credential match"}, 500

        logging.info(f"User Service: User {username} logged in with ID {user_id}")
        return {"status": "success", "message": "Login successful", "token": user_id}, 200 # Using user_id as token for simplicity

    def _handle_get_user_profile(self, data: Dict) -> tuple[Dict, int]:
        """Simulates User Service profile retrieval."""
        user_id = data.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User ID is required"}, 400
        
        user_data = users_db.get(user_id)
        if not user_data:
            return {"status": "error", "message": "User not found"}, 404
        
        logging.info(f"User Service: Fetched profile for user {user_id}")
        return {"status": "success", "user": user_data}, 200

    def _handle_create_group(self, data: Dict) -> tuple[Dict, int]:
        """Simulates Group Service group creation."""
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
        logging.info(f"Group Service: Created group '{group_name}' ({group_id}) by user {user_id}")
        return {"status": "success", "message": "Group created successfully", "group_id": group_id}, 201

    def _handle_join_group(self, data: Dict) -> tuple[Dict, int]:
        """Simulates Group Service joining a group."""
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
        logging.info(f"Group Service: User {user_id} joined group {group_id}")
        return {"status": "success", "message": "Successfully joined group"}, 200

    def _handle_leave_group(self, data: Dict) -> tuple[Dict, int]:
        """Simulates Group Service leaving a group."""
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
        logging.info(f"Group Service: User {user_id} left group {group_id}")
        return {"status": "success", "message": "Successfully left group"}, 200

    def _handle_get_group_members(self, group_id: str) -> tuple[Dict, int]:
        """Simulates Group Service fetching group members."""
        if not group_id:
            return {"status": "error", "message": "Group ID is required"}, 400

        if group_id not in groups_db:
            return {"status": "error", "message": "Group not found"}, 404

        member_ids = list(groups_db[group_id]["members"])
        member_details = [users_db.get(uid) for uid in member_ids if uid in users_db]
        
        logging.info(f"Group Service: Fetched members for group {group_id}")
        return {"status": "success", "members": member_details}, 200

    def _handle_send_message(self, data: Dict) -> tuple[Dict, int]:
        """Simulates Messaging Service sending a message."""
        user_id = data.get("user_id")
        group_id = data.get("group_id")
        content = data.get("content")
        message_type = data.get("type", "text") # 'text' or 'multimedia'

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

        # Store in message database
        messages_db[group_id].append(message)
        logging.info(f"Messaging Service: Stored message {message_id} in group {group_id}")

        # Publish to message queue for real-time delivery
        with message_queue_lock:
            message_queue.append(message)
        logging.info(f"Messaging Service: Published message {message_id} to queue")

        # In a real system, Notification Service would also be triggered here.
        # For example, by publishing an event to another queue.

        return {"status": "success", "message": "Message sent successfully", "message_id": message_id}, 201

    def _handle_get_message_history(self, group_id: str, data: Optional[Dict] = None) -> tuple[Dict, int]:
        """Simulates Messaging Service fetching message history."""
        if not group_id:
            return {"status": "error", "message": "Group ID is required"}, 400
        
        # In a real app, we'd also check if the requesting user is a member of the group.
        # For simplicity, we assume the API Gateway already did this check.

        history = messages_db.get(group_id, [])
        logging.info(f"Messaging Service: Fetched message history for group {group_id}")
        return {"status": "success", "messages": history}, 200

# --- Real-time Communication Layer ---

class RealtimeServer:
    def __init__(self):
        self.running = False
        self.thread = None
        self.message_processor_thread = None
        self.message_processor_stop_event = threading.Event()

    def start(self):
        if not self.running:
            logging.info(f"Real-time Server: Starting on {REALTIME_SERVER_HOST}:{REALTIME_SERVER_PORT}")
            self.running = True
            # Simulate WebSocket server startup
            self.thread = threading.Thread(target=self._simulate_websocket_server, daemon=True)
            self.thread.start()
            
            # Start message processor thread
            self.message_processor_stop_event.clear()
            self.message_processor_thread = threading.Thread(target=self._process_messages, daemon=True)
            self.message_processor_thread.start()

    def stop(self):
        if self.running:
            logging.info("Real-time Server: Stopping...")
            self.running = False
            self.message_processor_stop_event.set()
            if self.thread:
                # In a real scenario, you'd close WebSocket connections here.
                pass
            if self.message_processor_thread:
                self.message_processor_thread.join()
            logging.info("Real-time Server: Stopped.")

    def _simulate_websocket_server(self):
        """Simulates a WebSocket server accepting connections and subscriptions."""
        logging.info("Real-time Server: WebSocket server simulation started.")
        # In a real app, this would be a loop accepting connections.
        # For this simulation, we'll assume clients connect and subscribe.
        
        # Simulate a client connecting and subscribing to a group
        client_id_1 = "client_abc"
        connected_clients[client_id_1] = "simulated_ws_connection_1"
        client_subscriptions[client_id_1].add("group_123")
        logging.info(f"Real-time Server: Simulated client {client_id_1} connected and subscribed to group_123")

        client_id_2 = "client_xyz"
        connected_clients[client_id_2] = "simulated_ws_connection_2"
        client_subscriptions[client_id_2].add("group_123")
        client_subscriptions[client_id_2].add("group_456")
        logging.info(f"Real-time Server: Simulated client {client_id_2} connected and subscribed to group_123 and group_456")

        while self.running:
            time.sleep(1) # Keep the thread alive

    def _process_messages(self):
        """Consumes messages from the queue and broadcasts them."""
        logging.info("Real-time Server: Message processor started.")
        while not self.message_processor_stop_event.is_set():
            message = None
            with message_queue_lock:
                if message_queue:
                    message = message_queue.pop(0)
            
            if message:
                group_id = message.get("group_id")
                logging.info(f"Real-time Server: Processing message {message.get('message_id')} for group {group_id}")
                
                # Broadcast to clients subscribed to this group
                for client_id, subscribed_groups in client_subscriptions.items():
                    if group_id in subscribed_groups:
                        # Simulate sending message over WebSocket
                        if client_id in connected_clients:
                            logging.info(f"Real-time Server: Broadcasting message to {client_id} in group {group_id}")
                            # In a real app: connected_clients[client_id].send(json.dumps(message))
                            # For simulation, we just log.
                            pass
            else:
                time.sleep(0.1) # Wait a bit if queue is empty
        logging.info("Real-time Server: Message processor stopped.")

# --- Mock Notification Service (for completeness, not fully implemented) ---
class NotificationService:
    def __init__(self):
        logging.info("Notification Service: Initialized.")

    def send_notification(self, user_id: str, message: str):
        """Simulates sending a push notification."""
        logging.info(f"Notification Service: Sending notification to user {user_id}: '{message}'")
        # In a real app, this would interact with FCM, APNS, etc.

# --- Main Application Setup ---

class GroupChatApp:
    def __init__(self):
        self.api_gateway = APIGateway()
        self.realtime_server = RealtimeServer()
        self.notification_service = NotificationService() # Mock

    def start(self):
        logging.info("Starting GroupChat Application...")
        self.realtime_server.start()
        logging.info("GroupChat Application started.")

    def stop(self):
        logging.info("Stopping GroupChat Application...")
        self.realtime_server.stop()
        logging.info("GroupChat Application stopped.")

# --- Simulation of Client Interaction ---

def simulate_client_interactions(app: GroupChatApp):
    """Simulates a client interacting with the API Gateway."""
    logging.info("\n--- Simulating Client Interactions ---")

    # 1. User Registration
    logging.info("\n--- User Registration ---")
    reg_data = {"username": "alice", "password": "password123"}
    response, status = app.api_gateway.handle_request("/users/register", "POST", body=reg_data)
    logging.info(f"Register Response: {response}, Status: {status}")
    alice_id = response.get("user_id")
    alice_token = response.get("token") # For simplicity, token is user_id

    reg_data_bob = {"username": "bob", "password": "password456"}
    response, status = app.api_gateway.handle_request("/users/register", "POST", body=reg_data_bob)
    logging.info(f"Register Response: {response}, Status: {status}")
    bob_id = response.get("user_id")
    bob_token = response.get("token")

    # 2. User Login
    logging.info("\n--- User Login ---")
    login_data_alice = {"username": "alice", "password": "password123"}
    response, status = app.api_gateway.handle_request("/users/login", "POST", body=login_data_alice)
    logging.info(f"Login Response: {response}, Status: {status}")
    
    login_data_bob = {"username": "bob", "password": "password456"}
    response, status = app.api_gateway.handle_request("/users/login", "POST", body=login_data_bob)
    logging.info(f"Login Response: {response}, Status: {status}")

    # 3. Create Group
    logging.info("\n--- Create Group ---")
    create_group_data = {"name": "Project Alpha", "description": "Team for Project Alpha"}
    headers_alice = {"Authorization": f"Bearer {alice_token}"}
    response, status = app.api_gateway.handle_request("/groups/create", "POST", body=create_group_data, headers=headers_alice)
    logging.info(f"Create Group Response: {response}, Status: {status}")
    group_id_alpha = response.get("group_id")

    # 4. Join Group
    logging.info("\n--- Join Group ---")
    join_group_data_bob = {"group_id": group_id_alpha}
    headers_bob = {"Authorization": f"Bearer {bob_token}"}
    response, status = app.api_gateway.handle_request("/groups/join", "POST", body=join_group_data_bob, headers=headers_bob)
    logging.info(f"Join Group Response: {response}, Status: {status}")

    # 5. Get Group Members
    logging.info("\n--- Get Group Members ---")
    response, status = app.api_gateway.handle_request(f"/groups/{group_id_alpha}/members", "GET", headers=headers_alice) # Using GET for path param example
    logging.info(f"Get Group Members Response: {response}, Status: {status}")

    # 6. Send Message
    logging.info("\n--- Send Message ---")
    send_message_data_alice = {"group_id": group_id_alpha, "content": "Hello team! Let's start planning."}
    response, status = app.api_gateway.handle_request("/messages/send", "POST", body=send_message_data_alice, headers=headers_alice)
    logging.info(f"Send Message Response: {response}, Status: {status}")
    message_id_1 = response.get("message_id")

    # Simulate another message
    send_message_data_bob = {"group_id": group_id_alpha, "content": "Sounds good, Alice. I'll prepare the initial agenda."}
    response, status = app.api_gateway.handle_request("/messages/send", "POST", body=send_message_data_bob, headers=headers_bob)
    logging.info(f"Send Message Response: {response}, Status: {status}")
    message_id_2 = response.get("message_id")

    # 7. Fetch Message History
    logging.info("\n--- Fetch Message History ---")
    response, status = app.api_gateway.handle_request(f"/messages/{group_id_alpha}", "GET", headers=headers_alice) # Using GET for path param example
    logging.info(f"Message History Response: {response}, Status: {status}")

    # 8. Simulate Real-time Delivery (This is observed by the RealtimeServer processing messages)
    logging.info("\n--- Simulating Real-time Delivery (check logs for RealtimeServer) ---")
    # The RealtimeServer thread will pick up messages from the queue and log broadcasting.
    # In a real client, this would trigger UI updates.
    time.sleep(2) # Give time for the message processor to run

    # 9. Leave Group
    logging.info("\n--- Leave Group ---")
    leave_group_data = {"group_id": group_id_alpha}
    response, status = app.api_gateway.handle_request("/groups/leave", "POST", body=leave_group_data, headers=headers_bob)
    logging.info(f"Leave Group Response: {response}, Status: {status}")

    # 10. Attempt to send message after leaving
    logging.info("\n--- Attempt to send message after leaving group ---")
    send_message_data_bob_after_leave = {"group_id": group_id_alpha, "content": "Can I still send messages?"}
    response, status = app.api_gateway.handle_request("/messages/send", "POST", body=send_message_data_bob_after_leave, headers=headers_bob)
    logging.info(f"Send Message Response: {response}, Status: {status}")

    # 11. Get Group Members after leave
    logging.info("\n--- Get Group Members after leave ---")
    response, status = app.api_gateway.handle_request(f"/groups/{group_id_alpha}/members", "GET", headers=headers_alice)
    logging.info(f"Get Group Members Response: {response}, Status: {status}")


if __name__ == "__main__":
    app = GroupChatApp()
    app.start()

    # Simulate client interactions
    simulate_client_interactions(app)

    # Keep the main thread alive to allow background threads to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        app.stop()