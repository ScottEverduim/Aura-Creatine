import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from src.autonomy.world_state import create_world_state_manager, Fact, Event, Relationship
from src.agentic.episodic_memory import EpisodicMemoryStore

class UnifiedMemory:
    """
    Single interface to all memory systems.
    Automatically syncs and cross-references data.
    """
    
    def __init__(self, core=None):
        self.core = core
        self._init_systems()
        
    def _init_systems(self):
        """Initialize all memory subsystems"""
        # World State
        try:
            self.world_state = create_world_state_manager(self.core)
            print("✅ World State connected")
        except Exception as e:
            print(f"⚠️ World State unavailable: {e}")
            self.world_state = None
            
        # Episodic Memory
        try:
            self.episodic_memory = EpisodicMemoryStore(storage_path="/Users/ton/aura_creatine_agents/data/episodic_memory.json")
            print("✅ Episodic Memory connected")
        except Exception as e:
            print(f"⚠️ Episodic Memory unavailable: {e}")
            self.episodic_memory = None
            
        # Placeholder for Enhanced Memory (Vector DB) - not implemented yet
        self.enhanced_memory = None
        print("ℹ️ Enhanced Memory (Vector DB) not yet implemented")
            
        # Placeholder for Phase 12 Learning - not implemented yet
        self.phase12 = None
        print("ℹ️ Phase 12 Learning not yet implemented")
            
    # =================================================================
    # Unified Storage API
    # =================================================================
    
    def store(self, content: str, memory_type: str = 'general', 
              metadata: Optional[Dict] = None, entity_id: Optional[str] = None) -> str:
        """
        Store a memory across all relevant systems
        
        Args:
            content: The memory content
            memory_type: Type of memory (interaction, learning, goal, entity, fact)
            metadata: Additional context
            entity_id: Optional entity to associate with
            
        Returns:
            memory_id: Unique identifier for this memory
        """
        memory_id = f"mem_{datetime.now().timestamp()}"
        metadata = metadata or {}
        
        # 1. Store in Episodic Memory (for learning from outcomes)
        if self.episodic_memory and memory_type in ['interaction', 'learning', 'goal_outcome']:
            self.episodic_memory.record(
                context=content,
                action=metadata.get('action', 'unknown'),
                outcome=metadata.get('outcome', 'unknown'),
                emotional_valence=metadata.get('emotional_valence', 0.0),
                behavior_delta=metadata.get('behavior_delta'),
                trigger_patterns=metadata.get('trigger_patterns')
            )

        # 2. Store in World State (if entity-related or significant event)
        if self.world_state:
            if entity_id:
                self.world_state.add_fact(Fact(
                    entity_id=entity_id,
                    attribute=memory_type,
                    value=content,
                    source='unified_memory',
                    timestamp=datetime.now().isoformat()
                ))
            
            if memory_type in ['interaction', 'achievement', 'learning', 'error']:
                self.world_state.add_event(Event(
                    event_type=memory_type,
                    actor_id=entity_id or 'self',
                    target_id=metadata.get('target_id'),
                    platform=metadata.get('platform', 'unknown'),
                    data={'content': content, 'metadata': metadata}
                ))
            
        # 3. Placeholder for Enhanced Memory (vector DB for semantic search)
        if self.enhanced_memory:
            self.enhanced_memory.add_memory(
                content=content,
                memory_type=memory_type,
                metadata={**metadata, 'memory_id': memory_id, 'entity_id': entity_id}
            )
        
        return memory_id
    
    # =================================================================
    # Unified Retrieval API
    # =================================================================
    
    def recall(self, query: str, k: int = 5, memory_type: Optional[str] = None) -> List[Dict]:
        """
        Semantic search across all memory systems
        
        Args:
            query: Search query
            k: Number of results
            memory_type: Filter by type
            
        Returns:
            List of relevant memories with sources
        """
        results = []
        
        # 1. Search Episodic Memory (keyword matching for now)
        if self.episodic_memory:
            episodic_results = self.episodic_memory.recall_relevant(query, k=k)
            for mem in episodic_results:
                results.append({
                    'id': mem.id,
                    'content': mem.context,
                    'memory_type': 'episodic_memory',
                    'source': 'episodic_memory',
                    'timestamp': mem.timestamp.isoformat(),
                    'metadata': mem.to_dict()
                })

        # 2. Search World State entities and facts
        if self.world_state:
            entities = self.world_state.search_entities(query, limit=k)
            for entity in entities:
                results.append({
                    'id': entity.id,
                    'content': f"Entity: {entity.name or entity.id} ({entity.type})",
                    'memory_type': 'entity',
                    'source': 'world_state',
                    'timestamp': entity.updated_at,
                    'metadata': entity.attributes
                })
            
            facts = self.world_state.get_facts_by_entity(query) # Assuming query can be entity_id
            for fact in facts:
                results.append({
                    'id': fact.id,
                    'content': f"Fact about {fact.entity_id}: {fact.attribute} = {fact.value}",
                    'memory_type': 'fact',
                    'source': 'world_state',
                    'timestamp': fact.timestamp,
                    'metadata': fact.to_dict()
                })
        
        # 3. Placeholder for Enhanced Memory (vector DB)
        if self.enhanced_memory:
            enhanced_memories = self.enhanced_memory.search_memories(query, k=k, memory_type=memory_type)
            for mem in enhanced_memories:
                mem['source'] = 'enhanced_memory'
                results.append(mem)
        
        # Sort by relevance/timestamp and return top k (simple sort for now)
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return results[:k]
    
    def get_entity_context(self, entity_id: str) -> Dict[str, Any]:
        """
        Get comprehensive context about an entity from all systems
        
        Returns merged data from:
        - World State (facts, relationships)
        - Episodic Memory (related interactions)
        - Placeholder for Phase 12 (interaction history)
        - Placeholder for Enhanced Memory (related memories)
        """
        context = {
            'entity_id': entity_id,
            'world_state': None,
            'relationships': [],
            'facts': [],
            'interaction_count': 0,
            'recent_memories': []
        }
        
        # 1. World State data
        if self.world_state:
            entity_data = self.world_state.get_entity_with_facts(entity_id)
            if entity_data:
                context['world_state'] = entity_data
                context['facts'] = [f for f in entity_data.get('facts', [])]
                
            # Get relationships
            relationships = self.world_state.get_relationships(entity_id)
            context['relationships'] = [r.to_dict() for r in relationships]
        
        # 2. Episodic Memory related to this entity
        if self.episodic_memory:
            # Search for memories where the entity_id is in the context or outcome
            entity_memories = self.episodic_memory.recall_relevant(entity_id, k=5)
            context['recent_memories'] = [m.to_dict() for m in entity_memories]
        
        # 3. Placeholder for Phase 12 user data
        if self.phase12:
            profile = self.phase12.get_user_profile(entity_id)
            if profile:
                context['interaction_count'] = profile.get('interaction_count', 0)
                context['preferred_topics'] = profile.get('preferred_topics', [])
                context['sentiment_trend'] = profile.get('sentiment_trend', 'neutral')
        
        # 4. Placeholder for Enhanced Memory (vector DB)
        if self.enhanced_memory:
            memories = self.enhanced_memory.search_memories(entity_id, k=10)
            context['enhanced_memories'] = memories
        
        return context
    
    # =================================================================
    # Learning & Adaptation
    # =================================================================
    
    def learn_from_interaction(self, user_id: str, interaction_type: str, 
                               content: str, outcome: Optional[str] = None,
                               platform: str = 'unknown') -> bool:
        """
        Record an interaction and update all relevant learning systems
        """
        try:
            # 1. Store as memory (will go to episodic and world state)
            self.store(
                content=content,
                memory_type='interaction',
                metadata={
                    'user_id': user_id,
                    'interaction_type': interaction_type,
                    'outcome': outcome,
                    'platform': platform,
                    'action': 'interact'
                },
                entity_id=user_id
            )
            
            # 2. Track in Phase 12 (placeholder)
            if self.phase12:
                self.phase12.track_user_interaction(
                    user_id=user_id,
                    platform=platform,
                    interaction_type=interaction_type
                )
            
            # 3. Update World State relationship
            if self.world_state:
                # Strengthen relationship
                existing = self.world_state.get_relationships(user_id, relation_type='interacted_with')
                strength = 0.5
                if existing:
                    strength = min(1.0, existing[0].strength + 0.1)
                
                self.world_state.add_relationship(Relationship(
                    from_entity='aura_agent',
                    to_entity=user_id,
                    relation_type='interacted_with',
                    strength=strength,
                    context={'last_interaction': interaction_type, 'platform': platform}
                ))
            
            return True
        except Exception as e:
            print(f"❌ Failed to learn from interaction: {e}")
            return False
    
    def get_behavior_weights(self, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Get dynamically adjusted behavior weights based on memory
        """
        weights = {
            'formality': 0.5,
            'verbosity': 0.5,
            'emoji_usage': 0.7,
            'technical_depth': 0.5
        }
        
        user_id = context.get('user_id')
        if not user_id:
            return weights
        
        # Adjust based on user profile (placeholder for phase12)
        if self.phase12:
            profile = self.phase12.get_user_profile(user_id)
            if profile:
                if profile.get('interaction_count', 0) > 10:
                    weights['formality'] = 0.3
                    weights['emoji_usage'] = 0.9
                
                topics = profile.get('preferred_topics', [])
                if any(t in ['AI', 'coding', 'dev', 'tech'] for t in topics):
                    weights['technical_depth'] = 0.8
        
        # Adjust based on episodic memory
        if self.episodic_memory:
            modulation = self.episodic_memory.get_behavior_modulation(context.get('observation', ''))
            for param, delta in modulation.items():
                weights[param] = max(0.0, min(1.0, weights.get(param, 0.5) + delta))
        
        return weights
    
    def get_unified_stats(self) -> Dict:
        """
        Get statistics from all connected memory systems
        """
        stats = {
            'world_state': self.world_state.get_stats() if self.world_state else {'status': 'unavailable'},
            'episodic_memory': self.episodic_memory.get_stats() if self.episodic_memory else {'status': 'unavailable'},
            'enhanced_memory': {'status': 'not implemented'},
            'phase12_learning': {'status': 'not implemented'}
        }
        return stats

def create_unified_memory(core=None) -> UnifiedMemory:
    """Factory function to create a UnifiedMemory instance"""
    return UnifiedMemory(core=core)
