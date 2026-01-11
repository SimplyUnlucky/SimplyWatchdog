from abc import ABC, abstractmethod
from threading import Thread, Event as ThreadEvent
from typing import Optional
from utils.logger import logger
from core.event_bus import event_bus, Event, EventType
from utils.config import config

class BaseMonitor(ABC):
    def __init__(self, name: str, interval: float = 1.0):
        self.name = name
        self.interval = interval
        self._stop_event = ThreadEvent()
        self._thread: Optional[Thread] = None

    def start(self):
        if self._thread and self._thread.is_alive():
            logger.warning(f"{self.name} is already running.")
            return

        logger.info(f"Starting {self.name}...")
        self._stop_event.clear()
        self._thread = Thread(target=self._run_loop, daemon=True, name=self.name)
        self._thread.start()

    def stop(self):
        if not self._thread or not self._thread.is_alive():
            return
            
        logger.info(f"Stopping {self.name}...")
        self._stop_event.set()
        self._thread.join(timeout=2.0)
        logger.info(f"{self.name} stopped.")

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self.collect()
            except Exception as e:
                logger.error(f"Error in {self.name} loop: {e}")
            
            self._stop_event.wait(self.interval)

    @abstractmethod
    def collect(self):
        """Implement data collection logic here."""
        pass
