# ==========================================================
# AI KNOWLEDGE BASE — WINDOWS SYSTEM WATCHDOG (DEFENSIVE)
# ==========================================================

# 1. Suspicious / High-Risk Ports
SUSPICIOUS_PORTS = {
    4444: "Metasploit / Reverse Shell",
    1337: "Backdoor / C2 Channel",
    2222: "Alternate SSH (Backdoor)",
    6667: "IRC Botnet C2",
    9001: "Tor ORPort",
    9050: "Tor SOCKS Proxy",
    3389: "RDP from Untrusted Source",
    5900: "VNC Remote Control",
    5985: "WinRM HTTP",
    5986: "WinRM HTTPS",
    53: "DNS Tunneling Possible",
    443: "HTTPS C2 Possible"
}

# 2. Suspicious Process Names
SUSPICIOUS_PROCESS_NAMES = {
    "mimikatz.exe", "procdump.exe", "rubeus.exe",
    "powershell.exe", "cmd.exe",
    "wscript.exe", "cscript.exe",
    "mshta.exe", "rundll32.exe",
    "regsvr32.exe", "installutil.exe",
    "certutil.exe", "bitsadmin.exe",
    "nc.exe", "ncat.exe", "netcat.exe",
    "plink.exe", "putty.exe",
    "whoami.exe", "net.exe", "nltest.exe",
    "tasklist.exe", "ipconfig.exe"
}

# 3. Suspicious Parent → Child Relationships
SUSPICIOUS_PROCESS_PARENTS = {
    "winword.exe": ["cmd.exe", "powershell.exe", "mshta.exe", "wscript.exe", "cscript.exe"],
    "excel.exe": ["cmd.exe", "powershell.exe", "mshta.exe"],
    "outlook.exe": ["powershell.exe", "cmd.exe"],
    "chrome.exe": ["cmd.exe", "powershell.exe", "rundll32.exe", "mshta.exe"],
    "msedge.exe": ["cmd.exe", "powershell.exe"],
    "wscript.exe": ["powershell.exe", "cmd.exe"]
}

# 4. Suspicious Network Indicators
SUSPICIOUS_NETWORK_INDICATORS = {
    "ip_ranges": [
        "45.0.0.0/8",
        "185.0.0.0/8",
        "91.0.0.0/8"
    ],
    "dynamic_dns": [
        "duckdns.org", "no-ip.com",
        "dynu.net", "ddns.net"
    ],
    "domain_keywords": [
        "pastebin", "anonfiles",
        "transfer", "cdn-", "update-",
        "panel", "gate", "c2"
    ]
}

# 5. Persistence Indicators
PERSISTENCE_LOCATIONS = {
    "registry": [
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
        r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        r"HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce"
    ],
    "folders": [
        "Startup",
        "AppData\\Roaming",
        "AppData\\Local\\Temp"
    ],
    "scheduled_tasks": True,
    "services": True
}

# 6. Risk Scoring Engine
RISK_SCORING = {
    "suspicious_port": 30,
    "lolbin_usage": 20,
    "office_spawning_shell": 40,
    "browser_spawning_shell": 35,
    "unknown_external_ip": 25,
    "dynamic_dns_usage": 30,
    "persistence_attempt": 50,
    "unsigned_binary": 20,
    "multiple_indicators_multiplier": 2.0
}

# 7. Severity Thresholds
SEVERITY_LEVELS = {
    "LOW": 0,
    "MEDIUM": 30,
    "HIGH": 60,
    "CRITICAL": 90
}

# 8. MITRE ATT&CK Mapping
MITRE_MAPPING = {
    "office_spawning_shell": "T1204.002",
    "lolbin_execution": "T1059",
    "credential_dumping": "T1003",
    "command_and_control": "T1071",
    "persistence": "T1547",
    "lateral_movement": "T1021",
    "defense_evasion": "T1218"
}

# 9. AI Verdict Template
AI_VERDICT_TEMPLATE = {
    "timestamp": None,
    "hostname": None,
    "severity": None,
    "risk_score": 0,
    "process": None,
    "parent_process": None,
    "command_line": None,
    "network_activity": {
        "destination_ip": None,
        "destination_domain": None,
        "destination_port": None
    },
    "persistence": False,
    "indicators": [],
    "mitre_techniques": [],
    "explanation": []
}
