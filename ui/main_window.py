import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QTabWidget, QLabel, QStatusBar)
from PySide6.QtCore import Qt
from .bridge import bridge
from .assets import assets
from .process_view import ProcessView
from .network_view import NetworkView
from .dashboard import Dashboard
from .header import CustomHeader
from PySide6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simply Watchdog")
        self.resize(1280, 800)
        self.setWindowIcon(QIcon("ui/app_icon.png"))
        
        # Setup Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Background Image
        central_widget.setObjectName("CentralWidget")
        central_widget.setStyleSheet("""
            #CentralWidget {
                background-color: #0b0f19; /* Deep dark blue/black */
            }
        """)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        
        # Custom Header
        self.header = CustomHeader()
        layout.addWidget(self.header)
        
        # Tabs container (for padding)
        tab_container = QWidget()
        tab_layout = QVBoxLayout(tab_container)
        tab_layout.setContentsMargins(10, 0, 10, 10)
        
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True) # Removes standard border, cleaner
        
        self.dashboard = Dashboard()
        self.process_view = ProcessView()
        self.network_view = NetworkView()
        
        self.tabs.addTab(self.dashboard, assets.get_icon("dashboard"), "Dashboard")
        self.tabs.addTab(self.process_view, assets.get_icon("list_tree"), "Processes")
        self.tabs.addTab(self.network_view, assets.get_icon("network"), "Network")
        
        tab_layout.addWidget(self.tabs)
        
        layout.addWidget(tab_container)
        
        # Status Bar (kept for debug messages, but minimal)
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background: rgba(0,0,0,200); color: #888;")
        self.setStatusBar(self.status_bar)
        
        # Connect Alerts
        bridge.alert.connect(self.handle_alert)
        
        # Connect Settings
        self.header.settings_clicked.connect(self.open_settings)

    def open_settings(self):
        from .settings import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.exec_()

    def handle_alert(self, data):
        msg = f"[{data['severity']}] {data['message']}"
        self.status_bar.showMessage(msg)
        
        if data['severity'] in ["High", "Medium"]:
            self.header.set_status(False)

def run_ui():
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Load Styles
    with open("ui/styles.qss", "r") as f:
        app.setStyleSheet(f.read())
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
