import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .unified_memory import UnifiedMemory, create_unified_memory
from .episodic_memory import EpisodicMemoryStore, BehaviorModulator
from .autonomous_goals import AutonomousGoalManager, create_autonomous_goal_manager
# from .meta_learning import MetaLearningEngine, AdaptiveLearner, create_adaptive_learner # Not implemented yet
# from .self_reflection import SelfReflectionEngine, ReflectionScheduler, create_reflection_engine # Not implemented yet
# from .symod_core import SyModCoreManager, get_symod_manager # Not implemented yet


class AGIKernel:
    """
    Central integration point for all AGI systems
    
    This is the 'consciousness' layer that:
    - Coordinates memory systems
    - Generates autonomous goals
    - Modulates behavior based on learning
    - Provides unified API for the rest of the system
    """
    
    def __init__(self, core=None):
        self.core = core
        print("🧠 Initializing AGI Kernel...")
        
        # Initialize all AGI subsystems
        self.unified_memory = create_unified_memory(core)
        self.episodic_memory_store = EpisodicMemoryStore(storage_path="/Users/ton/aura_creatine_agents/data/episodic_memory.json")
        self.behavior_modulator = BehaviorModulator(self.episodic_memory_store)
        
        # SyMod mathematical validation layer (core system) - Placeholder for now
        self.symod = None # get_symod_manager(core) # Not implemented yet
        print("🔢 SyMod Core Manager: Placeholder (not implemented)")
        
        # Goal system
        self.goal_manager = create_autonomous_goal_manager(
            unified_memory=self.unified_memory,
            # phase12_learning=getattr(self.unified_memory, 'phase12', None), # Not implemented yet
            # onchain_plugin=self._get_onchain_plugin() # Not implemented yet
        )
        
        # Meta-learning - Placeholder for now
        self.meta_engine = None # MetaLearningEngine()
        self.adaptive_learner = None # AdaptiveLearner(
            # meta_engine=self.meta_engine,
            # episodic_store=self.episodic_memory,
            # unified_memory=self.unified_memory
        # )
        print("📚 Meta-learning: Placeholder (not implemented)")
        
        # Self-reflection - Placeholder for now
        self.reflection_engine = None # create_reflection_engine(self)
        self.reflection_scheduler = None
        print("🤔 Self-reflection: Placeholder (not implemented)")
        
        print("✅ AGI Kernel ready")
    
    def _get_onchain_plugin(self):
        """Get onchain plugin if available"""
        if self.core and hasattr(self.core, 'plugin_manager'):
            return self.core.plugin_manager.plugins.get('onchain')
        return None
    
    # =================================================================
    # Core AGI Interface
    # =================================================================
    
    def perceive(self, observation: str, context: Dict[str, Any]) -> Dict:
        """
        Process an observation through the AGI system
        
        This is the main entry point - every input goes through here.
        Returns context-enriched understanding with behavioral adjustments.
        """
        # 1. Store the observation
        self.unified_memory.store(
            content=observation,
            memory_type='observation',
            metadata=context
        )
        
        # 2. Recall relevant episodic memories
        relevant_memories = self.episodic_memory_store.recall_relevant(
            current_context=observation,
            k=3
        )
        
        # 3. Get behavior modulation from memory
        behavior_params = self.behavior_modulator.get_effective_params(observation)
        
        # 4. Get user context if available
        user_id = context.get('user_id')
        user_context = {}
        if user_id:
            user_context = self.unified_memory.get_entity_context(user_id)
        
        # 5. Check for active goals that might influence response
        active_goals = self.goal_manager.get_active_goals()
        
        return {
            'observation': observation,
            'relevant_memories': [m.to_dict() for m in relevant_memories],
            'behavior_params': behavior_params,
            'user_context': user_context,
            'active_goals': [g.to_dict() for g in active_goals],
            'recommended_style': self.behavior_modulator.get_response_style(observation)
        }
    
    def decide(self, options: List[str], context: str) -> str:
        """
        Make a decision based on learned preferences and goals
        
        Uses:
        - Past outcomes (episodic memory)
        - Current goals (autonomous goal system)
        - Meta-learned strategies
        """
        # Get behavior modulation for this context
        modulation = self.episodic_memory_store.get_behavior_modulation(context)
        
        # Adjust initiative based on learning
        initiative = modulation.get('initiative', 0.0)
        
        # Check if any active goals influence this decision
        next_goal_action = self.goal_manager.get_next_action()
        
        if next_goal_action and initiative > 0.1:
            # Autonomous goal takes priority if we're feeling proactive
            return f"[AUTONOMOUS_GOAL:{next_goal_action['action']}]"
        
        # Otherwise, use learned preferences
        # (In practice, this would use more sophisticated decision logic)
        return options[0] if options else "no_action"
    
    def act(self, action: str, context: Dict, expected_outcome: str = None) -> Dict:
        """
        Execute an action with full learning tracking
        
        Returns action with behavioral adjustments applied.
        """
        # Get behavior params
        behavior_params = self.behavior_modulator.get_effective_params(
            context.get('observation', '')
        )
        
        # Apply style adjustments
        style = self.behavior_modulator.get_response_style(context.get('observation', ''))
        
        # Prepare for learning (placeholder)
        learning_context = {} # self.adaptive_learner.learn(
            # domain=context.get('domain', 'general'),
            # context=context.get('observation', ''),
            # attempt_action=action
        # )
        
        return {
            'action': action,
            'style': style,
            'behavior_params': behavior_params,
            'learning_context': learning_context,
            'timestamp': datetime.now().isoformat()
        }
    
    def learn(self, context: str, action: str, outcome: str, 
              success: bool, user_id: str = None):
        """
        Learn from an experience
        
        This is the key AGI feedback loop - every outcome gets processed
        through all learning systems.
        """
        # 1. Record in episodic memory
        self.behavior_modulator.record_outcome(
            context=context,
            action=action,
            outcome=outcome,
            success=success,
            user_id=user_id
        )
        
        # 2. Record in unified memory
        self.unified_memory.store(
            content=f"Action: {action}, Outcome: {outcome}",
            memory_type='learning' if success else 'failure',
            metadata={
                'context': context,
                'success': success,
                'user_id': user_id
            },
            entity_id=user_id
        )
        
        # 3. Update goal progress if applicable
        if success and self.goal_manager:
            # Try to complete current goal step
            active = self.goal_manager.get_next_action()
            if active and active['action'] == action: # Only complete if it's the expected action
                self.goal_manager.complete_action(
                    active['goal_id'],
                    success=True,
                    outcome=outcome
                )
        
        # 4. Meta-learning feedback (placeholder)
        if self.adaptive_learner:
            self.adaptive_learner.feedback(
                learning_attempt={'domain': 'general', 'context': context, 'strategy': 'default'},
                success=success,
                outcome_description=outcome
            )
    
    # =================================================================
    # Autonomous Operations
    # =================================================================
    
    async def run_autonomous_cycle(self):
        """
        Run one cycle of autonomous operation
        
        This is where the agent acts on its own goals.
        Call this periodically (e.g., every 5 minutes).
        """
        # 1. Scan for new opportunities and generate goals
        # onchain = self._get_onchain_plugin() # Not implemented yet
        new_goals = self.goal_manager.scan_and_generate(onchain_plugin=None)
        
        # 2. Auto-approve high-priority goals
        for goal in new_goals:
            if goal.priority_score >= 8.0:
                self.goal_manager.approve_goal(goal.id)
        
        # 3. Execute next action from active goals
        action = self.goal_manager.get_next_action()
        if action:
            print(f"🎯 Executing autonomous goal: {action['goal_description']}")
            print(f"   Action: {action['action']}")
            
            # In practice, this would actually execute the action
            # For now, just log it
            # self.act(action['action'], {'domain': 'autonomous', 'observation': action['goal_description']})
            return action
        
        return None
    
    def get_introspection(self) -> Dict:
        """
        Get the agent's current mental state
        
        This enables the agent to report on:
        - What it's thinking about (active goals)
        - What it remembers (recent episodic memories)
        - How it's feeling (aggregated emotional valence)
        - What it's learned (meta-learning insights)
        """
        # Get active goals
        active_goals = self.goal_manager.get_active_goals()
        proposed_goals = self.goal_manager.get_proposed_goals()
        
        # Get recent experiences
        recent_experiences = [
            m.to_dict() for m in self.episodic_memory_store.memories[-5:]
        ]
        
        # Calculate "mood" from recent emotional valence
        recent_valence = [m.emotional_valence for m in self.episodic_memory_store.memories[-10:]]
        avg_mood = sum(recent_valence) / len(recent_valence) if recent_valence else 0
        
        # Get learning insights (placeholder)
        learning_report = {} # self.adaptive_learner.get_learning_report()
        
        # Get memory stats
        memory_stats = self.unified_memory.get_unified_stats()
        
        return {
            'mental_state': {
                'mood': avg_mood,
                'mood_description': 'positive' if avg_mood > 0.2 else 'negative' if avg_mood < -0.2 else 'neutral',
                'active_goal_count': len(active_goals),
                'proposed_goal_count': len(proposed_goals),
                'total_memories': memory_stats['episodic_memory']['count'] if 'episodic_memory' in memory_stats and 'count' in memory_stats['episodic_memory'] else 0
            },
            'active_goals': [g.to_dict() for g in active_goals],
            'proposed_goals': [g.to_dict() for g in proposed_goals],
            'recent_experiences': recent_experiences,
            'learning_report': learning_report,
            'memory_stats': memory_stats
        }

def create_agi_kernel(core=None) -> AGIKernel:
    """
    Factory function to create an AGIKernel instance
    """
    return AGIKernel(core=core)
