from core.event_bus import event_bus, Event, EventType
from core.database import db
from utils.logger import logger
from utils.config import config
from .knowledge_base import (
    SUSPICIOUS_PORTS, SUSPICIOUS_PROCESS_NAMES, SUSPICIOUS_PROCESS_PARENTS,
    SUSPICIOUS_NETWORK_INDICATORS, RISK_SCORING, SEVERITY_LEVELS,
    MITRE_MAPPING, AI_VERDICT_TEMPLATE
)
import time
import threading
import psutil
import socket
import ipaddress

class AIDetector:
    def __init__(self):
        self.running = False
        self.lock = threading.Lock()
        
        # Subscribe to events
        event_bus.subscribe(EventType.PROCESS_NEW, self.check_process_rules)
        event_bus.subscribe(EventType.NET_CONN_NEW, self.check_network_rules)

    def check_process_rules(self, event: Event):
        data = event.data
        verdict = self._evaluate_process(data)
        if verdict['risk_score'] >= SEVERITY_LEVELS['MEDIUM']:
            self._publish_verdict(verdict)

    def check_network_rules(self, event: Event):
        data = event.data
        verdict = self._evaluate_network(data)
        if verdict['risk_score'] >= SEVERITY_LEVELS['MEDIUM']:
            self._publish_verdict(verdict)

    def _evaluate_process(self, proc_info):
        verdict = self._create_empty_verdict()
        verdict['process'] = proc_info.get('name')
        verdict['pid'] = proc_info.get('pid')
        verdict['command_line'] = " ".join(proc_info.get('cmdline', []))
        
        pname = proc_info.get('name', '').lower()
        ppid = proc_info.get('ppid')
        
        # 1. Suspicious Name
        if pname in [n.lower() for n in SUSPICIOUS_PROCESS_NAMES]:
            verdict['risk_score'] += RISK_SCORING['lolbin_usage']
            verdict['indicators'].append(f"Known suspicious process/LOLBin: {pname}")
            verdict['mitre_techniques'].append(MITRE_MAPPING.get('lolbin_execution', 'T1059'))

        # 2. Parent-Child Relationship
        if ppid:
            try:
                parent = psutil.Process(ppid)
                p_name = parent.name().lower()
                verdict['parent_process'] = p_name
                
                if p_name in SUSPICIOUS_PROCESS_PARENTS:
                    children = SUSPICIOUS_PROCESS_PARENTS[p_name]
                    if pname in [c.lower() for c in children]:
                        score = RISK_SCORING.get('office_spawning_shell', 40) if 'word' in p_name or 'excel' in p_name else RISK_SCORING.get('browser_spawning_shell', 35)
                        verdict['risk_score'] += score
                        verdict['indicators'].append(f"Suspicious parent-child: {p_name} -> {pname}")
                        verdict['mitre_techniques'].append(MITRE_MAPPING.get('office_spawning_shell', 'T1204.002'))
            except: pass

        # 3. Command Line Flags (Shells)
        if pname in ["powershell.exe", "cmd.exe"]:
            cmdline = verdict['command_line'].lower()
            suspicious_args = ["-enc", "-encodedcommand", "downloadstring", "invoke-webrequest", "bypass", "hidden"]
            if any(arg in cmdline for arg in suspicious_args):
                verdict['risk_score'] += 30
                verdict['indicators'].append("Obfuscated or download-cradle shell command")

        self._finalize_verdict(verdict)
        return verdict

    def _evaluate_network(self, net_info):
        verdict = self._create_empty_verdict()
        verdict['process'] = net_info.get('process_name')
        remote_ip = net_info.get('remote_ip')
        remote_port = net_info.get('remote_port')
        verdict['network_activity'] = {
            'destination_ip': remote_ip,
            'destination_port': remote_port
        }

        # 1. Suspicious Port
        if remote_port in SUSPICIOUS_PORTS:
            verdict['risk_score'] += RISK_SCORING['suspicious_port']
            verdict['indicators'].append(f"Connection to high-risk port {remote_port} ({SUSPICIOUS_PORTS[remote_port]})")
            verdict['mitre_techniques'].append(MITRE_MAPPING.get('command_and_control', 'T1071'))

        # 2. IP Range Check
        try:
            r_ip = ipaddress.ip_address(remote_ip)
            for cidr in SUSPICIOUS_NETWORK_INDICATORS['ip_ranges']:
                if r_ip in ipaddress.ip_network(cidr):
                    verdict['risk_score'] += RISK_SCORING['unknown_external_ip']
                    verdict['indicators'].append(f"Connection to suspicious IP range: {cidr}")
                    break
        except: pass

        # 3. Domain Keywords (if available)
        # Note: In our current bridge, we might not always have domain. 
        # But if we did, we'd check SUSPICIOUS_NETWORK_INDICATORS['domain_keywords']

        self._finalize_verdict(verdict)
        return verdict

    def _create_empty_verdict(self):
        v = AI_VERDICT_TEMPLATE.copy()
        v['indicators'] = []
        v['mitre_techniques'] = []
        v['explanation'] = []
        v['timestamp'] = time.time()
        v['hostname'] = socket.gethostname()
        return v

    def _finalize_verdict(self, verdict):
        score = verdict['risk_score']
        
        # Apply Multiplier for multiple indicators
        if len(verdict['indicators']) > 1:
            verdict['risk_score'] *= RISK_SCORING.get('multiple_indicators_multiplier', 2.0)
            verdict['explanation'].append("Risk multiplied due to multiple suspicious indicators.")

        # Determine Severity
        for level, threshold in sorted(SEVERITY_LEVELS.items(), key=lambda x: x[1], reverse=True):
            if verdict['risk_score'] >= threshold:
                verdict['severity'] = level
                break
        
        if not verdict.get('severity'):
            verdict['severity'] = "INFO"

    def _publish_verdict(self, verdict):
        msg = f"AI Verdict [{verdict['severity']}] - Score: {verdict['risk_score']} - Procs: {verdict['process']} - Tags: {', '.join(verdict['indicators'])}"
        
        alert_data = {
            'severity': verdict['severity'],
            'message': msg,
            'timestamp': verdict['timestamp'],
            'score': verdict['risk_score'],
            'mitre': verdict['mitre_techniques'],
            'indicators': verdict['indicators']
        }
        
        event_bus.publish(Event(EventType.ALERT_GENERATED, data=alert_data, source="AIDetector"))
        logger.warning(msg)

    def run_deep_scan(self, stop_event=None, callback=None):
        """
        Deep scan now uses the new risk scoring engine for all processes.
        """
        logger.info("Starting Scored Deep Scan...")
        total = 0
        issues = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'ppid']):
            if stop_event and stop_event.is_set(): break
            total += 1
            verdict = self._evaluate_process(proc.info)
            if verdict['risk_score'] >= SEVERITY_LEVELS['MEDIUM']:
                issues += 1
                self._publish_verdict(verdict)
            if callback and total % 10 == 0: callback(total)
                
        logger.info(f"Deep Scan complete. Scanned {total} processes. Found {issues} suspicious items.")
        return total, issues
