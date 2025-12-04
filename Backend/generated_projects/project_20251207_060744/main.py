import sqlite3
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import bcrypt
import jwt
import os

# --- Configuration ---
DATABASE_NAME = "chat_app.db"
SECRET_KEY = os.environ.get("SECRET_KEY", "your-super-secret-key") # Use environment variable for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
BASE_URL = "http://localhost:8080/api"
UPLOAD_FOLDER = "uploads"

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Database Setup ---
def get_db():
    """Opens and returns a database connection."""
    db = sqlite3.connect(DATABASE_NAME)
    db.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    return db

def init_db():
    """Initializes the database with the schema if it doesn't exist."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            avatar_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_by_user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_groups_group_name ON groups (group_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_groups_created_by_user_id ON groups (created_by_user_id);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            group_member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE (group_id, user_id)
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_members_group_id ON group_members (group_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_members_user_id ON group_members (user_id);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            sender_user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            media_url TEXT,
            FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
            FOREIGN KEY (sender_user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_group_id ON messages (group_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender_user_id ON messages (sender_user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages (sent_at);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            message TEXT,
            read_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications (user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications (type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications (created_at);")

    db.commit()
    db.close()

# Initialize the database when the application starts
init_db()

# --- Pydantic Models ---

# User Models
class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    token: str

class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    email: str
    is_online: bool = False # Placeholder, actual implementation would involve presence tracking

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

# Group Models
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class GroupResponse(BaseModel):
    group_id: str
    name: str
    creator_id: str

class GroupDetailsResponse(BaseModel):
    group_id: str
    name: str
    description: Optional[str] = None
    members: List[str] # List of usernames or user_ids

class GroupListResponse(BaseModel):
    group_id: str
    name: str

# Message Models
class MessageCreate(BaseModel):
    group_id: str
    sender_id: str
    content: str
    media_url: Optional[str] = None

class MessageResponse(BaseModel):
    message_id: str
    group_id: str
    sender_id: str
    content: str
    timestamp: datetime
    media_url: Optional[str] = None

# Upload Models
class UploadResponse(BaseModel):
    media_url: str

# --- Security ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{BASE_URL}/users/login")

def create_access_token(data: dict):
    """Creates a JWT access token."""
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    """Verifies a JWT access token and returns the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    """Dependency to get the current user ID from the token."""
    payload = verify_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user_id

def get_user_from_db(db: sqlite3.Connection, user_id: int):
    """Fetches a user from the database by ID."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    return user

# --- Helper Functions ---
def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user_by_username(db: sqlite3.Connection, username: str):
    """Fetches a user from the database by username."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

def get_user_by_email(db: sqlite3.Connection, email: str):
    """Fetches a user from the database by email."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone()

def get_group_by_id(db: sqlite3.Connection, group_id: int):
    """Fetches a group from the database by ID."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
    return cursor.fetchone()

def get_group_members(db: sqlite3.Connection, group_id: int):
    """Fetches all members of a group."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.username FROM group_members gm
        JOIN users u ON gm.user_id = u.user_id
        WHERE gm.group_id = ?
    """, (group_id,))
    return [row["username"] for row in cursor.fetchall()]

def is_user_in_group(db: sqlite3.Connection, user_id: int, group_id: int) -> bool:
    """Checks if a user is a member of a group."""
    cursor = db.cursor()
    cursor.execute("SELECT 1 FROM group_members WHERE user_id = ? AND group_id = ?", (user_id, group_id))
    return cursor.fetchone() is not None

def get_user_id_from_username(db: sqlite3.Connection, username: str) -> Optional[int]:
    """Gets a user ID from their username."""
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_username_from_user_id(db: sqlite3.Connection, user_id: int) -> Optional[str]:
    """Gets a username from their user ID."""
    cursor = db.cursor()
    cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# --- FastAPI Application ---
