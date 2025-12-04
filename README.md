# EngAi - Multi-Agent MCP System

A complete multi-agent system that uses the Model Context Protocol (MCP) to generate complete software applications from descriptions. The system uses Google's Gemini API, includes a web-based UI, and tracks LLM usage.

## Project Overview

EngAi is an AI-powered software generation system that takes a software description and requirements as input and generates:
- Complete software architecture
- Executable code (Python)
- Comprehensive test cases

The system uses a multi-agent architecture where specialized agents collaborate using the Model Context Protocol (MCP) to accomplish the task.

## Architecture

### Multi-Agent System

The system consists of six specialized agents:

1. **Orchestrator Agent**: Coordinates the entire generation process
2. **Architect Agent**: Analyzes requirements and creates software architecture
3. **Database Agent**: Creates SQLite database schema and setup code
4. **Backend Code Generator Agent**: Generates FastAPI REST API backend code with database integration based on architecture and schema
5. **Frontend Generator Agent**: Generates React frontend application that consumes the backend API
6. **Test Generator Agent**: Creates comprehensive test cases for the generated code

### Technology Stack

- **Backend**: Python 3.9+ with FastAPI
- **LLM**: Google Gemini API (gemini-pro)
- **Frontend**: Next.js 14 with React and TypeScript
- **Styling**: Tailwind CSS
- **Database**: SQLite (for usage tracking)
- **Communication**: Model Context Protocol (MCP) for agent-to-agent communication

## Project Structure

```
EngAi/
├── Backend/
│   ├── src/
│   │   ├── agents/          # Multi-agent system
│   │   │   ├── base_agent.py
│   │   │   ├── orchestrator_agent.py
│   │   │   ├── architect_agent.py
│   │   │   ├── code_generator_agent.py
│   │   │   └── test_generator_agent.py
│   │   ├── mcp/             # MCP servers and clients
│   │   │   ├── server.py
│   │   │   ├── client.py
│   │   │   └── message.py
│   │   ├── llm/             # Gemini integration
│   │   │   └── gemini_service.py
│   │   ├── tracking/        # Usage tracking
│   │   │   └── usage_tracker.py
│   │   ├── api/             # FastAPI endpoints
│   │   │   └── main.py
│   │   └── main.py          # FastAPI application entry point
│   └── requirements.txt
├── Frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── SoftwareDescriptionForm.tsx
│   │   │   ├── CodeDisplay.tsx
│   │   │   ├── TestDisplay.tsx
│   │   │   └── UsageStats.tsx
│   │   ├── pages/           # Next.js pages
│   │   │   ├── index.tsx
│   │   │   └── _app.tsx
│   │   ├── api/             # API client
│   │   │   └── client.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── package.json
│   └── next.config.js
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd EngAi
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd Backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd Frontend

# Install dependencies
npm install
# or
yarn install
```

#### 4. Environment Configuration

Create a `.env` file in the `Backend` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./usage_tracking.db
BACKEND_PORT=8000
ENVIRONMENT=development
OUTPUT_DIR=./generated_projects
GEMINI_MODEL=gemini-2.5-flash-lite
```

**Environment Variables:**
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `DATABASE_URL`: SQLite database URL for usage tracking (optional, defaults to `./usage_tracking.db`)
- `OUTPUT_DIR`: Directory where generated projects will be saved (optional, defaults to `./generated_projects`)
- `GEMINI_MODEL`: Gemini model to use (optional, defaults to `gemini-2.5-flash-lite`)

Create a `.env.local` file in the `Frontend` directory (optional):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running the Application

#### 1. Start the Backend Server

```bash
# From Backend directory
cd Backend
python src/main.py
```

Or using uvicorn directly:

```bash
uvicorn src.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

#### 2. Start the Frontend Development Server

