import psutil
import time
from .base import BaseMonitor
from core.event_bus import event_bus, Event, EventType

class ResourceMonitor(BaseMonitor):
    def __init__(self, interval: float = 1.0):
        super().__init__("ResourceMonitor", interval)

    def collect(self):
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # Memory
        mem = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Network Speed
        net_io = psutil.net_io_counters()
        now = time.time()
        
        if hasattr(self, '_last_net_io'):
            # Calculate bytes per second
            dt = now - self._last_net_time
            if dt > 0:
                bytes_sent = (net_io.bytes_sent - self._last_net_io.bytes_sent) / dt
                bytes_recv = (net_io.bytes_recv - self._last_net_io.bytes_recv) / dt
            else:
                bytes_sent = 0
                bytes_recv = 0
        else:
            bytes_sent = 0
            bytes_recv = 0
            
        self._last_net_io = net_io
        self._last_net_time = now
        
        data = {
            'cpu': cpu_percent,
            'memory': {
                'percent': mem.percent,
                'used': mem.used,
                'total': mem.total
            },
            'disk': {
                'percent': disk.percent,
                'used': disk.used,
                'total': disk.total
            },
            'network': {
                'speed_sent': bytes_sent,
                'speed_recv': bytes_recv
            }
        }
        
        # Publish generic resource update (optional, usually pulled by UI)
        # But for AI anomaly detection, we might want to stream this
        if cpu_percent > 90.0:
            event_bus.publish(Event(EventType.RES_CPU_HIGH, data=data, source="ResourceMonitor"))
        
        if mem.percent > 90.0:
            event_bus.publish(Event(EventType.RES_MEM_HIGH, data=data, source="ResourceMonitor"))
            
        # Continuous Update for UI
        event_bus.publish(Event(EventType.RES_UPDATE, data=data, source="ResourceMonitor"))
