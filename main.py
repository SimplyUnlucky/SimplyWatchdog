import sys
import time
import signal
from utils.logger import logger
from utils.config import config
from core.event_bus import event_bus, Event, EventType

def signal_handler(sig, frame):
    logger.info("Shutdown signal received...")
    event_bus.publish(Event(EventType.SHUTDOWN, source="main"))
    sys.exit(0)

def main():
    logger.info(f"Starting {config.get('app.name')} v{config.get('app.version')}")
    
    # Register Signal Handlers
    signal.signal(signal.SIGINT, signal_handler)
    
    # Publish Startup Event
    event_bus.publish(Event(EventType.STARTUP, source="main"))
    
    # Initialize Monitors
    from monitors.process import ProcessMonitor
    from monitors.network import NetworkMonitor
    from monitors.resources import ResourceMonitor
    from monitors.filesystem import FileSystemMonitor

    from ai.detector import AIDetector
    
    # Initialize Core Engines
    ai_engine = AIDetector()

    monitors = [
        ProcessMonitor(),
        NetworkMonitor(),
        ResourceMonitor(),
        FileSystemMonitor()
    ]

    for m in monitors:
        m.start()
    
    # Start UI
    try:
        from ui.main_window import run_ui
        logger.info("Starting GUI...")
        run_ui()
            
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
    finally:
        logger.info("Stopping monitors...")
        # Signal cleanup
        event_bus.publish(Event(EventType.SHUTDOWN, source="main"))
        for m in monitors:
            m.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