```bash
# From Frontend directory
cd Frontend
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Enter a software description in the form (e.g., "A simple calculator that can add, subtract, multiply, and divide two numbers")
3. Optionally add specific requirements
4. Click "Generate Software"
5. Wait for the system to generate:
   - Software architecture
   - Complete executable code
   - Test cases
6. View usage statistics at the bottom of the page

## API Endpoints

### POST /api/generate

Generate software from description and requirements.

**Request Body:**
```json
{
  "description": "Software description",
  "requirements": "Optional requirements",
  "save_files": true,
  "project_name": "my-project"
}
```

**Response:**
```json
{
  "architecture": "Architecture document",
  "database_schema": "SQLite database schema and setup code",
  "code": "Generated FastAPI backend REST API code with database integration",
  "frontend_code": "Generated React frontend application code",
  "tests": "Generated test cases",
  "success": true,
  "files": {
    "project_path": "./generated_projects/my-project_20240101_120000",
    "architecture_file": "./generated_projects/my-project_20240101_120000/ARCHITECTURE.md",
    "database_schema_file": "./generated_projects/my-project_20240101_120000/database/schema.sql",
    "code_file": "./generated_projects/my-project_20240101_120000/main.py",
    "test_file": "./generated_projects/my-project_20240101_120000/tests/test_main.py",
    "readme_file": "./generated_projects/my-project_20240101_120000/README.md",
    "requirements_file": "./generated_projects/my-project_20240101_120000/requirements.txt"
  }
}
```

### GET /api/usage

Get LLM usage statistics.

**Response:**
```json
{
  "total_api_calls": 10,
  "total_input_tokens": 5000,
  "total_output_tokens": 3000,
  "total_tokens": 8000,
  "agents": [
    {
      "agent_name": "architect",
      "total_api_calls": 3,
      "total_input_tokens": 2000,
      "total_output_tokens": 1000,
      "total_tokens": 3000
    }
  ]
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "EngAi Multi-Agent MCP System"
}
```

## How It Works

1. **User Input**: User provides software description and requirements through the web UI
2. **Orchestration**: Orchestrator agent receives the request
3. **Architecture Generation**: Orchestrator calls Architect agent via MCP to create software architecture
4. **Database Schema Generation**: Orchestrator calls Database agent via MCP to create SQLite database schema
5. **Backend API Generation**: Orchestrator calls Backend Code Generator agent via MCP to generate FastAPI REST API with database integration
6. **Frontend Generation**: Orchestrator calls Frontend Generator agent via MCP to generate React frontend that consumes the backend API
7. **Test Generation**: Orchestrator calls Test Generator agent via MCP to create test cases
8. **File Generation**: Generated code, frontend, database schema, and tests are saved to files in the output directory (if `save_files` is true)
9. **Usage Tracking**: All LLM API calls are tracked and stored in SQLite database
10. **Response**: Complete software (architecture, database schema, backend API, frontend, tests) is returned to the user with file paths

## File Generation

The system automatically generates a complete project structure when `save_files` is enabled (default: true):

```
generated_projects/
└── project-name_20240101_120000/
    ├── main.py                 # FastAPI backend REST API with SQLite integration
    ├── ARCHITECTURE.md         # Architecture document
    ├── README.md              # Project README
    ├── requirements.txt        # Python dependencies (includes fastapi, uvicorn)
    ├── frontend/               # React frontend application
    │   ├── src/
    │   │   ├── App.tsx        # Main application component
    │   │   ├── components/    # React components
    │   │   ├── services/       # API client services
    │   │   └── types/         # TypeScript type definitions
    │   └── package.json       # Frontend dependencies
    ├── database/
    │   ├── schema.sql         # SQLite database schema
    │   └── init_db.py         # Database initialization script
    └── tests/
        └── test_main.py       # Generated test cases
```

**Configuration:**
- Set `OUTPUT_DIR` environment variable to change the output directory (default: `./generated_projects`)
- Set `save_files: false` in the API request to disable file generation
- Provide `project_name` in the request to customize the project folder name

## Model Context Protocol (MCP)

The system implements a simplified MCP for agent-to-agent communication:

- **MCP Server**: Handles message routing and tool execution
- **MCP Client**: Provides interface for agents to communicate
- **Message Types**: Request, Response, Notification, Error
- **Tool Registration**: Agents can register tools that other agents can call

## Usage Tracking

The system tracks:
- Total API calls to the LLM
- Input tokens consumed
- Output tokens generated
- Total tokens used
- Per-agent statistics

All usage data is stored in a SQLite database and can be viewed through the web UI or API.

## Development

### Running Tests

```bash
# Backend tests (when implemented)
cd Backend
pytest

# Frontend tests (when implemented)
cd Frontend
npm test
```

### Code Style

- Backend: Follow PEP 8 style guide
- Frontend: ESLint and Prettier configuration

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure you're in the virtual environment and all dependencies are installed
- **API key errors**: Verify your `GEMINI_API_KEY` is set correctly in the `.env` file
- **Port already in use**: Change the port in `src/main.py` or use `--port` flag with uvicorn

### Frontend Issues

- **API connection errors**: Verify the backend is running and `NEXT_PUBLIC_API_URL` is correct
- **Build errors**: Clear `.next` directory and reinstall dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Specify your license here]

## Support

For issues and questions, please open an issue on the repository.

## Future Enhancements

- Support for multiple programming languages
- Code execution and validation
- Integration with version control systems
- Advanced agent capabilities
- Real-time collaboration features
- Enhanced error handling and retry mechanisms

