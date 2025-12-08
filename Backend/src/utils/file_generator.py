"""
Aman singh(67401334)
Sanmith Kurian (22256557)
Yash Agarwal (35564877)
Swapnil Nagras (26761683)

File generation service for saving generated code and tests to files.
"""
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class FileGenerator:
    """Service for generating and saving project files."""
    
    def __init__(self, base_output_dir: Optional[str] = None):
        """
        Initialize the file generator.
        
        Args:
            base_output_dir: Base directory for generated files (defaults to OUTPUT_DIR env var or ./generated_projects)
        """
        self.base_output_dir = base_output_dir or os.getenv(
            "OUTPUT_DIR", 
            os.path.join(os.getcwd(), "generated_projects")
        )
        # Ensure base directory exists
        Path(self.base_output_dir).mkdir(parents=True, exist_ok=True)
    
    def create_project_folder(self, project_name: Optional[str] = None) -> str:
        """
        Create a project folder with a unique name.
        
        Args:
            project_name: Optional project name (will be sanitized)
        
        Returns:
            Path to the created project folder
        """
        if project_name:
            # Sanitize project name
            project_name = re.sub(r'[^\w\s-]', '', project_name)
            project_name = re.sub(r'[-\s]+', '-', project_name)
            project_name = project_name[:50]  # Limit length
        else:
            project_name = "project"
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{project_name}_{timestamp}"
        
        project_path = os.path.join(self.base_output_dir, folder_name)
        Path(project_path).mkdir(parents=True, exist_ok=True)
        
        return project_path
    
    def save_architecture(self, project_path: str, architecture: str) -> str:
        """
        Save architecture document to a file.
        
        Args:
            project_path: Path to the project folder
            architecture: Architecture content
        
        Returns:
            Path to the saved architecture file
        """
        arch_path = os.path.join(project_path, "ARCHITECTURE.md")
        with open(arch_path, 'w', encoding='utf-8') as f:
            f.write(architecture)
        return arch_path
    
    def save_code(self, project_path: str, code: str, filename: str = "main.py") -> str:
        """
        Save FastAPI backend API code to a file.
        
        Args:
            project_path: Path to the project folder
            code: Code content (FastAPI backend code)
            filename: Name of the code file (default: main.py for FastAPI)
        
        Returns:
            Path to the saved code file
        """
        # Extract code blocks if present (markdown code blocks)
        code_content = self._extract_code_from_markdown(code)
        
        code_path = os.path.join(project_path, filename)
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        return code_path
    
    def save_tests(self, project_path: str, tests: str, filename: str = "test_main.py") -> str:
        """
        Save test cases to a file.
        
        Args:
            project_path: Path to the project folder
            tests: Test code content
            filename: Name of the test file (default: test_main.py)
        
        Returns:
            Path to the saved test file
        """
        # Create tests directory if it doesn't exist
        tests_dir = os.path.join(project_path, "tests")
        Path(tests_dir).mkdir(parents=True, exist_ok=True)
        
        # Extract code blocks if present
        test_content = self._extract_code_from_markdown(tests)
        
        test_path = os.path.join(tests_dir, filename)
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        return test_path
    
    def save_readme(self, project_path: str, description: str, requirements: str = "") -> str:
        """
        Save a README file for the project.
        
        Args:
            project_path: Path to the project folder
            description: Project description
            requirements: Project requirements
        
        Returns:
            Path to the saved README file
        """
        readme_content = f"""# Generated Project

## Description
{description}

## Requirements
{requirements if requirements else "None specified"}

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
"""
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        return readme_path
    
    def save_requirements(self, project_path: str, requirements_content: Optional[str] = None) -> str:
        """
        Save a requirements.txt file.
        
        Args:
            project_path: Path to the project folder
            requirements_content: Optional requirements content (defaults to basic pytest)
        
        Returns:
            Path to the saved requirements file
        """
        if not requirements_content:
            requirements_content = "fastapi>=0.104.0\nuvicorn[standard]>=0.24.0\npydantic>=2.5.0\npytest>=7.0.0\n"
        
        req_path = os.path.join(project_path, "requirements.txt")
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        return req_path
    
    def save_database_schema(self, project_path: str, database_schema: str) -> str:
        """
        Save database schema to file.
        
        Args:
            project_path: Path to the project folder
            database_schema: SQL schema content
        
        Returns:
            Path to the saved database schema file
        """
        # Create database directory
        db_dir = os.path.join(project_path, "database")
        Path(db_dir).mkdir(parents=True, exist_ok=True)
        
        # Extract SQL from the schema (in case it's in a code block)
        sql_content = self._extract_sql_from_schema(database_schema)
        
        # Save SQL schema
        sql_path = os.path.join(db_dir, "schema.sql")
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        return sql_path
    
    def _extract_sql_from_schema(self, content: str) -> str:
        """
        Extract SQL code from database schema content.
        
        Args:
            content: Database schema content that may contain SQL code blocks
        
        Returns:
            Extracted SQL code
        """
        # Check for SQL code blocks
        sql_pattern = r'```sql\s*\n(.*?)```'
        match = re.search(sql_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Check for generic code blocks that might be SQL
        code_pattern = r'```\s*\n(.*?CREATE.*?)\n```'
        match = re.search(code_pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # If no code blocks, return content as-is (might be plain SQL)
        return content.strip()
    
    def _extract_python_from_schema(self, content: str) -> str:
        """
        Extract Python code from database schema content.
        
        Args:
            content: Database schema content that may contain Python code blocks
        
        Returns:
            Extracted Python code or empty string
        """
        # Check for Python code blocks
        python_pattern = r'```python\s*\n(.*?)```'
        match = re.search(python_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def save_api_documentation(self, project_path: str, api_documentation: Dict[str, Any]) -> str:
        """
        Save API documentation to a JSON file.
        
        Args:
            project_path: Path to the project folder
            api_documentation: API documentation dictionary
        
        Returns:
            Path to the saved API documentation file
        """
        import json
        
        # Create docs directory if it doesn't exist
        docs_dir = os.path.join(project_path, "docs")
        Path(docs_dir).mkdir(parents=True, exist_ok=True)
        
        # Save as JSON file
        api_doc_path = os.path.join(docs_dir, "api_documentation.json")
        with open(api_doc_path, 'w', encoding='utf-8') as f:
            json.dump(api_documentation, f, indent=2, ensure_ascii=False)
        
        return api_doc_path
    
    def save_api_route_plan(self, project_path: str, api_route_plan: Dict[str, Any]) -> str:
        """
        Save API route plan to a JSON file.
        
        Args:
            project_path: Path to the project folder
            api_route_plan: API route plan dictionary
        
        Returns:
            Path to the saved API route plan file
        """
        import json
        
        # Create docs directory if it doesn't exist
        docs_dir = os.path.join(project_path, "docs")
        Path(docs_dir).mkdir(parents=True, exist_ok=True)
        
        # Save as JSON file
        route_plan_path = os.path.join(docs_dir, "api_route_plan.json")
        with open(route_plan_path, 'w', encoding='utf-8') as f:
            json.dump(api_route_plan, f, indent=2, ensure_ascii=False)
        
        return route_plan_path
    
    def save_frontend(self, project_path: str, frontend_code: str) -> Dict[str, str]:
        """Save frontend code to files. Expects format: ```javascript:src/path/to/file.jsx\ncontent```"""
        frontend_path = os.path.join(project_path, "frontend")
        Path(frontend_path).mkdir(parents=True, exist_ok=True)
        
        files_saved = {}
        import re
        
        # Pattern matches: ```javascript:src/path/to/file.jsx\ncontent```
        # Also handles: ```jsx:path```, ```json:package.json```, etc.
        # Pattern: language tag, colon, filepath, then content
        # More specific: requires language tag and colon before filepath to avoid false matches
        file_pattern = r'```(?:javascript|jsx|js|typescript|tsx|ts|json|css|html):([^\n]+)\n(.*?)```'
        matches = re.findall(file_pattern, frontend_code, re.DOTALL)
        
        if matches:
            for match in matches:
                filepath = match[0].strip() if match[0] else None
                content = match[1].strip()
                
                # Skip if no content
                if not content or len(content) < 10:  # Minimum content length
                    continue
                
                # If no filepath specified, use default
                if not filepath:
                    filepath = "src/App.jsx"
                
                # Clean filepath - preserve public/ and src/ directories
                filepath = filepath.lstrip('/').replace('frontend/', '').strip()
                
                # Validate filepath - must have valid extension or be a known config file
                valid_extensions = ['.jsx', '.js', '.json', '.html', '.css', '.tsx', '.ts']
                has_valid_extension = any(filepath.endswith(ext) for ext in valid_extensions)
                is_known_config = filepath in ['package.json', 'tsconfig.json']
                
                # Skip if filepath is invalid
                # Must have valid extension OR be a known config file
                # Must not be a common word
                # Must be at least 5 chars (to avoid "on", "off", etc.)
                common_words = ['on', 'off', 'in', 'at', 'to', 'as', 'if', 'of', 'is', 'it', 'we', 'do', 'go', 'no']
                if not (has_valid_extension or is_known_config):
                    continue
                if len(filepath) < 5 and filepath not in ['package.json', 'tsconfig.json']:
                    continue
                if filepath.lower() in common_words:
                    continue
                
                # Handle root level files (package.json, tsconfig.json)
                if filepath in ['package.json', 'tsconfig.json']:
                    # Keep at root level
                    pass
                # Don't modify paths that already start with public/ or src/
                elif not filepath.startswith('public/') and not filepath.startswith('src/'):
                    # Root level files (like package.json) stay at root
                    if '/' not in filepath and filepath.endswith('.json'):
                        # Root level config files
                        pass
                    elif '/' not in filepath:
                        # Single filename without path, default to src/
                        filepath = f"src/{filepath}"
                    else:
                        # Has path but doesn't start with public/ or src/, add src/
                        filepath = f"src/{filepath}"
                
                # Create full path
                full_path = os.path.join(frontend_path, filepath)
                file_dir = os.path.dirname(full_path)
                
                # Create directory structure
                if file_dir:
                    Path(file_dir).mkdir(parents=True, exist_ok=True)
                
                # Save file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Store relative path for reference
                relative_path = filepath
                files_saved[relative_path] = full_path
        else:
            # Fallback: save as single App.jsx
            content = self._extract_code_from_markdown(frontend_code)
            src_dir = os.path.join(frontend_path, "src")
            Path(src_dir).mkdir(parents=True, exist_ok=True)
            app_path = os.path.join(src_dir, "App.jsx")
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(content)
            files_saved["src/App.jsx"] = app_path
        
        return files_saved
    
    def generate_project(
        self,
        architecture: str,
        database_schema: str,
        code: str,
        api_route_plan: Dict[str, Any] = None,
        api_documentation: Dict[str, Any] = None,
        requirements_txt: Optional[str] = None,
        frontend_code: str = "",
        tests: str = "",
        description: str = "",
        requirements: str = "",
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete project with all files.
        
        Args:
            architecture: Architecture document
            database_schema: Database schema and setup code
            code: Generated backend code
            api_route_plan: API route plan dictionary
            api_documentation: API documentation dictionary
            requirements_txt: Generated requirements.txt content
            frontend_code: Generated frontend code
            tests: Generated test cases
            description: Project description
            requirements: Project requirements
            project_name: Optional project name
        
        Returns:
            Dictionary with project path and file paths
        """
        # Create project folder
        project_path = self.create_project_folder(project_name)
        
        # Save all files
        files = {
            "project_path": project_path,
            "architecture_file": self.save_architecture(project_path, architecture),
            "database_schema_file": self.save_database_schema(project_path, database_schema),
            "code_file": self.save_code(project_path, code),
            "readme_file": self.save_readme(project_path, description, requirements),
            "requirements_file": self.save_requirements(project_path, requirements_txt)
        }
        
        # Save API route plan if provided
        if api_route_plan:
            files["api_route_plan_file"] = self.save_api_route_plan(project_path, api_route_plan)
        
        # Save API documentation if provided
        if api_documentation:
            files["api_documentation_file"] = self.save_api_documentation(project_path, api_documentation)
        
        # Save frontend if provided
        if frontend_code:
            frontend_files = self.save_frontend(project_path, frontend_code)
            files["frontend_files"] = frontend_files
            files["frontend_path"] = os.path.join(project_path, "frontend")
        
        # Save tests if provided
        if tests:
            files["test_file"] = self.save_tests(project_path, tests)
        
        return files
    
    def _extract_code_from_markdown(self, content: str) -> str:
        """
        Extract code from markdown code blocks if present.
        
        Args:
            content: Content that may contain markdown code blocks
        
        Returns:
            Extracted code or original content
        """
        # Check for Python code blocks
        python_pattern = r'```python\s*\n(.*?)```'
        match = re.search(python_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Check for generic code blocks
        code_pattern = r'```\s*\n(.*?)```'
        match = re.search(code_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Return original if no code blocks found
        return content.strip()

