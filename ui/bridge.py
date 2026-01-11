from PySide6.QtCore import QObject, Signal
from core.event_bus import event_bus, Event, EventType

class EventBridge(QObject):
    # Define Qt Signals for each event type we care about in UI
    process_new = Signal(dict)
    process_term = Signal(dict)
    net_new = Signal(dict)
    alert = Signal(dict)
    resource_update = Signal(dict)
    
    def __init__(self):
        super().__init__()
        # Subscribe to EventBus and emit Qt Signal
        event_bus.subscribe(EventType.PROCESS_NEW, lambda e: self.process_new.emit(e.data))
        event_bus.subscribe(EventType.PROCESS_TERM, lambda e: self.process_term.emit(e.data))
        event_bus.subscribe(EventType.NET_CONN_NEW, lambda e: self.net_new.emit(e.data))
        event_bus.subscribe(EventType.ALERT_GENERATED, lambda e: self.alert.emit(e.data))
        
        # Resource monitoring usually comes via polling or events
        event_bus.subscribe(EventType.RES_UPDATE, lambda e: self.resource_update.emit(e.data))
        event_bus.subscribe(EventType.RES_CPU_HIGH, lambda e: self.resource_update.emit(e.data))
        event_bus.subscribe(EventType.RES_MEM_HIGH, lambda e: self.resource_update.emit(e.data))

# Global UI Bridge
bridge = EventBridge()
