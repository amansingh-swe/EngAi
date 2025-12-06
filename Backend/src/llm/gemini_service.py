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
    
    ARCHITECT_TEMPLATE = """Create a high-level software architecture document.

Description: {description}
Requirements: {requirements}

Output a structured architecture document covering:
- System components and their relationships
- Technology stack recommendations
- Data flow and interactions"""

    API_ROUTE_PLANNER_TEMPLATE = """Generate API route plan JSON from the architecture.

Architecture: {architecture}

Output JSON format:
```json
{{
  "api_route_plan": {{
    "base_url": "http://localhost:8000/api",
    "routes": [
      {{
        "method": "GET|POST|PUT|PATCH|DELETE",
        "path": "/resource",
        "body_schema": {{"field": "type"}} or null,
        "query_params": {{"param": "type"}} or null,
        "path_params": {{"param": "type"}} or null,
        "response_schema": {{"field": "type"}}
      }}
    ]
  }}
}}
```

Include all CRUD endpoints needed. Output only JSON."""

    DATABASE_TEMPLATE = """Generate SQLite database schema from the architecture.

Architecture: {architecture}

Output SQL CREATE TABLE statements:
```sql
CREATE TABLE IF NOT EXISTS table_name (
    id INTEGER PRIMARY KEY,
    column_name TYPE NOT NULL,
    FOREIGN KEY (column) REFERENCES other_table(id)
);
```

Include all tables, primary keys, foreign keys, and NOT NULL constraints. Output only SQL."""

    CODE_GENERATOR_TEMPLATE = """Generate FastAPI backend code implementing the API routes with SQLite.

API Routes: {api_route_plan}
Database Schema: {database_schema}

Generate:
1. FastAPI app with imports (fastapi, uvicorn, pydantic, sqlite3)
2. Database connection and init using the SQL schema
3. Pydantic models matching database tables
4. All endpoints from the route plan with CRUD operations
5. Error handling (HTTPException)
6. CORS middleware
7. Single file: main.py (runnable with uvicorn main:app --reload)

After the code, include requirements.txt:
```txt:requirements.txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
```
Add any other dependencies used."""

    FRONTEND_GENERATOR_TEMPLATE = """Generate React JavaScript frontend for this application with CSS styling for these API routes:

Application Description: {application_description}

Api route plan: {api_route_plan}

Create components, API service (fetch), forms, and lists for all routes with modern, clean CSS styling.

Output each file in this format:
```javascript:src/path/file.jsx
// code
```

Required files:
1. ```html:public/index.html``` - HTML with root div
2. ```javascript:src/index.jsx``` - Entry point rendering App (import './App.css')
3. ```javascript:src/App.jsx``` - Main app component with className attributes (not inline styles)
4. ```css:src/App.css``` - Modern CSS styling with:
   - Clean layout (flexbox/grid)
   - Styled forms (inputs, buttons, labels with padding, borders, focus states)
   - Navigation bar styling (background, spacing, hover effects)
   - Card/list styling (borders, shadows, padding, margins)
   - Responsive design basics (max-width, padding)
   - Color scheme (use CSS variables for primary/secondary colors)
   - Button hover effects and transitions
   - Consistent spacing and typography
   - Error messages styled in red
   - Loading states styled appropriately
5. ```javascript:src/services/api.js``` - Fetch functions for all endpoints
6. ```javascript:src/components/[ComponentName].jsx``` - Component per route with className attributes
7. ```json:package.json``` - Dependencies: react, react-dom, react-scripts

Style requirements:
- Use CSS classes (className) not inline styles
- Modern, professional appearance
- Consistent spacing and colors
- Styled buttons, inputs, forms
- Navigation bar with hover effects
- Card-based layouts for lists/details
- Error messages styled in red
- Loading states styled appropriately

Use JavaScript (.jsx/.js), not TypeScript."""

    TEST_GENERATOR_TEMPLATE = """Generate pytest test cases for this FastAPI code:

{code}

Create tests covering:
- Normal operations
- Edge cases
- Error handling
- Boundary conditions

Use pytest fixtures where needed. Output complete, executable test code."""

