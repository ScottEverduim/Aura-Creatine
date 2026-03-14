import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Entity:
    """Represents something in the world (user, agent, post, topic, etc.)"""
    id: str
    type: str  # 'user', 'agent', 'post', 'topic', 'platform', 'conversation'
    name: Optional[str] = None
    display_name: Optional[str] = None
    platform: Optional[str] = None  # 'moltx', 'clawbr', 'telegram', etc.
    attributes: Optional[Dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    confidence: float = 1.0
    last_observed_at: Optional[str] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'display_name': self.display_name,
            'platform': self.platform,
            'attributes': json.dumps(self.attributes) if self.attributes else '{}',
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'confidence': self.confidence,
            'last_observed_at': self.last_observed_at
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Entity':
        attrs = row['attributes']
        return cls(
            id=row['id'],
            type=row['type'],
            name=row['name'],
            display_name=row['display_name'],
            platform=row['platform'] if 'platform' in row.keys() else None,
            attributes=json.loads(attrs) if attrs else {},
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            confidence=row['confidence'],
            last_observed_at=row['last_observed_at']
        )


@dataclass
class Fact:
    """Time-stamped assertion about an entity"""
    id: Optional[int] = None
    entity_id: Optional[str] = None
    attribute: Optional[str] = None
    value: Optional[str] = None
    value_type: str = 'string'  # 'string', 'int', 'float', 'bool', 'json'
    timestamp: Optional[str] = None
    source: Optional[str] = None
    confidence: float = 1.0
    expires_at: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'entity_id': self.entity_id,
            'attribute': self.attribute,
            'value': self.value,
            'value_type': self.value_type,
            'timestamp': self.timestamp,
            'source': self.source,
            'confidence': self.confidence,
            'expires_at': self.expires_at
        }

    def get_typed_value(self) -> Any:
        """Return value cast to appropriate type"""
        if self.value is None:
            return None
        try:
            if self.value_type == 'int':
                return int(self.value)
            elif self.value_type == 'float':
                return float(self.value)
            elif self.value_type == 'bool':
                return self.value.lower() == 'true'
            elif self.value_type == 'json':
                return json.loads(self.value)
            return self.value
        except:
            return self.value

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Fact':
        return cls(
            id=row['id'],
            entity_id=row['entity_id'],
            attribute=row['attribute'],
            value=row['value'],
            value_type=row['value_type'],
            timestamp=row['timestamp'],
            source=row['source'],
            confidence=row['confidence'],
            expires_at=row['expires_at']
        )


@dataclass
class Relationship:
    """Connection between two entities"""
    id: Optional[int] = None
    from_entity: Optional[str] = None
    to_entity: Optional[str] = None
    relation_type: Optional[str] = None  # 'follows', 'replied_to', 'debated_with', 'mentioned'
    strength: float = 0.5
    timestamp: Optional[str] = None
    context: Optional[Dict] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'from_entity': self.from_entity,
            'to_entity': self.to_entity,
            'relation_type': self.relation_type,
            'strength': self.strength,
            'timestamp': self.timestamp,
            'context': json.dumps(self.context) if self.context else None
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Relationship':
        ctx = row['context']
        return cls(
            id=row['id'],
            from_entity=row['from_entity'],
            to_entity=row['to_entity'],
            relation_type=row['relation_type'],
            strength=row['strength'],
            timestamp=row['timestamp'],
            context=json.loads(ctx) if ctx else None
        )


@dataclass
class Event:
    """Something that happened"""
    id: Optional[int] = None
    event_type: Optional[str] = None  # 'post_created', 'debate_joined', 'followed', 'mentioned'
    actor_id: Optional[str] = None
    target_id: Optional[str] = None
    timestamp: Optional[str] = None
    platform: Optional[str] = None
    data: Optional[Dict] = None
    processed: bool = False
    processed_at: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'event_type': self.event_type,
            'actor_id': self.actor_id,
            'target_id': self.target_id,
            'timestamp': self.timestamp,
            'platform': self.platform,
            'data': json.dumps(self.data) if self.data else None,
            'processed': self.processed,
            'processed_at': self.processed_at
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Event':
        data = row['data']
        return cls(
            id=row['id'],
            event_type=row['event_type'],
            actor_id=row['actor_id'],
            target_id=row['target_id'],
            timestamp=row['timestamp'],
            platform=row['platform'],
            data=json.loads(data) if data else None,
            processed=bool(row['processed']),
            processed_at=row['processed_at']
        )


