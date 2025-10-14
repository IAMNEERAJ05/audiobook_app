"""
Modern progress bar components for the audiobook app.
"""

from PyQt5.QtWidgets import QProgressBar, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient

class ModernProgressBar(QProgressBar):
    """A modern, styled progress bar with gradient."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styling()
    
    def _setup_styling(self):
        """Setup modern styling for the progress bar."""
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #E0E0E0;
                text-align: center;
                font-weight: bold;
                color: white;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #4A90E2, stop: 1 #357ABD);
                border-radius: 10px;
            }
        """)
        self.setMinimumHeight(20)

class ProgressWidget(QWidget):
    """A complete progress widget with label and progress bar."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the progress widget UI."""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #333333;
                padding: 5px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Progress percentage label
        self.percentage_label = QLabel("0%")
        self.percentage_label.setFont(QFont("Segoe UI", 10))
        self.percentage_label.setStyleSheet("""
            QLabel {
                color: #666666;
                padding: 2px;
            }
        """)
        self.percentage_label.setAlignment(Qt.AlignCenter)
        self.percentage_label.setVisible(False)
        layout.addWidget(self.percentage_label)
        
        self.setLayout(layout)
    
    def set_progress(self, value, text=""):
        """Set progress value and optional text."""
        self.progress_bar.setValue(value)
        self.percentage_label.setText(f"{value}%")
        
        if text:
            self.status_label.setText(text)
        
        # Show progress elements when value > 0
        if value > 0:
            self.progress_bar.setVisible(True)
            self.percentage_label.setVisible(True)
        else:
            self.progress_bar.setVisible(False)
            self.percentage_label.setVisible(False)
    
    def set_status(self, text):
        """Set status text."""
        self.status_label.setText(text)
    
    def reset(self):
        """Reset progress to 0."""
        self.set_progress(0, "Ready")
