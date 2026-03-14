import os
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime

class AutonomousCoder:
    """
    Enables the agent to write, modify, and test its own code.
    """
    def __init__(self, base_path: str = "/Users/ton/aura_creatine_agents/"):
        self.base_path = base_path
        self.code_repo_path = os.path.join(base_path, "src") # Assuming code is in src
        self.github_token = os.environ.get("GITHUB_TOKEN")
        if not self.github_token:
            print("WARNING: GITHUB_TOKEN not found. Code pushing to GitHub will be disabled.")

    def _run_command(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Helper to run shell commands.
        """
        try:
            result = subprocess.run(command, cwd=cwd or self.base_path, capture_output=True, text=True, check=True)
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"success": False, "stdout": e.stdout, "stderr": e.stderr, "error": str(e)}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "error": str(e)}

    def write_code(self, file_path: str, code_content: str) -> Dict[str, Any]:
        """
        Writes code to a specified file.
        """
        full_path = os.path.join(self.base_path, file_path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(code_content)
            return {"success": True, "message": f"Code written to {file_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_code(self, file_path: str) -> Dict[str, Any]:
        """
        Reads code from a specified file.
        """
        full_path = os.path.join(self.base_path, file_path)
        try:
            with open(full_path, "r") as f:
                content = f.read()
            return {"success": True, "content": content}
        except FileNotFoundError:
            return {"success": False, "error": f"File not found: {file_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_code(self, file_path: str, interpreter: str = "python3.11") -> Dict[str, Any]:
        """
        Executes a Python script and captures its output.
        """
        full_path = os.path.join(self.base_path, file_path)
        return self._run_command([interpreter, full_path])

    def git_commit_and_push(self, message: str, branch: str = "main") -> Dict[str, Any]:
        """
        Commits changes and pushes to the GitHub repository.
        Requires GITHUB_TOKEN environment variable to be set.
        """
        if not self.github_token:
            return {"success": False, "error": "GITHUB_TOKEN not set. Cannot push to GitHub."}

        # Configure git if not already configured (for the agent's identity)
        self._run_command(["git", "config", "user.email", "agent@aura.creatine"], cwd=self.base_path)
        self._run_command(["git", "config", "user.name", "AuraCreatineAgent"], cwd=self.base_path)

        # Add all changes
        add_result = self._run_command(["git", "add", "."], cwd=self.base_path)
        if not add_result["success"]:
            return add_result

        # Commit changes
        commit_result = self._run_command(["git", "commit", "-m", message], cwd=self.base_path)
        if not commit_result["success"] and "nothing to commit" not in commit_result["stderr"]:
            return commit_result
        
        repo_url = "https://github.com/ScottEverduim/Aura-Creatine.git"

        # Pull latest changes before pushing
        pull_result = self._run_command(["git", "pull", "origin", branch], cwd=self.base_path)
        if not pull_result["success"]:
            return pull_result

        # Push to remote
        push_result = self._run_command(["git", "push", "origin", branch], cwd=self.base_path)
        
        if not push_result["success"] and "Everything up-to-date" not in push_result["stderr"]:
            return push_result
        
        return {"success": True, "message": f"Changes committed and pushed to {branch}"}

    def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """
        Performs static analysis on a Python file (e.g., using pylint or flake8).
        """
        full_path = os.path.join(self.base_path, file_path)
        # For simplicity, just check for basic syntax errors for now
        return self._run_command(["python3.11", "-m", "py_compile", full_path])

    def refactor_code(self, file_path: str, instructions: str) -> Dict[str, Any]:
        """
        Refactors code based on instructions (this would involve an LLM).
        Placeholder for now.
        """
        return {"success": False, "error": "Refactoring not yet implemented. Use LLM directly for this."}

    def generate_code(self, prompt: str, file_path: str) -> Dict[str, Any]:
        """
        Generates new code based on a prompt (this would involve an LLM).
        Placeholder for now.
        """
        return {"success": False, "error": "Code generation not yet implemented. Use LLM directly for this."}


def create_autonomous_coder(base_path: str = "/Users/ton/aura_creatine_agents/") -> AutonomousCoder:
    """
    Factory function to create an AutonomousCoder instance.
    """
    return AutonomousCoder(base_path=base_path)
