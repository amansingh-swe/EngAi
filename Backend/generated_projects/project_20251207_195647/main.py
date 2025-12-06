# main.py
import sqlite3
import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import secrets
import os

# --- Database Configuration ---
DATABASE_NAME = "chat_app.db"

def get_db_connection():
    """Establishes and returns a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    return conn

def init_db():
    """Initializes the database with the defined schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for storing user information
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table for storing group information
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT NOT NULL,
        group_description TEXT,
        created_by_user_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
    );
    """)

    # Table for managing group memberships
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_members (
        group_member_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        UNIQUE(group_id, user_id) -- A user can only be a member of a group once
    );
    """)

    # Table for storing chat messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        sender_user_id INTEGER NOT NULL,
        message_text TEXT,
        media_url TEXT, -- URL to the multimedia file in cloud storage
        media_type TEXT, -- e.g., 'image', 'video', 'file'
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
        FOREIGN KEY (sender_user_id) REFERENCES users(user_id)
    );
    """)

    # Table for storing authentication tokens (e.g., JWT refresh tokens if needed for persistence)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auth_tokens (
        token_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

# Initialize the database when the script starts
init_db()

# --- Pydantic Models ---

# User Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

# Group Models
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    member_ids: Optional[List[int]] = None # Expecting user_ids

class Group(BaseModel):
    group_id: int
    group_name: str
    group_description: Optional[str] = None
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    members: List[int] = [] # List of user_ids

    class Config:
        orm_mode = True

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class GroupMemberAdd(BaseModel):
    user_id: int

# Message Models
class MessageCreate(BaseModel):
    group_id: int
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None

class Message(BaseModel):
    message_id: int
    group_id: int
    sender_id: int
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    timestamp: datetime

    class Config:
        orm_mode = True

# Media Upload Model
class MediaUploadResponse(BaseModel):
    media_url: str
    file_name: str
    file_type: str

# --- FastAPI App ---
app = FastAPI(title="Chat App API", version="1.0.0")

# CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3001", # Example for a frontend running on port 3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Functions ---
def hash_password(password: str) -> str:
    """
    In a real application, use a strong hashing library like bcrypt.
    For simplicity, this example uses a basic hash.
    """
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return hash_password(plain_password) == hashed_password

def generate_token() -> str:
    """Generates a secure random token."""
    return secrets.token_urlsafe(32)

# --- API Routes ---

# User Routes
@app.post("/api/users/register", response_model=Dict[str, str])
async def register_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (user.username, user.email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return {"message": "User registered successfully", "user_id": str(user_id)}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    finally:
        conn.close()

@app.post("/api/users/login", response_model=Dict[str, str])
async def login_user(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    user_db = cursor.fetchone()
    conn.close()

    if not user_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, user_db["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # In a real app, you'd generate a JWT here and return it.
    # For simplicity, we'll just return a placeholder token.
    # You might also store a refresh token in the auth_tokens table.
    token = generate_token()
    return {"token": token}

@app.get("/api/users/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, email, created_at FROM users WHERE user_id = ?", (user_id,))
    user_db = cursor.fetchone()
    conn.close()

    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        user_id=str(user_db["user_id"]),
        username=user_db["username"],
        email=user_db["email"],
        created_at=user_db["created_at"]
    )

@app.put("/api/users/{user_id}", response_model=Dict[str, Any])
async def update_user_profile(user_id: int, user_update: UserUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if user_update.username is not None:
        updates.append("username = ?")
        params.append(user_update.username)
    if user_update.email is not None:
        updates.append("email = ?")
        params.append(user_update.email)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(datetime.now()) # updated_at
    params.append(user_id)

    query = f"UPDATE users SET {', '.join(updates)}, updated_at = ? WHERE user_id = ?"
    try:
        cursor.execute(query, tuple(params))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch the updated user to return
        cursor.execute("SELECT user_id, username, email, created_at FROM users WHERE user_id = ?", (user_id,))
        updated_user_db = cursor.fetchone()

        return {
            "message": "User profile updated successfully",
            "updated_user": UserProfile(
                user_id=str(updated_user_db["user_id"]),
                username=updated_user_db["username"],
                email=updated_user_db["email"],
                created_at=updated_user_db["created_at"]
            )
        }
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    finally:
        conn.close()

@app.delete("/api/users/{user_id}", response_model=Dict[str, str])
async def delete_user_account(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User account deleted successfully"}
    finally:
        conn.close()

# Group Routes
@app.post("/api/groups", response_model=Group)
async def create_group(group_create: GroupCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Assuming the user creating the group is the first member
    # In a real app, you'd likely get the creator's ID from authentication
    if not group_create.member_ids:
        group_create.member_ids = []

    # Check if creator_id is provided or assume it's the first user for simplicity
    # For this example, we'll assume the creator is the first member if not specified.
    # A better approach would be to pass creator_id or get it from auth.
    # Let's assume the first member_id is the creator if it exists.
    creator_id = group_create.member_ids[0] if group_create.member_ids else None

    if creator_id is None:
        # If no members are provided, we can't create a group without a creator.
        # Or, we could assign a default creator if the system allows.
        # For now, let's require at least one member (the creator).
        raise HTTPException(status_code=400, detail="Group must have at least one member (creator)")

    # Verify creator exists
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (creator_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Creator user with ID {creator_id} not found")

    # Verify all other members exist
    for member_id in group_create.member_ids:
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (member_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Member user with ID {member_id} not found")

    try:
        cursor.execute(
            "INSERT INTO groups (group_name, group_description, created_by_user_id) VALUES (?, ?, ?)",
            (group_create.name, group_create.description, creator_id)
        )
        group_id = cursor.lastrowid

        # Add members to the group_members table
        for member_id in group_create.member_ids:
            cursor.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
                (group_id, member_id)
            )

        conn.commit()

        # Fetch the created group to return
        cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
        created_group_db = cursor.fetchone()

        # Fetch members for the response
        cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
        members_db = [row["user_id"] for row in cursor.fetchall()]

        return Group(
            group_id=created_group_db["group_id"],
            group_name=created_group_db["group_name"],
            group_description=created_group_db["group_description"],
            created_by_user_id=created_group_db["created_by_user_id"],
            created_at=created_group_db["created_at"],
            updated_at=created_group_db["updated_at"],
            members=members_db
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating group: {e}")
    finally:
        conn.close()

@app.get("/api/groups/{group_id}", response_model=Group)
async def get_group_details(group_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
    group_db = cursor.fetchone()

    if not group_db:
        raise HTTPException(status_code=404, detail="Group not found")

    cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
    members_db = [row["user_id"] for row in cursor.fetchall()]

    conn.close()

    return Group(
        group_id=group_db["group_id"],
        group_name=group_db["group_name"],
        group_description=group_db["group_description"],
        created_by_user_id=group_db["created_by_user_id"],
        created_at=group_db["created_at"],
        updated_at=group_db["updated_at"],
        members=members_db
    )

@app.get("/api/groups", response_model=Dict[str, List[Group]])
async def get_all_groups(user_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT g.* FROM groups g"
    params = []

    if user_id is not None:
        query += " JOIN group_members gm ON g.group_id = gm.group_id WHERE gm.user_id = ?"
        params.append(user_id)

    cursor.execute(query, tuple(params))
    groups_db = cursor.fetchall()

    all_groups_data = []
    for group_db in groups_db:
        cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_db["group_id"],))
        members_db = [row["user_id"] for row in cursor.fetchall()]
        all_groups_data.append(Group(
            group_id=group_db["group_id"],
            group_name=group_db["group_name"],
            group_description=group_db["group_description"],
            created_by_user_id=group_db["created_by_user_id"],
            created_at=group_db["created_at"],
            updated_at=group_db["updated_at"],
            members=members_db
        ))

    conn.close()
    return {"groups": all_groups_data}

@app.put("/api/groups/{group_id}", response_model=Dict[str, Any])
async def update_group_details(group_id: int, group_update: GroupUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if group_update.name is not None:
        updates.append("group_name = ?")
        params.append(group_update.name)
    if group_update.description is not None:
        updates.append("group_description = ?")
        params.append(group_update.description)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(datetime.now()) # updated_at
    params.append(group_id)

    query = f"UPDATE groups SET {', '.join(updates)}, updated_at = ? WHERE group_id = ?"
    try:
        cursor.execute(query, tuple(params))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Group not found")

        # Fetch the updated group to return
        cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
        updated_group_db = cursor.fetchone()

        cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
        members_db = [row["user_id"] for row in cursor.fetchall()]

        return {
            "message": "Group details updated successfully",
            "updated_group": Group(
                group_id=updated_group_db["group_id"],
                group_name=updated_group_db["group_name"],
                group_description=updated_group_db["group_description"],
                created_by_user_id=updated_group_db["created_by_user_id"],
                created_at=updated_group_db["created_at"],
                updated_at=updated_group_db["updated_at"],
                members=members_db
            )
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating group: {e}")
    finally:
        conn.close()

@app.delete("/api/groups/{group_id}", response_model=Dict[str, str])
async def delete_group(group_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM groups WHERE group_id = ?", (group_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Group not found")
        return {"message": "Group deleted successfully"}
    finally:
        conn.close()

@app.post("/api/groups/{group_id}/members", response_model=Dict[str, Any])
async def add_member_to_group(group_id: int, member_add: GroupMemberAdd):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if group exists
    cursor.execute("SELECT group_id FROM groups WHERE group_id = ?", (group_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if user exists
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (member_add.user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"User with ID {member_add.user_id} not found")

    try:
        cursor.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
            (group_id, member_add.user_id)
        )
        conn.commit()

        # Fetch updated members
        cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
        updated_members_db = [row["user_id"] for row in cursor.fetchall()]

        return {
            "message": "Member added to group successfully",
            "group_id": str(group_id),
            "updated_members": [str(m) for m in updated_members_db]
        }
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="User is already a member of this group")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding member: {e}")
    finally:
        conn.close()

@app.delete("/api/groups/{group_id}/members/{user_id}", response_model=Dict[str, Any])
async def remove_member_from_group(group_id: int, user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if group exists
    cursor.execute("SELECT group_id FROM groups WHERE group_id = ?", (group_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if user is a member
    cursor.execute("SELECT group_member_id FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id))
    member_row = cursor.fetchone()
    if not member_row:
        raise HTTPException(status_code=404, detail="User is not a member of this group")

    try:
        cursor.execute("DELETE FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user_id))
        conn.commit()

        # Fetch updated members
        cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
        updated_members_db = [row["user_id"] for row in cursor.fetchall()]

        return {
            "message": "Member removed from group successfully",
            "group_id": str(group_id),
            "updated_members": [str(m) for m in updated_members_db]
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error removing member: {e}")
    finally:
        conn.close()

@app.get("/api/groups/{group_id}/messages", response_model=Dict[str, Any])
async def get_group_messages(group_id: int, limit: Optional[int] = 20, offset: Optional[int] = 0):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if group exists
    cursor.execute("SELECT group_id FROM groups WHERE group_id = ?", (group_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")

    # Get messages with pagination
    cursor.execute(
        "SELECT COUNT(*) FROM messages WHERE group_id = ?",
        (group_id,)
    )
    total_messages = cursor.fetchone()[0]

    cursor.execute(
        "SELECT * FROM messages WHERE group_id = ? ORDER BY sent_at DESC LIMIT ? OFFSET ?",
        (group_id, limit, offset)
    )
    messages_db = cursor.fetchall()

    formatted_messages = []
    for msg_db in messages_db:
        formatted_messages.append(Message(
            message_id=msg_db["message_id"],
            group_id=msg_db["group_id"],
            sender_id=msg_db["sender_user_id"],
            content=msg_db["message_text"],
            media_url=msg_db["media_url"],
            media_type=msg_db["media_type"],
            timestamp=msg_db["sent_at"]
        ))

    conn.close()
    return {
        "messages": formatted_messages,
        "total_messages": total_messages
    }

@app.post("/api/messages", response_model=Message)
async def send_message(message_create: MessageCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # In a real app, sender_id would come from authentication.
    # For this example, we'll assume a sender_id is provided or we pick one.
    # Let's require sender_id for now.
    if not hasattr(message_create, 'sender_id') or message_create.sender_id is None:
         raise HTTPException(status_code=400, detail="Sender ID is required")

    # Check if group exists
    cursor.execute("SELECT group_id FROM groups WHERE group_id = ?", (message_create.group_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if sender is a member of the group
    cursor.execute("SELECT user_id FROM group_members WHERE group_id = ? AND user_id = ?", (message_create.group_id, message_create.sender_id))
    if not cursor.fetchone():
        raise HTTPException(status_code=403, detail="Sender is not a member of this group")

    try:
        cursor.execute(
            "INSERT INTO messages (group_id, sender_user_id, message_text, media_url, media_type) VALUES (?, ?, ?, ?, ?)",
            (message_create.group_id, message_create.sender_id, message_create.content, message_create.media_url, message_create.media_type)
        )
        message_id = cursor.lastrowid
        conn.commit()

        # Fetch the created message to return
        cursor.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))
        created_message_db = cursor.fetchone()

        return Message(
            message_id=created_message_db["message_id"],
            group_id=created_message_db["group_id"],
            sender_id=created_message_db["sender_user_id"],
            content=created_message_db["message_text"],
            media_url=created_message_db["media_url"],
            media_type=created_message_db["media_type"],
            timestamp=created_message_db["sent_at"]
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending message: {e}")
    finally:
        conn.close()

@app.post("/api/media/upload", response_model=MediaUploadResponse)
async def upload_media(file: UploadFile = File(...)):
    # In a real application, you would upload this file to a cloud storage service
    # like AWS S3, Google Cloud Storage, or a dedicated media server.
    # For this example, we'll just save it locally and return a placeholder URL.

    # Create a directory for uploads if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Generate a placeholder URL. In a real app, this would be a URL to your cloud storage.
    media_url = f"http://localhost:8080/static/{file.filename}" # Assuming static files are served

    return MediaUploadResponse(
        media_url=media_url,
        file_name=file.filename,
        file_type=file.content_type
    )

# --- Static File Serving (for media uploads) ---
# This is a basic setup. For production, use a more robust static file server.
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="uploads"), name="static")


# --- Main Execution ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)