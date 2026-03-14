import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .agi_kernel import AGIKernel, create_agi_kernel
from .unified_memory import UnifiedMemory
from .episodic_memory import BehaviorModulator
from .autonomous_goals import AutonomousGoalManager


class AutonomousBrain:
    """
    The core decision-making and orchestration layer of the AGI.
    
    This component is responsible for:
    - Orchestrating the AGI cycle (Perceive -> Decide -> Act -> Learn)
    - Managing the agent's goals and priorities
    - Adapting behavior based on learned experiences
    - Interacting with external systems via the AGIKernel
    """
    
    def __init__(self, core=None, agi_kernel: Optional[AGIKernel] = None):
        self.core = core
        self.agi_kernel = agi_kernel or create_agi_kernel(core)
        self.is_running = False
        self.cycle_interval = timedelta(seconds=30)  # How often the brain 
cycles
        self.last_cycle_time: Optional[datetime] = None
        print("🧠 Autonomous Brain initialized")

    async def start(self):
        """
        Starts the autonomous brain's continuous operation cycle.
        """
        if self.is_running:
            print("Autonomous Brain is already running.")
            return
        
        self.is_is_running = True
        print("🚀 Starting Autonomous Brain loop...")
        while self.is_running:
            await self.run_cycle()
            await asyncio.sleep(self.cycle_interval.total_seconds())

    async def stop(self):
        """
        Stops the autonomous brain's operation cycle.
        """
        self.is_running = False
        print("🛑 Autonomous Brain stopped.")

    async def run_cycle(self):
        """
        Executes one full Perceive-Decide-Act-Learn cycle.
        """
        self.last_cycle_time = datetime.now()
        print(f"--- Autonomous Brain Cycle Started ({self.last_cycle_time}) ---")

        # 1. Perceive: Gather observations and current context
        observation_context = await self._perceive()
        print(f"Perceived: {observation_context.get("observation", "No direct observation")}")

        # 2. Decide: Determine the next best action based on perception and goals
        decision = await self._decide(observation_context)
        print(f"Decided: {decision}")

        # 3. Act: Execute the chosen action
        action_result = await self._act(decision, observation_context)
        print(f"Acted: {action_result}")

        # 4. Learn: Update memory and adapt behavior based on action outcome
        await self._learn(action_result, observation_context)
        print("--- Autonomous Brain Cycle Completed ---")

    async def _perceive(self) -> Dict:
        """
        Gathers all relevant information from the environment and internal state.
        """
        # For now, a simple observation. In a real system, this would pull from sensors/plugins.
        # We can simulate an observation based on the state of autonomous goals.
        active_goals = self.agi_kernel.goal_manager.get_active_goals()
        if active_goals:
            observation = f"There are {len(active_goals)} active autonomous goals. Highest priority: {active_goals[0].description}"
        else:
            observation = "No active autonomous goals. Scanning for opportunities."
        
        context = {
            "user_id": "system_agent", # The brain itself is the 'user' here
            "domain": "self_management",
            "observation": observation
        }
        return self.agi_kernel.perceive(observation, context)

    async def _decide(self, observation_context: Dict) -> str:
        """
        Makes a decision based on the perceived state and internal goals.
        """
        # The AGIKernel's decide method will prioritize autonomous goals
        # if the agent is feeling proactive (based on behavior modulation).
        # We'll pass a dummy option list for now.
        return self.agi_kernel.decide(
            options=["run_autonomous_goal_action", "scan_for_opportunities"],
            context=observation_context.get("observation", "")
        )

    async def _act(self, decision: str, observation_context: Dict) -> Dict:
        """
        Executes the chosen action.
        """
        action_result = {"status": "no_action"}
        
        if decision.startswith("[AUTONOMOUS_GOAL:"):
            # Extract the actual action from the decision string
            action_to_execute = decision.replace("[AUTONOMOUS_GOAL:", "").replace("]", "")
            
            # This is where the actual execution of the autonomous goal action would happen.
            # For the initial setup, we'll just log it and mark the goal step as complete.
            print(f"Executing autonomous goal action: {action_to_execute}")
            
            # Simulate success for now
            current_goal_action = self.agi_kernel.goal_manager.get_next_action()
            if current_goal_action and current_goal_action["action"] == action_to_execute:
                self.agi_kernel.goal_manager.complete_action(
                    current_goal_action["goal_id"],
                    success=True,
                    outcome=f"Successfully simulated execution of {action_to_execute}"
                )
                action_result = {"status": "success", "action": action_to_execute, "outcome": "simulated_success"}
            else:
                action_result = {"status": "failed", "action": action_to_execute, "outcome": "goal_mismatch"}

        elif decision == "scan_for_opportunities":
            print("Scanning for new opportunities and generating goals...")
            new_goals = self.agi_kernel.goal_manager.scan_and_generate()
            if new_goals:
                print(f"Generated {len(new_goals)} new goals.")
                action_result = {"status": "success", "action": "scan_and_generate", "outcome": f"generated {len(new_goals)} goals"}
            else:
                action_result = {"status": "success", "action": "scan_and_generate", "outcome": "no new opportunities"}
        
        # The AGIKernel's act method would also apply behavior modulation
        return self.agi_kernel.act(decision, observation_context, expected_outcome=action_result.get("outcome"))

    async def _learn(self, action_result: Dict, observation_context: Dict):
        """
        Updates memory and adapts behavior based on the outcome of the action.
        """
        success = action_result.get("status") == "success"
        outcome = action_result.get("outcome", "unknown")
        action = action_result.get("action", "unknown")
        
        self.agi_kernel.learn(
            context=observation_context.get("observation", ""),
            action=action,
            outcome=outcome,
            success=success,
            user_id=observation_context.get("user_id")
        )

    def get_introspection(self) -> Dict:
        """
        Returns the current mental state of the autonomous brain.
        """
        return self.agi_kernel.get_introspection()

def create_autonomous_brain(core=None) -> AutonomousBrain:
    """
    Factory function to create an AutonomousBrain instance.
    """
    return AutonomousBrain(core=core)
