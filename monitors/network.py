import psutil
import socket
from typing import Dict, Set
import time
from .base import BaseMonitor
from core.event_bus import event_bus, Event, EventType
from utils.logger import logger
from utils.config import config

class NetworkMonitor(BaseMonitor):
    def __init__(self, interval: float = 1.0):
        super().__init__("NetworkMonitor", interval)
        self._known_connections: Set[str] = set() # "pid:local_port:remote_ip:remote_port"

    def collect(self):
        try:
            # kind='inet' ensures we look at IPv4/IPv6 TCP/UDP
            connections = psutil.net_connections(kind='inet')
            current_conn_signatures = set()

            for conn in connections:
                if conn.status == psutil.CONN_ESTABLISHED:
                    remote_ip = conn.raddr.ip if conn.raddr else "0.0.0.0"
                    remote_port = conn.raddr.port if conn.raddr else 0
                    
                    # Ignore loopback for now to reduce noise idx
                    if remote_ip in ("127.0.0.1", "::1", "0.0.0.0"):
                        continue
                        
                    sig = f"{conn.pid}:{conn.laddr.port}:{remote_ip}:{remote_port}"
                    current_conn_signatures.add(sig)

                    if sig not in self._known_connections:
                        self._publish_new_connection(conn, sig)
            
            self._known_connections = current_conn_signatures

        except Exception as e:
            logger.error(f"Network scan failed: {e}")

    def _publish_new_connection(self, conn, signature):
        try:
            proc_name = psutil.Process(conn.pid).name()
        except:
            proc_name = "unknown"

        data = {
            'pid': conn.pid,
            'process_name': proc_name,
            'local_ip': conn.laddr.ip,
            'local_port': conn.laddr.port,
            'remote_ip': conn.raddr.ip,
            'remote_port': conn.raddr.port,
            'status': conn.status,
            'signature': signature
        }
        
        # Filters
        ignored_ips = config.get("filters.network_ignore", "").split(",")
        ignored_ips = [ip.strip() for ip in ignored_ips if ip.strip()]
        
        if conn.raddr:
            remote_ip = conn.raddr.ip
            if remote_ip in ignored_ips:
                return # Ignored
        
        event_bus.publish(Event(EventType.NET_CONN_NEW, data=data, source="NetworkMonitor"))
        logger.info(f"New Connection: {proc_name} -> {data['remote_ip']}:{data['remote_port']}")
