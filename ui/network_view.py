from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from .bridge import bridge
import psutil

class NetworkView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Process", "PID", "Local Addr", "Remote Addr", "Status", "Risk"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.rows = {} # Signature -> Row Index (Simplified, just appending for log feel)
        self.max_rows = 100
        
        # Wire up
        bridge.net_new.connect(self.add_connection)
        
        # Initial Population (Hardcore Mode)
        self.populate_initial()

    def populate_initial(self):
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_ESTABLISHED:
                    # Resolve process name safely
                    try:
                        proc_name = psutil.Process(conn.pid).name()
                    except:
                        proc_name = "unknown"
                        
                    data = {
                        'pid': conn.pid,
                        'process_name': proc_name,
                        'local_ip': conn.laddr.ip,
                        'local_port': conn.laddr.port,
                        'remote_ip': conn.raddr.ip if conn.raddr else "0.0.0.0",
                        'remote_port': conn.raddr.port if conn.raddr else 0,
                        'status': conn.status
                    }
                    self.add_connection(data)
        except:
            pass

    def add_connection(self, data):
        # Insert at top
        self.table.insertRow(0)
        
        self.table.setItem(0, 0, QTableWidgetItem(str(data.get('process_name'))))
        self.table.setItem(0, 1, QTableWidgetItem(str(data.get('pid'))))
        self.table.setItem(0, 2, QTableWidgetItem(f"{data.get('local_ip')}:{data.get('local_port')}"))
        self.table.setItem(0, 3, QTableWidgetItem(f"{data.get('remote_ip')}:{data.get('remote_port')}"))
        self.table.setItem(0, 4, QTableWidgetItem(str(data.get('status'))))
        
        # Risk (Placeholder)
        risk_item = QTableWidgetItem("Normal")
        self.table.setItem(0, 5, risk_item)
        
        # Limit rows
        if self.table.rowCount() > self.max_rows:
            self.table.removeRow(self.max_rows)
