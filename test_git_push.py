import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agentic.autonomous_coder import create_autonomous_coder

def test_push():
    coder = create_autonomous_coder(base_path="/Users/ton/aura_creatine_agents/")
    print("Attempting to push changes...")
    # Create a dummy file to commit
    with open("/Users/ton/aura_creatine_agents/test_file.txt", "w") as f:
        f.write(f"Test content from autonomous coder at {datetime.now().isoformat()}")
    result = coder.git_commit_and_push(message="Test commit from autonomous coder", branch="main")
    print(result)
    if result["success"]:
        print("Successfully pushed!")
    else:
        print(f"Failed to push: {result.get('error') or result.get('stderr')}")

if __name__ == "__main__":
    test_push()
