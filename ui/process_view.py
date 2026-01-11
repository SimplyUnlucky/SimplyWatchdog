from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, 
                               QTreeWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from .bridge import bridge
import psutil

class ProcessView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Process Name", "PID", "Parent ID", "User", "Status"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 300) # Name
        self.tree.setColumnWidth(1, 80)  # PID
        self.tree.setColumnWidth(2, 80) # PPID
        self.tree.setColumnWidth(3, 150) # User
        
        # Styles
        self.tree.setStyleSheet("""
            QTreeWidget::item { padding: 4px; border-bottom: 1px solid #222; }
            QTreeWidget::item:selected { background-color: rgba(0, 188, 212, 0.2); border: 1px solid #00bcd4; }
        """)
        
        layout.addWidget(self.tree)
        
        self.items = {} # PID -> QTreeWidgetItem
        
        # Connect signals
        bridge.process_new.connect(self.add_process)
        bridge.process_term.connect(self.remove_process)
        
        # Initial Population (Hardcore Mode)
        self.populate_initial()

    def populate_initial(self):
        self.tree.clear()
        
        # 1. Fetch all processes
        procs = []
        try:
            for p in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'status']):
                procs.append(p.info)
        except:
            pass
            
        # 2. Build Map
        proc_map = {p['pid']: p for p in procs}
        children_map = {}
        for p in procs:
            ppid = p['ppid']
            if ppid not in children_map:
                children_map[ppid] = []
            children_map[ppid].append(p)
            
        # 3. Recursive Insert
        items = {}
        
        def add_proc(p_info, parent_item=None):
            pid = p_info['pid']
            name = p_info['name']
            
            item = QTreeWidgetItem(parent_item or self.tree)
            item.setText(0, name)
            item.setText(1, str(pid))
            item.setText(2, str(p_info['ppid']))
            item.setText(3, str(p_info.get('username', '')))
            
            # Status styling
            status = p_info['status']
            item.setText(4, status)
            
            # Icon (use generic or asset if available)
            # item.setIcon(0, assets.get_icon("cpu")) 
            
            items[pid] = item
            
            # Add children
            if pid in children_map:
                for child in children_map[pid]:
                    add_proc(child, item)
                    
        # Add roots (orphan processes or those whose parents aren't in list)
        for p in procs:
            if p['ppid'] not in proc_map:
                add_proc(p)
                
        self.tree.expandAll()

    def add_process(self, data):
        pid = data['pid']
        if pid in self.items:
            return

        item = QTreeWidgetItem([
            str(data['name']),
            str(data['pid']),
            str(data['ppid']),
            str(data['username']),
            str(data['status'])
        ])
        
        # Simple color coding for suspicious items could go here
        
        self.items[pid] = item
        self.tree.addTopLevelItem(item)

    def remove_process(self, data):
        pid = data['pid']
        if pid in self.items:
            item = self.items[pid]
            index = self.tree.indexOfTopLevelItem(item)
            self.tree.takeTopLevelItem(index)
            del self.items[pid]
