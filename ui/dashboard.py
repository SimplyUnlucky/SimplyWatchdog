from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFrame, QListWidget, QProgressBar, QGridLayout, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, QTimer, Signal
from .bridge import bridge
from .assets import assets
import threading
import time
from utils.config import config

class StatCard(QFrame):
    def __init__(self, title, icon_name=""):
        super().__init__()
        self.setObjectName("StatCard")
        self.setStyleSheet("""
            #StatCard {
                background-color: rgba(30, 30, 40, 180);
                border: 1px solid #333;
                border-radius: 10px;
            }
        """)
        self.layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(assets.get_pixmap(icon_name, 24))
        header.addWidget(icon)
        
        self.title_lbl = QLabel(f"{title}")
        self.title_lbl.setStyleSheet("color: #888; font-weight: bold; font-size: 10pt;")
        header.addWidget(self.title_lbl)
        header.addStretch()
        self.layout.addLayout(header)
        
        self.value_lbl = QLabel("0%")
        self.value_lbl.setStyleSheet("color: #fff; font-size: 18pt; font-weight: bold;")
        self.value_lbl.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.value_lbl)
        
        self.bar = QProgressBar()
        self.bar.setFixedHeight(4)
        self.bar.setTextVisible(False)
        self.layout.addWidget(self.bar)

    def update_val(self, val_str, val_int, color="#00bcd4"):
        self.value_lbl.setText(val_str)
        self.bar.setValue(min(100, int(val_int)))
        self.bar.setStyleSheet(f"""
            QProgressBar {{ background: #333; border: none; border-radius: 2px; }}
            QProgressBar::chunk {{ background: {color}; border-radius: 2px; }}
        """)