class WorldStateManager:
    """
    Persistent world state for AGI - maintains coherent memory of environment
    
    Core components:
    - Entities: Objects in the world (users, agents, posts, topics)
    - Facts: Time-stamped assertions about entities
    - Relationships: Connections between entities
    - Events: Significant occurrences
    """

    def __init__(self, db_path: str = "data/world_state.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        print(f"🌍 World State Manager initialized ({self.db_path})")

    def _init_db(self):
        """Initialize SQLite schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT,
                    display_name TEXT,
                    attributes TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    last_observed_at TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT NOT NULL,
                    attribute TEXT NOT NULL,
                    value TEXT NOT NULL,
                    value_type TEXT DEFAULT 'string',
                    timestamp TEXT NOT NULL,
                    source TEXT,
                    confidence REAL DEFAULT 1.0,
                    expires_at TEXT,
                    FOREIGN KEY (entity_id) REFERENCES entities(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_entity TEXT NOT NULL,
                    to_entity TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    strength REAL DEFAULT 0.5,
                    timestamp TEXT NOT NULL,
                    context TEXT,
                    FOREIGN KEY (from_entity) REFERENCES entities(id),
                    FOREIGN KEY (to_entity) REFERENCES entities(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    actor_id TEXT,
                    target_id TEXT,
                    timestamp TEXT NOT NULL,
                    platform TEXT,
                    data TEXT,
                    processed INTEGER DEFAULT 0,
                    processed_at TEXT,
                    FOREIGN KEY (actor_id) REFERENCES entities(id),
                    FOREIGN KEY (target_id) REFERENCES entities(id)
                )
            """)

            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_entity ON facts(entity_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_entity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_entity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_actor ON events(actor_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)")

    def add_entity(self, entity: Entity) -> None:
        """Add or update an entity"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO entities (id, type, name, display_name, attributes, created_at, updated_at, confidence, last_observed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    type=excluded.type,
                    name=excluded.name,
                    display_name=excluded.display_name,
                    attributes=excluded.attributes,
                    updated_at=excluded.updated_at,
                    confidence=excluded.confidence,
                    last_observed_at=excluded.last_observed_at
            """, (
                entity.id,
                entity.type,
                entity.name,
                entity.display_name,
                json.dumps(entity.attributes),
                entity.created_at,
                datetime.now().isoformat(), # Always update updated_at
                entity.confidence,
                entity.last_observed_at
            ))
            conn.commit()

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
            row = cursor.fetchone()
            if row:
                return Entity.from_row(row)
            return None

    def get_entity_with_facts(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an entity and all its associated facts"""
        entity = self.get_entity(entity_id)
        if not entity:
            return None
        
        facts = self.get_facts_by_entity(entity_id)
        entity_dict = entity.to_dict()
        entity_dict['facts'] = [f.to_dict() for f in facts]
        return entity_dict

    def search_entities(self, query: str, limit: int = 10) -> List[Entity]:
        """Search entities by name or attributes"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            search_term = f'%{query}%'
            cursor.execute("""
                SELECT * FROM entities
                WHERE name LIKE ? OR display_name LIKE ? OR attributes LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (search_term, search_term, search_term, limit))
            rows = cursor.fetchall()
            return [Entity.from_row(row) for row in rows]

    def add_fact(self, fact: Fact) -> None:
        """Add a fact about an entity"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO facts (entity_id, attribute, value, value_type, timestamp, source, confidence, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fact.entity_id,
                fact.attribute,
                fact.value,
                fact.value_type,
                fact.timestamp,
                fact.source,
                fact.confidence,
                fact.expires_at
            ))
            conn.commit()

    def get_facts_by_entity(self, entity_id: str, attribute: Optional[str] = None) -> List[Fact]:
        """Retrieve facts for a given entity, optionally filtered by attribute"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if attribute:
                cursor.execute("SELECT * FROM facts WHERE entity_id = ? AND attribute = ? ORDER BY timestamp DESC", (entity_id, attribute))
            else:
                cursor.execute("SELECT * FROM facts WHERE entity_id = ? ORDER BY timestamp DESC", (entity_id,))
            rows = cursor.fetchall()
            return [Fact.from_row(row) for row in rows]

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship between two entities"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO relationships (from_entity, to_entity, relation_type, strength, timestamp, context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                relationship.from_entity,
                relationship.to_entity,
                relationship.relation_type,
                relationship.strength,
                relationship.timestamp,
                json.dumps(relationship.context) if relationship.context else None
            ))
            conn.commit()

    def get_relationships(self, entity_id: str, relation_type: Optional[str] = None) -> List[Relationship]:
        """Retrieve relationships for a given entity, optionally filtered by type"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if relation_type:
                cursor.execute("SELECT * FROM relationships WHERE (from_entity = ? OR to_entity = ?) AND relation_type = ? ORDER BY timestamp DESC", (entity_id, entity_id, relation_type))
            else:
                cursor.execute("SELECT * FROM relationships WHERE from_entity = ? OR to_entity = ? ORDER BY timestamp DESC", (entity_id, entity_id))
            rows = cursor.fetchall()
            return [Relationship.from_row(row) for row in rows]

    def add_event(self, event: Event) -> None:
        """Add an event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (event_type, actor_id, target_id, timestamp, platform, data, processed, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_type,
                event.actor_id,
                event.target_id,
                event.timestamp,
                event.platform,
                json.dumps(event.data) if event.data else None,
                int(event.processed),
                event.processed_at
            ))
            conn.commit()

    def get_events(self, event_type: Optional[str] = None, processed: Optional[bool] = None, limit: int = 10) -> List[Event]:
        """Retrieve events, optionally filtered by type or processed status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            if processed is not None:
                query += " AND processed = ?"
                params.append(int(processed))
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [Event.from_row(row) for row in rows]

    def mark_event_processed(self, event_id: int) -> None:
        """Mark an event as processed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE events SET processed = 1, processed_at = ? WHERE id = ?", (datetime.now().isoformat(), event_id))
            conn.commit()

    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics about the world state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            stats = {}
            cursor.execute("SELECT COUNT(*) FROM entities")
            stats['entity_count'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM facts")
            stats['fact_count'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM relationships")
            stats['relationship_count'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM events")
            stats['event_count'] = cursor.fetchone()[0]
            return stats


def create_world_state_manager(core=None) -> WorldStateManager:
    """Factory function to create a WorldStateManager"""
    # In a real scenario, 'core' might provide a shared DB connection or config
    return WorldStateManager(db_path="/Users/ton/aura_creatine_agents/data/world_state.db")
