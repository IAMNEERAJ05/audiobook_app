"""
Modern status log component for the audiobook app.
"""

from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel, QScrollBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCharFormat, QColor

class ModernStatusLog(QTextEdit):
    """A modern, styled status log with colored messages."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styling()
        self._setup_formats()
    
    def _setup_styling(self):
        """Setup modern styling for the status log."""
        self.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #333333;
                selection-background-color: #4A90E2;
            }
            QTextEdit:focus {
                border-color: #4A90E2;
            }
            QScrollBar:vertical {
                background: #F1F3F4;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #C1C8CD;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A8B2B9;
            }
        """)
        self.setReadOnly(True)
        self.setMaximumHeight(200)
    
    def _setup_formats(self):
        """Setup text formats for different message types."""
        # Success format (green)
        self.success_format = QTextCharFormat()
        self.success_format.setForeground(QColor("#28A745"))
        self.success_format.setFontWeight(QFont.Bold)
        
        # Error format (red)
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor("#DC3545"))
        self.error_format.setFontWeight(QFont.Bold)
        
        # Warning format (orange)
        self.warning_format = QTextCharFormat()
        self.warning_format.setForeground(QColor("#FD7E14"))
        self.warning_format.setFontWeight(QFont.Bold)
        
        # Info format (blue)
        self.info_format = QTextCharFormat()
        self.info_format.setForeground(QColor("#17A2B8"))
        
        # Default format (dark gray)
        self.default_format = QTextCharFormat()
        self.default_format.setForeground(QColor("#6C757D"))
    
    def add_message(self, message, msg_type="info"):
        """Add a message with specified type."""
        # Get current cursor position
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        
        # Set appropriate format
        if msg_type == "success":
            cursor.setCharFormat(self.success_format)
            prefix = "✓ "
        elif msg_type == "error":
            cursor.setCharFormat(self.error_format)
            prefix = "✗ "
        elif msg_type == "warning":
            cursor.setCharFormat(self.warning_format)
            prefix = "⚠ "
        elif msg_type == "info":
            cursor.setCharFormat(self.info_format)
            prefix = "ℹ "
        else:
            cursor.setCharFormat(self.default_format)
            prefix = "• "
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Insert message
        cursor.insertText(f"[{timestamp}] {prefix}{message}\n")
        
        # Scroll to bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def clear_log(self):
        """Clear all messages."""
        self.clear()
        self.add_message("Log cleared", "info")
    
    def add_success(self, message):
        """Add a success message."""
        self.add_message(message, "success")
    
    def add_error(self, message):
        """Add an error message."""
        self.add_message(message, "error")
    
    def add_warning(self, message):
        """Add a warning message."""
        self.add_message(message, "warning")
    
    def add_info(self, message):
        """Add an info message."""
        self.add_message(message, "info")

class StatusLogWidget(QWidget):
    """A complete status log widget with header."""
    
    def __init__(self, title="Processing Log", parent=None):
        super().__init__(parent)
        self.title = title
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the status log widget UI."""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                padding: 5px;
                background-color: #E9ECEF;
                border-radius: 5px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Status log
        self.status_log = ModernStatusLog()
        layout.addWidget(self.status_log)
        
        self.setLayout(layout)
    
    def add_message(self, message, msg_type="info"):
        """Add a message to the log."""
        self.status_log.add_message(message, msg_type)
    
    def clear_log(self):
        """Clear the log."""
        self.status_log.clear_log()
    
    def add_success(self, message):
        """Add a success message."""
        self.status_log.add_success(message)
    
    def add_error(self, message):
        """Add an error message."""
        self.status_log.add_error(message)
    
    def add_warning(self, message):
        """Add a warning message."""
        self.status_log.add_warning(message)
    
    def add_info(self, message):
        """Add an info message."""
        self.status_log.add_info(message)