class Dashboard(QWidget):
    scan_finished = Signal(int, int) # Total, Issues

    def __init__(self):
        super().__init__()
        self.scan_finished.connect(self.on_scan_finished)
         # Main Layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 1. Top KPI Row (Uptime, Threats)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        
        self.uptime_card = StatCard("UPTIME", "clock")
        self.uptime_card.setObjectName("GlassCard")
        self.uptime_card.update_val("00:00:00", 100, "#00ffff")
        
        self.threats_card = StatCard("THREATS BLOCKED", "shield")
        self.threats_card.setObjectName("GlassCard")
        self.threats_card.update_val("0", 0, "#ff0055") # Red for threats
        
        kpi_layout.addWidget(self.uptime_card)
        kpi_layout.addWidget(self.threats_card)
        layout.addLayout(kpi_layout)

        # 2. Status Banner & Scan
        banner = QFrame()
        banner.setObjectName("StatusBanner")
        banner_layout = QHBoxLayout(banner)
        
        # ... Status Text ...
        txt_layout = QVBoxLayout()
        lbl1 = QLabel("System Status")
        lbl1.setStyleSheet("color: #64748b; border: none; font-size: 10pt;")
        self.main_status = QLabel("MONITORING ACTIVE")
        self.main_status.setStyleSheet("color: #00ffff; font-size: 20px; font-weight: bold; border: none;")
        txt_layout.addWidget(lbl1)
        txt_layout.addWidget(self.main_status)
        banner_layout.addLayout(txt_layout)

        layout.addWidget(banner)
        
        # 3. Resource Grid
        grid_layout = QHBoxLayout()
        self.cpu_card = StatCard("CPU Usage", "cpu")
        self.mem_card = StatCard("Memory", "memory") # Changed ram -> memory
        self.disk_card = StatCard("Disk I/O", "disk") # Changed hdd -> disk
        self.net_card = StatCard("Network", "wifi")
        
        grid_layout.addWidget(self.cpu_card)
        grid_layout.addWidget(self.mem_card)
        grid_layout.addWidget(self.disk_card)
        grid_layout.addWidget(self.net_card)
        
        layout.addLayout(grid_layout)

        # 4. Bottom Section (Quick Stats & Alerts)
        bottom_layout = QHBoxLayout()
        
        # Quick Stats
        qs_frame = QFrame()
        qs_frame.setObjectName("GlassCard")
        qs_layout = QVBoxLayout(qs_frame)
        qs_title = QLabel("Quick Stats")
        qs_title.setStyleSheet("color: #e0faff; font-size: 12pt; border: none; margin-bottom: 15px;")
        
        # Add Activity Icon to title or beside it? 
        # User listed: Activity, Clock, Zap, TrendingUp.
        # Let's add them as rows with icons.
        
        title_box = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(assets.get_pixmap("activity", 24))
        title_box.addWidget(title_icon)
        title_box.addWidget(qs_title)
        title_box.addStretch()
        qs_layout.addLayout(title_box)
        
        # Helper to create row with icon
        def create_stat_row(icon_name, text, ref_name):
            row = QHBoxLayout()
            icon = QLabel()
            icon.setPixmap(assets.get_pixmap(icon_name, 20))
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #94a3b8; font-size: 10pt; border: none;")
            row.addWidget(icon)
            row.addWidget(lbl)
            row.addStretch()
            setattr(self, ref_name, lbl) # Store ref
            qs_layout.addLayout(row)
            
        create_stat_row("trending_up", "Active Processes: --", "qs_procs")
        create_stat_row("clock", "Network Conns: --", "qs_conns")
            
        qs_layout.addStretch()
        bottom_layout.addWidget(qs_frame, 1)

        # Recent Alerts
        alert_frame = QFrame()
        alert_frame.setObjectName("GlassCard")
        alert_layout = QVBoxLayout(alert_frame)
        alert_title = QLabel("Recent Alerts")
        alert_title.setStyleSheet("color: #e0faff; font-size: 12pt; border: none; margin-bottom: 10px;")
        alert_layout.addWidget(alert_title)
        
        self.alert_list = QListWidget()
        self.alert_list.setStyleSheet("""
            background: transparent; border: none; color: #ff0055; font-family: 'Consolas'; font-size: 9pt;
        """)
        alert_layout.addWidget(self.alert_list)
        
        bottom_layout.addWidget(alert_frame, 2)
        layout.addLayout(bottom_layout)
        
        # Start Clock
        self.start_time = time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_uptime)
        self.timer.start(1000)
        
        # Connect
        bridge.resource_update.connect(self.update_resources)
        bridge.process_new.connect(self.update_proc_count)
        bridge.net_new.connect(self.update_net_count)
        bridge.alert.connect(self.add_alert)
        
        # Initial Stats Fix
        import psutil
        try:
            self.proc_count = len(list(psutil.process_iter()))
            self.net_count = len(psutil.net_connections())
        except:
            self.proc_count = 0
            self.net_count = 0
            
        self.qs_procs.setText(f"Active Processes: {self.proc_count}")
        self.qs_conns.setText(f"Network Conns: {self.net_count}")
        
        self.scanning = False
        self.stop_scan_event = None

    def _update_uptime(self):
        elapsed = int(time.time() - self.start_time)
        args = (elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60)
        self.uptime_card.update_val(f"{args[0]:02}:{args[1]:02}:{args[2]:02}", 100, "#00ffff")

    def update_resources(self, data):
        if 'cpu' in data:
            self.cpu_card.update_val(f"{data['cpu']}%", data['cpu'], "#00bcd4")
        if 'memory' in data:
            self.mem_card.update_val(f"{data['memory']['percent']}%", data['memory']['percent'], "#ffbd2e")
        if 'disk' in data:
             self.disk_card.update_val(f"{data['disk']['percent']}%", data['disk']['percent'], "#00bcd4")
        if 'network' in data:
            sent = data['network']['speed_sent']
            recv = data['network']['speed_recv']
            speed_str = self._format_bytes(sent + recv) + "/s"
            percent = min(100, (sent+recv) / (10*1024*1024) * 100)
            self.net_card.update_val(speed_str, percent, "#ff00ff")

    def _format_bytes(self, size):
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.1f} {power_labels[n]}B"

    def update_proc_count(self, data):
        # Only increment if it's truly new? 
        # Actually EventBus emits PROCESS_NEW for start/stop.
        # But Monitor emits for ALL on startup. 
        # If we manually init, we might double count if events arrive later.
        # Ideally Bridge should just emit the COUNT, not individual events if we display count.
        # But for now, let's trust the manual init + delta.
        # Wait, if Monitor emits all on startup, we will get +X events.
        # If we init manually to X, we get 2X.
        # Monitor emits BEFORE blocking on run? No, Monitor is in thread.
        # ProcessMonitor logic: `populate_initial` -> emits.
        # If we start Monitor BEFORE UI, events fire into void (unless Bridge caches?). Bridge does NOT cache.
        # So manual init is correct. Subsequent events are for NEW processes started AFTER app launch.
        self.proc_count += 1
        self.qs_procs.setText(f"Active Processes: {self.proc_count}")

    def update_net_count(self, data):
        self.net_count += 1
        self.qs_conns.setText(f"Network Conns: {self.net_count}")

    def add_alert(self, data):
        from PySide6.QtWidgets import QListWidgetItem
        from PySide6.QtGui import QColor
        
        severity = data.get('severity', 'Info')
        message = data.get('message', '')
        score = data.get('score')
        mitre = data.get('mitre', [])
        
        # Construct Display Text
        prefix = f"[{severity}]"
        if score is not None:
            prefix += f" (Score: {score})"
            
        display_text = f"{message}"
        if mitre:
            display_text += f"\n   ↳ [ATT&CK: {', '.join(mitre)}]"
            
        # Color based on severity
        color = "#e0faff"
        if severity == "High": color = "#ff5252"
        elif severity == "Medium": color = "#ffbd2e"
        elif severity == "Info": color = "#00bcd4"
        
        item = QListWidgetItem(f"{time.strftime('%H:%M:%S')} - {prefix} {display_text}")
        item.setForeground(QColor(color))
        self.alert_list.insertItem(0, item)
        
        # Only update big status if it's actually a threat
        if severity in ["High", "Medium"]:
            self.header.set_status(False)
            self.main_status.setText("THREAT DETECTED")
            self.main_status.setStyleSheet("color: #ff5252; font-size: 24px; font-weight: bold; border: none;")

    def run_deep_scan(self):
        if self.scanning:
            # Stop it
            if self.stop_scan_event:
                self.stop_scan_event.set()
                self.scan_btn.setText("STOPPING...")
                self.scan_btn.setEnabled(False) # Prevent double click
                bridge.alert.emit({'severity':'Info', 'message': 'Deep Scan stopped by user.'})
            return

        from ai.detector import AIDetector 
        
        self.scanning = True
        self.stop_scan_event = threading.Event()
        self.scan_btn.setText("STOP SCAN")
        self.scan_btn.setEnabled(True)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 0.2); 
                border: 1px solid #ff0000; 
                color: #ff0000;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 10pt;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: rgba(255, 0, 0, 0.4); }
        """)
        
        def worker():
            detector = AIDetector()
            total, issues = detector.run_deep_scan(stop_event=self.stop_scan_event)
            return total, issues
            
        self.thread = threading.Thread(target=self._scan_finished_trigger, args=(worker,))
        self.thread.start()

    def _scan_finished_trigger(self, worker_func):
        total, issues = worker_func()
        # Emit signal to update UI safely
        self.scan_finished.emit(total, issues)
        
    def on_scan_finished(self, total, issues):
        print(f"Scan complete: {total} items, {issues} issues")
        self.scanning = False
        self.scan_btn.setText("RUN DEEP SCAN")
        self.scan_btn.setEnabled(True)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 255, 255, 0.1); 
                border: 1px solid #00ffff; 
                color: #00ffff;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 10pt;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: rgba(0, 255, 255, 0.2); }
            QPushButton:disabled { border-color: #555; color: #555; }
        """)
        bridge.alert.emit({'severity':'Info', 'message': f'Deep Scan Finished. Scanned {total} items.'})
