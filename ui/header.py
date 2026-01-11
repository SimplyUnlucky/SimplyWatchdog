from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal
from .assets import assets

class CustomHeader(QWidget):
    settings_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo/Title Area
        title_chem = QWidget()
        title_chem.setObjectName("HeaderTitle")
        title_layout = QHBoxLayout(title_chem)
        title_layout.setContentsMargins(0,0,0,0)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(assets.get_pixmap("shield", 32))
        title_layout.addWidget(self.icon_label)
        
        self.title = QLabel("Simply Watchdog")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffff; margin-left: 10px;")
        title_layout.addWidget(self.title)
        
        layout.addWidget(title_chem)
        layout.addStretch()
        
        # Status Text
        self.status = QLabel("● SYSTEM SECURE")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            background-color: rgba(0, 255, 0, 0.1); 
            color: #00ff88; 
            border: 1px solid #00ff88; 
            border-radius: 12px; 
            padding: 4px 12px;
            font-weight: bold;
            font-size: 10pt;
            margin-right: 20px;
        """)
        layout.addWidget(self.status)
        
        layout.addSpacing(20)
        
        # Settings Icon
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(assets.get_icon("settings"))
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton:hover { background-color: rgba(0, 255, 255, 0.1); border-radius: 5px; }
        """)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.settings_btn)

    def set_status(self, safe: bool):
        if safe:
            self.status.setText("● SYSTEM SECURE")
            self.status.setStyleSheet("""
                background-color: rgba(0, 255, 0, 0.1); 
                color: #00ff88; 
                border: 1px solid #00ff88; 
                border-radius: 12px; 
                padding: 4px 12px;
                font-weight: bold;
                font-size: 10pt;
                margin-right: 20px;
            """)
        else:
            self.status.setText("● THREAT DETECTED")
            self.status.setStyleSheet("""
                background-color: rgba(255, 0, 0, 0.1); 
                color: #ff5252; 
                border: 1px solid #ff5252; 
                border-radius: 12px; 
                padding: 4px 12px;
                font-weight: bold;
                font-size: 10pt;
                margin-right: 20px;
            """)
