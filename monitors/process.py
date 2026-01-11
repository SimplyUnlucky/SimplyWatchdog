import psutil
import time
from typing import Dict, Set
from .base import BaseMonitor
from core.event_bus import event_bus, Event, EventType
from utils.logger import logger

class ProcessMonitor(BaseMonitor):
    def __init__(self, interval: float = 2.0):
        super().__init__("ProcessMonitor", interval)
        self._known_pids: Set[int] = set()
        self._process_cache: Dict[int, Dict] = {}
        
        # Initial snapshot
        self._refresh_processes()

    def _refresh_processes(self):
        current_pids = set(psutil.pids())
        
        # New processes
        new_pids = current_pids - self._known_pids
        for pid in new_pids:
            try:
                proc = psutil.Process(pid)
                with proc.oneshot():
                    proc_info = {
                        'pid': pid,
                        'name': proc.name(),
                        'ppid': proc.ppid(),
                        'create_time': proc.create_time(),
                        'cmdline': proc.cmdline(),
                        'status': proc.status(),
                        'username': proc.username(),
                        'exe': proc.exe()
                    }
                self._process_cache[pid] = proc_info
                self._publish_new_process(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Terminated processes
        terminated_pids = self._known_pids - current_pids
        for pid in terminated_pids:
            if pid in self._process_cache:
                self._publish_term_process(self._process_cache[pid])
                del self._process_cache[pid]

        self._known_pids = current_pids

    def _publish_new_process(self, info: Dict):
        event_bus.publish(Event(EventType.PROCESS_NEW, data=info, source="ProcessMonitor"))
        logger.debug(f"New Process: {info['name']} ({info['pid']})")

    def _publish_term_process(self, info: Dict):
        event_bus.publish(Event(EventType.PROCESS_TERM, data=info, source="ProcessMonitor"))

    def collect(self):
        self._refresh_processes()
