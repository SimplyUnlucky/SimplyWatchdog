from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QRect, Qt

class AssetManager:
    _instance = None
    
    def __init__(self):
        self.sheet = None
        self.icons = {}

    def _ensure_loaded(self):
        if self.sheet is not None:
            return
        self.sheet = QPixmap("ui/icons.png")
        self._slice_sheet()

    def _slice_sheet(self):
        if self.sheet.isNull():
            return
            
        w = self.sheet.width() // 4
        h = self.sheet.height() // 4
        
        # Row 0
        names_r0 = ["shield", "settings", "bell", "dashboard"]
        for i, name in enumerate(names_r0):
            self.icons[name] = self.sheet.copy(i * w, 0, w, h)
            
        # Row 1
        names_r1 = ["list_tree", "network", "cpu", "memory"]
        for i, name in enumerate(names_r1):
            self.icons[name] = self.sheet.copy(i * w, h, w, h)
            
        # Row 2
        names_r2 = ["disk", "wifi", "activity", "clock"]
        for i, name in enumerate(names_r2):
            self.icons[name] = self.sheet.copy(i * w, h*2, w, h)
            
        # Row 3
        names_r3 = ["zap", "trending_up"]
        for i, name in enumerate(names_r3):
            self.icons[name] = self.sheet.copy(i * w, h*3, w, h)

    def get_icon(self, name):
        self._ensure_loaded()
        return QIcon(self.icons.get(name, QPixmap()))

    def get_pixmap(self, name, size=None):
        self._ensure_loaded()
        pix = self.icons.get(name, QPixmap())
        if size:
            return pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return pix

assets = AssetManager()
