import os
import sys
from datetime import datetime

# Add the parent directory of src to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agentic.autonomous_coder import create_autonomous_coder

def run_test():
    coder = create_autonomous_coder()

    # Create a dummy file with a unique timestamp to ensure changes
    test_file_path = os.path.join(coder.base_path, 'test_file.txt')
    with open(test_file_path, 'w') as f:
        f.write(f'Test content from autonomous coder at {datetime.now().isoformat()}\n')

    print(f"Attempting to commit and push changes for {test_file_path}")
    result = coder.git_commit_and_push(message='Test commit from autonomous coder', branch='main')
    print(result)

if __name__ == "__main__":
    run_test()
