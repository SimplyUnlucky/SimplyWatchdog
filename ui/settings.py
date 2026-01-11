from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                               QLabel, QDoubleSpinBox, QDialogButtonBox, QSlider, QLineEdit,
                               QTabWidget, QWidget, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt
from utils.config import config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 300)
        self.setStyleSheet("""
            QDialog { background: #1e1e1e; color: #fff; }
            QLabel { color: #ccc; }
            QDoubleSpinBox { background: #333; color: #fff; border: 1px solid #555; padding: 5px; }
            QSlider::handle:horizontal { background: #00bcd4; width: 15px; margin: -5px 0; border-radius: 7px; }
        """)
        
        layout = QVBoxLayout(self)
        
        # 1. Monitoring Interval
        form = QFormLayout()
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 10.0)
        self.interval_spin.setValue(config.get('monitoring_interval', 1.0))
        self.interval_spin.setStyleSheet("background: #222; color: #fff; border: 1px solid #444;")
        form.addRow("Update Interval (s):", self.interval_spin)
        layout.addLayout(form)
        
        # 2. Filters Group (Tabs)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; }
            QTabBar::tab { background: #222; color: #888; padding: 8px 16px; }
            QTabBar::tab:selected { background: #00bcd4; color: #000; }
        """)
        
        self.net_tab = QWidget()
        self.proc_tab = QWidget()
        
        self.tabs.addTab(self.net_tab, "Ignored IPs")
        self.tabs.addTab(self.proc_tab, "Ignored Services")
        
        # Network Filter Setup
        net_layout = QVBoxLayout(self.net_tab)
        net_lbl = QLabel("Select IPs to IGNORE (Whitelist):")
        net_layout.addWidget(net_lbl)
        
        self.net_list = QListWidget()
        self.net_list.setSelectionMode(QListWidget.MultiSelection) # Allow multiple select? No, using check boxes better
        net_layout.addWidget(self.net_list)
        
        # Process Filter Setup
        proc_layout = QVBoxLayout(self.proc_tab)
        proc_lbl = QLabel("Select Processes to IGNORE (Whitelist):")
        proc_layout.addWidget(proc_lbl)
        
        self.proc_list = QListWidget()
        proc_layout.addWidget(self.proc_list)
        
        # Refresh Button for lists
        refresh_btn = QPushButton("Refresh Active Lists")
        refresh_btn.clicked.connect(self.populate_lists)
        layout.addWidget(self.tabs)
        layout.addWidget(refresh_btn)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("SAVE SETTINGS")
        save_btn.clicked.connect(self.save_settings)
        btns.addWidget(save_btn)
        layout.addLayout(btns)
        
        self.populate_lists()

    def populate_lists(self):
        import psutil
        self.net_list.clear()
        self.proc_list.clear()
        
        # Current Config
        ignored_ips = set(config.get('filters', {}).get('network_ignore', []))
        ignored_procs = set(config.get('filters', {}).get('service_ignore', []))
        
        # --- Network ---
        # Add existing ignored first
        seen_ips = set()
        for ip in ignored_ips:
            self._add_check_item(self.net_list, ip, True)
            seen_ips.add(ip)
            
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    ip = conn.raddr.ip
                    if ip not in seen_ips:
                        self._add_check_item(self.net_list, ip, False)
                        seen_ips.add(ip)
        except: pass
        
        # --- Processes ---
        seen_procs = set()
        for p in ignored_procs:
            self._add_check_item(self.proc_list, p, True)
            seen_procs.add(p)
            
        try:
            for p in psutil.process_iter(['name']):
                name = p.info['name']
                if name and name not in seen_procs:
                     self._add_check_item(self.proc_list, name, False)
                     seen_procs.add(name)
        except: pass

    def _add_check_item(self, list_widget, text, checked):
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        list_widget.addItem(item)

    def save_settings(self):
        # 1. Interval
        config.set('monitoring_interval', self.interval_spin.value())
        
        # 2. Network Filters
        new_ips = []
        for i in range(self.net_list.count()):
            item = self.net_list.item(i)
            if item.checkState() == Qt.Checked:
                new_ips.append(item.text())
                
        # 3. Proc Filters
        new_procs = []
        for i in range(self.proc_list.count()):
            item = self.proc_list.item(i)
            if item.checkState() == Qt.Checked:
                new_procs.append(item.text())
        
        filters = config.get('filters', {})
        filters['network_ignore'] = new_ips
        filters['service_ignore'] = new_procs
        config.set('filters', filters)
        
        self.accept()