app = FastAPI(
    title="Chat App API",
    description="API for a real-time chat application.",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- API Endpoints ---

@app.post("/api/users/register", response_model=UserResponse, tags=["Users"])
def register_user(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    """
    Registers a new user.
    """
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hash_password(user.password)
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (user.username, user.email, password_hash)
        )
        db.commit()
        user_id = cursor.lastrowid
        return UserResponse(user_id=str(user_id), username=user.username, email=user.email)
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database integrity error during registration")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/api/users/login", response_model=Token, tags=["Users"])
def login_user(user_login: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    """
    Logs in a user and returns an access token.
    """
    user = get_user_by_username(db, user_login.username)
    if not user or not verify_password(user_login.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": str(user["user_id"])})
    return Token(token=access_token)

@app.get("/api/users/{user_id}", response_model=UserProfileResponse, tags=["Users"])
def get_user_profile(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """
    Retrieves a user's profile information.
    """
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = get_user_from_db(db, user_id_int)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Placeholder for is_online. In a real app, this would involve a presence system.
    is_online = False

    return UserProfileResponse(
        user_id=str(user["user_id"]),
        username=user["username"],
        email=user["email"],
        is_online=is_online
    )

@app.patch("/api/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user_profile(
    user_id: str,
    user_update: UserUpdate,
    db: sqlite3.Connection = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Updates a user's profile information.
    Only the authenticated user can update their own profile.
    """
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if user_id_int != current_user_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    user = get_user_from_db(db, user_id_int)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = {}
    if user_update.username is not None:
        if get_user_by_username(db, user_update.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        updates["username"] = user_update.username
    if user_update.email is not None:
        if get_user_by_email(db, user_update.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        updates["email"] = user_update.email

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values()) + [user_id_int]

    cursor = db.cursor()
    try:
        cursor.execute(f"UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", values)
        db.commit()
        # Fetch the updated user to return
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id_int,))
        updated_user = cursor.fetchone()
        return UserResponse(
            user_id=str(updated_user["user_id"]),
            username=updated_user["username"],
            email=updated_user["email"]
        )
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database integrity error during update")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/api/groups", response_model=GroupResponse, tags=["Groups"])
def create_group(group: GroupCreate, db: sqlite3.Connection = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """
    Creates a new group.
    """
    if get_group_by_id(db, group.name): # Check if group name already exists
        raise HTTPException(status_code=400, detail="Group name already exists")

    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO groups (group_name, description, created_by_user_id) VALUES (?, ?, ?)",
            (group.name, group.description, current_user_id)
        )
        group_id = cursor.lastrowid

        # Add the creator as the first member
        cursor.execute(
            "INSERT INTO group_members (group_id, user_id, role) VALUES (?, ?, ?)",
            (group_id, current_user_id, 'admin') # Creator is an admin
        )
        db.commit()
        return GroupResponse(group_id=str(group_id), name=group.name, creator_id=str(current_user_id))
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database integrity error during group creation")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/api/groups", response_model=List[GroupListResponse], tags=["Groups"])
def get_user_groups(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """
    Retrieves all groups a user is a member of.
    """
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Verify user exists
    if not get_user_from_db(db, user_id_int):
        raise HTTPException(status_code=404, detail="User not found")

    cursor = db.cursor()
    cursor.execute("""
        SELECT g.group_id, g.group_name
        FROM groups g
        JOIN group_members gm ON g.group_id = gm.group_id
        WHERE gm.user_id = ?
    """, (user_id_int,))
    groups = [GroupListResponse(group_id=str(row["group_id"]), name=row["group_name"]) for row in cursor.fetchall()]
    return groups

@app.get("/api/groups/{group_id}", response_model=GroupDetailsResponse, tags=["Groups"])
def get_group_details(group_id: str, db: sqlite3.Connection = Depends(get_db)):
    """
    Retrieves details of a specific group, including its members.
    """
    try:
        group_id_int = int(group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group ID format")

    group = get_group_by_id(db, group_id_int)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    members = get_group_members(db, group_id_int)

    return GroupDetailsResponse(
        group_id=str(group["group_id"]),
        name=group["group_name"],
        description=group["description"],
        members=members
    )

@app.post("/api/groups/{group_id}/join", response_model={}, tags=["Groups"])
def join_group(group_id: str, db: sqlite3.Connection = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """
    Allows a user to join a group.
    """
    try:
        group_id_int = int(group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group ID format")

    group = get_group_by_id(db, group_id_int)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if is_user_in_group(db, current_user_id, group_id_int):
        raise HTTPException(status_code=400, detail="You are already a member of this group")

    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
            (group_id_int, current_user_id)
        )
        db.commit()
        return {"message": "Successfully joined the group"}
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database integrity error when joining group")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/api/groups/{group_id}/leave", response_model={}, tags=["Groups"])
def leave_group(group_id: str, db: sqlite3.Connection = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """
    Allows a user to leave a group.
    """
    try:
        group_id_int = int(group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group ID format")

    group = get_group_by_id(db, group_id_int)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if not is_user_in_group(db, current_user_id, group_id_int):
        raise HTTPException(status_code=400, detail="You are not a member of this group")

    # Prevent leaving if you are the only admin and the creator
    cursor = db.cursor()
    cursor.execute("SELECT role FROM group_members WHERE user_id = ? AND group_id = ?", (current_user_id, group_id_int))
    user_role = cursor.fetchone()
    if user_role and user_role["role"] == 'admin' and group["created_by_user_id"] == current_user_id:
        cursor.execute("SELECT COUNT(*) FROM group_members WHERE group_id = ? AND role = 'admin'", (group_id_int,))
        admin_count = cursor.fetchone()[0]
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="You cannot leave as you are the only admin and creator of the group.")

    try:
        cursor.execute("DELETE FROM group_members WHERE group_id = ? AND user_id = ?", (group_id_int, current_user_id))
        db.commit()
        return {"message": "Successfully left the group"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/api/messages", response_model=MessageResponse, tags=["Messages"])
def send_message(
    message: MessageCreate,
    db: sqlite3.Connection = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Sends a message to a group.
    """
    try:
        group_id_int = int(message.group_id)
        sender_id_int = int(message.sender_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group ID or sender ID format")

    if group_id_int not in [g["group_id"] for g in get_user_groups(db, str(current_user_id))]:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    if sender_id_int != current_user_id:
        raise HTTPException(status_code=403, detail="Sender ID must match authenticated user ID")

    group = get_group_by_id(db, group_id_int)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO messages (group_id, sender_user_id, content, media_url) VALUES (?, ?, ?, ?)",
            (group_id_int, sender_id_int, message.content, message.media_url)
        )
        db.commit()
        message_id = cursor.lastrowid

        # Fetch the created message to return
        cursor.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))
        created_message = cursor.fetchone()

        return MessageResponse(
            message_id=str(created_message["message_id"]),
            group_id=str(created_message["group_id"]),
            sender_id=str(created_message["sender_user_id"]),
            content=created_message["content"],
            timestamp=created_message["sent_at"],
            media_url=created_message["media_url"]
        )
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database integrity error during message sending")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/api/messages/{group_id}", response_model=List[MessageResponse], tags=["Messages"])
def get_messages_in_group(
    group_id: str,
    limit: Optional[int] = 20,
    before: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Retrieves messages from a specific group.
    Supports pagination with 'limit' and 'before' (message_id).
    """
    try:
        group_id_int = int(group_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group ID format")

    if not is_user_in_group(db, current_user_id, group_id_int):
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    cursor = db.cursor()
    query = """
        SELECT * FROM messages
        WHERE group_id = ?
    """
    params = [group_id_int]

    if before:
        try:
            before_message_id_int = int(before)
            cursor.execute("SELECT sent_at FROM messages WHERE message_id = ?", (before_message_id_int,))
            before_timestamp_result = cursor.fetchone()
            if not before_timestamp_result:
                raise HTTPException(status_code=404, detail="Message ID for 'before' parameter not found")
            before_timestamp = before_timestamp_result["sent_at"]
            query += " AND sent_at < ? ORDER BY sent_at DESC"
            params.append(before_timestamp)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'before' message ID format")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing 'before' parameter: {e}")
    else:
        query += " ORDER BY sent_at DESC"

    query += " LIMIT ?"
    params.append(limit)

    cursor.execute(query, tuple(params))
    messages_rows = cursor.fetchall()

    # Reverse to maintain chronological order in response if 'before' was used
    if before:
        messages_rows.reverse()

    messages = [
        MessageResponse(
            message_id=str(row["message_id"]),
            group_id=str(row["group_id"]),
            sender_id=str(row["sender_user_id"]) if row["sender_user_id"] else None, # Handle potential NULL sender_user_id
            content=row["content"],
            timestamp=row["sent_at"],
            media_url=row["media_url"]
        )
        for row in messages_rows
    ]
    return messages

@app.post("/api/upload", response_model=UploadResponse, tags=["Upload"])
async def upload_media(file: UploadFile = File(...), db: sqlite3.Connection = Depends(get_db)):
    """
    Uploads a media file and returns its URL.
    (This is a simplified implementation. In a real app, you'd use cloud storage like S3.)
    """
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        # In a real application, you would upload this to a cloud storage service
        # and return the permanent URL. For this example, we return a local path.
        media_url = f"/static/{file.filename}" # Assuming static files are served
        return UploadResponse(media_url=media_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

# --- Main Application Runner ---
if __name__ == "__main__":
    # This block is for running the app directly with `python main.py`
    # For `uvicorn main:app --reload`, this block is not strictly necessary
    # but good for local development.
    uvicorn.run(app, host="0.0.0.0", port=8080)