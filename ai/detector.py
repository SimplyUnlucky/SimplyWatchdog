from core.event_bus import event_bus, Event, EventType
from core.database import db
from utils.logger import logger
from utils.config import config
from .knowledge_base import OBSERVED_SUSPICIOUS_PORTS, SUSPICIOUS_PROCESS_NAMES, SUSPICIOUS_PARENTS
import time
import pandas as pd
from sklearn.ensemble import IsolationForest
import threading
import pickle
import base64
import psutil

class AIDetector:
    def __init__(self):
        self.running = False
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        self.event_buffer = []
        self.lock = threading.Lock()
        
        # Subscribe to events
        event_bus.subscribe(EventType.PROCESS_NEW, self.check_process_rules)
        event_bus.subscribe(EventType.NET_CONN_NEW, self.check_network_rules)
        
        # Start background learning loop
        threading.Thread(target=self._learning_loop, daemon=True).start()

    def check_process_rules(self, event: Event):
        data = event.data
        self._check_suspicious(data)

        # 2. Suspicious Parent (Heuristic)
        # In a real app, we'd look up parent name from PPID. 
        # For now, we assume we might track ppid->name mappings or check live.
        # This is a placeholder for that logic.
        pass

    def check_network_rules(self, event: Event):
        data = event.data
        remote_port = data.get('remote_port')
        
        # 1. Suspicious Port
        if remote_port in OBSERVED_SUSPICIOUS_PORTS:
            desc = OBSERVED_SUSPICIOUS_PORTS[remote_port]
            self._alert("Medium", f"Connection to suspicious port {remote_port} ({desc}) by {data.get('process_name')}")

    def _alert(self, severity: str, message: str):
        alert_data = {
            'severity': severity,
            'message': message,
            'timestamp': time.time()
        }
        event_bus.publish(Event(EventType.ALERT_GENERATED, data=alert_data, source="AIDetector"))
        logger.warning(f"[{severity}] {message}")

    def _learning_loop(self):
        """
        Periodically trains the anomaly detection model on historical data.
        In a real scenario, this would load from DB, feature engineer, and train.
        """
        while True:
            time.sleep(600) # Train every 10 mins
            self._train_model()

        pass

    def _check_suspicious(self, proc_info):
        """
        Shared logic to check if a process is suspicious.
        Returns (is_suspicious: bool, severity: str, message: str)
        """
        # 1. Check Name
        pname = proc_info.get('name', '').lower()
        pid = proc_info.get('pid', 0)
        
        # Smart Check for Shells
        if pname in ["powershell.exe", "cmd.exe"]:
            cmdline = ""
            # Handle different data structures (psutil dict vs event data)
            if 'cmdline' in proc_info:
                cmdline = " ".join(proc_info['cmdline'] or []).lower()
            
            suspicious_args = ["-enc", "-encodedcommand", "downloadstring", "invoke-webrequest", "bypass", "hidden"]
            if any(arg in cmdline for arg in suspicious_args):
                self._alert("High", f"Suspicious Shell Command: {pname} (PID: {pid})")
                return True
            return False # Safe shell

        # Generic Suspicious List
        if pname in SUSPICIOUS_PROCESS_NAMES:
            self._alert("Medium", f"Suspicious Process Name: {pname} (PID: {pid})")
            return True
            
        return False

    def run_deep_scan(self, stop_event=None, callback=None):
        """
        Iterate all running processes and check for anomalies.
        This is a 'manual' scan triggered by the user.
        """
        logger.info("Starting Deep Scan...")
        total = 0
        issues = 0
        
        # Get parent process to whitelist self
        try:
            myself = psutil.Process()
            parents = [p.pid for p in myself.parents()]
            parents.append(myself.pid)
        except:
            parents = []
            
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe', 'ppid']):
            if stop_event and stop_event.is_set():
                logger.info("Deep Scan stopped by user.")
                break
                
            total += 1
            
            # Whitelist Self and Parents (Shell)
            if proc.info['pid'] in parents:
                continue
                
            if self._check_suspicious(proc.info):
                issues += 1

            if callback and total % 10 == 0:
                callback(total)
                
        logger.info(f"Deep Scan complete. Scanned {total} processes. Found {issues} issues.")
        return total, issues
