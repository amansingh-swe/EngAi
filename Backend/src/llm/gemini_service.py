"""
Gemini LLM service for interacting with Google's Gemini API.
"""
import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini service with API key."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        
        # Use model from environment or default to gemini-2.5-flash-lite
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.model = self._initialize_model(model_name)
        self.model_name = model_name
    
    def _initialize_model(self, model_name: str):
        """
        Initialize a Gemini model with fallback options.
        
        Args:
            model_name: Name of the model to initialize
        
        Returns:
            Initialized GenerativeModel
        """
        # List of models to try in order
        models_to_try = [
            model_name,
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]
        
        last_error = None
        for model in models_to_try:
            try:
                return genai.GenerativeModel(model)
            except Exception as e:
                last_error = e
                continue
        
        # If all models fail, try to list available models
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Extract just the model name (e.g., "models/gemini-1.5-flash" -> "gemini-1.5-flash")
                    model_id = m.name.split('/')[-1] if '/' in m.name else m.name
                    available_models.append(model_id)
            
            raise ValueError(
                f"Failed to initialize any Gemini model. "
                f"Tried: {models_to_try}. "
                f"Available models with generateContent support: {available_models}. "
                f"Last error: {str(last_error)}"
            )
        except Exception as list_error:
            raise ValueError(
                f"Failed to initialize Gemini model and could not list available models. "
                f"Please check your API key. Error: {str(last_error)}. "
                f"List error: {str(list_error)}"
            )
    
    def generate(
        self,
        prompt: str,
        agent_name: str = "default",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using Gemini API.
        
        Args:
            prompt: The input prompt
            agent_name: Name of the agent making the request
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (optional)
        
        Returns:
            Dictionary containing:
                - text: Generated response text
                - usage: Token usage information
                - agent_name: Name of the agent
        """
        try:
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract usage information
            usage_info = {
                "input_tokens": len(prompt.split()),  # Approximate
                "output_tokens": len(response.text.split()) if response.text else 0,  # Approximate
                "total_tokens": len(prompt.split()) + (len(response.text.split()) if response.text else 0)
            }
            
            return {
                "text": response.text if response.text else "",
                "usage": usage_info,
                "agent_name": agent_name
            }
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_with_template(
        self,
        template: str,
        variables: Dict[str, str],
        agent_name: str = "default",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a response using a template with variable substitution.
        
        Args:
            template: Prompt template with {variable} placeholders
            variables: Dictionary of variables to substitute
            agent_name: Name of the agent making the request
            temperature: Sampling temperature
        
        Returns:
            Dictionary containing response and usage information
        """
        prompt = template.format(**variables)
        return self.generate(prompt, agent_name, temperature)


# Prompt templates for different agent roles
class PromptTemplates:
    """Prompt templates for different agent roles."""
    
    ARCHITECT_TEMPLATE = """You are an expert software architect. Your task is to analyze the following software description and requirements, then create a detailed software architecture.

Software Description:
{description}

Requirements:
{requirements}

Please provide:
1. A high-level architecture overview

Format your response as a structured architecture document."""

    API_ROUTE_PLANNER_TEMPLATE = """Based on the architecture below, generate a concise API route plan with only the information needed to implement the endpoints.

Architecture:
{architecture}

Requirements:
{requirements}

Output JSON with routes containing:
- method: HTTP method (GET, POST, PUT, PATCH, DELETE)
- path: Endpoint path
- body_schema: Request body fields and types (for POST/PUT/PATCH, null for GET/DELETE)
- query_params: Query parameters as {{"param": "type"}} (null if none)
- path_params: Path parameters as {{"param": "type"}} (null if none)
- response_schema: Response data structure

```json
{{
  "api_route_plan": {{
    "base_url": "http://localhost:8000/api",
    "routes": [
      {{
        "method": "GET",
        "path": "/items",
        "body_schema": null,
        "query_params": {{"page": "integer", "limit": "integer"}},
        "path_params": null,
        "response_schema": [{{"id": "integer", "name": "string"}}]
      }},
      {{
        "method": "POST",
        "path": "/items",
        "body_schema": {{"name": "string", "description": "string"}},
        "query_params": null,
        "path_params": null,
        "response_schema": {{"id": "integer", "name": "string", "description": "string"}}
      }},
      {{
        "method": "GET",
        "path": "/items/{{id}}",
        "body_schema": null,
        "query_params": null,
        "path_params": {{"id": "integer"}},
        "response_schema": {{"id": "integer", "name": "string", "description": "string"}}
      }}
    ]
  }}
}}
```

Include all CRUD operations needed. Keep it minimal - only what's needed to generate the code."""

    DATABASE_TEMPLATE = """You are an expert database designer. Based on the following architecture and requirements, create a SQLite database schema.

Architecture:
{architecture}

Requirements:
{requirements}

Please generate SQL CREATE TABLE statements for SQLite with:
1. All necessary tables with appropriate columns, data types, and constraints
2. Primary keys and foreign keys where applicable
3. Indexes for performance if needed
4. NOT NULL constraints where appropriate

Format your response as SQL schema in a code block:

```sql
CREATE TABLE IF NOT EXISTS table_name (
    column1 TYPE CONSTRAINT,
    column2 TYPE CONSTRAINT,
    ...
    PRIMARY KEY (column1),
    FOREIGN KEY (column2) REFERENCES other_table(id)
);
```

Be specific and create a complete, working SQL schema. Only output the SQL schema, no other code or explanations."""

    CODE_GENERATOR_TEMPLATE = """You are an expert Python developer specializing in FastAPI. Based on the following API route plan and database schema, generate a complete FastAPI backend REST API with SQLite database integration.

API Route Plan:
{api_route_plan}

Database Schema:
{database_schema}

Requirements:
{requirements}

Please generate a complete FastAPI backend API with:
1. FastAPI application setup with proper imports (fastapi, uvicorn, pydantic, sqlite3)
2. Database connection and initialization using the provided SQLite schema and initialization code
3. Pydantic models for request/response validation based on the database tables
4. REST API endpoints based on the requirements:
   - GET endpoints for retrieving data
   - POST endpoints for creating data
   - PUT/PATCH endpoints for updating data (if needed)
   - DELETE endpoints for deleting data (if needed)
5. Proper error handling with HTTPException
6. Database CRUD operations using SQLite
7. CORS middleware configuration
8. Clear comments and documentation
9. Follow Python best practices (PEP 8)
10. Use the provided API route plan to implement all specified endpoints
11. Use the provided database schema to create appropriate endpoints

Structure the code as a single FastAPI application file that can be run with: uvicorn main:app --reload

IMPORTANT: After the code, also provide a requirements.txt file with all necessary Python dependencies. Format it as:

```txt:requirements.txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
# Add all other dependencies used in the code (e.g., bcrypt, jwt, python-multipart, etc.)
```

Include all packages imported in the code (fastapi, uvicorn, pydantic, sqlite3 is built-in, but add any other third-party packages like bcrypt, python-jose, python-multipart, etc.)
"""

    FRONTEND_GENERATOR_TEMPLATE = """Generate React JavaScript frontend for these API routes:

{api_route_plan}

Requirements: {requirements}

Create:
- Components for each route
- API service (fetch)
- Forms (POST/PUT/PATCH)
- Lists (GET)
- Delete (DELETE)

Output Format:
For each file, use this format:
```javascript:src/path/to/file.jsx
// file content here
```

Required files (MUST include all):
1. ```html:public/index.html
   // Main HTML file with root div
   ```

2. ```javascript:src/index.jsx
   // Entry point that renders App component
   ```

3. ```javascript:src/App.jsx
   // Main app component
   ```

4. ```javascript:src/services/api.js
   // API service with fetch functions
   ```

5. ```javascript:src/components/[ComponentName].jsx
   // Individual components (one per route)
   ```

6. ```json:package.json
   // Dependencies: react, react-dom, react-scripts
   // Scripts: start, build, test, eject
   ```

Generate all files in the format above. Each file must be in a separate code block with the file path. Use JavaScript (.jsx, .js), not TypeScript. The public/index.html and src/index.jsx are REQUIRED for the app to run."""

    TEST_GENERATOR_TEMPLATE = """You are an expert in software testing. Based on the following code, generate comprehensive test cases.

Code:
{code}

Requirements:
{requirements}

Please generate:
1. Unit tests using pytest
2. Test cases covering:
   - Normal operation
   - Edge cases
   - Error handling
   - Boundary conditions
3. Test fixtures where needed
4. Clear test names and documentation

Generate complete, executable test code."""


