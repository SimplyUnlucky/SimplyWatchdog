OBSERVED_SUSPICIOUS_PORTS = {
    4444: "Metasploit Default",
    6667: "IRC (Botnet C2)",
    1337: "Hacker Speak Port",
    3389: "RDP (Unknown source)",
    5900: "VNC"
}

SUSPICIOUS_PROCESS_NAMES = {
    "nc.exe", "ncat.exe", "netcat.exe", 
    "powershell.exe", "cmd.exe", # Context dependent, but worth watching
    "wscript.exe", "cscript.exe",
    "mimikatz.exe", "procdump.exe"
}

SUSPICIOUS_PARENTS = {
    "winword.exe": ["cmd.exe", "powershell.exe"],
    "excel.exe": ["cmd.exe", "powershell.exe"],
    "outlook.exe": ["cmd.exe", "powershell.exe"],
    "chrome.exe": ["cmd.exe", "powershell.exe", "unknown.exe"] # Drive-by downloads
}
