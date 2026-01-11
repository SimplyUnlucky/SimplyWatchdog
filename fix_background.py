from PySide6.QtGui import QImage, QColor

def fix_image():
    img = QImage("ui/icons.png")
    img = img.convertToFormat(QImage.Format_ARGB32)
    
    width = img.width()
    height = img.height()
    
    for y in range(height):
        for x in range(width):
            pixel_color = QColor(img.pixel(x, y))
            
            # Check saturation
            # Checkerboard is gray/black/white -> Low saturation
            # Cyan is High saturation
            
            # Threshold
            if pixel_color.saturation() < 50:
                # Make transparent
                # But wait, if it's very dark (black background), maybe we want to keep it?
                # User says "background behind images", implying the checkerboard.
                # Let's just make it transparent.
                img.setPixelColor(x, y, QColor(0, 0, 0, 0))
            else:
                # Keep it, but maybe ensure it's on transparent?
                # The "glow" might be blended with the checkerboard.
                # If we just keep it, it will have gray edges.
                # Simple fix: Low sat -> transparent. High sat -> keep.
                pass
                
    img.save("ui/icons_fixed.png")
    print("Fixed image saved to ui/icons_fixed.png")

if __name__ == "__main__":
    fix_image()
