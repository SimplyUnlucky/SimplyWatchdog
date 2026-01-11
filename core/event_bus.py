from typing import Callable, Dict, List, Any
from enum import Enum
import time
import traceback
from utils.logger import logger

class EventType(Enum):
    # System Events
    STARTUP = "system.startup"
    SHUTDOWN = "system.shutdown"
    
    # Process Events
    PROCESS_NEW = "process.new"
    PROCESS_TERM = "process.term"
    PROCESS_SUSPICIOUS = "process.suspicious"
    
    # Network Events
    NET_CONN_NEW = "net.connection.new"
    NET_DATA_SPIKE = "net.data.spike"
    
    # File Events
    FILE_MODIFIED = "file.modified"
    FILE_CREATED = "file.created"
    FILE_DELETED = "file.deleted"
    
    # Resource Events
    RES_UPDATE = "resource.update"
    RES_CPU_HIGH = "resource.cpu.high"
    RES_MEM_HIGH = "resource.mem.high"
    
    # AI/Alert Events
    ANOMALY_DETECTED = "ai.anomaly"
    ALERT_GENERATED = "alert.generated"

class Event:
    def __init__(self, event_type: EventType, data: Any = None, source: str = "unknown"):
        self.type = event_type
        self.data = data
        self.source = source
        self.timestamp = time.time()
        
    def __str__(self):
        return f"[{self.timestamp}] {self.type.value} from {self.source}: {self.data}"

class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._all_subscribers: List[Callable[[Event], None]] = [] # Subscribe to everything

    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """Subscribe to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type.value}: {callback.__name__}")

    def subscribe_all(self, callback: Callable[[Event], None]):
        """Subscribe to ALL events (for logging/UI stream)."""
        self._all_subscribers.append(callback)

    def publish(self, event: Event):
        """Publish an event to all subscribers."""
        # logger.debug(f"Publishing event: {event.type.value}")
        
        # Notify specific subscribers
        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                self._safe_execute(callback, event)
                
        # Notify global subscribers
        for callback in self._all_subscribers:
            self._safe_execute(callback, event)

    def _safe_execute(self, callback, event):
        try:
            callback(event)
        except Exception as e:
            logger.error(f"Error in event handler {callback.__name__}: {e}")
            logger.debug(traceback.format_exc())

# Global Instance
event_bus = EventBus()
