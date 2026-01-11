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
        self.status = QLabel("SECURE")
        self.status.setStyleSheet("color: #00ff00; font-weight: bold; margin-right: 20px;")
        layout.addWidget(self.status)
        
        layout.addSpacing(20)
        
        # Bell Icon (Notification)
        self.bell_btn = QPushButton()
        self.bell_btn.setIcon(assets.get_icon("bell"))
        self.bell_btn.setFixedSize(32, 32)
        self.bell_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton:hover { background-color: rgba(0, 255, 255, 0.1); border-radius: 5px; }
        """)
        layout.addWidget(self.bell_btn)
        
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
            self.status.setText("SECURE")
            self.status.setStyleSheet("color: #00ff00; font-weight: bold; margin-right: 20px;")
        else:
            self.status.setText("THREAT DETECTED")
            self.status.setStyleSheet("color: #ff0055; font-weight: bold; margin-right: 20px;")
