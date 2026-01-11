from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .base import BaseMonitor
from core.event_bus import event_bus, Event, EventType
from utils.logger import logger
from utils.config import config
import os

class SystemWatchHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            event_bus.publish(Event(EventType.FILE_CREATED, data={'path': event.src_path}, source="FileMonitor"))
            logger.debug(f"File Created: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            event_bus.publish(Event(EventType.FILE_MODIFIED, data={'path': event.src_path}, source="FileMonitor"))

    def on_deleted(self, event):
        if not event.is_directory:
            event_bus.publish(Event(EventType.FILE_DELETED, data={'path': event.src_path}, source="FileMonitor"))

class FileSystemMonitor(BaseMonitor):
    def __init__(self, interval: float = 1.0):
        # Watchdog uses its own threads, so interval is just for the dummy loop
        super().__init__("FileSystemMonitor", interval)
        self.observer = Observer()
        self.handler = SystemWatchHandler()
        self._configured = False

    def start(self):
        # Configure paths from config
        paths = config.get("monitoring.file_system_paths", [])
        for path in paths:
            # Expand vars like %USERNAME% (Windows)
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                self.observer.schedule(self.handler, expanded_path, recursive=False)
                logger.info(f"Watching directory: {expanded_path}")
                self._configured = True
            else:
                logger.warning(f"Path not found, skipping watch: {expanded_path}")

        if self._configured:
            self.observer.start()
            super().start()
        else:
            logger.warning("No valid paths to watch. FileSystemMonitor idle.")

    def stop(self):
        if self._configured:
            self.observer.stop()
            self.observer.join()
        super().stop()

    def collect(self):
        # Watchdog does the work, we just keep the thread alive or do periodic status checks
        pass
