import pytest
import sqlite3
import os
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Import the FastAPI app and database functions from your main.py
from main import app, get_db_connection, DATABASE_NAME, init_db

# --- Pytest Fixtures ---

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Initializes the database for testing.
    Uses a separate test database file.
    Cleans up the test database file after tests.
    """
    global DATABASE_NAME
    original_db_name = DATABASE_NAME
    DATABASE_NAME = "test_chat_app.db"
    init_db()
    yield
    # Clean up the test database
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
    DATABASE_NAME = original_db_name # Restore original for potential other uses

@pytest.fixture(scope="function")
def client():
    """Provides a TestClient for making requests to the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def db_cursor():
    """Provides a database cursor for direct database operations within tests."""
    conn = get_db_connection()
    cursor = conn.cursor()
    yield cursor
    conn.commit() # Ensure any changes made by tests are committed
    conn.close()

@pytest.fixture(scope="function")
def create_user(client, db_cursor):
    """Fixture to create a user and return their details."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/api/users/register", json=user_data)
    assert response.status_code == 200
    user_id = int(response.json()["user_id"])

    # Fetch user from DB to get created_at and updated_at for accurate comparison
    db_cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_db = db_cursor.fetchone()

    return {
        "user_id": user_id,
        "username": user_db["username"],
        "email": user_db["email"],
        "created_at": datetime.fromisoformat(user_db["created_at"]),
        "updated_at": datetime.fromisoformat(user_db["updated_at"]),
        "password": user_data["password"] # Include password for login tests
    }

@pytest.fixture(scope="function")
def create_group(client, create_user):
    """Fixture to create a group with a member and return group details."""
    group_data = {
        "name": "Test Group",
        "description": "A group for testing",
        "member_ids": [create_user["user_id"]]
    }
    response = client.post("/api/groups", json=group_data)
    assert response.status_code == 200
    group_info = response.json()

    # Fetch group from DB to get accurate timestamps and members
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_info["group_id"],))
    group_db = cursor.fetchone()
    cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_info["group_id"],))
    members_db = [row["user_id"] for row in cursor.fetchall()]
    conn.close()

    return {
        "group_id": group_info["group_id"],
        "group_name": group_db["group_name"],
        "group_description": group_db["group_description"],
        "created_by_user_id": group_db["created_by_user_id"],
        "created_at": datetime.fromisoformat(group_db["created_at"]),
        "updated_at": datetime.fromisoformat(group_db["updated_at"]),
        "members": members_db
    }

# --- User API Tests ---

def test_register_user_success(client, db_cursor):
    """Tests successful user registration."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword"
    }
    response = client.post("/api/users/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"
    assert "user_id" in response.json()

    # Verify user is in the database
    user_id = int(response.json()["user_id"])
    db_cursor.execute("SELECT username, email FROM users WHERE user_id = ?", (user_id,))
    user_db = db_cursor.fetchone()
    assert user_db["username"] == user_data["username"]
    assert user_db["email"] == user_data["email"]

def test_register_user_duplicate_username(client):
    """Tests user registration with a duplicate username."""
    user_data = {
        "username": "existinguser",
        "email": "existing@example.com",
        "password": "password123"
    }
    # First registration
    response1 = client.post("/api/users/register", json=user_data)
    assert response1.status_code == 200

    # Second registration with the same username
    user_data_duplicate = {
        "username": "existinguser",
        "email": "another@example.com",
        "password": "anotherpassword"
    }
    response2 = client.post("/api/users/register", json=user_data_duplicate)
    assert response2.status_code == 400
    assert "Username or email already exists" in response2.json()["detail"]

def test_register_user_duplicate_email(client):
    """Tests user registration with a duplicate email."""
    user_data = {
        "username": "uniqueuser",
        "email": "duplicate@example.com",
        "password": "password123"
    }
    # First registration
    response1 = client.post("/api/users/register", json=user_data)
    assert response1.status_code == 200

    # Second registration with the same email
    user_data_duplicate = {
        "username": "anotheruniqueuser",
        "email": "duplicate@example.com",
        "password": "anotherpassword"
    }
    response2 = client.post("/api/users/register", json=user_data_duplicate)
    assert response2.status_code == 400
    assert "Username or email already exists" in response2.json()["detail"]

def test_login_user_success(client, create_user):
    """Tests successful user login."""
    login_data = {
        "email": create_user["email"],
        "password": create_user["password"]
    }
    response = client.post("/api/users/login", json=login_data)
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_user_invalid_credentials(client, create_user):
    """Tests user login with invalid email."""
    login_data = {
        "email": "wrong@example.com",
        "password": create_user["password"]
    }
    response = client.post("/api/users/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_login_user_wrong_password(client, create_user):
    """Tests user login with incorrect password."""
    login_data = {
        "email": create_user["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/users/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_get_user_profile_success(client, create_user):
    """Tests retrieving a user's profile."""
    response = client.get(f"/api/users/{create_user['user_id']}")
    assert response.status_code == 200
    profile = response.json()
    assert profile["user_id"] == str(create_user["user_id"])
    assert profile["username"] == create_user["username"]
    assert profile["email"] == create_user["email"]
    # Compare datetime strings, accounting for potential timezone differences or precision
    assert datetime.fromisoformat(profile["created_at"]).replace(microsecond=0) == create_user["created_at"].replace(microsecond=0)

def test_get_user_profile_not_found(client):
    """Tests retrieving a profile for a non-existent user."""
    response = client.get("/api/users/99999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_update_user_profile_success(client, create_user):
    """Tests updating a user's profile with new username and email."""
    update_data = {
        "username": "updateduser",
        "email": "updated@example.com"
    }
    response = client.put(f"/api/users/{create_user['user_id']}", json=update_data)
    assert response.status_code == 200
    assert "User profile updated successfully" in response.json()["message"]
    updated_user = response.json()["updated_user"]

    assert updated_user["user_id"] == str(create_user["user_id"])
    assert updated_user["username"] == update_data["username"]
    assert updated_user["email"] == update_data["email"]

    # Verify changes in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, updated_at FROM users WHERE user_id = ?", (create_user["user_id"],))
    user_db = cursor.fetchone()
    conn.close()
    assert user_db["username"] == update_data["username"]
    assert user_db["email"] == update_data["email"]
    assert datetime.fromisoformat(user_db["updated_at"]) > create_user["created_at"] # Check if updated_at changed

def test_update_user_profile_no_fields(client, create_user):
    """Tests updating a user's profile with no fields provided."""
    response = client.put(f"/api/users/{create_user['user_id']}", json={})
    assert response.status_code == 400
    assert "No fields to update" in response.json()["detail"]

def test_update_user_profile_not_found(client):
    """Tests updating a profile for a non-existent user."""
    update_data = {"username": "ghost"}
    response = client.put("/api/users/99999", json=update_data)
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_update_user_profile_duplicate_email(client, create_user):
    """Tests updating a user's profile to an email that already exists."""
    # Create another user with an email that will be used for the duplicate update
    user_data_other = {
        "username": "otheruser",
        "email": "other@example.com",
        "password": "password123"
    }
    client.post("/api/users/register", json=user_data_other)

    update_data = {
        "email": "other@example.com"
    }
    response = client.put(f"/api/users/{create_user['user_id']}", json=update_data)
    assert response.status_code == 400
    assert "Username or email already exists" in response.json()["detail"]

def test_delete_user_account_success(client, create_user):
    """Tests deleting a user account."""
    response = client.delete(f"/api/users/{create_user['user_id']}")
    assert response.status_code == 200
    assert "User account deleted successfully" in response.json()["message"]

    # Verify user is deleted from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (create_user["user_id"],))
    user_db = cursor.fetchone()
    conn.close()
    assert user_db is None

def test_delete_user_account_not_found(client):
    """Tests deleting a non-existent user account."""
    response = client.delete("/api/users/99999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

# --- Group API Tests ---

def test_create_group_success(client, create_user):
    """Tests successful group creation."""
    group_data = {
        "name": "New Group",
        "description": "This is a test group",
        "member_ids": [create_user["user_id"]]
    }
    response = client.post("/api/groups", json=group_data)
    assert response.status_code == 200
    group = response.json()

    assert group["group_name"] == group_data["name"]
    assert group["group_description"] == group_data["description"]
    assert group["created_by_user_id"] == create_user["user_id"]
    assert group["members"] == group_data["member_ids"]
    assert "group_id" in group
    assert "created_at" in group
    assert "updated_at" in group

def test_create_group_no_members(client):
    """Tests group creation without any members (should fail as creator is required)."""
    group_data = {
        "name": "No Members Group",
        "description": "This group has no members initially"
    }
    response = client.post("/api/groups", json=group_data)
    assert response.status_code == 400
    assert "Group must have at least one member (creator)" in response.json()["detail"]

def test_create_group_creator_not_found(client):
    """Tests group creation with a non-existent creator ID."""
    group_data = {
        "name": "Invalid Creator Group",
        "description": "Creator does not exist",
        "member_ids": [99999] # Non-existent user ID
    }
    response = client.post("/api/groups", json=group_data)
    assert response.status_code == 404
    assert "Creator user with ID 99999 not found" in response.json()["detail"]

def test_create_group_member_not_found(client, create_user):
    """Tests group creation with a non-existent member ID."""
    group_data = {
        "name": "Invalid Member Group",
        "description": "A member does not exist",
        "member_ids": [create_user["user_id"], 99999] # One valid, one invalid
    }
    response = client.post("/api/groups", json=group_data)
    assert response.status_code == 404
    assert "Member user with ID 99999 not found" in response.json()["detail"]

def test_get_group_details_success(client, create_group):
    """Tests retrieving details of an existing group."""
    response = client.get(f"/api/groups/{create_group['group_id']}")
    assert response.status_code == 200
    group = response.json()

    assert group["group_id"] == create_group["group_id"]
    assert group["group_name"] == create_group["group_name"]
    assert group["group_description"] == create_group["group_description"]
    assert group["created_by_user_id"] == create_group["created_by_user_id"]
    assert sorted(group["members"]) == sorted(create_group["members"])
    assert datetime.fromisoformat(group["created_at"]).replace(microsecond=0) == create_group["created_at"].replace(microsecond=0)

def test_get_group_details_not_found(client):
    """Tests retrieving details for a non-existent group."""
    response = client.get("/api/groups/99999")
    assert response.status_code == 404
    assert "Group not found" in response.json()["detail"]

def test_get_all_groups(client, create_user, create_group):
    """Tests retrieving all groups, optionally filtered by user."""
    # Test getting all groups
    response_all = client.get("/api/groups")
    assert response_all.status_code == 200
    assert len(response_all.json()["groups"]) > 0
    assert any(g["group_id"] == create_group["group_id"] for g in response_all.json()["groups"])

    # Test getting groups for a specific user
    response_user = client.get(f"/api/groups?user_id={create_user['user_id']}")
    assert response_user.status_code == 200
    assert len(response_user.json()["groups"]) > 0
    assert any(g["group_id"] == create_group["group_id"] for g in response_user.json()["groups"])

def test_update_group_details_success(client, create_group):
    """Tests updating group name and description."""
    update_data = {
        "name": "Updated Group Name",
        "description": "New description for the group"
    }
    response = client.put(f"/api/groups/{create_group['group_id']}", json=update_data)
    assert response.status_code == 200
    assert "Group details updated successfully" in response.json()["message"]
    updated_group = response.json()["updated_group"]

    assert updated_group["group_id"] == create_group["group_id"]
    assert updated_group["group_name"] == update_data["name"]
    assert updated_group["group_description"] == update_data["description"]
    assert updated_group["created_by_user_id"] == create_group["created_by_user_id"]
    assert sorted(updated_group["members"]) == sorted(create_group["members"])

    # Verify changes in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_name, group_description, updated_at FROM groups WHERE group_id = ?", (create_group["group_id"],))
    group_db = cursor.fetchone()
    conn.close()
    assert group_db["group_name"] == update_data["name"]
    assert group_db["group_description"] == update_data["description"]
    assert datetime.fromisoformat(group_db["updated_at"]) > create_group["created_at"] # Check if updated_at changed

def test_update_group_details_no_fields(client, create_group):
    """Tests updating a group with no fields provided."""
    response = client.put(f"/api/groups/{create_group['group_id']}", json={})
    assert response.status_code == 400
    assert "No fields to update" in response.json()["detail"]

def test_update_group_details_not_found(client):
    """Tests updating a non-existent group."""
    update_data = {"name": "Ghost Group"}
    response = client.put("/api/groups/99999", json=update_data)
    assert response.status_code == 404
    assert "Group not found" in response.json()["detail"]

def test_delete_group_success(client, create_group):
    """Tests deleting an existing group."""
    response = client.delete(f"/api/groups/{create_group['group_id']}")
    assert response.status_code == 200
    assert "Group deleted successfully" in response.json()["message"]

    # Verify group is deleted from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id FROM groups WHERE group_id = ?", (create_group["group_id"],))
    group_db = cursor.fetchone()
    conn.close()
    assert group_db is None

def test_delete_group_not_found(client):
    """Tests deleting a non-existent group."""
    response = client.delete("/api/groups/99999")
    assert response.status_code == 404
    assert "Group not found" in response.json()["detail"]

def test_add_member_to_group_success(client, create_user, create_group):
    """Tests adding a new member to an existing group."""
    # Create another user to add
    user_data_new_member = {
        "username": "newmember",
        "email": "newmember@example.com",
        "password": "password123"
    }
    register_response = client.post("/api/users/register", json=user_data_new_member)
    assert register_response.status_code == 200
    new_member_id = int(register_response.json()["user_id"])

    add_member_data = {"user_id": new_member_id}
    response = client.post(f"/api/groups/{create_group['group_id']}/members", json=add_member_data)
    assert response.status_code == 200
    assert "Member added to group successfully" in response.json()["message"]
    assert str(new_member_id) in response.json()["updated_members"]
    assert str(create_group["members"][0]) in response.json()["updated_members"] # Original member should still be there

    # Verify member is in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM group_members WHERE group_id = ? AND user_id = ?", (create_group["group_id"], new_member_id))
    member_db = cursor.fetchone()
    conn.close()
    assert member_db is not None
    assert member_db["user_id"] == new_member_id

def test_add_member_to_group_already_member(client, create_user, create_group):
    """Tests adding a user who is already a member of the group."""
    add_member_data = {"user_id": create_user["user_id"]} # Adding the creator again
    response = client.post(f"/api/groups/{create_group['group_id']}/members", json=add_member_data)
    assert response.status_code == 400
    assert "User is already a member of this group" in response.json()["detail"]

def test_add_member_to_group_group_not_found(client, create_user):
    """Tests adding a member to a non-existent group."""
    add_member_data = {"user_id": create_user["user_id"]}
    response = client.post("/api/groups/99999/members", json=add_member_data)
    assert response.status_code == 404
    assert "Group not found" in response.json()["detail"]

def test_add_member_to_group_user_not_found(client, create_group):
    """Tests adding a non-existent user to a group."""
    add_member_data = {"user_id": 99999}
    response = client.post(f"/api/groups/{create_group['group_id']}/members", json=add_member_data)
    assert response.status_code == 404
    assert "User with ID 99999 not found" in response.json()["detail"]

def test_remove_member_from_group_success(client, create_user, create_group):
    """Tests removing a member from an existing group."""
    # Add another member first
    user_data_new_member = {
        "username": "anothermember",
        "email": "anothermember@example.com",
        "password": "password123"
    }
    register_response = client.post("/api/users/register", json=user_data_new_member)
    assert register_response.status_code == 200
    new_member_id = int(register_response.json()["user_id"])
    client.post(f"/api/groups/{create_group['group_id']}/members", json={"user_id": new_member_id})

    # Remove the newly added member
    response = client.delete(f"/api/groups/{create_group['group_id']}/members/{new_member_id}")
    assert response.status_code == 200
    assert "Member removed from group successfully" in response.json()["message"]
    assert str(create_group["members"][0]) in response.json()["updated_members"] # Original member should still be there
    assert str(new_member_id) not in response.json()["updated_members"]

    # Verify member is removed from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_member_id FROM group_members WHERE group_id = ? AND user_id = ?", (create_group["group_id"], new_member_id))
    member_db = cursor.fetchone()
    conn.close()
    assert member_db is None

def test_remove_member_from_group_not_member(client, create_user, create_group):
    """Tests removing a user who is not a member of the group."""
    # Try to remove a user who is not in the group (e.g., a user not created by this test)
    response = client.delete(f"/api/groups/{create_group['group_id']}/members/12345") # Assuming 12345 is not a member
    assert response.status_code == 404
    assert "User is not a member of this group" in response.json()["detail"]

def test_remove_member_from_group_group_not_found(client, create_user):
    """Tests removing a member from a non-existent group."""
    response = client.delete("/api/groups/99999/members/12345")
    assert response.status_code == 404
    assert "Group not found" in response.json()["detail"]

# --- Message API Tests ---

def test_send_message_success(client, create_user, create_group):
    """Tests successfully sending a text message."""
    message_data = {
        "group_id": create_group["group_id"],
        "sender_id": create_user["user_id"],
        "content": "Hello, this is a test message!"
    }
    response = client.post("/api/messages", json=message_data)
    assert response.status_code == 200
    message = response.json()

    assert message["group_id"] == message_data["group_id"]
    assert message["sender_id"] == message_data["sender_id"]
    assert message["content"] == message_data["content"]
    assert message["media_url"] is None
    assert message["media_type"] is None
    assert "message_id" in message
    assert "timestamp" in message

def test_send_message_with_media(client, create_user, create_group):
    """Tests sending a message with media URL and type."""
    message_data = {
        "group_id": create_group["group_id"],
        "sender_id": create_user["user_id"],
        "content": "Check out this image!",
        "media_url": "http://example.com/images/test.jpg",
        "media_type": "image"
    }
    response = client.post("/api/messages", json=message_data)
    assert response.status_code == 200
    message = response.json()

    assert message["group_id"] == message_data["group_id"]
    assert message["sender_id"] == message_data["sender_id"]
    assert message["content"] == message_data["content"]
    assert message["media_url"] == message_data["media_url"]
    assert message["media_type"] == message_data["media_type"]

def test_send_message_group_not_found(client, create_user):
    """Tests sending a message to a non-existent group."""
    message_data = {
        "group_id": 99999,
        "sender_id": create_user["user_id"],
        "content": "This should fail"
    }
    response = client.post("/api/messages", json=message_data)
    assert response.status_code == 404
    assert "Group not found" in response.json()["detail"]

def test_send_message_sender_not_in_group(client, create_user, create_group):
    """Tests sending a message from a user not in the group."""
    # Create a new user who is not part of the group
    user_data_outsider = {
        "username": "outsider",
        "email": "outsider@example.com",
        "password": "password123"
    }
    register_response = client.post("/api/users/register", json=user_data_outsider)
    assert register_response.status_code == 200
    outsider_id = int(register_response.json()["user_id"])

    message_data = {
        "group_id": create_group["group_id"],
        "sender_id": outsider_id,
        "content": "I'm not in this group!"
    }
    response = client.post("/api/messages", json=message_data)
    assert response.status_code == 403
    assert "Sender is not a member of this group" in response.json()["detail"]

def test_send_message_missing_sender_id(client, create_group):
    """Tests sending a message without a sender_id."""
    message_data = {
        "group_id": create_group["group_id"],
        "content": "Missing sender"
    }
    response = client.post("/api/messages", json=message_data)
    assert response.status_code == 400
    assert "Sender ID is required" in response.json()["detail"]

def test_get_group_messages_success(client, create_user, create_group, db_cursor):
    """Tests retrieving messages from a group."""
    # Send a few messages
    message1_data = {
        "group_id": create_group["group_id"],
        "sender_id": create_user["user_id"],
        "content": "First message"
    }
    client.post("/api/messages", json=message1_data)

    message2_data = {
        "group_id": create_group["group_id"],
        "sender_id": create_user["user_id"],
        "content": "Second message"
    }
    client.post("/api/messages", json=message2_data)

    # Retrieve messages
    response = client.get(f"/api/groups/{create_group['group_id']}/messages")
    assert response.status_code == 200
    messages_data = response.json()

    assert len(messages_data["messages"]) == 2
    assert messages_data["total_messages"] == 2

    # Messages should be in descending order of sent_at
    assert messages_data["messages"][0]["content"] == "Second message"
    assert messages_data["messages"][1]["content"] == "First message"

def test_get_group_messages_pagination(client, create_user, create_group, db_cursor):
    """Tests retrieving messages with pagination."""
    # Send 5 messages
    for i in range(5):
        message_data = {
            "group_id": create_group["group_id"],
            "sender_id": create_user["user_id"],
            "content": f"Message {i+1}"
        }
        client.post("/api/messages", json=message_data)

    # Retrieve with limit=2, offset=0
    response1 = client.get(f"/api/groups/{create_group['group_id']}/messages?limit=2&offset=0")
    assert response1.status_code == 200
    assert len(response1.json()["messages"]) == 2
    assert response1.json()["total_messages"] == 5
    assert response1.json()["messages"][0]["content"] == "Message 5"
    assert response1.json()["messages"][1]["content"] == "Message 4"

    # Retrieve with limit=2, offset=2
    response2 = client.get(f"/api/groups/{create_group['group_id']}/messages?limit=2&offset=2")
    assert response2.status_code == 200
    assert len(response2.json()["messages"]) == 2
    assert response2.json()["total_messages"] == 5
    assert response2.json()["messages"][0]["content"] == "Message 3"
    assert response2.json()["messages"][1]["content"] == "Message 2"

    # Retrieve with limit=2, offset=4 (should return only one message)
    response3 = client.get(f"/api/groups/{create_group['group_id']}/messages?limit=2&offset=4")
    assert response3.status_code == 200
    assert len(response3.json()["messages"]) == 1
    assert response3.json()["total_messages"] == 5
    assert response3.json()["messages"][0]["content"] == "Message 1"

def test_get_group_messages_empty_group(client, create_group):
    """Tests retrieving messages from a group with no messages."""
    response = client.get(f"/api/groups/{create_group['group_id']}/messages")
    assert response.status_code == 200
    messages_data = response.json()
    assert len(messages_data["messages"]) == 0
    assert messages_data["total_messages"] == 0

def test_get_group_messages_group_not_found(client):
    """Tests retrieving messages from a non-existent group."""
    response = client.get("/api/groups/99999/messages")
    assert response.status_code == 404
    assert "Group not found" in response.json()["detail"]

# --- Media Upload API Tests ---

def test_upload_media_success(client):
    """Tests successfully uploading a file."""
    # Create a dummy file
    with open("test_image.png", "wb") as f:
        f.write(b"This is dummy image content")

    with open("test_image.png", "rb") as f:
        files = {"file": ("test_image.png", f, "image/png")}
        response = client.post("/api/media/upload", files=files)

    assert response.status_code == 200
    upload_response = response.json()

    assert "media_url" in upload_response
    assert upload_response["file_name"] == "test_image.png"
    assert upload_response["file_type"] == "image/png"
    assert upload_response["media_url"].startswith("http://localhost:8000/static/")

    # Clean up the dummy file and uploaded file
    os.remove("test_image.png")
    # The file is saved in the 'uploads' directory, so we need to clean that up
    uploaded_file_path = os.path.join("uploads", "test_image.png")
    if os.path.exists(uploaded_file_path):
        os.remove(uploaded_file_path)
    if os.path.exists("uploads") and not os.listdir("uploads"): # Remove dir if empty
        os.rmdir("uploads")

def test_upload_media_no_file(client):
    """Tests uploading without providing a file."""
    response = client.post("/api/media/upload")
    # FastAPI's File(...) annotation expects a file, so it will likely return 422 Unprocessable Entity
    assert response.status_code == 422

# --- Database Initialization and Helper Function Tests ---

def test_database_initialization(db_cursor):
    """Tests that the database is initialized correctly with tables."""
    db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table["name"] for table in db_cursor.fetchall()]
    expected_tables = [
        "users", "groups", "group_members", "messages", "auth_tokens"
    ]
    for table in expected_tables:
        assert table in tables

def test_get_db_connection_returns_connection(db_cursor):
    """Tests that get_db_connection returns a valid connection object."""
    conn = get_db_connection()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

# --- Edge Cases and Boundary Conditions ---

def test_user_update_empty_payload(client, create_user):
    """Tests updating user with an empty JSON payload."""
    response = client.put(f"/api/users/{create_user['user_id']}", json={})
    assert response.status_code == 400
    assert "No fields to update" in response.json()["detail"]

def test_group_update_empty_payload(client, create_group):
    """Tests updating group with an empty JSON payload."""
    response = client.put(f"/api/groups/{create_group['group_id']}", json={})
    assert response.status_code == 400
    assert "No fields to update" in response.json()["detail"]

def test_get_messages_with_large_limit_and_offset(client, create_user, create_group, db_cursor):
    """Tests retrieving messages with a very large limit and offset."""
    # Send a few messages
    for i in range(3):
        message_data = {
            "group_id": create_group["group_id"],
            "sender_id": create_user["user_id"],
            "content": f"Boundary message {i+1}"
        }
        client.post("/api/messages", json=message_data)

    # Request more messages than exist with a large offset
    response = client.get(f"/api/groups/{create_group['group_id']}/messages?limit=100&offset=50")
    assert response.status_code == 200
    messages_data = response.json()
    assert len(messages_data["messages"]) == 0
    assert messages_data["total_messages"] == 3 # Should still report the total correctly

# --- Error Handling Tests ---

def test_non_existent_endpoints(client):
    """Tests accessing non-existent API endpoints."""
    response_get = client.get("/api/nonexistent")
    assert response_get.status_code == 404

    response_post = client.post("/api/nonexistent", json={})
    assert response_post.status_code == 404

    response_put = client.put("/api/nonexistent", json={})
    assert response_put.status_code == 404

    response_delete = client.delete("/api/nonexistent")
    assert response_delete.status_code == 404