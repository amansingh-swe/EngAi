# Generated Project

## Description
GroupChat is a social networking software application that allows users to create and participate in group chats with individuals who share common interests or hobbies. Users can join existing groups or create their own and invite others to join. Each group chat has text and multimedia messaging capabilities, allowing users to share content, discuss various topics, and build connections within the group. GroupChat provides a platform for users to engage in meaningful conversations and form communities around specific interests or hobbies.

## Requirements
make sure the backend code runs on port 8080

## Generated Files
- `main.py`: FastAPI backend REST API
- `frontend/`: React TypeScript frontend
- `docs/api_route_plan.json`: API route plan
- `database/schema.sql`: SQLite database schema
- `ARCHITECTURE.md`: Architecture document

## Installation
```bash
pip install -r requirements.txt
```

## Running

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm start
```
Frontend runs at `http://localhost:3000`

## Testing
```bash
pytest tests/
```
