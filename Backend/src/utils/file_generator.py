"""
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
        Save code to a file.
        
        Args:
            project_path: Path to the project folder
            code: Code content
            filename: Name of the code file (default: main.py)
        
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
- `main.py`: Main application code
- `tests/test_main.py`: Test cases
- `ARCHITECTURE.md`: Software architecture document

## Installation
```bash
pip install -r requirements.txt
```

## Running
```bash
python main.py
```

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
            requirements_content = "pytest>=7.0.0\n"
        
        req_path = os.path.join(project_path, "requirements.txt")
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        return req_path
    
    def generate_project(
        self,
        architecture: str,
        code: str,
        tests: str,
        description: str = "",
        requirements: str = "",
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete project with all files.
        
        Args:
            architecture: Architecture document
            code: Generated code
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
            "code_file": self.save_code(project_path, code),
            "test_file": self.save_tests(project_path, tests),
            "readme_file": self.save_readme(project_path, description, requirements),
            "requirements_file": self.save_requirements(project_path)
        }
        
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

