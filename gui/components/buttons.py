"""
Modern button components for the audiobook app.
"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPalette

class ModernButton(QPushButton):
    """A modern, styled button with hover effects."""
    
    def __init__(self, text, icon=None, primary=False, size="large"):
        super().__init__(text)
        
        # Set button properties
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(50 if size == "large" else 40)
        
        # Set icon if provided
        if icon:
            self.setIcon(icon)
            self.setIconSize(icon.actualSize(icon.availableSizes()[0]))
        
        # Apply styling
        self._apply_styling(primary, size)
        
        # Add hover animation
        self._setup_animation()
    
    def _apply_styling(self, primary, size):
        """Apply modern styling to the button."""
        
        # Font
        font_size = 14 if size == "large" else 12
        font = QFont("Segoe UI", font_size, QFont.Bold)
        self.setFont(font)
        
        if primary:
            # Primary button style (blue gradient)
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #4A90E2, stop: 1 #357ABD);
                    border: none;
                    border-radius: 25px;
                    color: white;
                    padding: 12px 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #5BA0F2, stop: 1 #4A8ACD);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #357ABD, stop: 1 #2A6A9D);
                }
                QPushButton:disabled {
                    background: #CCCCCC;
                    color: #666666;
                }
            """)
        else:
            # Secondary button style (white with border)
            self.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 2px solid #4A90E2;
                    border-radius: 25px;
                    color: #4A90E2;
                    padding: 10px 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #F0F8FF;
                    border-color: #5BA0F2;
                    color: #5BA0F2;
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: #E0F0FF;
                    border-color: #357ABD;
                    color: #357ABD;
                }
                QPushButton:disabled {
                    background: #F5F5F5;
                    border-color: #CCCCCC;
                    color: #999999;
                }
            """)
    
    def _setup_animation(self):
        """Setup hover animation."""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

class IconButton(ModernButton):
    """A button with an icon and text."""
    
    def __init__(self, text, icon_path=None, primary=True):
        icon = QIcon(icon_path) if icon_path else None
        super().__init__(text, icon, primary)

class ActionButton(ModernButton):
    """A button specifically for actions like Upload, Library, etc."""
    
    def __init__(self, text, action_type="primary"):
        primary = action_type == "primary"
        super().__init__(text, primary=primary, size="large")
        
        # Add action-specific styling
        if action_type == "success":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #28A745, stop: 1 #1E7E34);
                    border: none;
                    border-radius: 25px;
                    color: white;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #34CE57, stop: 1 #28A745);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #1E7E34, stop: 1 #155724);
                }
            """)
        elif action_type == "info":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #17A2B8, stop: 1 #138496);
                    border: none;
                    border-radius: 25px;
                    color: white;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #20C997, stop: 1 #17A2B8);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #138496, stop: 1 #0F6674);
                }
            """)
