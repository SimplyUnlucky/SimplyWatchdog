from PySide6.QtGui import QImage, QColor

def fix_black_bg():
    img = QImage("ui/icons.png")
    img = img.convertToFormat(QImage.Format_ARGB32)
    
    width = img.width()
    height = img.height()
    
    for y in range(height):
        for x in range(width):
            c = QColor(img.pixel(x, y))
            # Strict Black Check (or very dark)
            if c.red() < 10 and c.green() < 10 and c.blue() < 10:
                img.setPixelColor(x, y, QColor(0, 0, 0, 0))
                
    img.save("ui/icons.png")
    print("Fixed black background.")

if __name__ == "__main__":
    fix_black_bg()
