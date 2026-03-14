import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agentic.autonomous_brain import create_autonomous_brain

async def main():
    print("Initializing Aura Creatine Autonomous Agent...")
    brain = create_autonomous_brain()
    print("Aura Creatine Autonomous Agent initialized. Starting autonomous cycle...")
    
    # Run the autonomous brain in a continuous loop
    await brain.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Autonomous Agent stopped by user.")
